#! /sw/bin/python2.7
# vim: fileencoding=utf-8 encoding=utf-8
# BSD license, Andrzej Zaborowski
import PIL.Image as Image
import ImageDraw as ImageDraw
import os
import sys
import math
import xml.etree.cElementTree as ElementTree

# 8-way search
order = [
	( 1, 0 ),
	( 1, 1 ),
	( 0, 1 ),
	( -1, 1 ),
	( -1, 0 ),
	( -1, -1 ),
	( 0, -1 ),
	( 1, -1 ),
]

# 4-way search
order = [
	( 0, 0, 1, 0 ),
	( -1, 0, 0, 1 ),
	( -1, -1, -1, 0 ),
	( 0, -1, 0, -1 ),
]

tile = None
data = None
draw = None
def iswall(x, y):
	global tile, data
	if x < 0 or y < 0 or x >= tile.size[0] or y >= tile.size[1]:
		raise Exception('throw this shape away')
		#return False
	return data[x, y][1] < 100
def isempty(x, y):
	global data
	return data[x, y][1] > 200
def markdone(x, y):
	global draw
	draw.point(( x, y ), fill=( 128, 128, 128 ))
def markclean(x, y):
	global draw
	draw.point(( x, y ), fill=( 255, 255, 255 ))
def walk(orig, marks):
	cur = ( orig[0] + 1, orig[1] + 1)
	curdir = 0

	shape = []

	while 1:
		shape.append(cur)
		if curdir == 0:
			marks.append(( cur[0] - 1, cur[1] - 1 ))
			markdone( cur[0] - 1, cur[1] - 1 )

		dirs = [ (curdir + i) & 3 for i in [ 0, 1, 2 ] ]
		wall = [ iswall(cur[0] + order[d][0], cur[1] + order[d][1]) \
			for d in dirs ]
		if not wall[0] and not wall[1]:
			r = dirs[0]
		elif not wall[1] and not wall[2]:
			r = dirs[1]
		else:
			r = dirs[2]
		cur = ( cur[0] + order[r][2], cur[1] + order[r][3] )
		curdir = (r + 3) & 3

		if cur == shape[0]:
			break
	shape.reverse()
	return shape

def intersection(a, b, c, d):
	x = a[0] * b[1] - a[1] * b[0]
	y = c[0] * d[1] - c[1] * d[0]
	z = (a[0] - b[0]) * (c[1] - d[1]) - (a[1] - b[1]) * (c[0] - d[0])
	return ( (x * (c[0] - d[0]) - y * (a[0] - b[0])) / z,
		(x * (c[1] - d[1]) - y * (a[1] - b[1])) / z )

shape = None
def shape_idx_wrap(x):
	global shape
	if x >= len(shape):
		return x - len(shape)
	if x < 0:
		return x + len(shape)
	return x

