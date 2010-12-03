#!/usr/bin/env python

import os
import sys
import sqlite3

# name of database
dbname = 'stations.sqlite'
# sql file to create tables
createsql = 'create_tables.sql'
# default table for importing data files
dfltable = 'stations'

prefix = os.path.dirname(__file__)
db = os.path.join(prefix, dbname)
if os.path.exists(db):
	sys.stderr.write('Please remove database file first: %s\n'%db)
	sys.exit(1)

con = sqlite3.connect(db)
cur = con.cursor()
# performance improvements
cur.executescript('''
	PRAGMA journal_mode = OFF;
	PRAGMA locking_mode = EXCLUSIVE;
''')

def readfile(filename):
	f = open(filename, 'r')
	r = f.read()
	f.close()
	return r

# create table first
print 'Creating table'
cur.executescript(readfile(os.path.join(prefix, createsql)))

# then import all other sql files
for filename in os.listdir(prefix):
	if not filename.endswith('.sql'): continue
	if filename == createsql: continue
	print 'Importing SQL: %s'%filename
	cur.executescript(readfile(os.path.join(prefix, filename)))

# and import tab-seperated files; first line are fields,
# hash '#' at start of a line is a comment
for filename in os.listdir(prefix):
	if not filename.endswith('.tsv'): continue
	print 'Importing tab-separated data: %s'%filename
	f = open(os.path.join(prefix, filename), 'r')
	fields = None
	for line in f:
		if line.startswith('#'): continue
		data = [x.strip() for x in line.decode('utf-8').split('\t')]
		if not fields:
			fields = data
		else:
			query = 'INSERT INTO %s (%s) VALUES (%s);'%(
					dfltable,
					','.join(fields),
					','.join(['?'] * len(fields)),
				)
			cur.execute(query, data)
	f.close()

# compact database
print 'Compacting database'
cur.executescript('''
	VACUUM;
''')

print 'Done!'

