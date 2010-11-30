#
# OV-chipkaart stations: module
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
import ns
import gvb
import ret
import htm
import veolia
import connexxion


def ovc_get_dict(company):
	'''return dictionary with station names for ovc company number'''
	if   company ==  1: return connexxion.stations
	elif company ==  2: return gvb.stations
	elif company ==  3: return htm.stations
	elif company ==  4: return ns.stations
	elif company ==  5: return ret.stations
	elif company ==  7: return veolia.stations
	else:               return dict()

def ovc_get_name(company, station):
	'''return station name for ovc company and station number; or None if not found'''
	stations = ovc_get_dict(company)
	if stations and station in stations:
		return stations[station]
	else:
		return None

