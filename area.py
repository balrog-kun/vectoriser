# BSD license, Andrzej Zaborowski
def area(poly):
	a = 0
	j = poly[-1]
	for i in poly:
		a += j[0] * i[1] - i[0] * j[1]
		j = i
	return 0.5 * abs(a)

import math

def expand(poly, dist):
	p = []
	x = poly[-2]
	y = poly[-1]
	for z in poly:
		v0 = ( y[0] - x[0], y[1] - x[1] )
		v1 = ( z[0] - y[0], z[1] - y[1] )
		l0 = math.hypot(v0[0], v0[1])
		l1 = math.hypot(v1[0], v1[1])
		o = ( -v0[1] / l0 - v1[1] / l1, v0[0] / l0 + v1[0] / l1 )
		d = abs(o[0] * v1[1] - o[1] * v1[0]) / l1;
		l = math.hypot(o[0], o[1])
		# Drop it or leave it?  Drop the point
		if l > 0.2:
			p.append(( y[0] + o[0] * dist / d,
				y[1] + o[1] * dist / d))

		x, y = ( y, z )
	return p

def contains(poly, pos):
	cont = 0
	prev = poly[-1]
	for node in poly:
		if (node[1] > pos[1]) != (prev[1] > pos[1]) and \
				pos[0] < node[0] + (prev[0] - node[0]) * \
				(pos[1] - node[1]) / (prev[1] - node[1]):
			cont = not cont
		prev = node
	return cont
