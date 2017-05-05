from gevent import monkey; monkey.patch_all()
from bottle import Bottle, request, response, run
from gevent import Greenlet
from gevent import pywsgi
from gevent import queue
import gevent
import struct

import sys
import datetime
import threading
import json
import time

from gevent import select

import msg_q as msg_q
import webapi_conf as Config

from entrycontainer import EntryContainer
import date_utils

VERSION='1.0'
APPNAME='WEBAPI'

BASE_URL = ''

start = time.time()
tic = lambda: 'at %1.1f seconds' % (time.time() - start)


_suspend_file_name = None 
_suspend_file_format = None
_mid_dic  = None
_lock = threading.Lock()

class UrlRule(object):
    def __init__(self, url, func, methods='GET', base_url=BASE_URL):
        if base_url != '':
            self.url = '%s/%s' % (base_url, url)
        else:
            self.url = url
        self.url_short = url       
        self.func = func
        self.methods = methods


def set_default_headers(response):
    try: 
        response.headers["Content-type"] = "application/json"          
        response.headers["User-Agent"] = " ".join ([str(APPNAME) , str(VERSION) ] )
    except Exception as e:
        sys.stdout.write("%s: set_default_headers Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))            

def send_error(response, errCode=400):
    set_default_headers(response)
    response.status = errCode
    res = {'status': response.status, 'result': { 'message': 'Sorry. Not Found here.'}}
    return json.dumps(res)



def get_version():
    global mymap

    response.status = 200
    set_default_headers(response)
   
    data = (request, response)

    print ( data )

    print ( "get_version ***" , mymap )

    mykey =  EntryContainer.generate_seqno()  
    mymap[str(mykey)] = data

    v = mymap.get( mykey)

    print ( v )

    r = v  

    res = {'status':  response.status, 'result': {'version': VERSION}}
    return res

def save_book_order():
    global mymap
    try:
        response.status = 500
        set_default_headers(response)   
        res = {'status': response.status, 'result': {'message': 'INVALID'}}

        clen = request.content_length
        request.body.seek(0)

        info = request.body.read(clen)
        dic = json.loads(info.decode("utf-8") )

        sys.stdout.write("%s: %s request dictionary %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), __name__, 
                str(dic) ) )       
       
        print ( "save_book_order ***", mymap )

        try:
            fare = -1
            if "fare" in dic:
                fare = dic["fare"]         
                if len (str(fare)) >  6:
                    fare  = fare[-6:].lstrip('0')           


        except AttributeError:    
            return json.dumps(res)
        except Exception as e:          
            sys.stdout.write("%s: invalid fare number Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))            
            return json.dumps(res)

        try:
            q = gevent.queue.Queue()
            l = [ gevent.spawn(get_save_rsp, fare, 5, response, res, q, mymap) ]           
        
            gevent.wait(l)
              
            res = q. get()

            if res != None:
                sys.stdout.write("%s: return from spawn fare res=%s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), res))            
                if  res['status']  == 200 or  res['status']  == "200 OK" :
                    response.status = 200
                            
        except Exception as e:
            sys.stdout.write("%s: could not spawn fare Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))            
          
    except Exception as e:
        print ('Exception ', str(e))

    return json.dumps(res)   

def worker(body):    
    data = [ 'one', 'two', 'three', 'four' , ' \n']
    for d in data:
        body.put(d)
        # gevent.sleep(0.1)
    body.put(StopIteration)


def def1():
    body = gevent.queue.Queue()
    g = Greenlet.spawn(worker, body)
    return body


def get_save_rsp(f, to,  response, res, q, mymap):

    loc_data = gevent.local.local()
    loc_data.v = None
    loc_data.c = 0

    try:
        
       
        if f == None:
            return 

        try:
            loc_data.maxiters = 30
            for loc_data.i in range (loc_data.maxiters):
            #with gevent.Timeout(to):   
                try:                   
                    loc_data.v = mymap.get(f)                      
                    if loc_data.v != None:   
                        #print ('get_save_rsp **** ', v ) 
                        loc_data.j = loc_data.v [ 0]
                        response.status = 200                
                        res = {'status': response.status, 'result': {'message': 'success', 'job_number': str(loc_data.j)}}  

                        #mymap [ str(f )] = None
                                                      
                        q.put(res)

                        return

                    gevent.sleep(0.1)

                except Exception as e:
                    sys.stdout.write("%s: get_save_rsp *** Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))                                


        except Exception as e:
            res = {'status': response.status, 'result': {'message': 'no response from server', 'job_number': -1 }}   
            sys.stdout.write("%s: get_save_rsp *** Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))            

        res = {'status': 500 , 'result': {'message': 'error response from server', 'job_number': -1 }}    


          
    except Exception as e:
        res = {'status': 500, 'result': {'message': 'no response from server', 'job_number': -1 }}   
        sys.stdout.write("%s: get_save_rsp Exception %s \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))            

        

    q.put(res)



def get_driver_suspension_fileinfo():
    global _suspend_file_name
    global _suspend_file_format
    try:    
        file_name = Config.DRIVER_SUSPEND_LIST 
        frmt = 'i i I h 33s 33s c c h h 10s'       
        if _suspend_file_name == None:
            file_name = Config.DRIVER_SUSPEND_LIST 
            frmt = 'i i I h 33s 33s c c h h 10s'               
            with _lock:              
                res =  ( 1,17, 2)
                if res != None and len(res) > 2 and res[1] > 0 and res [0] > 0:           
                    file_name = Config.DRIVER_MID_SUSPEND_LIST 
                    frmt = 'i i I h 33s 33s c c h h 8s 17s 53s'      
                _suspend_file_name = file_name
                _suspend_file_format = frmt 
        else:
            return _suspend_file_name, _suspend_file_format 
    except Exception as e:
        sys.stdout.write("%s: get_driver_suspension_fileinfo Exception %s ...\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str (e)  ))
   
    #sys.stdout.write("%s: get_driver_suspension_fileinfo %s %s ...\n" % ( 
    #            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), file_name, frmt ))

    return  file_name, frmt


def driver_suspend_list():
    global _mid_dic 
    try: 
        '''
        import psutil
        proc = psutil.Process()
        print ( 'proc psutil open files ', proc.open_files() )

        l = list_fds()
        print ( 'using lsof ', l )
        '''

        l = get_open_fds()
        print ( 'get_open_fds using lsof ', l )

        response.status = 500            
        
        res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_drivers': 0, 'drivers': []}
        }

        set_default_headers(response)
        try:
           file_name, frmt = get_driver_suspension_fileinfo()
        except Exception as e:
            sys.stdout.write("%s: get_driver_suspend_list Exception %s\n" % (
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))
            file_name = Config.DRIVER_SUSPEND_LIST 
            frmt = 'i i I h 33s 33s c c h h 10s'


        s = struct.Struct(frmt)
        
        drivers = []
        number_of_drivers = 0
        try:
            counter = 0
            #print ('opening file ', file_name)
            
            with open(file_name, "rb") as fp: 
                gevent.sleep(10)   
                while True:           
                    counter = counter + 1
                    data = fp.read(s.size)
                    if data:
                        tmp = struct.unpack(frmt, data)
                        #print ('record ', counter, tmp )
                        # record ( driver_id, duration, timestamp, authority_d, )
                        if tmp[0] > 0 :
                            susp_time = susp_time_m = susp_time_h = 0
                            msgs=[]
                            if tmp[1] >= 0:
                                try:
                                    susp_time_h = tmp[1] % 1000
                                    susp_time = susp_time_h
                                    susp_time_m = int(tmp[1] / 1000)

                                    t_start=t_end=''

                                    company_id=0
                                    if len (tmp) > 11:
                                        market_id = tmp[11]
                                        market_id = market_id.strip(' ') 
                                        market_id = market_id.strip('\x00') 
                                        if market_id in _mid_dic:
                                            company_id = _mid_dic[market_id]

                                    for i in range(2):
                                        m =  tmp[4 + i]
                                        if len(m) > 0:
                                            i = m.find('\x00') 
                                            if i > 0:
                                                m = m[:i]
                                        m=m.strip('\x00')                                                
                                        msgs.append(m)

                                    try:
                                        t_end = ''
                                        if  tmp[2] != 0 and tmp[1] > 0:                                 
                                            t_end = date_utils.convert_2_datetimestring(timestamp=tmp[2], hours=susp_time_h, minutes=susp_time_m)
                                    except Exception as e:   
                                        print ('exception ', str(e) )
                                        t_end = ''                                                              
                             
                                    try:
                                        t_start = ''
                                        if  tmp[2] != 0:                                           
                                            t_start = date_utils.timestamp_2_datetimestring (tmp[2] )                                
                                    except Exception as e:   
                                        print( 'exception ', e )
                                        t_start = ''

                                except Exception as e:
                                    pass

                                number_of_drivers = number_of_drivers + 1
                                drivers.append ({
                                    "driver_id": tmp[0], 
                                    "authority_id" : tmp[3],
                                    "suspension_time": susp_time,
                                    "suspension_time_min": susp_time_m,
                                    #"suspension_time_h": susp_time_h,
                                    "suspension_timestamp": tmp[2],
                                    "suspension_datetime_end" : t_end,
                                    "suspension_datetime_start" : t_start,
                                    "company_id" : company_id,
                                    "suspension_reasons" :  msgs,      
                                    })
                
                    else:
                        break                
                         
               
            response.status = 200
            res = {'status': response.status,
                   'result': {'message': 'OK',  'number_of_drivers': number_of_drivers, 'drivers': drivers}
            }
            #print json.dumps(res)
            return json.dumps(res)
        except Exception as e:
            sys.stdout.write("%s: driver_suspend_list... Exception %s\n" % ( 
                datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e)))            
   
            response.status
            return json.dumps(res)
    except Exception as e:
        sys.stdout.write("%s: driver_suspend_list... Exception %s\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e)))

    set_default_headers(response)
    response.status = 500
    res = {'status': response.status,
               'result': {'message': 'failure', 'number_of_drivers': 0, 'drivers': []}}
    return json.dumps(res)


def get_open_fds():
    '''
    return the number of open file descriptors for current process

    .. warning: will only work on UNIX-like os-es.
    '''
    import subprocess
    import os

    try:
        nprocs = [ ] 
        pid = os.getpid()
        procs = subprocess.check_output( 
            [ "lsof", '-w', '-Ff', "-p", str( pid ) ] )

        nprocs = len( 
            filter( 
                lambda s: s and s[ 0 ] == 'f' and s[1: ].isdigit(),
                procs.split( '\n' ) )
            )
        return nprocs

    except Exception as e:
        sys.stdout.write("%s: get_open_fds ... Exception %s\n" % ( 
            datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , str(e)))        

    return nprocs

def list_fds():

    import os
    import sys
    import errno

    """List process currently open FDs and their target 
    if sys.platform != 'linux2':
        raise NotImplementedError('Unsupported platform: %s' % sys.platform)

    """
    ret = {}
    base = '/proc/self/fd'
    for num in os.listdir(base):
        path = None
        try:
            path = os.readlink(os.path.join(base, num))
        except OSError as err:
            # Last FD is always the "listdir" one (which may be closed)
            if err.errno != errno.ENOENT:
                raise
        ret[int(num)] = path

    return ret





def gr1():
    # Busy waits for a second, but we don't want to stick around...
    print('gr1 Started Polling: %s' % tic())
    select.select([], [], [], 2)
    print('gr1 Ended Polling: %s' % tic())

def gr2():
    # Busy waits for a second, but we don't want to stick around...
    print('gr2 Started Polling: %s' % tic())
    select.select([], [], [], 4)
    print('gr2 Ended Polling: %s' % tic())

def gr3():
    print("gr3 Hey lets do some stuff while the greenlets poll, %s" % tic())
    gevent.sleep(1)

def test_gevent():    

    gevent.joinall([
        gevent.spawn(gr1),
        gevent.spawn(gr2),
        gevent.spawn(gr3),
    ])


all_rules = []
# UrlRule (url, func, methods=None, base_url=BASE_URL)
all_rules.extend([
    UrlRule('/', def1, methods='GET'),
    UrlRule('/version/', get_version, methods='GET'),    
    UrlRule('/save_book_order/', save_book_order, methods='POST'),  

    UrlRule('/driver_suspend_list/',driver_suspend_list, methods='GET'),  

    UrlRule('/test_gevent/', test_gevent, methods='GET'),  
  ])

def setup_routing(app):  
    try:
        for i in all_rules:
            app.route( i.url, i.methods, i.func)  
    except Exception as e:
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )        

def create_services():
    try:
        default_rsp = None

        if hasattr(Config, 'LOGGING') and Config.LOGGING:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            logger.addHandler(ch)

        app = Bottle()

        setup_routing(app)

        app.error_handler[404] = send_error     

        return app
    except Exception as e:
        #logger.exception('Main')
        sys.stdout.write("%s: Exception %s\n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )

    return default_rsp

try:
    app= create_services()  

    mylist = [app]
    if  any (v is None for v in mylist):
        #logger.critical('%s ERROR ... EXITING ... check the server ...\n' % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )    
        sys.stdout.write('%s ERROR ... EXITING ... check the server ...\n' % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) ) )    
    else: 
        m = ' STARTING ...\n' 
        #logger.debug('%s %s'  % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , m))
        sys.stdout.write('%s %s'  % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT) , m))
except Exception as e:
    #logger.exception("%s: Exception %s. Please check server ... \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )    
    sys.stdout.write("%s: Exception %s. Please check server ... \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )


if __name__ == "__main__":
    try:

        mymap = {}

        thr = gevent.spawn(msg_q.gmsg_main, mymap)

        app.run(host="0.0.0.0", port=8000, debug=True,reloader=True, server="gevent")

        gevent.sleep(0)  
        gevent.joinall(thr)

    except Exception as e:
        sys.stdout.write("%s: main Exception %s \n" % ( datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), (str(e) ) ) )


