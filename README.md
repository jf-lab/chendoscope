# CHEndoscope Overview
### Contents

- [Acquiring images with your CHEndoscope](#chendoscope-acquisition) 
	- [Installing acquisition code](#installation-windows)
	- [Running the acquisition software](#to-run-windows)

1. Assembly of your CHEndoscope
3. Analysis of calcium imaging videos: [jflab-minipipe](https://github.com/jf-lab/jflab-minipipe)

# CHEndoscope assembly
The CHEndoscope consists of 4 plastic components that can be 3D printed

![3D printed components of the CHEndoscope](printed-parts.png)

# CHEndoscope acquisition

CHEndoscope acquisition software allows you to capture video from the CHEndoscope's Ximea USB camera.

## Installation (Windows)

**Dependencies:**

- Python 3.5
  - numpy
  - scipy

1. Install opencv
	- Go to "http://www.lfd.uci.edu/~gohlke/pythonlibs/#opencv", download "opencv_python‑3.2.0+contrib‑cp35‑cp35m‑win_amd64.whl"
	- In a command line, run 
		`pip install "path\to\file\opencv_python‑3.2.0+contrib‑cp35‑cp35m‑win_amd64.whl`

2. Install XIMEA driver - https://www.ximea.com/downloads/recent/XIMEA_Installer.exe

3. Install python bindings for XIMEA driver
	- Download "https://github.com/cyanut/pyximea/raw/master/dist/pyximea-0.0.2-cp35-cp35m-win_amd64.whl"
	- In a command line, run
		`pip install "path\to\file\pyximea-0.0.2-cp35-cp35m-win_amd64.whl"`

4. Test that everything works
	- In a command line, run
		`python -i`
	- then run
		`import numpy,scipy,cv2,pyximea`
	-> python should not complain about any errors

5. Download CHEndoscope acquisition code
	- Go to https://github.com/cyanut/scope-recorder, download the code as zip
	- extract the code to a directory 

6. Download ffmpeg
	- Go to "https://ffmpeg.zeranoe.com/builds/", choose a stable version, 64-bit, static, then download
	- extract the three executable files in the "bin" directory to a new directory

7. Add ffmpeg directory to system path
	- In the windows search bar, type "environment", open the "Edit system environment variable" dialog
	- Click "environment variables ..."
	- In the new dialog, select the "Path" variable, click on "edit"
	- Put in the path for ffmpeg
8. Test
	- In a command line, type `ffmpeg`. It should show a bunch of stuff but not complain about unable to find "ffmpeg"

9. Install nmap (to communicate with the recorder for changing gain, exposure etc.)
	- https://nmap.org/download.html#windows, download a stable version
	- During install, make sure the "NCat" and "Register system path" are selected

10. Install VLC (for video playback)

Installation complete!

## To run (Windows)

1. Open a new cmd window
    - `cd [path for storing video files]`
    - `python "path\to\scope-recorder-master\vid.py"`

2. To change gains/exposure etc:
    - Open a second cmd window and run 
		`ncat -u 127.0.0.1 6557`
    - Then type for example:
		`[set_gain 10]`

