#
# OV-chipkaart decoder: record matching
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

import re
from util import getbits
from ovctypes import *


class OvcRecord:
	'''Match binary records with templates. Needs to be subclassed.'''

	'''Description of record fields. Each record is matched to each of the
	fields. Hex digits ([0-9a-f]) must match literally, while uppercase
	characters ([G-Z?]) are fields.
	Each item is a tuple of the template string and an optional dict of
	bit-offsets in the nibble. See child classes for examples.'''
	_templates = []
	'''Field descriptions, to bind characters in _templates to fields.
	list of: (fieldname, char, bitlength, type_or_conversion_function)'''
	_fieldchars = []

	def __init__(self, data):
		self.parsed = False
		self.data = data
		# create empty fields
		for fieldinfo in self._fieldchars:
			fname, fchar, flen, ftype = fieldinfo
			self.__dict__[fname] = None
		# parse template
		for t in self._templates:
			if self._parsetemplate(t):
				self.parsed = True
				break

	def _parsetemplate(self, template):
		if isinstance(template, str): template = [template]
		# remove spaces from template
		tmplstr = re.sub('\s+', '', template[0])
		# if template is shorter than data, don't match
		data = self.data.rstrip('\0')
		if len(data) > len(tmplstr)/2: return False
		# pad data with zeroes to match with template
		data = self.data + '\0'*max(0, len(tmplstr)/2-len(self.data))
		# create template data with variables set to zero to be able to use getdata()
		tmpldatastr = re.sub('[^0-9a-f]', '0', tmplstr)
		tmpldata = ''.join([chr(int(tmpldatastr[i:i+2], 16)) for i in range(0, len(tmpldatastr), 2)])

		# determine fields and their nibble-offsets from template
		fields = []		# field names (or '0' for literal)
		tmploffsets = []	# offsets of fields from template
		lastchar = None
		for i in range(len(tmplstr)):
			curchar = tmplstr[i]
			if curchar in '0123456789abcdef': curchar = '0'
			if curchar != lastchar:
				fields.append(curchar)
				tmploffsets.append(i*4)
				lastchar = curchar
		tmploffsets.append(len(tmplstr)*4)

		# determine field boundaries, in the following order:
		# 1. specified start-offsets, if any
		#    1b. apply fixed-width fields with known start-offsets
		# 2. boundaries of template characters
		#    2b. apply fixed-width fields with known start-offsets
		# 3. boundaries of template literals
		offsets = [None] * (len(fields)+1)
		if len(template) > 1 and template[1]:
			for fchar,bitoffs in template[1].iteritems():
				offsets[fields.index(fchar)] = tmplstr.find(fchar)*4 + bitoffs
		self._apply_fixedwidth(fields, offsets)
		# boundaries of template characters
		for i in range(len(tmploffsets)-1):
			if offsets[i] is not None: continue
			if fields[i] == '0': continue
			offsets[i] = tmploffsets[i]
			self._apply_fixedwidth(fields, offsets)
		# boundaries of template literals
		for i in range(len(tmploffsets)):
			if offsets[i] is not None: continue
			offsets[i] = tmploffsets[i]
			self._apply_fixedwidth(fields, offsets)

		# now parse all fields
		fieldvalues={}
		for i in range(len(fields)):
			value = getbits(data, offsets[i], offsets[i+1])
			curchar = fields[i]
			if curchar == '0':
				# literal: check with template
				tmplvalue = getbits(tmpldata, offsets[i], offsets[i+1])
				if tmplvalue != value: return False
			else:
				# template variable: store
				fname, fchar, flen, ftype = self._field_by_char(curchar)
				try: fieldvalues[fname] = ftype(value, obj=self, width=(offsets[i+1]-offsets[i]+3)/4)
				except TypeError: fieldvalues[fname] = ftype(value)

		# everything is ok, incorporate fields
		self.__dict__.update(fieldvalues)
		return True

	def _field_by_char(self, fchar):
		'''Return fieldinfo record by character'''
		fieldinfo = filter(lambda x: x[1]==fchar, self._fieldchars)
		if not fieldinfo:
			raise KeyError("Template character '%c' not found in fieldchars"%fchar)
		elif len(fieldinfo) > 1:
			raise KeyError("Template character '%c' defined multiple times in fieldchars"%fchar)
		return fieldinfo[0]

	def _apply_fixedwidth(self, fields, offsets):
		'''Update offsets from fixed-width fields where possible (recursively)'''
		while self._apply_fixedwidth_it(fields, offsets): pass

	def _apply_fixedwidth_it(self, fields, offsets):
		'''Update offsets from fixed-width fields where possible (one iteration)'''
		changed = False
		for i in range(len(fields)-1):
			if offsets[i] is None: continue
			if fields[i] == '0': continue
			fname, fchar, flen, ftype = self._field_by_char(fields[i])
			if not flen: continue
			if offsets[i+1] is not None: continue
			offsets[i+1] = offsets[i] + flen
			changed = True
		return changed

	def getbits(self, start, end):
		# return number at bit positions of data (0 is beginning)
		return getbits(self.data, start, end)

	def __str__(self):
		s = ''
		if self.parsed:
			if self.id is None: s += '     '
			fields = filter(lambda x: self.__dict__[x] is not None, [x[0] for x in self._fieldchars])
			s += ' '.join([str(self.__dict__[x]) for x in fields])
		else:
			data = self.data
			while data and data[-1]=='\0': data = data[:-1]
			s += ' '.join(['%02x'%ord(x) for x in data])
		return s


