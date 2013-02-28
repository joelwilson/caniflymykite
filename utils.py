import math


def between(num, low, high):
    '''Returns True if num between low & high (inclusive), else False.'''
    return True if num >= low and num <= high else False


def closest_point(start, points):
    '''Returns the point of the form (lat, lon) in a list of points which
    is closest to the starting point.'''
    return min(points, key=lambda p: distance(start, p))


def distance(start, end):
    '''Returns the distance (kilometers) between two points on the Earth.
    
    Uses the Spherical Law of Cosines to calculate distance.'''
    R = 6371        # Earth's radius in KM
    start = (math.radians(start[0]), math.radians(start[1]))
    end = (math.radians(end[0]), math.radians(end[1]))
    d = (math.acos(math.sin(start[0]) * math.sin(end[0]) +
         math.cos(start[0]) * math.cos(end[0]) *
         math.cos(end[1] - start[1])) * R)
    return (round(d, 2) if len(str(d).split('.')[0]) <= 2 else
            round(d, 1) if len(str(d).split('.')[0]) == 3 else
            round(d))


def tomph(knots, precision=1):
    '''Converts knots to MPH.'''
    return round(float(knots) * 1.15078, precision)


def ctof(temp):
    '''Converts Celsius to Fahrenheit.'''
    return float(temp) * 1.8 + 32


def heading(deg):
    '''Returns a string representation of an numerical direction in degrees.

    Examples:
        heading(360) => "N"
        heading('45')  => "NE"
    '''
    deg = float(deg)
    head = {
        'N1':  (0,     22.5),
        'NE':  (22.6,  67.5),
        'E':   (67.6,  112.5),
        'SE':  (112.6, 157.5),
        'S':   (157.6, 202.5),
        'SW':  (202.6, 247.5),
        'W':   (247.6, 292.5),
        'NW':  (292.6, 337.5),
        'N2':  (337.6, 360.0)
    }
    for key, val in head.iteritems():
        if between(deg, *val):
            return 'N' if key == 'N1' or key == 'N2' else key
    return None