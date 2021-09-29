#!/usr/bin/python3
import os
import threading
from gps import *
from time import *
import time
from datetime import datetime
from math import sin, cos, sqrt, atan2, radians


gpsd = None
dbg = True


class GpsProcessor:
    def __init__(self):
        # self.gps_values_valid = False
        pass

    @staticmethod
    def is_gps_values_valid():
        gps_values_valid = False
        if gpsd.satellites_used < 4 or \
                gpsd.utc is NaN or \
                gpsd.fix.latitude is NaN or gpsd.fix.longitude is NaN or \
                (gpsd.fix.latitude == 0.0 and gpsd.fix.longitude == 0.0):
            gps_values_valid = False
        else:
            gps_values_valid = True

        return gps_values_valid

    @staticmethod
    def is_gps_values_filtered():
        return False

    @staticmethod
    def show():
        if dbg:
            print(gpsd.fix.latitude, '\t', gpsd.fix.longitude, '\t', gpsd.utc, '\t',
                  gpsd.fix.altitude, '\t', gpsd.fix.epx,       '\t', gpsd.fix.speed, '\t', gpsd.satellites_used, '\t',
                  GpsProcessor.is_gps_values_valid())

    # print(' GPS reading')
    # print('----------------------------------------')
    # print('latitude    ', gpsd.fix.latitude)
    # print('longitude   ', gpsd.fix.longitude)
    # print('time utc    ', gpsd.utc, ' + ', gpsd.fix.time)
    # print('altitude (m)', gpsd.fix.altitude)
    # print('eps         ', gpsd.fix.eps)
    # print('epx         ', gpsd.fix.epx)
    # print('epv         ', gpsd.fix.epv)
    # print('ept         ', gpsd.fix.ept)
    # print('speed (m/s) ', gpsd.fix.speed)
    # print('speed (mph) ', gpsd.fix.speed * 2.237)
    # print('climb       ', gpsd.fix.climb)
    # print('track       ', gpsd.fix.track)
    # print('mode        ', gpsd.fix.mode)
    # print('satellites in view:', len(gpsd.satellites))
    # print
    # print('sats        ', gpsd.satellites)


class Point:
    date = ''
    latitude = 0.0
    longitude = 0.0
    altitude = 0.0
    speed = 0.0


