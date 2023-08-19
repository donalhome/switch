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
micros=250 #microsec
NONE=0
REPEATS=10

def transmit_string(pi, gpio, code):

	#print(code)
	
	pi.wave_clear() # clear all waveforms
	wf=[]
	#bits=[[1,0,0,0,0,0,0,0,0,0],
		  #[1,0,0,0,0],
		  #[1,0,1,0,0,0,0],
		  #[1,0,1,0,1,0,0,0,0],
		  #[0,0,0,0,0,0,0,0,0]	
		 #]
	for i in code:
		i=int(i)
		if i==0 :
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 10 * micros))
		elif i==1:
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 5 * micros))
		elif i==2:
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 1 * micros))
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 5 * micros))
		elif i==3:
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 1 * micros))
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 1 * micros))
			wf.append(pigpio.pulse(1<<gpio, NONE, 1 * micros))
			wf.append(pigpio.pulse(NONE, 1<<gpio, 5 * micros))
		elif i==4:
			wf.append(pigpio.pulse(NONE, 1<<gpio, 10 * micros))
	
	wf.append(pigpio.pulse(NONE, 1<<gpio, 3 * micros))
	pi.wave_add_generic(wf)
	wid = pi.wave_create()
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
	codes= [[	"02212322222212223212222312322222214",
				"02212322222212223212222312322222124",
				"02212322222212223212222312322221314",
				"02131322213122312222322122322222214",
				"02131322213122312222322122322222124",
				"02131322213122312222322122322221314"],
			[	"02212322222212223212222312321322214",
				"02212322222212223212222312321322124",
				"02212322222212223212222312321321314",
				"02131322213122312222322122321322214",
				"02131322213122312222322122321322124",
				"02131322213122312222322122321321314"]]
	
	#pi = pigpio.pi("192.168.1.10") # connect to  Pi in hall 
	pi = pigpio.pi("localhost") # connect to  Pi locally

	if pi!=0 : pi = pigpio.pi("localhost") # connect to  Pi locally
	pi.set_mode(GPIO, pigpio.OUTPUT)
	sw=int(sys.argv[1])

	if int(sys.argv[2]):
		transmit_string(pi, GPIO,codes[1][sw-1])
	else: 
		transmit_string(pi, GPIO,codes[0][sw-1])
	
	
	while pi.wave_tx_busy():
	   time.sleep(0.1)
	
	pi.stop() # disconnect from Pi
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
