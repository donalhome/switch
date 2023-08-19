#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  updateTemp.py
#  
#  Copyright 2016 Donal Murtagh <donal@donal-VirtualBox>
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



def main(args):
	db=sqlite.connect(expanduser('~/projekt/switch/VindThermo.db'))
	cur=db.cursor()
	newtemp=float(args[1])
	print 'newtemp is ', newtemp
	if ((newtemp>0) and (newtemp<25)) :
		tt=cur.execute ('insert into ControlTable values (?,?)',(DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),newtemp)) 
		db.commit()
		cur.close()
		db.close()
	else : print 'Temp not valid'
	return 0

if __name__ == '__main__':
	import sqlite3 as sqlite
	from os.path import expanduser
	import datetime as DT
	import sys
	sys.exit(main(sys.argv))