# Orthogonalise just a bit
def orthogonalise():
	global shape
	for i in range(0, len(shape)):
		a = shape[i]
		b = shape[shape_idx_wrap(i + 1)]
		v = ( b[0] - a[0], b[1] - a[1] )
		d = math.hypot(v[0], v[1])
		if d < 17:
			continue
		# We found an edge longer than 20 px, now see if we have
		# any adjacent edgest shorter than 10 px and if so, make
		# them orthogonal to this one.  The shorter an edge, the
		# less accurate is its angle, and vice versa.
		x = a
		y = b
		previdx = i
		for j in range(i + 2, i + 6):
			z = shape[shape_idx_wrap(j)]
			w = ( z[0] - y[0], z[1] - y[1] )
			e = math.hypot(w[0], w[1])
			if e > 15:
				break
			if d < 0.001:
				break
			xyz = rhr.getangle(x, y, z)
			if abs(xyz) < 50 - e * 4:
				normal = ( v[0] / d, v[1] / d )
			if abs(xyz) > 150 + e * 1:
				normal = ( -v[0] / d, -v[1] / d )
			elif abs(90 - xyz) < 45 - e * 3:
				normal = ( -v[1] / d, v[0] / d )
			elif abs(-90 - xyz) < 45 - e * 3:
				normal = ( v[1] / d, -v[0] / d )
			else:
				break
			mid = ( (z[0] + y[0]) * 0.5, (z[1] + y[1]) * 0.5 )
			dist = douglaspeucker.line_distance(x, y, mid)

			y = ( mid[0] - dist * normal[0],
				mid[1] - dist * normal[1] )
			shape[shape_idx_wrap(j - 1)] = y
			z = ( mid[0] + dist * normal[0],
				mid[1] + dist * normal[1] )
			shape[shape_idx_wrap(j - 0)] = z

			w = ( z[0] - y[0], z[1] - y[1] )
			e = math.hypot(w[0], w[1])
			x = y
			y = z
			v = w
			d = e

		a = shape[i]
		b = shape[shape_idx_wrap(i + 1)]
		v = ( a[0] - b[0], a[1] - b[1] )
		d = math.hypot(v[0], v[1])
		x = b
		y = a
		previdx = i
		for j in [ i - 1, i - 2, i - 3, i - 4 ]:
			z = shape[shape_idx_wrap(j)]
			w = ( z[0] - y[0], z[1] - y[1] )
			e = math.hypot(w[0], w[1])
			if e > 15:
				break
			if d < 0.001:
				break
			xyz = rhr.getangle(x, y, z)
			if abs(xyz) < 50 - e * 4:
				normal = ( v[0] / d, v[1] / d )
			if abs(xyz) > 150 + e * 1:
				normal = ( -v[0] / d, -v[1] / d )
			elif abs(90 - xyz) < 40 - e * 3:
				normal = ( -v[1] / d, v[0] / d )
			elif abs(-90 - xyz) < 40 - e * 3:
				normal = ( v[1] / d, -v[0] / d )
			else:
				break
			mid = ( (z[0] + y[0]) * 0.5, (z[1] + y[1]) * 0.5 )
			dist = douglaspeucker.line_distance(x, y, mid)

			y = ( mid[0] - dist * normal[0],
				mid[1] - dist * normal[1] )
			shape[shape_idx_wrap(j + 1)] = y
			z = ( mid[0] + dist * normal[0],
				mid[1] + dist * normal[1] )
			shape[shape_idx_wrap(j + 0)] = z

			w = ( z[0] - y[0], z[1] - y[1] )
			e = math.hypot(w[0], w[1])
			x = y
			y = z
			v = w
			d = e

# Remove excessive segments at funny angles at the corners
def fixcorners():
	global shape
	todel = []
	skip = 0
	for i in range(0, len(shape)):
		if skip:
			skip -= 1
			continue
		a = shape[i]
		b = shape[shape_idx_wrap(i + 1)]
		v = ( b[0] - a[0], b[1] - a[1] )
		d = math.hypot(v[0], v[1])
		if d < 11:
			continue
		# We found an edge longer than 11 px, now see if we have
		# any adjacent edges shorter than 10 px at funny angles
		# and an orthogonal longer edge (or a long one) later.
		# Simplify away the whole thing then
		x = a
		y = b
		previdx = i
		funny = 0
		for j in range(i + 2, i + 6):
			z = shape[shape_idx_wrap(j)]
			w = ( z[0] - y[0], z[1] - y[1] )
			e = math.hypot(w[0], w[1])
			abyz = rhr.getangle(a, b, ( b[0] + w[0], b[1] + w[1] ))
			abyz = abs(abs(abyz) - 90)
			if (e > 16 or (e > 10 and abyz < 10)) and \
					abyz < 70 and funny:
				# Place a new node at the intersection of
				# the two long segments and scrub everything
				# in between
				for k in range(i + 1, j - 1):
					todel.append(shape_idx_wrap(k))
				skip = j - i - 2
				j1 = shape_idx_wrap(j - 1)
				shape[j1] = intersection(a, b, y, z)
				break
			if e > 9:
				break
			if abs(abyz - 90) > 15 and abs(abyz - 90) < 75:
				funny = 1
			if math.hypot(z[0] - b[0], z[1] - b[1]) > 9:
				break
			x = y
			y = z
			v = w
			d = e

	todel.sort()
	todel.reverse()
	for i in todel:
		del shape[i]

