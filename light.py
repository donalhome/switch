import smbus
import datetime as DT
import numpy as np
import os
import time

adr=0x39
bus=smbus.SMBus(1)
#turn on the detector
bus.write_i2c_block_data(adr,0x00,[0x03,])
while True:
	b=bus.read_i2c_block_data(adr,0x8C,2)
	ch0=b[1]*256.0 + b[0]
	b=bus.read_i2c_block_data(adr,0x8E,2)
	ch1= b[1]*256.0 + b[0]
	if ch1/ch0 <=0.50: Lux=0.0304*ch0-0.062*ch0*(ch1/ch0)**1.4
	elif ch1/ch0<=0.61:Lux=0.0224*ch0-0.0231*ch1 
	elif ch1/ch0<=0.80:Lux = 0.0128*ch0 - 0.0153*ch1
	elif ch1/ch0<=1.3:Lux = 0.00146*ch0 - 0.00112*ch1
	else: Lux=0
	print Lux
	time.sleep(1)