class OvcClassicTransaction(OvcRecord):
	'''Transaction on a mifare classic card'''

	_fieldchars = [
			('id',        'I',   12, OvcTransactionId),
			('date',      'T',   25, OvcDatetime),
			('company',   'M',    4, OvcCompany),
			('transfer',  'Y',    4, OvcTransfer),
			('amount',    'N',   16, OvcAmount),
			('station',   'S',   16, OvcStation),

			# Meaning of ritnr unsure yet; is equal for check-in/checkout and
			# 28/29-type records. Also same line on same day sometimes can have
			# the same number here. May be bus number instead.
			('ritnr',     'J',   40, FixedWidthHex),
			# Meaning of portnr unsure yet; can be equal when station is equal
			# but this may be something completely different as well.
			('portnr',    'K',   24, FixedWidthHex),

			# Unknowns: use each once per template
			('unkU',      'U', None, FixedWidthHex),
			('unkV',      'V', None, FixedWidthHex),
			('unkW',      'W', None, FixedWidthHex),
			('unkQ',      '?', None, FixedWidthHex),

			# subscription fields
			('validfrom', 'R',   14, OvcDate),
			('validto',   'O',   14, OvcDate),
	]
	_templates = [
		# journey transactions
		( '28 00 55 6T TT TT T2 94 00 00 Y0 00 M0 00 II IS SS SK KK KK KN NN N? ?? ??' ),
		( '28 04 55 6T TT TT T2 94 00 00 Y0 00 M0 00 II IS SS SJ JJ JJ JJ JJ JN NN N? ?? ??' ),
		# 2nd journey log
		( '29 00 55 4T TT TT TV V0 00 M0 00 II IS SS SK KK KK K0 VV VN NN NW 1? ?? ??' ),
		( '29 04 55 4T TT TT TV V0 00 M0 00 II IS SS SJ JJ JJ JJ JJ J0 VV VN NN N? ?? ??'),
		# special transaction: add product
		#( '20 00 55 2T TT TT T2 94 00 0U UU U0 00 VV VV VV VV WW WW WW WW' ), # TODO
		#( '20 04 55 4T TT TT TV VV 00 M0 00 II IS SS SU UU UU UU UU U?' ),  # some guesswork
		# special transaction: add money
		( '08 10 55 0T TT TT TU UU M0 00 0V VS SS SW WW WW WW NN NN ?0', {'M':1, 'N':2, 'S':1} ),
		# subscription
		#( '0a 00 e0 00 40 0U U0 00 00 II I......5 RR RO OO O.........................', {'R':-1}),
		#( '0a 02 e0 00 40 0U U0 00 00 II I......a RR RO OO O............................', {'R':-1}),
	] 

	def __init__(self, data):
		OvcRecord.__init__(self, data)
		# TODO move this pretty-print stuff to some better place
		if self.transfer is None: self.transfer = '         '
		if self.amount is None: self.amount = '       '
		if self.data[0]=='\x08': self.transfer = 'credit   '

	def __str__(self):
		s = '[%02x_%02x_%02x_%x] '%(ord(self.data[0]),ord(self.data[1]),ord(self.data[2]),ord(self.data[3])>>4)
		return s + OvcRecord.__str__(self)


# TODO this is very very prelim
class OvcULTransaction(OvcRecord):
	'''Transaction on a mifare ultralight card (only GVB tested)'''
	_fieldchars = [
		('id',        'I',   14, OvcTransactionId),
		('date',      'T',   25, OvcDatetime),
		('company',   'M',    4, OvcCompany),
		('transfer',  'Y',    3, OvcTransfer),
		('station',   'S',   16, OvcStation),
		('unkU',      'U', None, FixedWidthHex),
		('unkV',      'V', None, FixedWidthHex),
		('unkW',      'W', None, FixedWidthHex),
		('unkQ',      '?', None, FixedWidthHex),
	]
	_templates = [
		('?I II UU UU YT TT TT TV VV VV VV VV VV VV VV VV', {'I':1, 'T':-1}),
	]

