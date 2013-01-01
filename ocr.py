#! /sw/bin/python2.7
# BSD license, Andrzej Zaborowski
import PIL.Image as Image
import ImageDraw as ImageDraw
import os
import sys
import math

chars = {}
classifier = {
	# Cyfry
	'.': [ 2, 2, 2, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0,
		0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'0': [ 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 0 ],
	'1': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0 ],
	'2': [ 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 6, 0 ],
	'2_':[ 4, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8, 0 ],
	'22':[ 2, 3, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 8 ],
	'3': [ 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1,
		1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 0 ],
	'3_':[ 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1,
		1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 4, 0 ],
	'4': [ 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0 ],
	'5': [ 5, 1, 1, 1, 1, 1, 1, 1, 3, 3, 3, 3, 2, 1,
		1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 0 ],
	'6': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 0 ],
	'7': [ 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0 ],
	'8': [ 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 0 ],
	'9': [ 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 1,
		1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 3, 0 ],
	# Male litery
	'a': [ 3, 1, 1, 1, 1, 1, 1, 1, 4, 2, 2, 2, 2, 2,
		2, 2, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'b': [ 1, 1, 1, 1, 1, 1, 1, 1, 4, 2, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 0 ],
	'b_':[ 1, 1, 1, 1, 1, 1, 1, 1, 5, 2, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 2 ],
	'c': [ 4, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	#'d': [ 1, 1, 1, 1, 1, 1, 1, 1, 5, 2, 2, 2, 2, 2, # collides with b
	#	2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 0 ],
	'e': [ 3, 2, 2, 2, 2, 2, 2, 2, 5, 1, 1, 1, 1, 1,
		1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'f': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0 ],
	'g': [ 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 5, 1, 1, 1, 1, 1, 1, 1, 1, 2 ],
	'h': [ 1, 1, 1, 1, 1, 1, 1, 1, 4, 3, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0 ],
	'i': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'i_':[ 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'k': [ 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2,
		1, 1, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0 ],
	'k_':[ 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 1,
		1, 1, 1, 1, 2, 2, 2, 2, 2, 1, 0, 0 ],
	#'l': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, #same as 1 :(
	#	1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 3, 0 ],
	'm': [ 3, 4, 4, 4, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
		3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'n': [ 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'o': [ 3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'p': [ 4, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1 ],
	'r': [ 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	's': [ 4, 1, 1, 1, 1, 1, 1, 1, 3, 1, 1, 1, 1, 1,
		1, 1, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	't': [ 1, 1, 1, 1, 3, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0 ],
	'w': [ 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3,
		4, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'z': [ 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	# Duze litery
	'A': [ 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0 ],
	'B': [ 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 0 ],
	'C': [ 3, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 4, 0 ],
	'D': [ 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 0 ],
	'F': [ 6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 4, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0 ],
	'H': [ 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0 ],
	'K': [ 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		3, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0 ],
	'M': [ 2, 2, 3, 4, 4, 4, 4, 4, 3, 2, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0 ],
	'N': [ 1, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
		3, 3, 3, 3, 3, 3, 3, 3, 2, 2, 2, 0 ],
	'R': [ 5, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 5, 2, 2, 2, 2, 2, 2, 2, 1, 0 ],
	'S': [ 4, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 4, 1,
		1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 3, 0 ],
	'T': [ 7, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0 ],
	'U': [ 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2,
		2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 4, 0 ],
	# Symbole
	'*': [ 1, 3, 3, 3, 3, 3, 2, 2, 6, 1, 2, 3, 3, 3,
		3, 3, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
	'/': [ 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
		1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
}

tile = None
data = None
bboxes = None
def scan(x, y):
	global data, chars, bboxes, tile
	x0 = x
	x1 = x
	while 1:
		tx = x0 - 1
		empty = 1
		for ty in range(y, y + 26):
			px = tx - int((ty - y) * 8 / 25)
			py = ty
			if px < 0 or py >= tile.size[1]:
				break
			if data[px, py]:
				empty = 0
				break
		if empty:
			break
		x0 -= 1
	empty = 0
	while 1:
		tx = x1 + 1
		if tx >= tile.size[0]:
			break
		empty += 1
		for ty in range(y, y + 26):
			px = tx - int((ty - y) * 8 / 25)
			py = ty
			if px < 0 or py >= tile.size[1]:
				break
			if data[px, py]:
				empty = 0
				break
		if empty == 2:
			break
		x1 += 1
	x1 -= 1
	bb = ( x0 - 9, y - 1, x1 + 1, y + 26 )
	bboxes.append(bb)

	cs = []
	for py in range(y, y + 26):
		c = 0
		v = 0
		px0 = x0 - int((py - y) * 8 / 25)
		for px in range(px0, px0 + (x1 - x0) + 1):
			if px >= 0 and py < tile.size[1] and data[px, py]:
				if not v:
					c += 1
					v = 1
				else:
					v = 0
			else:
				v = 0
		cs.append(min(c, 5))

	matches = []
	for c in classifier:
		diff = [ cs[i] - min(classifier[c][i], 5)
			for i in range(0, 26) ]
		ok = 1
		errsum = 0
		for err in diff:
			errsum += err
			if abs(errsum) > 4:
				ok = 0
				break
		if ok:
			matches.append(( c, sum([ abs(err) for err in diff ]) ))
	if matches:
		m = sorted(matches, key=lambda match: abs(match[1]))[0]
		chars[( x0, y )] = m[0][0]
		#print(repr(( x0, y, m[0][0] )))
		#if m[1]:
		#	print(cs)
		return
	#if x0 > 8 and x1 < 4094:
	#	print(repr(( x0, y, cs )))

def scanimg(x, y):
	global data, bboxes, tile
	if os.path.getsize('atiles/' + str(x) + '/' + str(y) + '.png') == 2190:
		# Nothing to do
		return
	t0 = Image.open('atiles/' + str(x) + '/' + str(y) + '.png')
	try:
		t1 = Image.open('atiles/' + str(x + 1) + '/' + str(y) + '.png')
	except:
		t1 = None
	try:
		t2 = Image.open('atiles/' + str(x) + '/' + str(y - 1) + '.png')
	except:
		t2 = None
	try:
		t3 = Image.open('atiles/' + str(x + 1) + '/' + str(y - 1) + \
			'.png')
	except:
		t3 = None

	ovl = 26
	tile = Image.new(t0.mode, ( 4096 + ovl, 4096 + ovl ), 0)
	tile.paste(t0, ( 0, 0, 4096, 4096 ))
	if t1:
		r = t1.crop(( 0, 0, ovl, 4096 ))
		tile.paste(r, ( 4096, 0, 4096 + ovl, 4096 ))
	if t2:
		r = t2.crop(( 0, 0, 4096, ovl ))
		tile.paste(r, ( 0, 4096, 4096, 4096 + ovl ))
	if t3:
		r = t3.crop(( 0, 0, ovl, ovl ))
		tile.paste(r, ( 4096, 4096, 4096 + ovl, 4096 + ovl ))

	data = tile.load()

	bboxes = []

	## check for empty

	for y in range(0, tile.size[1]):
		for x in range(1, tile.size[0]):
			if not data[x, y]:
				continue
			done = 0
			for bb in bboxes:
				if x > bb[0] and x < bb[2] and \
						y > bb[1] and y < bb[3]:
					done = 1
			if done:
				continue

			scan(x, y)

bbox = ( 7564868, 5533526, 7578210.31, 5549568.53 )
tilesize = ( 410.0, 410.0 )

allchars = []
for x in range(0, int((bbox[2] - bbox[0]) / tilesize[0])):
	for y in range(0, int((bbox[3] - bbox[1]) / tilesize[1])):
		chars = {}
		scanimg(x, y)
		print('in ' + str(x) + ', ' + str(y) + ' found ' +
			str(len(chars.keys())) + ' chars')

		tbbox = (
			bbox[0] + (x + 0) * tilesize[0],
			bbox[1] + (y + 0) * tilesize[1],
			bbox[0] + (x + 1) * tilesize[0],
			bbox[1] + (y + 1) * tilesize[1] )

		for cx, cy in chars:
			midx = cx + 4
			midy = cy + 10
			fx = tbbox[0] + midx * tilesize[0] / 4096
			fy = tbbox[3] - midy * tilesize[1] / 4096
			allchars.append(( fx, fy, x, y, chars[( cx, cy )] ))
chfile = open('chars', 'wb')
for x, y, tx, ty, ch in allchars:
	chfile.write(str(x) + ' ' + str(y) + ' ' + str(tx) + ' ' +
		str(ty) + ' ' + ch + '\n')
chfile.close()
