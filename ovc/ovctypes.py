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
from util import bcd2int


def _rfill(s, l):
	'''Fill string right with spaces to make as long as longest value in list/dict'''
	return s + ' '*(_maxlength(l)-len(s))

def _maxlength(l):
	'''Return maximum length of strings in (nested) list or dict'''
	if isinstance(l, dict): l = l.values()
	if isinstance(l, list): return max([_maxlength(x) for x in l])
	return len(l)


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

class OvcBcdDate(datetime.date):
	'''date with ovc-BCD constructor'''
	def __new__(cls, x, **kwargs):
		day   = bcd2int((x>> 0)&0xff)
		month = bcd2int((x>> 8)&0xff)
		year  = bcd2int((x>>16)&0xffff)
		if not year: return None
		return datetime.date.__new__(cls, year, month, day)

class OvcCardType(int):
	_strs = { 0: 'anonymous', 2: 'personal'}
	def __new__(cls, x, **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		try: return self._strs[self]
		except KeyError: return 'cardtype %d'%self

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
	# pending: Breng (Novio), GVU, Hermes, Qbuzz
	# company 25 is used for credit machines at Albert Heijn, Primera and in Hermes busses
	# company 26 has been seen as well
	_strs = {
		 0: 'TLS',         1: 'Connexxion',  2: 'GVB',        3: 'HTM',
		 4: 'NS',          5: 'RET',                          7: 'Veolia',
		 8: 'Arriva',      9: 'Syntus',
	}
	def __new__(cls, x, **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		try: return _rfill(self._strs[self], self._strs)
		except KeyError: return _rfill('company %d'%self, self._strs)

class OvcSubscription(int):
	_strs = {
		 2: {
 			0x0bbd: 'Supplement fiets',
		}, 
		 4: {
			0x00af: 'vrijweek09', #could also be kortweek09
			0x00b1: 'kortweek09', #could also be vrijweek09
			0x00ca: 'Reizen op saldo (2e klas)',
			0x00ce: 'Voordeelurenabonnement',
		},
		12: {
			0x09c9: 'studwkvrij', #could also be studwkkort
			0x09ca: 'studwkkort', #could also be studwkvrij
		}
	}
	def __new__(cls, x, obj, **kwargs):
		i = int.__new__(cls, x)
		i._obj = obj
		return i
	def __str__(self):
		try: return _rfill(self._strs[self._obj.company][self], self._strs)
		except KeyError: return _rfill('subscription %d'%self, self._strs)

_ostwidth = 0
class OvcStation(int):
	def __new__(cls, x, obj, **kwargs):
		i = int.__new__(cls, x)
		i._obj = obj
		return i
	def __str__(self):
		# compute maximum length of station name and cache it
		global _ostwidth
		if not _ostwidth: _ostwidth = stations.get_max_len('title')
		# get station name and pad string
		s = stations.get(self._obj.company, self)
		if not s or not s.title:
			s = '(station %5d)'%self
		else:
			s = s.title
		return s + ' '*(_ostwidth-len(s))

class OvcTransactionId(int):
	def __new__(cls, x,  **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		return '#%03d'%self

class OvcSaldoTransactionId(int):
	def __new__(cls, x,  **kwargs):
		return int.__new__(cls, x)
	def __str__(self):
		return '$%03d'%self

class OvcAmount(float):
	'''amount in euro; prints '-' when zero'''
	def __new__(cls, x, **kwargs):
		return float.__new__(cls, x/100.0)
	def __str__(self):
		if self < 1e-6: return '    -  '
		return '\xe2\x82\xac%6.2f'%self

class OvcAmountSigned(float):
	'''amount in euro; 16 bit signed number'''
	def __new__(cls, x, **kwargs):
 		x = x - (1<<15)
		return float.__new__(cls, x/100.0)
	def __str__(self):
		return '\xe2\x82\xac%6.2f'%self

class FixedWidthDec(long):
	def __new__(cls, x, width=0, **kwargs):
		i = long.__new__(cls, x)
		i._fieldwidth = width
		return i
	def __str__(self):
		return ('%d'%long(self)).zfill(self._fieldwidth)

class FixedWidthHex(long):
	def __new__(cls, x, width=0, **kwargs):
		i = long.__new__(cls, x)
		i._fieldwidth = width
		return i
	def __str__(self):
		return '0x'+('%x'%self).zfill(self._fieldwidth)