# Add new nodes at unnoded intersections
def checkintersect(nodes, ways, way):
	epsilon = 0.0001
	prev0 = nodes[way[0]]
	add0 = []
	for nd0 in range(1, len(way)):
		cur0 = nodes[way[nd0]]
		for w1 in ways:
			if w1 is way:
				continue
			prev1 = nodes[w1[0]]
			add1 = []
			for nd1 in range(1, len(w1)):
				cur1 = nodes[w1[nd1]]
				val = rhr.isleft(prev0, cur0, prev1) * \
					rhr.isleft(prev0, cur0, cur1)
				if val > -epsilon:
					prev1 = cur1
					continue
				val = rhr.isleft(prev1, cur1, prev0) * \
					rhr.isleft(prev1, cur1, cur0)
				if val > -epsilon:
					prev1 = cur1
					continue
				# There's an unnoded intersection,
				# add it to both of our ways
				add0.append(( nd0, len(nodes) ))
				add1.append(( nd1, len(nodes) ))
				nodes.append(
					intersection(prev0, cur0, prev1, cur1))

				prev1 = cur1
			add1.reverse()
			for pos, nd in add1:
				w1.insert(pos, nd)
		prev0 = cur0
	add0.reverse()
	for pos, nd in add0:
		way.insert(pos, nd)

# Dump nodes that lie inside other, bigger buildings.
# This is because we assume that bigger buildings on average have longer
# straight walls and longer lines are always more accurately vectorised.
def checkwithin(nodes, ways, areas, num):
	epsilon = 0.0001
	a0 = areas[num]
	w0 = ways[num]
	del0 = []
	for i in range(1, len(w0)):
		pos = nodes[w0[i]]
		for j in range(0, len(ways)):
			a1 = areas[j]
			w1 = ways[j]
			#if a1 > a0 + epsilon and w0[i] not in w1:
			if w0[i] in w1:
				continue
			poly = [ nodes[k] for k in w1[1:] ]
			if len(poly) > 3 and area.contains(poly, pos):
				del0.append(i)
				break
	del0.reverse()
	for pos in del0:
		del w0[pos]
	if w0[0] != w0[-1]:
		del w0[0]
		w0.append(w0[0])

chars = {}
names = {}
ocrbbox = ( 7564868, 5533526, 7578210.31, 5549568.53 )
def addchar(x, y, tx, ty, ch):
	if ( tx, ty ) not in chars:
		chars[( tx, ty )] = []
	chars[( tx, ty )].append(( x, y, ch ))
chfile = open('chars', 'rb')
for line in chfile:
	x, y, tx, ty, ch = line.split()
	tx, ty = ( int(tx), int(ty) )
	x = float(x) + tx * 410.0
	y = float(y) - (ocrbbox[3] - ocrbbox[1]) + (ty + 1) * 410.0
	addchar(x, y, tx, ty, ch)
	addchar(x, y, tx - 1, ty, ch)
	addchar(x, y, tx, ty - 1, ch)
	addchar(x, y, tx + 1, ty, ch)
	addchar(x, y, tx, ty + 1, ch)
chfile.close()

import rhr
import douglaspeucker
import area

bbox = ( 7564868.068, 5533526.79, 7578210.31, 5549568.53 )
tilesize = ( 410.0, 410.0 )

allnodes = []
allways = []

tx0 = 0
tx1 = int((bbox[2] - bbox[0]) / tilesize[0])
ty0 = 0
ty1 = int((bbox[3] - bbox[1]) / tilesize[1])
if len(sys.argv) >= 5:
	tx0 = int(sys.argv[1])
	ty0 = int(sys.argv[2])
	tx1 = int(sys.argv[3])
	ty1 = int(sys.argv[4])