class FileTracker:
    def __init__(self):
        self.points = []
        self.gpx_file_started = False
        self.gpx_file = None
        self.gpx_file_name = ""
        self.prev_lat = 0.0
        self.prev_lng = 0.0

    def gpx_file_update(self):
        ret = False
        if not GpsProcessor.is_gps_values_valid():
            print("GPS data not ready. Waiting correct date...")
            return False

        if not self.gpx_file_started:
            print("Track GPX file isn't started")
            ret = self.gpx_file_init()
            return ret

        if self.is_filtered():
            print("GPS date filtered!")
            return False

        self.write_points()

    def gpx_file_init(self):
        ret = False
        if not GpsProcessor.is_gps_values_valid():
            print("GPS data isn't ready. Waiting correct date...")
            ret = False
            return ret

        print("gpx_file_init")
        date_time_obj = datetime.strptime(gpsd.utc, "%Y-%m-%dT%H:%M:%S.%f%z")
        self.gpx_file_name = str(date_time_obj.date()) + ".gpx"

        file_exist = os.path.exists(self.gpx_file_name)
        file_correct = False
        size = 0
        if file_exist:
            size = os.path.getsize(self.gpx_file_name)

        if size != 0:
            file_correct = True    # todo: Check zero size and structure

        if (not file_exist) or (not file_correct):
            try:
                print("Create file", self.gpx_file_name)
                self.gpx_file = open(self.gpx_file_name, "w+")
                gpx_head = '''<gpx version="1.1" creator="LVR GPX Lib" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
 xmlns="http://www.topografix.com/GPX/1/1"
 xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd"
>
<metadata><desc>foofoofoo</desc>
</metadata>
<trk>
<name>track name</name>
<desc>Track description</desc>'''
                gpx_trk_seg_open = "\n<trkseg>\n"
                self.gpx_file.write(gpx_head + gpx_trk_seg_open)
                print("Head created", self.gpx_file_name)

                self.prev_lat = gpsd.fix.latitude
                self.prev_lng = gpsd.fix.longitude

                point = Point()
                point.date = gpsd.utc
                point.latitude = gpsd.fix.latitude
                point.longitude = gpsd.fix.longitude
                point.altitude = gpsd.fix.altitude
                point.speed = gpsd.fix.speed
                trkpt = '<trkpt lat="{}" lon="{}"><ele>{}</ele><speed>{}</speed><time>{}</time></trkpt>' \
                    .format(point.latitude, point.longitude, point.altitude, point.speed, point.date)
                tail = "\n</trkseg>\n</trk>\n</gpx>\n"
                self.gpx_file.write(trkpt + tail)
                self.gpx_file.flush()
                self.gpx_file.close()
                os.sync()
                print("Tail created", self.gpx_file_name)
            except IOError:
                print("Can not create GPX file")
                self.gpx_file_started = False
                ret = False
                return ret
            self.gpx_file_started = True
            ret = True
        else:
            print("File already created")
            self.gpx_file_started = True
            ret = True
        return ret

    def add_point(self):
        if GpsProcessor.is_gps_values_valid():
            point = Point()
            point.date = gpsd.utc
            point.latitude = gpsd.fix.latitude
            point.longitude = gpsd.fix.longitude
            point.altitude = gpsd.fix.altitude
            point.speed = gpsd.fix.speed
            self.points.append(point)

    def write_points(self):
        point = Point()
        point.date = gpsd.utc
        point.latitude = gpsd.fix.latitude
        point.longitude = gpsd.fix.longitude
        point.altitude = gpsd.fix.altitude
        point.speed = gpsd.fix.speed

        # size = os.path.getsize(self.gpx_file_name)
        self.gpx_file = open(self.gpx_file_name, "r+b")

        # print("file size", size)
        # print("file tell 1", self.gpx_file.tell())
        self.gpx_file.seek(-24, 2)

        # <trkpt lat="53.932846" lon="27.488501"><ele>328.5</ele><speed>4.0</speed><time>2020-11-09T16:21:45Z</time></trkpt>
        trkpt = '<trkpt lat="{}" lon="{}"><ele>{}</ele><speed>{}</speed><time>{}</time></trkpt>'\
                .format(point.latitude, point.longitude, point.altitude, point.speed, point.date)
        tail = "\n</trkseg>\n</trk>\n</gpx>\n"
        self.gpx_file.write((trkpt+tail).encode())
        self.gpx_file.flush()
        self.gpx_file.close()
        os.sync()
        pass

    def distance_between(self, lat1, lon1, lat2, lon2):
        r = 6373.0
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)

        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (sin(dlat/2))**2 + cos(lat1) * cos(lat2) * (sin(dlon/2))**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = r * c
        return distance

    def is_filtered(self):
        ret = False
        if not GpsProcessor.is_gps_values_valid():
            print("GPS data isn't ready. Waiting correct date...")
            ret = False
            return ret

        d_max = 100.0   # spd<50km/h
        d_min = 5.0

        delta = self.distance_between(gpsd.fix.latitude,
                                      gpsd.fix.longitude,
                                      self.prev_lat,
                                      self.prev_lng)

        if (delta < d_min) or (delta > d_max):
            self.prev_lat = gpsd.fix.latitude
            self.prev_lng = gpsd.fix.longitude
            return True
        return ret


class IFTTT:    # If This Then That
    pass


class GpsPoller(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        global gpsd  # bring it in scope
        gpsd = gps(mode=WATCH_ENABLE)  # starting the stream of info
        self.current_value = None
        self.running = True  # setting the thread running to true

    def run(self):
        global gpsd
        while gpsp.running:
            gpsd.next()  # this will continue to loop and grab EACH set of gpsd info to clear the buffer


if __name__ == '__main__':
    gpsp = GpsPoller()  # create the thread
    gpsProcessor = GpsProcessor()
    fileTracker = FileTracker()
    ifttt = IFTTT()
    try:
        gpsp.start()  # start it up
        while True:
            gpsProcessor.show()
            fileTracker.gpx_file_update()
            # ifttt.check_home()

            time.sleep(1)  # set to whatever

    except (KeyboardInterrupt, SystemExit):  # when you press ctrl+c
        print("\nKilling Thread...")
        gpsp.running = False
        gpsp.join()  # wait for the thread to finish what it's doing
    print("Done.\nExiting.")
    sys.exit(1)
