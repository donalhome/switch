import sqlite3 as sqlite
from os.path import expanduser
import datetime as DT
db=sqlite.connect(expanduser('~/projekt/switch/VindThermo.db'))
cur=db.cursor()
cur.execute ('drop table if exists ControlTable')
cur.execute ('''create table ControlTable ('Timestamp' DateTime  PRIMARY KEY, 'Tset' real)''')
tt=cur.execute ('insert into ControlTable values (?,?)',(DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),20)) 
cur.execute ('drop table if exists Log')
cur.execute ('''create table Log ('Timestamp' DateTime PRIMARY KEY,'T_cur' real, 'SwitchPos'  INT)''')
cur.execute('insert into Log values (?,?,?)',
			((DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0, 0)))
cur.execute ('drop table if exists Alarms')
cur.execute ('''create table Alarms ('Timestamp' DateTime PRIMARY KEY,'T_max' real, 'T_min'  real)''')
tt=cur.execute ('insert into Alarms values (?,?,?)',(DT.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),0,25)) 
db.commit()
cur.close()
db.close()
