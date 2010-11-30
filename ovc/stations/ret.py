#
# OV-chipkaart stations: RET (Rotterdam municipal transport company)
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
	 3189: 'Rotterdam, Station Blaak',
}

tram = {
	 3007: 'Rotterdam, Centraal Station',
	 3061: 'Rotterdam, Centraal Station',	# ri Carnisselande
}

metro = {
	  507: 'Rotterdam, Station Alexander',
	  529: 'Rotterdam, Station Blaak',
	 1029: 'Rotterdam, Oostplein',
	 2566: 'Den Haag, Centraal Station',
}

stations = dict(bus, **dict(tram, **metro))