for y in range(ty0, ty1):
	for tx in range(0, tx1 - tx0):
		x = tx1 - 1 - tx
		print(x, y) ###
		if os.path.getsize('ctiles/' + str(x) + '/' + str(y) + \
				'.png') == 2190:
			# Nothing to do
			continue
		t0 = Image.open('ctiles/' + str(x) + '/' + str(y) + '.png')
		t0.convert('RGB')
		try:
			t1 = Image.open('ctiles/' + str(x + 1) + '/' +
				str(y) + '.png')
			t1.convert('RGB')
		except:
			t1 = None
		try:
			t2 = Image.open('ctiles/' + str(x) + '/' +
				str(y - 1) + '.png')
			t2.convert('RGB')
		except:
			t2 = None

		ovl = 250
		tile = Image.new('RGB', ( 4096 + ovl, 4096 + ovl ), 255)
		tile.paste(t0, ( 0, 0, 4096, 4096 ))
		if t1:
			r = t1.crop(( 0, 0, ovl, t1.size[1] ))
			tile.paste(r, ( 4096, 0, 4096 + ovl, t1.size[1] ))
		if t2:
			r = t2.crop(( 0, 0, 4096, ovl ))
			tile.paste(r, ( 0, 4096, 4096, 4096 + ovl ))

		data = tile.load()
		draw = ImageDraw.Draw(tile)
		if not t1 or t1.size[1] < 4096 + ovl:
			top = 0
			if t1:
				top = t1.size[1]
			draw.rectangle(( 4096, top, \
					4096 + ovl, 4096 + ovl ), \
				outline=( 255, 255, 255 ), \
				fill=( 255, 255, 255 ))

		tbbox = (
			bbox[0] + (x + 0) * tilesize[0],
			bbox[1] + (y + 0) * tilesize[1],
			bbox[0] + (x + 1) * tilesize[0],
			bbox[1] + (y + 1) * tilesize[1] )

		shapes = []
		remove = []
		for px in range(1, tile.size[1]):
			for py in range(0, tile.size[1]):
				if not iswall(px, py) or \
						not isempty(px - 1, py):
					continue
				marks = []
				try:
					shapes.append(walk(( px - 1, py ),
						marks))
				except Exception as e:
					remove += marks
		for px, py in remove:
			markclean(px, py)
		tile.save('ctiles/' + str(x) + '/' + str(y) + '.png')

		shapes = [ shape for shape in shapes if rhr.is_rhr(shape) ]
		shapes = [ douglaspeucker.simplify_poly(shape, 1.4)
			for shape in shapes ]
		shapes = [ shape for shape in shapes if len(shape) > 2 ]
		shapes = [ shape for shape in shapes if area.area(shape) > 150 ]

		for shape in shapes:
			orthogonalise()

		shapes = [ douglaspeucker.simplify_poly(shape, 1.0)
			for shape in shapes ]

		for shape in shapes:
			fixcorners()

		shapes = [ area.expand(shape, 1.5) for shape in shapes ]

		# Merge nodes
		nodes = []
		ways = []
		snappedways = []
		for shape in shapes:
			snapped = []
			snappedways.append(snapped)
			for p in shape:
				stored = 0
				for i in range(0, len(nodes)):
					n = nodes[i]
					px = n[0] - p[0]
					py = n[1] - p[1]
					if abs(px) < 5 and abs(py) < 5:
						if px * px + py * py < 1.1:
							n[2].append(p)
							snapped.append(i)
							stored = 1
							break
				if not stored:
					snapped.append(len(nodes))
					nodes.append(( p[0], p[1], [ p ]))
		shapes = None
		for i in range(0, len(nodes)):
			px = 0
			py = 0
			l = nodes[i][2]
			for p in l:
				px += p[0]
				py += p[1]
			px /= len(l)
			py /= len(l)
			if math.hypot(nodes[i][0] - px, nodes[i][1] - py) > 1.0:
				nodes[i] = nodes[i][:2]
				print('weird')
				continue
			nodes[i] = ( px, py )

		# Create ways using the new nodes
		for shape in snappedways:
			if not shape:
				continue
			n0 = shape[-1]
			way = []
			ways.append(way)
			for n1 in shape:
				nds = []
				a = nodes[n0]
				b = nodes[n1]
				x0 = min(a[0], b[0]) - 2
				y0 = min(a[1], b[1]) - 2
				x1 = max(a[0], b[0]) + 2
				y1 = max(a[1], b[1]) + 2
				d = math.hypot(a[0] - b[0], a[1] - b[1])
				if d < 0.5:
					n0 = n1
					continue
				for i in range(0, len(nodes)):
					n = nodes[i]
					if n[0] > x0 and n[0] < x1 and \
							n[1] > y0 and n[1] < y1:
						if douglaspeucker.line_distance(
								a, b, n) < 1.1:
							nds.append(( i, n ))
				nnds = []
				for i, n in nds:
					# Note that working with squares of the
					# distances would have worked just as
					# well and saved finding the square
					# roots
					d0 = math.hypot(n[0] - a[0],
						n[1] - a[1])
					d1 = math.hypot(n[0] - b[0],
						n[1] - b[1])
					if d0 > d + 0.1 or d1 > d + 0.1:
						pass
					elif d0 > d1:
						nnds.append(( i, d0 ))
					else:
						nnds.append(( i, d - d1 ))
				nds = sorted(nnds, key=lambda nd: nd[1])
				if nds[0][0] != n0 or nds[-1][0] != n1:
					print('hmmm')
				if way:
					way += [ i for i, d in nds[1:] ]
				else:
					way += [ i for i, d in nds ]

				n0 = nds[-1][0]
			if way[0] != way[-1]:
				print('hmmmhmmm')

		# Split at nodes that appear more than once in a way
		i = 0
		while i < len(ways):
			counts = {}
			for n in ways[i][1:]:
				if n in counts:
					counts[n] += 1
				else:
					counts[n] = 1

			for n in counts:
				if counts[n] == 1:
					continue
				while counts[n] > 1:
					i0 = ways[i].index(n)
					i1 = i0 + 1 + ways[i][i0 + 1:].index(n)
					ways.append(ways[i][i0:i1 + 1])
					ways[i] = ways[i][:i0] + ways[i][i1:]
					counts[n] -= 1
				ways.append(ways[i])
				ways[i] = []
				break
			i += 1
		ways = [ way for way in ways if len(way) > 3 and \
			area.area([ nodes[i] for i in way[1:] ]) > 120 ]

		# Create nodes at unnoded intersections
		for w in ways:
			checkintersect(nodes, ways, w)

		# Now we can safely dump nodes inside other buildings
		areas = [ area.area([ nodes[i] for i in w[1:] ]) for w in ways ]
		for i in range(0, len(ways)):
			checkwithin(nodes, ways, areas, i)
		ways = [ way for way in ways if len(way) > 3 ]

		# Refcount nodes
		counts = {}
		for w in ways:
			for n in w:
				if n in counts:
					counts[n] += 1
				else:
					counts[n] = 1

		start = len(allnodes)
		nodemap = {}
		for i in range(0, len(nodes)):
			if i not in counts:
				continue

			fx = tbbox[0] + nodes[i][0] * tilesize[0] / 4096
			fy = tbbox[3] - nodes[i][1] * tilesize[1] / 4096

			nodemap[i] = start
			allnodes.append(( fx, fy ))
			start += 1
		for w in ways:
			for i in range(0, len(w)):
				w[i] = nodemap[w[i]]
			namechars = []
			poly = [ allnodes[i] for i in w[1:] ]
			for px, py, ch in chars[( x, y )]:
				if area.contains(poly, ( px, py )):
					namechars.append(( ch, px ))
			if namechars:
				name = sorted(namechars, key=lambda ch: ch[1])
				name = ''.join([ ch[0] for ch, px in name ])
				names[len(allways)] = name
			elif area.area(poly) > 20:
				names[len(allways)] = '1k'
			allways.append(w)

