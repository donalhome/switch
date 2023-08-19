#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  thermorum.py
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
import sqlite3 as sqlite
from os.path import expanduser
import subprocess
import datetime as DT
import time
from sensors import read_temp,readBmp180

class rum ():
	
	def __init__(self,name,ip,device,switches):
		self.name=name
		self.ip=ip
		self.device=device
		self.switches=switches
		return 
	
	def set_temp(self,db,newtemp,newtempnatt): 
		if ((newtemp>0.) and (newtemp<25.) and (newtempnatt>0.) and (newtempnatt<25.)) :
			cur=db.cursor()
			tt=cur.execute ('insert into Control_' + self.name + ' values (?,?,?)',(DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), newtemp, newtempnatt)) 
			db.commit()
			cur.close()
			print  ("New temps for " + self.name + " set to " + str(newtemp) + " daytime and " + str(newtempnatt) + " nighttime\n")
			return 0
		else:
			print ('Temps not valid!')
			return 100
			
	def report_temp(self): 
		if self.device=="BMP": 
			try:
				(T, Pressure)=readBmp180()
			except:
				T=24.0
				pass
		else:
			cmd = 'ssh pi@' + self.ip + ' "cat /sys/bus/w1/devices/' + self.device + '/w1_slave" >/home/pi/xxx'
			T=85
			try:
				while T==85:
					subprocess.call ([cmd],shell=True)			
					T=read_temp('/home/pi/xxx')
			except: 
				T=24.0 #set high to keep radiator off since the sensor is not working
				pass
		return T	
		
	def control_temp(self,db):	
		cur=db.cursor()
		nnC = 'Control_'+self.name
		nnL = 'Log_'+self.name
		commandedT=cur.execute('select Tset,Tnatt from ' +  nnC +' order by Timestamp desc limit 1').fetchone()
		switchpos=cur.execute('select switchpos from '+ nnL + ' order by timestamp desc limit 1').fetchone()[0]
		#if DT.datetime.now().hour >=23 or DT.datetime.now().hour < 6:
		if  DT.datetime.now().hour < 6:
			commandedT=commandedT[1] #night 
		else:
			commandedT=commandedT[0] #day 
		print ('rum : ', self.name)
		print ('commanded T = ', commandedT)
		print ('switchpos = ', switchpos)
		currentT=self.report_temp()
		print ('currentT = ', currentT) 
		if currentT >commandedT :
			for sw in self.switches:
				cmd='sudo ~/projekt/switch/'+ sw +'0'
				subprocess.call ([cmd],shell=True)
			if switchpos==1:
				nnL='Log_'+self.name
				cur.execute('insert into ' + nnL + ' values (?,?,?)',
						((DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currentT, 0)))
		else: 
			 for sw in self.switches:
				 cmd='sudo ~/projekt/switch/'+ sw +'1'
				 subprocess.call ([cmd],shell=True)
			 if switchpos==0:
				 nnL='Log_'+self.name
				 cur.execute('insert into ' + nnL + ' values (?,?,?)',
						((DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), currentT, 1)))
		db.commit()
		cur.close()
		return
		
			

def main(args):
	db=sqlite.connect(expanduser('~/projekt/switch/Thermo.db'))
	cur=db.cursor()
	koket = rum('köket','192.168.1.9','28-000007053ca0',['newswitchaccurate.py 4 '])
	stora_rummet = rum('stora_rummet','192.168.1.5','28-00000704b7f5',['myswitchaccurate.py 3 ','newswitchaccurate.py 6 '])
	sovrummet = rum('sovrummet','192.168.1.8','28-00000705c52f',['newswitchaccurate.py 3 '])
	hallen = rum('hallen','192.168.1.10','28-000007057d28',[])
	ute=rum('ute','192.168.1.5','28-000005fce0db',[])
	rummen=[koket,stora_rummet,sovrummet,hallen,ute]
	tables=cur.execute('select name from sqlite_master where type="table"').fetchall()
	#The following lines will onlu be executed on convertion to the new program and can later be removed 
	if ('ControlTable',) in tables:
		cur.execute ('''alter table ControlTable RENAME TO Control_vardagsrum ''')
		cur.execute ('''alter table Log RENAME TO Log_vardagsrum ''')
		for rr in rummen[1:-1]:
			nn='Control_' + rr.name
			print (nn)
			cur.execute ('''create table ''' + nn + ''' ('Timestamp' DateTime  PRIMARY KEY, 'Tset' real)''')
			tt=cur.execute ('insert into ' + nn + ' values (?,?)',(DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),10)) 
			nn='Log_' + rr.name
			print (nn)
			cur.execute ('''create table ''' + nn + ''' ('Timestamp' DateTime PRIMARY KEY,'T_cur' real, 'SwitchPos'  INT)''')
			cur.execute('insert into ' + nn + ' values (?,?,?)',((DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 10, 0)))
			db.commit()
		cur.close()
	#The following lines are only executed once to change the names of the rooms and can be removed later
	schema=cur.execute('select sql from sqlite_master where type="table" and name="Control_köket"').fetchall()	
	if u'Tnatt' not in schema[0][0]: # not in the first controltable  not in any!
		ctrltables=cur.execute('select name from sqlite_master where type="table" and name like "Control%"').fetchall()
		for i,nn in enumerate (ctrltables):
			print (i, nn)
			addnatt='''alter table ''' + nn[0]  + ''' ADD column 'Tnatt' real default 5.0'''
			cur.execute(addnatt)
			print ("Added Tnatt  " ' to Control', rummen[i].name)
			db.commit()
		cur.close()
	if args[1].lower()=="report":
		res=[]
		for rr in rummen:
			res.append(rr.report_temp())
		for i,rr in enumerate(rummen):
			print ('%12s : %2.3f C' % (rr.name, res[i]))
	elif args[1].lower()=="set":
		if len(args) ==5:
			for rr in rummen:
				if rr.name==args[2]: 
					rr.set_temp(db,float(args[3]),float(args[4]))
					break
			else: print ("No such room")
		else:  print (len(args) , "Which room ? or  day and night temps not given.")
	elif args[1].lower() == 'control':
		if len(args) ==3:
			if args[2].lower()=='all':
				for rr in rummen[:-1]:
					rr.control_temp(db)
			else:
				for rr in rummen:
					if rr.name==args[2]: 
						rr.control_temp(db)
						break
				else: print ("No such room")
		else:  print (len(args) , "Which room ? ")
	else: print ("No command")
	db.close()		
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
