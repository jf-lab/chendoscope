from __future__ import (absolute_import, division, print_function, unicode_literals)

import cv2
import subprocess
import numpy as np
from datetime import datetime
import time
import argparse
import socket
import struct
import os

try:
    import cPickle as pickle
except ImportError:
    import pickle
try:
    import queue
except ImportError:
    import Queue as queue
import threading

try:
    import pyximea as xi
except ImportError:
    xi = None

#colour in BGR
blue = (0xa6/0xff, 0x6d/0xff, 0x33/0xff)
green = (0x7e/0xff, 0xab/0xff, 0x2b/0xff)
red = (0x40/0xff, 0x7e/0xff, 1)
yellow = (0x40/0xff, 0xb1/0xff, 1)



def get_video_name():
    return datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + '.mkv'
    
def get_video_pipe(fname, shape, rate):
    print(shape)
    if len(shape) == 2:
        pix_fmt = 'gray16'
        target_pix_fmt = 'yuv420p16'
    elif len(shape) == 3 and shape[2] == 3:
        pix_fmt = 'rgb48'
        target_pix_fmt = 'yuv444p16'
    shape = shape[:2]
    cmdstr = ('ffmpeg', '-y', '-r', str(rate),\
            '-f', 'rawvideo',
            '-pix_fmt', pix_fmt,
            '-s', '%ix%i' %shape[::-1],
            '-i', '-',
            '-c:v', 'ffv1', '-level', '3',
            #'-c:v', 'ffvhuff',
            #'-c:v', 'libx264', '-preset', 'medium', '-crf', '0',
            '-pix_fmt', target_pix_fmt,
            fname)
    print(cmdstr)
    p = subprocess.Popen(cmdstr, stdin=subprocess.PIPE, shell=False, bufsize=1024576)
    
    return p.stdin



class RecorderState(object):
    def __init__(self):
        self.is_bg = False
        self.is_writing = False
        self.split_channel = False

