#
# OV-chipkaart decoder: field types
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

import datetime
import stations


def _rfill(s, l):
	'''Fill string right with spaces to make as long as longest value in list/dict'''
	if isinstance(l, str): return s + ' '*max(0, len(l)-len(s))
	if isinstance(l, dict): l = l.values()
	return s + ' '*(max([len(x) for x in l])-len(s))

class OvcDate(datetime.date):
	'''date with ovc-integer constructor'''
	# TODO subclassing this built-in type doesn't work fully :(
	def __new__(cls, x, **kwargs):
		d = datetime.date.__new__(cls, 1997, 1, 1)
		d += datetime.timedelta(x)
		return d
	def __str__(self):
		return self.strftime('%d-%m-%Y')


class OvcDatetime(datetime.datetime):
	'''datetime with ovc-integer constructor'''
	# TODO subclassing this built-in type doesn't work fully :(
	def __new__(cls, x, **kwargs):
		d = datetime.datetime.__new__(cls, 1997, 1, 1)
		d += datetime.timedelta(x>>11, (x&((1<<11)-1))*60)
		return d
	def __str__(self):
		return self.strftime('%d-%m-%Y %H:%m')

class OvcTransfer(int):
	_strs = { 0: 'purchase', 1: 'check-in', 2: 'check-out', 6: 'transfer' }
	def __new__(cls, x, **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		try: return _rfill(self._strs[self], self._strs)
		except KeyError: return _rfill('trnsfr %d'%self, self._strs)

class OvcCompany(int):
	# most companies can be figured out using
	# https://www.ov-chipkaart.nl/webwinkel/aanvragen/aanvragen_pkaart/kaartaanvragen/?ovbedrijf=<number>
	# pending: Breng (Novio), GVU, Hermes, Qbuzz, Syntus
	# 25 might be Albert Heijn
	_strs = {
		 0: 'TLS',         1: 'Connexxion',  2: 'GVB',        3: 'HTM',
		 4: 'NS',          5: 'RET',                          7: 'Veolia',
		 8: 'Arriva',
	}
	def __new__(cls, x, **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		try: return _rfill(self._strs[self], self._strs)
		except KeyError: return _rfill('company %d'%self, self._strs)

_ostwidth = 0
class OvcStation(int):
	def __new__(cls, x, obj, **kwargs):
		i = int.__new__(cls, x)
		i._obj = obj
		return i
	def __str__(self):
		# compute maximum length of station name and cache it
		global _ostwidth
		if not _ostwidth:
			for i in range(0,8):
				_ostwidth = max([_ostwidth] +  [len(x) for x in stations.ovc_get_dict(i).values()])
		# get station name and pad string
		s = stations.ovc_get_name(self._obj.company, self)
		if not s: s = '(station %5d)'%self
		return s + ' '*(_ostwidth-len(s))

class OvcTransactionId(int):
	def __new__(cls, x,  **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		return '#%03d'%self

class OvcAmount(float):
	def __new__(cls, x, **kwargs):
		return float.__new__(cls, x/100.0)
	def __str__(self):
		if self < 1e-6: return '    -  '
		return '\xe2\x82\xac%6.2f'%self

class FixedWidthDec(long):
	def __new__(cls, x, width=0, **kwargs):
		i = long.__new__(cls, x)
		i._fieldwidth = width
		return i
	def __str__(self):
		return ('%d'%self).zfill(self._fieldwidth)

class FixedWidthHex(long):
	def __new__(cls, x, width=0, **kwargs):
		i = long.__new__(cls, x)
		i._fieldwidth = width
		return i
	def __str__(self):
		return '0x'+('%x'%self).zfill(self._fieldwidth)


