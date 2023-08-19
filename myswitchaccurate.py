#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  myswitchaccurate.py
#  
#  Copyright 2016 Donal Murtagh <donal.murtagh@chalmers.se>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  
import sys
import time

import pigpio
micros=300 #microsec
NONE=0
REPEATS=10

def transmit_string(pi, gpio, code):

#	print(code)
	
	pi.wave_clear() # clear all waveforms
	
	wf=[]
	for i in code: 
		if int(i) :
			wf.append(pigpio.pulse(1<<gpio, NONE, 3 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 1 * micros))
		else: 
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 3 * micros))
	
	wf.append(pigpio.pulse(NONE, 1<<gpio, 3 * micros))
#	print wf
	pi.wave_add_generic(wf)
	wid = pi.wave_create()
	print (wid)
	if wid >= 0:
		for i in range(REPEATS) : 
			pi.wave_send_once(wid)
			while pi.wave_tx_busy():
				time.sleep(0.01)
 
def main(args):
	if len(sys.argv) < 3:
		print ("usage:sudo python %s int_device int_state (e.g. '%s 2 1' switches device 2 on)" % \
			(sys.argv[0], sys.argv[0]) ) 
		sys.exit(1)
	
	GPIO=17	
	codes=[["0000000000000000000101010", "0000000001000000000101010", "0000000000010000000101010"],
		   ["0000000000000000000101000", "0000000001000000000101000", "0000000000010000000101000"]]
	
	pi = pigpio.pi("192.168.1.10") # connect to  Pi in sovrum
	print (pi) 
	if pi!=0 : pi = pigpio.pi("localhost") # connect to  Pi locally
	pi.set_mode(GPIO, pigpio.OUTPUT)
	sw=int(sys.argv[1])
	if int(sys.argv[2]):
		transmit_string(pi, GPIO,codes[0][sw-1])
	else: 
		transmit_string(pi, GPIO,codes[1][sw-1])
	
	
	while pi.wave_tx_busy():
	   time.sleep(0.1)
	
	pi.stop() # disconnect from Pi
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