class VideoRecorder(object):

    def __init__(self, vid_name = None, sync_params = [None] * 3, video_rate = 20):
        '''
        sync_params = (master_addr, data_port, listening_port)
        '''

        self.vid_stream = None
        
        (master_addr, master_data_port, listening_port) = sync_params
        self.bg = bg
        self.mean_img = None
        self.prev_frame = None
        self.current_frame = None
        self.command_queue = queue.Queue()
        self.listening_socket = None
        self.is_listening = False
        self.is_sending = False
        self.vid_name = vid_name
        self.frames = self.frame_generator()
        self.paradigm_name = ""
        self.video_duration = -1
        self.fps = None
        self.gain = None
        self.exposure = None
        
        
        if master_addr is not None and master_data_port is not None:
            self.listening_thread = True
            self.master_addr = (master_addr, master_data_port)

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setblocking(False)
            self.data_socket = sock

        self.listening_port = listening_port
        self.video_rate = video_rate
        self.timestamp = []

        self.state = RecorderState()
        
        self.pixel_level = 256
        self.is_ximea = False

    def frame_generator(self):
        vid_name = self.vid_name
        vid = None
        if vid_name:
            vid = cv2.VideoCapture(vid_name)
            _, frame = vid.read()
        elif xi:
            try: 
                vid = xi.Xi_Camera(DevID=0)
            except:
                vid = None
            if vid:
                self.is_ximea = True
                vid.set_debug_level("Warning")
                vid.set_binning(4, skipping=False)
                vid.set_param("shutter_type", 0)
                name = xi.get_device_info(0, "device_name")                

                if name[:5] == "MU9PC":
                    #colour camera
                    vid.set_param("imgdataformat", 2)
                    self.pixel_level = 2 ** 8
                else:
                    vid.set_param("imgdataformat", 6)
                    self.pixel_level = 2 ** 12

                self.exposure = 50000
                vid.set_param("exposure", self.exposure)
                self.gain = 15
                vid.set_param("gain", self.gain)
                _, frame = vid.read()
                print(np.max(frame))

        if vid is None:
            vid = cv2.VideoCapture(1)
            _, frame = vid.read()
            if frame is None:
                vid = cv2.VideoCapture(0)
                _, frame = vid.read()
        self.vid_stream = vid
        while not frame is None:
            timestamp = time.time()
            frame = np.float32(frame) / self.pixel_level
            yield (frame, timestamp)
            _, frame = vid.read()



    def _listen_for_command(self):
        while self.is_listening:
            data, addr = self.listening_socket.recvfrom(4096)
            self.command_queue.put(data)

    def _listen(self):
        if self.listening_port is None:
            return
        #set up listening UDP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", self.listening_port)) 
        self.listening_socket = sock
        self.is_listening = True
        self.listening_thread = threading.Thread(target = self._listen_for_command)
        self.listening_thread.daemon = True
        self.listening_thread.start()

    def _send_data(self, data):
        if self.data_socket:
            return self.data_socket.sendto(data, self.master_addr)

    def _thread_send_data(self, rate=25):
        sleep_time = 1 / rate
        while self.is_sending:
            if self.fps:
                sleep_time = 1.0 / self.fps
            if self.state.is_writing:
                fps = self.fps
            else:
                fps = 0
            if fps is None:
                fps = 0
            self._send_data(struct.pack("!IIf", 1, 1, fps))
            time.sleep(sleep_time)


    def start(self):
        time_start_frame = None
        self._listen()
        self.is_sending = True
        self.sending_thread = threading.Thread(target=self._thread_send_data, kwargs={"rate":25})
        self.sending_thread.daemon = True
        self.sending_thread.start()
        fps = None
        last_timestamp = None
        fps_counter = 0
        fps_average = 0

        for frame, timestamp in self.frames:
            try:
                command = self.command_queue.get_nowait()
            except queue.Empty:
                command = None

            self.process_command(command)
            self.current_frame = frame
            self.current_timestamp = timestamp
            
            if self.state.is_bg:
                self.bg_count += 1
                self.bg += (frame - self.bg) / self.bg_count
                cv2.imshow("bg", self.bg)


            if len(frame.shape) == 3:
                frame_show = frame.copy()
            elif len(frame.shape) == 2:
                frame_show = np.dstack([frame, frame, frame])


            if self.state.split_channel and len(frame_show.shape) == 3:
                cv2.imshow("Blue", frame_show[:,:,0])
                cv2.imshow("Green", frame_show[:,:,1])
                cv2.imshow("Red", frame_show[:,:,2])
                diffrb = frame_show[:,:,2] - frame_show[:,:,0]
                diffrb[diffrb < 0] = 0
                #diffrb = (diffrb / (np.max(diffrb)+0.01))
                cv2.imshow("Red-Blue", diffrb)


            if self.state.is_writing:
                if len(frame.shape) == 3:
                    ftmp = np.uint16(frame * 65535)[...,[2,1,0]]#bgr -> rgb
                else:
                    ftmp = np.uint16(frame * 65535)
                self.video_pipe.write(ftmp.tobytes())
                self.timestamp.append(timestamp)
                recording_time = timestamp - self.video_start_time
                cv2.putText(frame_show, 
                        "Recording: {:.2f}s of {}s".format(recording_time, self.video_duration), 
                        (0, 15), cv2.FONT_HERSHEY_TRIPLEX, 0.5, red)
                if self.video_duration > 0 and recording_time > self.video_duration:
                    self._write_end()
            else:
                cv2.putText(frame_show, 
                        "{:.2f}, recording duration: {}s".format(timestamp, self.video_duration), 
                        (0, 15), cv2.FONT_HERSHEY_TRIPLEX, 0.5, blue)

            if fps:
                cv2.putText(frame_show, 
                        "FPS: {:.1f}".format(fps),
                        (self.current_frame.shape[1]-100, 15), 
                        cv2.FONT_HERSHEY_TRIPLEX, 0.5, green)
            expo_str = ""
            gain_str = ""
            if self.exposure:
                expo_str = "exposure = {} us".format(self.exposure)
            if self.gain:
                gain_str = "gain = {}".format(self.gain)
            cam_str = ", ".join([expo_str, gain_str])
            if cam_str:
                cv2.putText(frame_show, 
                        cam_str,
                        (self.current_frame.shape[1]-304, 40), 
                        cv2.FONT_HERSHEY_TRIPLEX, 0.5, green)


            if self.bg is not None:
                fg = frame - self.bg
                cv2.imshow("fg", fg)

            cv2.imshow("raw", frame_show)
            
            if self.vid_name is not None: #it's playback, control frame rate
                process_time = time.time() - timestamp
                wait_time = int(1000 * (1.0 / self.video_rate - process_time))
                wait_time = 4 #just in case the rest takes a while
                if wait_time < 1:
                    wait_time = 1
            else:
                wait_time = 1
            k = cv2.waitKey(wait_time)
            self.process_keypress(k)
            if last_timestamp:
                fps = 1 / (timestamp - last_timestamp)
            self.fps = fps
            last_timestamp = timestamp

    def process_keypress(self, k):

        k = k % 256
        if k == ord(' '): 
            cv2.waitKey(0)
        elif k == 27: #'esc'
            self.process_command("[quit]")

        elif k == ord('b'): #background
            self.process_command("[background]")

        elif k == ord('w'): #record
            self.process_command("[start]")
            
        elif k == ord('s'): #show raw
            self.process_command("[end]")

        elif k == ord('3'):
            self.process_command("[split channel]")

        elif k == ord("["):
            self.process_command("[set_gain {}]".format(self.gain - 1))
            
        elif k == ord("]"):
            self.process_command("[set_gain {}]".format(self.gain + 1))
        elif k == ord("-"):
            self.process_command("[set_exposure {}]".format(self.exposure - 1000))
        elif k == ord("="):
            self.process_command("[set_exposure {}]".format(self.exposure + 1000))
        else: 
            return

    def process_command(self, command):

        if command is None:
            return
        if type(command) == type(b"x"):
            command = command.decode("utf-8")
        command = command.strip().lower()
        if command == "[start]":
            print("Experiment started, recording ...")
            self._write_start()
        elif command == "[background]":
            self._bg_start()
        elif len(command) > 5 and command[:5] == "[seek":
            pass
        elif command == "[end]":
            self._bg_end()
            self._write_end()
            self._split_channel_end()
        elif command == "[quit]":
            self._bg_end()
            self._write_end()
            quit()
        elif len(command) > 6 and command[:6]=="[ipadr":
            pass
        elif len(command) > 6 and command[:6] == "[stmnm":
            print(command)
            if len(command) == 24:
                paradigm_name  = command[6:]
            else:
                paradigm_name = command[6:-1]
            print("Selected paradigm: ", paradigm_name)
            self.paradigm_name = paradigm_name
        elif len(command) > 6 and command[:6] == "[durtn":
            duration = int(command[6:-1])
            print(command)
            print("Set recording duration to {}s".format(duration))
            self.video_duration = duration
        elif command == '[split channel]':
            self._split_channel_start()

        elif len(command) > 5 and command[:5] in {"[set_", "[get_"}:
            command = command[:-1]
            print(command)
            comm_parsed = command[5:].split(" ")
            comm_name = comm_parsed[0]
            if len(comm_parsed) > 1:
                comm_param = int(comm_parsed[1]) #single argument for now
            else:
                comm_param = ""
            op = command[1:4] #set or get
            if self.is_ximea:
                if op == "set":
                    print("setting {} to {}".format(comm_name, comm_param))
                    self.vid_stream.set_param(comm_name, comm_param)
                    if comm_name == "gain":
                        self.gain = int(comm_param)
                    elif comm_name == "exposure":
                        self.exposure = int(comm_param)
                elif op == "get":
                    comm_param = self.vid_stream.get_param(comm_name)
                    print("Pamameter {} equals {}".format(comm_name, comm_param))
                '''
                except e:
                    print("Cannot {} pamameter {} as {}".format(op, comm_name, comm_param))
                '''

        else:
            print(command)
            return


    def _bg_start(self):
        if self.state.is_bg:
            return
        self.bg = np.zeros_like(self.current_frame)
        self.bg_count = 0
        self.state.is_bg = True
        if self.state.is_writing:
            self._write_end()
        
    def _bg_end(self):
        if not self.state.is_bg:
            return
        self.bg_count = None
        self.state.is_bg = False

    def _write_start(self):
        if self.state.is_writing:
            return
        self.vid_path = get_video_name()
        self.data_path = self.vid_path + ".pkl"
        if self.state.is_bg:
            self._bg_end()
        self.video_pipe = get_video_pipe(self.vid_path, self.current_frame.shape, rate=self.fps)
        self.state.is_writing = True
        self.video_start_time = self.current_timestamp
        
    def _write_end(self):
        if not self.state.is_writing:
            return
        with open(self.data_path, "wb") as data_out:
            pickle.dump({"bg":self.bg, "timestamp":self.timestamp, "paradigm_name":self.paradigm_name, "video_duration":self.video_duration}, data_out)
        self.paradigm_name = ""
        self.video_duration = -1
        self.video_pipe.close()
        self.video_start_time = None
        self.video_pipe = None
        self.vid_path = None
        self.data_path = None
        self.timestamp = []
        self.state.is_writing = False


    def _split_channel_start(self):
        self.state.split_channel = True

    def _split_channel_end(self):
        self.state.split_channel = False


        
def get_args():
    parser = argparse.ArgumentParser(\
            description = "In vivo calcium imaging data recorder.",
            formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("input",
            help="Input video source number. Integer for live video, directory path for stored video.",
            nargs="?",
            default=None)
    parser.add_argument("-o", "--output",
            help="Output directory for recording, will create if not exist.")
    parser.add_argument("-l", "--listen-port",
            help="Port number to listen for command",
            type=int,
            default = 6557)
    parser.add_argument("-m", "--master-addr",
            help="IP address of the master FreezeFrame computer",
            default = "127.0.0.1")
    parser.add_argument("-p", "--data-port",
            help="Port number of the master FreezeFrame computer for data",
            type=int,
            default = 6548)
    return parser.parse_args()

if __name__ == "__main__":
    import json

    args = get_args()
    vid = None
    bg = None
    if args.input is not None:
        vid = args.input
        if os.path.exists(args.input + ".pkl"):
            with open(args.input + ".pkl") as bg_file:
                data = pickle.load(bg_file)
            bg = data["bg"]
    vid_recorder = VideoRecorder(vid_name=args.input, sync_params=(args.master_addr, args.data_port, args.listen_port))
    vid_recorder.start()
    quit()

