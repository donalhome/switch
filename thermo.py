#!/usr/bin/env python
import sqlite3 as sqlite
from os.path import expanduser
import os
import datetime as DT
import time
import smbus
from ctypes import c_short

DEVICE = 0x77 # Default device I2C address
 
#bus = smbus.SMBus(0)  # Rev 1 Pi uses 0
bus = smbus.SMBus(1) # Rev 2 Pi uses 1 
 
def convertToString(data):
  # Simple function to convert binary data into
  # a string
  return str((data[1] + (256 * data[0])) / 1.2)

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
  return c_short((data[index] << 8) + data[index + 1]).value

def getUshort(data, index):
  # return two bytes from data as an unsigned 16-bit value
  return (data[index] << 8) + data[index + 1]

def readBmp180Id(addr=DEVICE):
  # Register Address
  REG_ID     = 0xD0

  (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
  return (chip_id, chip_version)
  
def readBmp180(addr=DEVICE):
  # Register Addresses
  REG_CALIB  = 0xAA
  REG_MEAS   = 0xF4
  REG_MSB    = 0xF6
  REG_LSB    = 0xF7
  # Control Register Address
  CRV_TEMP   = 0x2E
  CRV_PRES   = 0x34 
  # Oversample setting
  OVERSAMPLE = 3    # 0 - 3
  
  # Read calibration data
  # Read calibration data from EEPROM
  cal = bus.read_i2c_block_data(addr, REG_CALIB, 22)

  # Convert byte data to word values
  AC1 = getShort(cal, 0)
  AC2 = getShort(cal, 2)
  AC3 = getShort(cal, 4)
  AC4 = getUshort(cal, 6)
  AC5 = getUshort(cal, 8)
  AC6 = getUshort(cal, 10)
  B1  = getShort(cal, 12)
  B2  = getShort(cal, 14)
  MB  = getShort(cal, 16)
  MC  = getShort(cal, 18)
  MD  = getShort(cal, 20)

  # Read temperature
  bus.write_byte_data(addr, REG_MEAS, CRV_TEMP)
  time.sleep(0.005)
  (msb, lsb) = bus.read_i2c_block_data(addr, REG_MSB, 2)
  UT = (msb << 8) + lsb

  # Read pressure
  bus.write_byte_data(addr, REG_MEAS, CRV_PRES + (OVERSAMPLE << 6))
  time.sleep(0.04)
  (msb, lsb, xsb) = bus.read_i2c_block_data(addr, REG_MSB, 3)
  UP = ((msb << 16) + (lsb << 8) + xsb) >> (8 - OVERSAMPLE)

  # Refine temperature
  X1 = ((UT - AC6) * AC5) >> 15
  X2 = (MC << 11) / (X1 + MD)
  B5 = X1 + X2
  temperature = (B5 + 8) >> 4

  # Refine pressure
  B6  = B5 - 4000
  B62 = B6 * B6 >> 12
  X1  = (B2 * B62) >> 11
  X2  = AC2 * B6 >> 11
  X3  = X1 + X2
  B3  = (((AC1 * 4 + X3) << OVERSAMPLE) + 2) >> 2

  X1 = AC3 * B6 >> 13
  X2 = (B1 * B62) >> 16
  X3 = ((X1 + X2) + 2) >> 2
  B4 = (AC4 * (X3 + 32768)) >> 15
  B7 = (UP - B3) * (50000 >> OVERSAMPLE)

  P = (B7 * 2) / B4

  X1 = (P >> 8) * (P >> 8)
  X1 = (X1 * 3038) >> 16
  X2 = (-7357 * P) >> 16
  pressure = P + ((X1 + X2 + 3791) >> 4)

  return (temperature/10.0,pressure/ 100.0)

def read_temp_raw(device_file): #a function that grabs the raw temperature data from the sensor
	f_1 = open(device_file, 'r')
	lines_1 = f_1.readlines()
	f_1.close()
	return lines_1
 
 
def read_temp(device_file): #a function that checks that the connection was good and strips out the temperature
	lines = read_temp_raw(device_file)
	while lines[0].strip()[-3:] != 'YES':
		time.sleep(0.2)
		lines = read_temp_raw(device_file)
	equals_pos = lines[1].find('t=')
	temp = float(lines[1][equals_pos+2:])/1000
	return temp
	
insrtstr='insert into  Log (?,?,?,)' #note Null for ptr as we don't know it
db=sqlite.connect(expanduser('~/projekt/switch/VindThermo.db'))
cur=db.cursor()
commandedT=cur.execute('select Tset from ControlTable order by Timestamp desc limit 1').fetchone()[0]
switchpos=cur.execute('select switchpos from Log order by timestamp desc limit 1').fetchone()[0]
print 'commanded T = ', commandedT
print 'switchpos = ', switchpos 
#~ Tvind=85
#~ while Tvind==85:
	#~ Tvind=read_temp('/sys/bus/w1/devices/28-00000704b7f5/w1_slave')
	#~ print Tvind
	#Tvind=17
(Tvind, Pressure)=readBmp180()	
if Tvind >commandedT :
	 #os.system('ssh pi@192.168.1.6 /home/pi/projekt/switch/sudoswitchoff.sh')
	 os.system('sudo ~/projekt/switch/myswitch.py 2 0')
	 if switchpos==1:
		 cur.execute('insert into Log values (?,?,?)',
			((DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), Tvind, 0)))
else: 
	 #os.system('ssh pi@192.168.1.6 /home/pi/projekt/switch/sudoswitchon.sh')
	 os.system('sudo ~/projekt/switch/myswitch.py 2 1')
	 if switchpos==0:
		 cur.execute('insert into Log values (?,?,?)',
			((DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), Tvind, 1)))
db.commit()
cur.close()
db.close()
