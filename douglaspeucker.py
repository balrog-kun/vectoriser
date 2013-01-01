# BSD license, Andrzej Zaborowski
import math

# Point-to-line distance
def line_distance(a, b, p):
	x, y = ( b[0] - a[0], b[1] - a[1] )
	return abs((p[0] - a[0]) * y - (p[1] - a[1]) * x) / math.hypot(x, y);

def simplify_sub(poly, dist):
	# trick:
	#if abs(abs(poly[0][0] - poly[-1][0]) / abs(poly[0][1] - poly[-1][1]))
	maxdist = 0
	middle = None
	for i in range(1, len(poly)):
		pdist = line_distance(poly[0], poly[-1], poly[i])
		if pdist > maxdist:
			maxdist = pdist
			middle = i
	if maxdist > dist:
		return simplify_sub(poly[:middle + 1], dist) + \
			simplify_sub(poly[middle:], dist)
	else:
		return [ poly[0] ]

def simplify_line(poly, dist):
	return simplify_sub(poly, dist) + [ poly[-1] ]

# The min-enclosing circle algorithm would work much better
def farthest_points(poly):
	maxdist = 0
	for i in range(0, len(poly) - 1):
		p = poly[i]
		for j in range(i + 1, len(poly)):
			p2 = poly[j]
			# math.hypot might be faster after all
			d = ( p2[0] - p[0], p2[1] - p[1] )
			dist = d[0] * d[0] + d[1] * d[1]
			if dist > maxdist:
				maxdist = dist
				x, y = ( i, j )
	return ( x, y )

def simplify_poly(poly, dist):
	x, y = farthest_points(poly)
	return simplify_sub(poly[x:y + 1], dist) + \
		simplify_sub(poly[y:] + poly[:x + 1], dist)
