#!/usr/bin/env python
"""
"elropi.py" for switching Elro devices using Python on Raspberry Pi
by Heiko H. 2012

This file uses RPi.GPIO to output a bit train to a 433.92 MHz transmitter, allowing you
to control light switches from the Elro brand.

Credits:
This file is mostly a port from C++ and Wiring to Python and the RPi.GPIO library, based on 
C++ source code written by J. Lukas:
	http://www.jer00n.nl/433send.cpp
and Arduino source code written by Piepersnijder:
	http://gathering.tweakers.net/forum/view_message/34919677
Some parts have been rewritten and/or translated.

This code uses the Broadcom GPIO pin naming by default, which can be changed in the 
"GPIOMode" class variable below. 
For more on pin naming see: http://elinux.org/RPi_Low-level_peripherals

Version 1.0
"""

import time
import RPi.GPIO as GPIO

class RemoteSwitch(object):
	repeat = 5 # Number of transmissions
	pulselength = 200 # microseconds
	GPIOMode = GPIO.BCM
	
	def __init__(self, pin=4):
		''' 
		devices: A = 1, B = 2, C = 4, D = 8, E = 16  
		key: according to dipswitches on your Elro receivers
		pin: according to Broadcom pin naming
		'''		
		self.pin = pin 
		GPIO.setmode(self.GPIOMode)
		GPIO.setup(self.pin, GPIO.OUT)
	
	def switch(self,code):
		bangs=[]
		bits=[[1,0,0,0,0,0,0,0,0,0],
			  [1,0,0,0,0],
			  [1,0,1,0,0,0,0],
			  [1,0,1,0,1,0,0,0,0],
			  [0,0,0,0,0,0,0,0,0]	
			 ]
		for i in code:
			bit=int(i)
			bangs.extend(bits[bit])
		print bangs, len(bangs)
		GPIO.output(self.pin, GPIO.LOW)
		for z in range(self.repeat):
			for b in bangs:
				GPIO.output(self.pin, b)
				time.sleep(self.pulselength/1000000.)
			time.sleep(self.pulselength/100000.)
		
		
if __name__ == '__main__':
	import sys
	GPIO.setwarnings(False)
	
	if len(sys.argv) < 3:
		print "usage:sudo python %s int_device int_state (e.g. '%s 2 1' switches device 2 on)" % \
			(sys.argv[0], sys.argv[0])  
		sys.exit(1)
		
	#codes=[["0000000000000000000101010", "0000000001000000000101010", "0000000000010000000101010"],
	#	    ["0000000000000000000101000", "0000000001000000000101000", "0000000000010000000101000"]]
	codes= [["02212322222212223212222312322222214"],
			["02212322222212223212222312321322214"],
			]
	

	# change the pin accpording to your wiring
	default_pin =17
	device = RemoteSwitch( pin=default_pin)
	sw=int(sys.argv[1])
	if int(sys.argv[2]):
		device.switch(codes[0][sw-1])
	else: 
		device.switch(codes[1][sw-1])
