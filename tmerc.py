# BSD license, Andrzej Zaborowski
import math

polar_radius = 6356752.3
eq_radius = 6378137.0
polar_length = polar_radius * 2.0 * math.pi
eq_length = eq_radius * 2.0 * math.pi

def lat_radius(lat):
    rad = math.radians(lat)
    a2 = eq_radius * math.cos(rad)
    a1 = eq_radius * a2
    b2 = polar_radius * math.sin(rad)
    b1 = polar_radius * b2
    return math.sqrt((a1 * a1 + b1 * b1) / (a2 * a2 + b2 * b2))

def unproj_epsg2178(x, y):
    lat = y / polar_length * 360.0
    deg_per_m = 180.0 / (math.pi * lat_radius(lat) *
            math.cos(math.radians(lat)))

    lon = 21.0 + (x - 7500000.0) * deg_per_m
    return ( lat, lon )

def proj_epsg2178(lat, lon):
    deg_per_m = 180.0 / (math.pi * lat_radius(lat) *
            math.cos(math.radians(lat)))

    x = 7500000.0 + (lon - 21.0) / deg_per_m
    y = lat * polar_length / 360.0
    return ( x, y )

# EPSG:2178
a = 6378137.0     # GRS80 eq radius
b = 6356752.3141  # GRS80 polar radius
f = 298.257222101 # GRS80 flattening
long0 = 21.0      # Central meridian of zone
x0 = 7500000.0
k0 = 0.999923     # Scale along long0
e = math.sqrt(1.0 - b * b / a / a) # Eccentricity of Earth's elliptical xsection
ep2 = e * e / (1.0 - e * e)
e1 = (1.0 - math.sqrt(1.0 - e * e)) / (1.0 + math.sqrt(1.0 - e * e))
J1 = 1.5 * e1 - 27.0 * e1 * e1 * e1 / 32.0 # + ....
J2 = 21.0 * e1 * e1 / 16.0 - 55.0 * e1 * e1 * e1 * e1 / 32.0 # + ....
J3 = 151.0 * e1 * e1 * e1 / 96.0 # + ....
J4 = 1097.0 * e1 * e1 * e1 * e1 / 512.0 # + ....

# Universal Traverse Mercator
def uproj_tmerc(x, y):
    easting = x - x0
    northing = y
    # Meridional Arc
    M = northing / k0
    mu = M / (a * (1.0 - e * e / 4.0 - 3.0 * e * e * e * e / 64.0 -
        5.0 * e * e * e * e * e * e / 256.0))

    # Footprint latitude
    fp = mu + J1 * math.sin(2.0 * mu) + J2 * math.sin(4.0 * mu) + \
            J3 * math.sin(6.0 * mu) + J4 * math.sin(8.0 * mu)
    C1 = ep2 * math.cos(fp) * math.cos(fp)
    T1 = math.tan(fp) * math.tan(fp)
    # Radius of curvature in meridian plane
    R1 = a * (1.0 - e * e) / \
            math.pow(1.0 - e * e * math.sin(fp) * math.sin(fp), 1.5)
    # Radius of curvature perpendicular to meridian plane
    N1 = a / math.sqrt(1.0 - e * e * math.sin(fp) * math.sin(fp))
    D = easting / (N1 * k0)

    Q1 = N1 * math.tan(fp) / R1
    Q2 = D * D / 2.0
    Q3 = (5.0 + 3.0 * T1 + 10.0 * C1 - 4.0 * C1 * C1 - 9.0 * ep2) * \
            D * D * D * D / 24.0
    Q4 = (61.0 + 90.0 * T1 + 298.0 * C1 + 45.0 * T1 * T1 - 3.0 * C1 * C1 -
            252.0 * ep2) * D * D * D * D * D * D / 720.0
    Q5 = D
    Q6 = (1.0 + 2.0 * T1 + C1) * D * D * D / 6.0
    Q7 = (5.0 - 2.0 * C1 + 28.0 * T1 - 3.0 * C1 * C1 + 8.0 * ep2 +
            24.0 * T1 * T1) * D * D * D * D * D / 120.0

    lat = fp - Q1 * (Q2 - Q3 + Q4)
    lon = math.radians(long0) + (Q5 - Q6 + Q7) / math.cos(fp)

    return ( math.degrees(lat), math.degrees(lon) )

# Could instead pipe through cs2cs +proj=latlong +datum=WGS84 +to +proj=tmerc +lat_0=0 +lon_0=21 +k=0.999923 +x_0=7500000 +y_0=0 +ellps=GRS80 +units=m +no_defs
