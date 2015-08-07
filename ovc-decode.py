#!/usr/bin/env python
#
# OV-chipkaart decoder: main program
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

from ovc import *
from ovc.ovctypes import *
from ovc.util import mfclassic_getsector, getbits


if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.stderr.write('Usage: %s <ovc_dump> [<ovc_dump_2> [...]]\n'%sys.argv[0])
		sys.exit(1)

	for fn in sys.argv[1:]:
		inp = open(fn, 'rb')
		data = inp.read()
		inp.close()

		if len(data) == 4096:	# mifare classic 4k
			# card details
			# TODO make the card an object in itself with fixed-position templates
			# note that these data areas are not yet fully understood
			cardid = getbits(data[0:4], 0, 4*8)
			cardtype = OvcCardType(getbits(data[0x10:0x36], 18*8+4, 19*8))
			validuntil = OvcDate(getbits(data[0x10:0x36], 11*8+6, 13*8+4))
			s = 'OV-Chipkaart id %d, %s, valid until %s'%(cardid, cardtype, validuntil)
			if cardtype==2:
				birthdate = OvcBcdDate(getbits(mfclassic_getsector(data, 22), 14*8, 18*8))
				s += ', birthdate %s'%birthdate
			print s

			# transactions
			for sector in range(32, 35):
				sdata = mfclassic_getsector(data, sector)[:-0x10]
				for chunk in range(0, len(sdata), 0x30):
					if ord(sdata[chunk]) == 0: continue
					print OvcClassicTransaction(sdata[chunk:chunk+0x30])
			for sector in range(35, 39):
				sdata = mfclassic_getsector(data, sector)[:-0x10]
				for chunk in range(0, len(sdata), 0x20):
					if ord(sdata[chunk]) == 0: continue
					print OvcClassicTransaction(sdata[chunk:chunk+0x20])

			# saldo
			class OvcSaldoTransaction(OvcRecord):
				_fieldchars = [
					('id',     'I',   12, OvcTransactionId),
					('idsaldo','H',   12, OvcSaldoTransactionId),
					('saldo',  'N',   16, OvcAmountSigned),
					('unkU',   'U', None, FixedWidthHex),
					('unkV',   'V', None, FixedWidthHex),
				]
				_templates = [
					('20 II I0 00 00 00 80 HH H0 0N NN N0', {'I':1, 'N':1}),
				]
				def __str__(self):
					s = '[saldo_%02x__] '%(ord(self.data[0]))
					return s + OvcRecord.__str__(self)
				
			sdata = mfclassic_getsector(data, 39)[:-0x10]
			for chunk in [0x90, 0xa0]:
				if ord(sdata[chunk]) == 0: continue
				print OvcSaldoTransaction(sdata[chunk:chunk+0x10])
				

		elif len(data) == 64:	# mifare ultralight GVB
			# TODO card id, otp, etc.
			for chunk in range(0x10, len(data)-0x10, 0x10):
				# skip empty slots
				if data[chunk:chunk+2] == '\xff\xff': continue
				# print data
				t = OvcULTransaction(data[chunk:chunk+0x10])
				print t

		else:
			sys.stderr.write('%s: expected 4096 or 64 bytes of ov-chipkaart dump file\n'%fn)
			sys.exit(2)

