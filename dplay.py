#!/usr/bin/env python
#
# colorised single-screen diff viewer
#   Shows text files specified on command line on screen consecutively
#   with differences indicated by colors.
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
import time
import optparse

parser = optparse.OptionParser()
parser.add_option('-r', '--repeat', dest='repeat', action='store_const', const=True, default=False, help='Repeat')
parser.add_option('-s', '--sleep', dest='sleep', default='1', help='Pause between files, in seconds')
(options, args) = parser.parse_args()

options.sleep = float(options.sleep)

COLORS = [
	(35,1),	# changed since previous
	(31,0),	# changed since one-but-previous
	(37,0), # changed since first
	(32,0),	# unchanged
]

if len(args) < 1:
	parser.error('specify one or more files')
	sys.exit(1)

def clear():
	sys.stdout.write('\x1b[H\x1b[2J')
	sys.stdout.flush()

def restore():
	sys.stdout.write('\x1b[!p\x1b[?3;4l\x1b[4l\x1b>')
	sys.stdout.flush()

def ansicolor(color=37, bold=False):
	boldnum=0
	if bold: boldnum=1
	return '\x1b[%d;%dm'%(boldnum, color)

def colorize(inp):
	if isinstance(inp, bool):
		if inp:
			return ansicolor(35, True)
		else:
			return ansicolor(32, False)
	else:
		return colorize(True) + inp + colorize(False)

def diffie(new, olds, oldcols):
	'''Return new with color codes for differences with old strings.
	@type new: string
	@param new: output string to colorize
	@type olds: list of string
	@param olds: list of output strings to compare to, most recent first
	@type oldcols: list of color tuples (as passed to {@ref ansicolor)
	@param oldcols: list of colors, one longer than {@param olds} for nodiff color
	@rtype: string
	@return: colorized new
	'''
	if not olds:
		return colorize(new)
	if (len(olds)+1) != len(oldcols):
		raise ValueError('Length of colors must be one more than length of old strings')
	lastj = None
	newj = None
	ret = ''
	for i in range(len(new)):
		newj = len(olds)
		for j in range(len(olds)):
			if olds[j] and i >= len(olds[j]):
				newj=j
				break
			elif olds[j] and new[i] != olds[j][i]:
				newj=j
				break;
		if newj != lastj:
			ret += ansicolor(*oldcols[newj])
			lastj = newj
		ret += new[i]
	ret += ansicolor(*oldcols[-1])
	return ret


try:
	firsttime = True
	while firsttime or options.repeat:
		firsttime = False
		oldlines=[None, None, None] # previous, one-but-previous, very-first
		for f in args:
			clear()
			print '%s==== %s ====%s'%(ansicolor(37,True), f, ansicolor(*COLORS[-1]))
			# read new file
			f = open(f, 'r')
			curlines = map(lambda x: x.rstrip(), f.readlines())
			f.close()
			# print colorized output
			for i in range(len(curlines)):
				oldls=[None]*len(oldlines)
				for j in range(len(oldlines)):
					if oldlines[j] and i < len(oldlines[j]):
						oldls[j] = oldlines[j][i]
				print diffie(curlines[i], oldls, COLORS)
			# save history
			oldlines[1] = oldlines[0]
			oldlines[0] = curlines
			if not oldlines[-1]:
				oldlines[-1] = curlines
			else:
				for i in range(len(curlines)):
					if i >= len(oldlines[-1]): continue
					for j in range(len(curlines[i])):
						if j >= len(oldlines[-1][i]):
							oldlines[-1][i] = oldlines[-1][i]+'\0'
						elif curlines[i][j] != oldlines[-1][i][j]:
							oldlines[-1][i] = oldlines[-1][i][:j]+'\0'+oldlines[-1][i][j+1:]
			# sleep a little before showing next one
			time.sleep(options.sleep)

		# clear screen for repeating
		if options.repeat:
			clear()
			time.sleep(options.sleep)
finally:
	restore()

