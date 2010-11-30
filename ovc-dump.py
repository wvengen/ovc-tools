#!/usr/bin/env python
#
# OV-chipkaart hexdumper
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

import sys
import datetime


def str2hex(data, sep=''):
	return sep.join(map(lambda x: '%02x'%ord(x), data))

def printhex(data, offset):
	s = ''
	addr = ''
	for a in range(0, len(data), 8):
		if not addr: addr = '%04x:'%(a+offset)
		if data[a:a+8] == '\0'*8: s += ' ' + '   '*8
		else: s += '  ' + str2hex(data[a:a+8],' ')
		if len(s) > 125:
			if s.strip(): print addr + s.rstrip()
			s = ''
			addr = ''
	s = s.rstrip()
	while s.endswith(' 00'): s=s[:-3]
	if s.strip(): print addr + s


if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.stderr.write('Usage: %s <ovc_dump> [<ovc_dump_2> [...]]\n'%sys.argv[0])
		sys.exit(1)

	isfirst = True
	for fn in sys.argv[1:]:
		if not isfirst: print
		isfirst = False
		inp = open(fn, 'r')
		data = inp.read()
		inp.close()

		if len(data) == 4096:	# mifare classic 4k
			# general card info
			printhex(data[0x00:0x10], 0);
			printhex(data[0x10:0x36], 0x10);

			# info below 1k (mostly zero)
			for sector in range(1, 32):
				addr = sector*0x40
				length = 0x30
				chunksize = 0x30

				for tr_offs in range(0, length, chunksize):
					if tr_offs+chunksize <= length:
						printhex(data[addr+tr_offs:addr+tr_offs+chunksize], addr+tr_offs)

			# subscriptions
			for sector in range(32, 35):
				addr = 0x800 + (sector-32)*0x100
				length = 0xf0
				chunksize = 0x30

				for tr_offs in range(0, length, chunksize):
					if tr_offs+chunksize <= length:
						printhex(data[addr+tr_offs:addr+tr_offs+chunksize], addr+tr_offs)

			# transactions
			for sector in range(35, 39):
				addr = 0x800 + (sector-32)*0x100
				length = 0xf0
				chunksize = 0x20
				
				for tr_offs in range(0, length, chunksize):
					if tr_offs+chunksize <= length:
						printhex(data[addr+tr_offs:addr+tr_offs+chunksize], addr+tr_offs)

			# trailer info
			addr=0xf00
			while data[addr]=='\0': addr+=1
			if addr<0xf50: printhex(data[addr:0xf50], addr)
			printhex(data[0xf50:0xf70], 0xf50)
			printhex(data[0xf70:0xf90], 0xf70)
			printhex(data[0xf90:0xfa0], 0xf90)
			printhex(data[0xfa0:0xfb0], 0xfa0)
			printhex(data[0xfb0:0xfd0], 0xfb0)
			printhex(data[0xfd0:0xff0], 0xfd0)

		else:
			sys.stderr.write('%s: expected 4096 bytes of ov-chipkaart dump file\n'%fn)
			sys.exit(2)