import tmerc

funcs = {
	'p': ( 'industrial', u'Przemysłowy', 'landuse', 'industrial' ),
	't': ( 'garage', u'Transportu lub łączności' ),
	'h': ( 'retail', u'Handlowo-usługowy', 'landuse', 'retail' ),
	's': ( 'storage', u'Skład lub magazyn' ),
	'b': ( 'office', u'Biurowy', 'landuse', 'commercial' ),
	'z': ( 'healthcare', u'Ochrony zdrowia, opieki socjalnej', 'amenity',
		'hospital' ),
	'm': ( 'residential', u'Mieszkalny' ),
	'k': ( 'cultural', u'Kultury, oświaty, kultu religijnego', 'amenity',
		'school;place_of_worship' ),
	'g': ( 'manufacture', u'Gospodarczy' ),
	'i': ( 'service', u'Inny' ),
	'x': ( 'yes', ),
	'ciepl': ( 'greenhouse', u'Cieplarnia' ),
	'trans': ( 'industrial', u'Transformator', 'power', 'substation' ),
	'f':     ( 'foundation', u'Fundament', 'building:levels', '0' ),
	'w':     ( 'industrial', u'Waga' ),
	'r':     ( 'ruin', u'Ruina' ),
}

root = ElementTree.Element("osm", { "version": "0.6" })
for i in range(0, len(allnodes)):
	x, y = allnodes[i]
	ll = tmerc.uproj_tmerc(x, y)
	node = ElementTree.SubElement(root, "node", {
		"lat": str(ll[0]),
		"lon": str(ll[1]),
		"version": str(1),
		"id": str(i + 1) })
