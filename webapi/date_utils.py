# coding=utf-8
from datetime import datetime, timedelta
import time
import os,sys

if __name__ == "__main__":      
    app_dir = os.path.dirname(__file__) + "./"
    sys.path.append (app_dir )


import webapi_conf as Config


SECONDS_PER_MINUTE = 60
SECONDS_PER_HOUR = 60 * SECONDS_PER_MINUTE
SECONDS_PER_DAY = 24*SECONDS_PER_HOUR
MINUTES_PER_DAY = 24*60
HOURS_PER_DAY = 24


def timestamp_2_datetime(ts):
    return datetime.fromtimestamp(ts)

def datetime_2_timestamp(dt):
    return time.mktime(dt.timetuple())

def timestamp_2_datetimestring(ts, fmt=None):
    try:
        dt = ''
        if fmt == None:
            fmt = Config.DateFormat_SaveOrder_Input

        dt = datetime.strftime( timestamp_2_datetime (ts), fmt)

    except Exception as e:
        sys.stdout.write("%s: timestamp_2_datetimestring Exception %s \n" % (datetime.strftime(datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))

    return dt


def datetimestring_2_timestamp(dts, fmt=None):
    try:
        dt=0

        if len(dts) > 0:
            dt = datetimestring_2_tuple(dts, fmt=fmt)

        if dt:
            return datetime_2_timestamp(dt)

    except Exception as e:
        sys.stdout.write("%s: datetimestring_2_timestamp Exception %s \n" % (datetime.strftime(datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))

    return dt



def datetimestring_2_tuple(dts, fmt=None):
    try:
        if fmt == None:
            fmt = Config.DateFormat_SaveOrder_Input

        dt = datetime.strptime( dts, fmt)

    except Exception as e:
        sys.stdout.write("%s: datetimestring_2_tuple Exception %s \n" % (datetime.strftime(datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))

    return dt

def convert_2_datetimestring(timestamp=0, hours=0, minutes=0, date_fmt= Config.DateFormat_SaveOrder_Input):
    try:
        t_end =''
        time_end =  timestamp_2_datetime (timestamp) + timedelta(hours=hours, minutes=minutes)
        t_end = datetime.strftime( time_end, date_fmt) 

    except Exception as e:
        sys.stdout.write("%s: get_datetime_string Exception %s \n" % (datetime.strftime(datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))

    return t_end

if __name__ == "__main__":    
    tm =  1486494296
    fmt = '%Y-%m-%d %H:%M:%S'
  
    print ('ts = ' , tm)

    x = timestamp_2_datetimestring(tm, fmt=fmt)
    print ( 'x =', x)

    y = datetimestring_2_tuple(x, fmt=fmt)
    print  ( 'y=', y )
   
    w = datetimestring_2_timestamp(x, fmt=fmt)
    print  ( 'w=', w )

    x = "2017-02-08 12:00:00"
    w = datetimestring_2_timestamp(x, fmt=fmt)
    print  ( 'w=', w )
