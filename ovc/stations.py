#
# OV-chipkaart decoder: station database access
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License at http://www.gnu.org/licenses/gpl.txt
# By using, editing and/or distributing this software you agree to
# the terms and conditions of this license.
#
# (c)2010 by Willem van Engen <dev-rfid@willem.engen.nl>
#

import os
import sys
import sqlite3


class OvcStation:
	'''single station'''

	# fields the are always present (irregardless or database, albeit possibly None)
	_fields = ['company', 'ovcid', 'title', 'zone', 'lonlat']

	def __init__(self, d):
		self.__dict__.update(dict.fromkeys(self._fields))
		self.__dict__.update(d)

	def __str__(self):
		return self.title


db = None
con = None
def init(_db=None):
	global db, con
	db = _db
	if not db: db = os.path.join(os.path.dirname(__file__), '..', 'stations', 'stations.sqlite')
	if not os.path.exists(db):
		sys.stderr.write('WARNING: No station database found, please run stations/createdb.py\n')
		return
	# for convenience also warn if any file in stations is newer than database file
	dbtime = os.path.getmtime(db)
	for filename in os.listdir(os.path.dirname(db)):
		if not filename.endswith('.tsv') or filename.endswith('.sql'): continue
		ftime = os.path.getmtime(os.path.join(os.path.dirname(db), filename))
		if ftime > dbtime:
			sys.stderr.write('WARNING: Station database older than its source files, ')
			sys.stderr.write('you may want to rerun stations/createdb.py\n')
	con = sqlite3.connect(db)

def get(company, number):
	'''return station object by number'''
	global con
	if not con: init()
	if not con: return None
	cur = con.cursor()
	cur.execute('SELECT * FROM stations WHERE company=? AND ovcid=?', (company, number))
	row = cur.fetchone()
	if not row: return None
	return OvcStation(dict(zip([x[0] for x in cur.description], row)))

def get_max_len(field='title', company=None):
	'''return maximum length of station names'''
	global con
	if not con: init()
	if not con: return 0
	where=''
	if company is not None: where = 'WHERE company=%d'%company
	cur = con.cursor()
	cur.execute('SELECT MAX(LENGTH(%s)) FROM stations %s'%(field, where))
	return int(cur.fetchone()[0])

