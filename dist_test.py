#!/usr/bin/python3
from math import sin, cos, sqrt, atan2, radians

# Simple distance calculation without other python module dependencies. Which results in errors of up to about 0.5%
# https://en.wikipedia.org/wiki/Haversine_formula

# An alternative package is gpxpy
# Vincenty distance uses more accurate ellipsoidal models such as WGS-84, and is implemented in geopy.
# import geopy.distance
# coords_1 = (52.2296756, 21.0122287)
# coords_2 = (52.406374, 16.9251681)
# print geopy.distance.vincenty(coords_1, coords_2).km

# An alternative package-2 is mpu
# import mpu
# dist = mpu.haversine_distance((lat1, lon1), (lat2, lon2))


# def distance_between(self, lat1, lon1, lat2, lon2):
def test():
    r = 6373.0
    # test data
    lat1 = radians(52.2296756)
    lon1 = radians(21.0122287)
    lat2 = radians(52.406374)
    lon2 = radians(16.9251681)

    # lat1 = radians(lat1)
    # lon1 = radians(lon1)
    # lat2 = radians(lat2)
    # lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    distance = r * c

    print("Result", distance)
    print("Should be", 278.546)
    return distance


test()
