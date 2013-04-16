import math
import re


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
    radius = 6371        # Earth's radius in KM
    start = (math.radians(start[0]), math.radians(start[1]))
    end = (math.radians(end[0]), math.radians(end[1]))
    dist = (math.acos(math.sin(start[0]) * math.sin(end[0]) +
            math.cos(start[0]) * math.cos(end[0]) *
            math.cos(end[1] - start[1])) * radius)

            # Rounds the distance to more precision for smaller distances.
            # This increases accuracy for very small distances.
    return (round(dist, 2) if len(str(dist).split('.')[0]) <= 2 else
            round(dist, 1) if len(str(dist).split('.')[0]) == 3 else
            round(dist))


def iszip(suspect):
    '''Based on the passed paramter, returns True if it looks like a
    valid zip code. Otherwise, it returns False.'''
    pattern = '^\d{5}$'
    match = re.match(pattern, str(suspect))
    return True if match is not None else False


def rem_chars(text, charlist):
    '''Returns text with all characters in charlist removed.'''
    new_text = text
    for char in charlist:
        if char in new_text:
            new_text = new_text.replace(char, '')
    return new_text


##############
## Unit Conversion tools
##############

def tomph(knots, precision=1):
    '''Converts knots to MPH.'''
    return round(float(knots) * 1.15078, precision)


def ctof(temp, precision=1):
    '''Converts Celsius to Fahrenheit.'''
    return round(float(temp) * 1.8 + 32, precision)


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