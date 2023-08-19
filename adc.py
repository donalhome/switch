import smbus
import datetime as DT
import numpy as np
import os
import time

adr=0x28
bus=smbus.SMBus(1)
channel =2
# The initiate and read are all on call.  The cmd is controlregister that selects the SDC
# The data come out with the first 8 high bits in the first byte and the last four bits 
# right shifted.   

while True:
	aa=bus.read_i2c_block_data(adr,0x80|(channel<<4),2)
	print float((aa[0]<<4)+(aa[1]>>4))/(2**12-1)*5 
	time.sleep(1)
