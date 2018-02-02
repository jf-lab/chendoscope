EESchema Schematic File Version 2
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:mylib
LIBS:test-cache
EELAYER 25 0
EELAYER END
$Descr USLetter 11000 8500
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L MU9P_MH_CONN_M P1001
U 1 1 57082062
P 3600 2450
F 0 "P1001" H 3600 3000 50  0000 C CNN
F 1 "MU9P_MH_CONN_M" H 3600 1900 50  0000 C CNN
F 2 "footprints:DF12A-20DS-M" H 3600 2450 50  0001 C CNN
F 3 "" H 3600 2450 50  0000 C CNN
	1    3600 2450
	1    0    0    -1  
$EndComp
NoConn ~ 3000 2600
NoConn ~ 3000 2700
NoConn ~ 4200 2800
NoConn ~ 4200 2900
NoConn ~ 3000 2000
NoConn ~ 3000 2100
Wire Wire Line
	4200 2400 4200 2700
Connection ~ 4200 2500
Connection ~ 4200 2600
Wire Wire Line
	3000 2400 3000 2500
Wire Wire Line
	3000 2450 4200 2450
Connection ~ 4200 2450
Connection ~ 3000 2450
Wire Wire Line
	4650 2500 4200 2500
Wire Wire Line
	4200 2100 4750 2100
NoConn ~ 4200 2200
NoConn ~ 3000 2300
NoConn ~ 3000 2800
NoConn ~ 3000 2900
Wire Wire Line
	3000 2200 2750 2200
Wire Wire Line
	2750 2200 2750 3300
Wire Wire Line
	2750 3300 4500 3300
$Comp
L CONN_01X05 P1002
U 1 1 573CA4D6
P 5100 2500
F 0 "P1002" H 5100 2800 50  0000 C CNN
F 1 "CONN_01X05" V 5200 2500 50  0000 C CNN
F 2 "footprints:SMD_05_Hole" H 5100 2500 50  0001 C CNN
F 3 "" H 5100 2500 50  0000 C CNN
	1    5100 2500
	1    0    0    -1  
$EndComp
Wire Wire Line
	4650 2300 4650 2500
Wire Wire Line
	4750 2100 4750 2500
Wire Wire Line
	4750 2500 4900 2500
Wire Wire Line
	4200 2000 4500 2000
Wire Wire Line
	4500 2000 4500 2600
Wire Wire Line
	4500 2600 4900 2600
Wire Wire Line
	4500 3300 4500 2700
Wire Wire Line
	4500 2700 4900 2700
Text Label 4250 2300 0    60   ~ 0
+5V
Text Label 4250 2500 0    60   ~ 0
GND
Text Label 4600 2100 0    60   ~ 0
D+
Text Label 4550 2600 0    60   ~ 0
D-
Text Label 3850 3300 0    60   ~ 0
GX2
Wire Wire Line
	4900 2300 4650 2300
Wire Wire Line
	4200 2300 4450 2300
Wire Wire Line
	4450 2300 4450 2400
Wire Wire Line
	4450 2400 4900 2400
$EndSCHEMATC
