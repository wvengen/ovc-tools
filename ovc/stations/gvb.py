#
# OV-chipkaart stations: GVB (Amsterdam municipal transport company)
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

bus = {
	20002: 'Muiderpoortstation',
	22332: 'Amstelstation',
}

tram = {
	21438: 'Amsterdam Centraal',
}

metro = {
	 1201: 'Amsterdam Centraal',
	 1206: 'Amsterdam Amstel',
	 1231: 'Amsterdam Zuid/WTC',
	 1221: 'Duivendrecht',
}

stations = dict(bus, **dict(tram, **metro))