for i in range(0, len(allways)):
	node = ElementTree.SubElement(root, "way", {
		"version": str(1),
		"id": str(i + 1) })
	for j in allways[i]:
		subnode = ElementTree.SubElement(node, "nd", {
			"ref": str(j + 1) })
	tags = {}
	tags['building'] = 'yes'
	tags['building:levels'] = '1'
	tags['source'] = u'UM Rzeszów'
	if i in names:
		name = names[i].lower()
		name.replace('.', '')
		pos = name[1:].find('k')
		if pos > -1:
			pos += 1
			st = pos
			while st > 0 and name[st - 1].isdigit():
				st -= 1
			if st < pos:
				if st < pos - 1 and name[pos - 1] == '5':
					levels = name[st:pos - 1] + '.5'
				else:
					levels = name[st:pos]
				name = name[:st] + name[pos + 1:]
				tags['building:levels'] = levels
		elif len(name) >= 2 and name[1].isdigit():
			st = 1
			while len(name) > st + 1 and name[st + 1].isdigit():
				st += 1
			if st >= 2 and name[st] == '5':
				levels = name[1:st] + '.5'
			else:
				levels = name[1:st + 1]
			name = name[:1] + name[st + 1:]
			tags['building:levels'] = levels
		func = 'm'
		if 'iep' in name:
			func = 'ciepl'
		elif 'ans' in name:
			func = 'trans'
		elif name:
			func = name[0]
		if func in funcs:
			f = funcs[func]
			tags['building'] = f[0]
			if len(f) > 1:
				tags['building:usage:pl'] = f[1]
			if len(f) >= 4:
				tags[f[2]] = f[3]
		elif name:
			tags['name'] = name ###
	for k in tags:
		ElementTree.SubElement(node, "tag", {
			"k": k,
			"v": tags[k] })
'''
i = len(allnodes)
for x, y, ch in chars[( tx0, ty0 )]:
	ll = tmerc.uproj_tmerc(x, y)
	node = ElementTree.SubElement(root, "node", {
		"lat": str(ll[0]),
		"lon": str(ll[1]),
		"version": str(1),
		"id": str(i + 1) })
	ElementTree.SubElement(node, "tag", {
		"k": 'name',
		"v": ch })
	i += 1
'''

ElementTree.ElementTree(root).write("output.osm", "utf-8")
