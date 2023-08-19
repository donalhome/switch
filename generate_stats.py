#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  generate_stats.py
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
import numpy as np
import datetime as DT
import time

def main(args):
	db=sqlite.connect(expanduser('~/projekt/switch/Thermo.db'))
	cur=db.cursor()
	ll=cur.execute('select * from Log_köket where strftime("%m",timestamp)="10"').fetchall()
	kk=np.array(ll)
	dates=[]
	for i in range(kk.shape[0]):
		dates.append(DT.datetime.strptime(kk[i,0],'%Y-%m-%d %H:%M:%S'))
		
	nomin=0
	turnons=kk[:,2]=='1'
	for i, state in enumerate (turnons[:-1]):
		if state : nomin+=(dates[i+1]-dates[i]).total_seconds()/60.
	print nomin/60.*0.8
	return 0

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
