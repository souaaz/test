#!/usr/bin/env python3
import connexion
import datetime
import logging
import random

import os
import json
import logging.config

from connexion import NoContent

import sqlite3
import uuid

DB_FILENAME = "cwebs_data_store.sqlite"
LOG_FILE_NAME = '/var/log/supervisor/cwebs_api.log'
PORT = 8080

##

# our memory-only fare storage
FARES = {
}


success_response = {
            "status": "200 OK",
            "result": {
                "message": "success"
        }
    }

error_response = {
            "status": "500 Internal Server Error",
            "result": {
                "message": "error"
            }
    }



def get_version():
    f = {
            "status": "200 OK",
            "result": {
                "version": "1.0.12DEV"
            }
        }
    return f,  200

def get_all_fares():
    return [f for f in FARES.values() ]

def get_fares(limit, fare_type=None):
    return [f for f in FARES.values() if not fare_type or f['fare_type'] == fare_type][:limit]

def get_fare(fare):    
    try:
        fare_number = fare['fare_number']
        fare_type = fare ['fare_type'] if 'fare_type' in fare else 'immediate'

        res, _ = find_in_db( db_cur, fare_number, table_name='FARES')

        logger.info ( "get_fare found this {} ".format (res))

        if res:
            logger.info('getting fare %s..', fare_number)        
            f = {
              "status": "200 OK",
                "result": {
                    "message": "success",
                    "job_number": fare_number,
                    "fare_type": fare_type
                }
            }
            return f, 200
        else:
            return error_response, 500
    except Exception as e:
        error_response ["result"] ["message"] = str(e)
        return error_response, 500

    return error_response, 500

def create_fare(fare):
    global db_cur

    try:
        logger.info('Received ...', fare)
    
        if insert_db(db_cur, fare["fare_id"],  fare["address"], table_name='FARES'):
            f = {
                "status": "200 OK",
                "result": {
                "message": "success",
                "zone": 17,
                "job_number": fare["fare_id"],
                "fare_type": "immediate"
                }
            }
        else:
            f = {
                "status": "500 Internal Server Error",
                "result": {
                "message": "Could not create a job",
                "zone": -1,
                "job_number": -1           
                }
            }        

        logger.info ( f)
        return f, 200
 
    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500        


def post_fare(fare, fare_id=None):

    ks = ["pick_up_street_number", "pick_up_street_name", 'pick_up_city', "pick_up_zip_code", "pickup"]

    try:
        address = ' '.join( fare[k] for k in ks if k in fare )
        fare ['address']= address
    except Exception as e:
        logger.error (' Exception ....', e)

    logger.info (  " ADDRESS .... " , address )

    try:
        if fare_id:
            exists = fare_id in FARES
            fare['id'] = fare_id
            if exists:
                logger.info('Updating fare %s..', fare_id)
                FARES[fare_id].update(fare)
                return NoContent, (200)            
        else:
            fare_id = str(uuid.uuid4().hex) #'201722' + str(random.randint(0,100))

        logger.info('Creating fare %s..', fare_id)
        fare['created'] = datetime.datetime.utcnow()
        fare['fare_id'] = fare_id
    
        return create_fare (fare)

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500
 

def cancel_fare(fare):
    try:
        fare_number = fare['fare_number']
        fare_type = fare ['fare_type']

        res, _ = find_in_db( db_cur, fare_number, table_name='FARES')

        logger.info ( "cancel_fare found this {} ".format (res))

        if res:
            logger.info('Canceling fare %s..', fare_number)        
            f = {
              "status": "200 OK",
                "result": {
                    "message": "success",
                    "job_number": fare_number,
                    "fare_type": fare_type
                }
            }
            return f, 200
        else:
            return error_response, 500
    except Exception as e:
        error_response ["result"] ["message"] = str(e)
        return error_response, 500

    return error_response, 500

def modify_fare(fare):
    try:

        ks = ["pick_up_street_number", "pick_up_street_name", 'pick_up_city', "pick_up_zip_code", "pickup"]

        try:
            address = ' '.join( fare[k] for k in ks if k in fare )
            fare ['address']= address
        except Exception as e:
            logger.error ('***modify_fare*** Exception ...', str(e) )

        fare_number = fare['fare_number']
        fare_type = fare ['fare_type'] if 'fare_type' in fare else 'immediate'

        res, _= find_in_db( db_cur, fare_number, table_name='FARES')

        logger.info ( "modify_fare found this {} ".format (res))
        if res:
            logger.info('Modifying fare %s..', fare_number)        
            res = update_db(db_cur, fare_number, address,  table_name='FARES')
            if res:
                f = {
                    "status": "200 OK",
                    "result": {
                        "message": "success",
                        "job_number": fare_number,
                        "fare_type": fare_type
                    }
                }
                return f, 200
            else:
                error_response ["result"] ["message"] = "Could not modify the fare"
        else:                    
            error_response ["result"] ["message"] = "Could not find the fare"
        
        return error_response, 500

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def update_fare(fare):
    try:
        fare_number = fare['fare_number']      

        res, _= find_in_db( db_cur, fare_number, table_name='FARES')

        logger.info ( "update_fare found this {} ".format (res))

        if res:
            logger.info('Updating fare %s..', fare_number)        
            address = fare['action']   
            res = update_db(db_cur, fare_number, address,  table_name='FARES')
            if res:              
                return success_response, 200
            else:
                error_response ["result"] ["message"] = "Could not update the fare"
        else:                    
            error_response ["result"] ["message"] = "Could not find the fare"
        
        return error_response, 500

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def send_msg(driver_msg=None, vehicle_msg=None, fleet_msg=None):
    try:
        if driver_msg is not None:
            return send_driver_msg  (driver_msg = driver_msg)
        if vehicle_msg is not None:
            return send_vehicle_msg  (vehicle_msg = vehicle_msg)
        if fleet_msg is not None:
            return send_fleet_msg  (fleet_msg = fleet_msg)
    except Exception as e:
        logger.error  ( " Exception {}". format ( str(e)) )


def send_driver_msg(driver_msg=None):
    try:
        #print ( "*** Received {}". format ( driver_msg ) )
        driver_id = driver_msg['driver_id']
        cnt = 'Received driver_id=' + str( driver_id)
        if driver_id <= 0:
            return ( cnt , 400)          
        return cnt, 200
    except Exception as e:
        logger.error (' Exception ....', e)
    return NoContent, 200


def send_vehicle_msg(vehicle_msg=None):
    try:
        #print ( "*** Received {}". format ( driver_msg ) )   
        my_id = vehicle_msg['taxi']
        cnt = 'Received taxi =' + str( my_id)
        if my_id <= 0:
            return ( cnt , 400)       
        return cnt, 200
    except Exception as e:
        logger.error  (' Exception ....', e)
    return NoContent, 200

def send_fleet_msg(fleet_msg=None):
    try:
        #print ( "*** Received {}". format ( driver_msg ) )   
        my_id = fleet_msg['fleet']
        cnt = 'Received fleet =' + str( my_id)
        if my_id <= 0:
            return ( cnt , 400)       
        return cnt, 200
    except Exception as e:
        logger.error  (' Exception ....', e)
    return NoContent, 200

def vehicle_action(action_params):
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500

def driver_action(action_params):
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500    

def fleet_action(action_params):
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500    

def supervisor_action(action_params):
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500    

def vehicle_suspend_list():
    try:

        f = {
              "status": "200 OK",
            "result": {
            "number_of_drivers": 2,
            "message": "OK",
            "drivers": [
                {
                "suspension_datetime_end": "",
                "driver_id": 8080,
                "suspension_reasons": [
                "test message for dispatch test me",
                "test message for driver test mess"
                    ],
                "company_id": 1,
                "suspension_timestamp": 1487196000,
                "suspension_time_min": 0,
                "authority_id": 667,
                "suspension_time": 0,
                "suspension_datetime_start": "2017-02-15 17:00"
                },
                {
                "suspension_datetime_end": "",
                "driver_id": 1111,
                "suspension_reasons": [
                "test message for dispatch test me",
                "test message for driver test mess"
                    ],
                "company_id": 1,
                "suspension_timestamp": 1489518712,
                "suspension_time_min": 0,
                "authority_id": 667,
                "suspension_time": 0,
                "suspension_datetime_start": "2017-03-14 15:11"
                }
                ]
            }   
        }

        return f, 200

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def driver_suspend_list():
    try:
        f = {
              "status": "200 OK",
                "result": {
                    "message": "success",
                    "vehicles": [],
                    "number_of_vehicles": 0
                }
            }

        return f, 200

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def get_corporate_account(account_number, customer_number): 
    try:
        f = {
            "status": "200 OK",            
            "result": 
            {
                "number_of_accounts": 1, 
                "account_number": account_number,
                "customer_number": customer_number,
                "message": "OK",                    
                "prompts": [   
                    {
                        "caption": "DOB",
                        "length": 10,
                        "prompt_number": 1,
                        "type": "string",
                        "to_be_validated": True
                    },
                    {
                        "caption": "VIP",
                        "length": 7,
                        "prompt_number": 2,
                        "type": "string",
                        "to_be_validated": True
                    }
                ]              
            }          
        }   
        return f, 200    
  
    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def get_all_accounts():
    try:

        f = {
            "status": "200 OK",            
            "result": 
            {
                "number_of_accounts": 1, 
                "message": "OK",     
                "accounts" :  [
                    {                
                        "account_number": "TEST",
                        "customer_number": "1",
                        "prompts": [   
                            {
                                "caption": "DOB",
                                "length": 10,
                                "prompt_number": 1,
                                "type": "string",
                                "to_be_validated": True
                            },
                        ],
                    },
                ]
            }
        }    
        return f , 200    
  
    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def send_device_msg(vehicle):
    try:
        msgtext = vehicle ["msgtext"]
        vehicle_id = vehicle ["vehicle_id"]

        return success_response, 200    
  
    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500

def clear_emergency():
    try:

        return success_response, 200    

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
      

    return error_response, 500


def redispatch_fare(fare):
    try:
        fare_number = fare['fare_number']
        fare_type = fare ['fare_type']

        res, recs = find_in_db( db_cur, fare_number, table_name='FARES')

        if res:
            logger.info('Redispatching fare %s..', fare_number)  
            fare["fare_id"] =  str(uuid.uuid4().hex)
            
            logger.info ( "recs recs= {rec}". format ( rec=recs ) )
            
            #
            fare["address"] = recs [1]
            if insert_db(db_cur, fare["fare_id"],  fare["address"], table_name='FARES'):
                f = {
                    "status": "200 OK",
                    "result": {
                    "message": "success",
                    "zone": 17,
                    "job_number": fare["fare_id"],
                    "fare_type": fare_type 
                    }
                }
            else:
                f = {
                    "status": "500 Internal Server Error",
                    "result": {
                    "message": "Could not redispatch the job",
                    "zone": -1,
                    "job_number": -1           
                    }   
                }                   
            return f, 200
        else:
            error_response ["result"] ["message"] = "Invalid fare number"
            return error_response, 500
    except Exception as e:
        error_response ["result"] ["message"] = str(e)
        return error_response, 500
    
    return error_response, 500

def validate_account(account):
    try:
        account_number = account ["account_number"]
        customer_number = account ["customer_number"]    
        f = {
            "status": "200 OK",
            "result": {
                "number_of_accounts": 1,
                "valid_response": [ False ],
                "customer_number": customer_number,
                "valid": False,
                "account_number":  account_number ,
                "message": "OK"
            }
        }
        return f , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500

def get_qtotals():
    try:
        f = {
            "1": [ 0, 0, 0, 0 ],
            "2": [ 0, 3, 0, 0],
            "22": [ 0, 0, 0, 0 ]
        }
        return f, 200    
    
    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def update_fare_amount(fare):
    try:

        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def get_zonesetzones():
    try:
        f = {
            "0": [
                101, 102, 103, 104, 105, 106, 107, 108, 109, 110,
                111, 112, 113, 114, 115, 116, 117, 118, 119, 120,
                121, 122, 123, 124, 125, 126, 127, 128, 129, 201,
                211, 221, 231, 241, 251, 261, 271, 281, 291, 301,
                311, 321, 331, 341, 351, 361, 371, 381, 601, 602,
                605, 895
            ],
            "1": [ 7, 13, 17, 117, 852, 920, 955 ]
        }
        return f, 200  

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        

    return error_response, 500


def callout_response():
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500


def update_destination():
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500  

def get_zonevehicles():
    try:
        f = {
            "0": [],
            "1": [],
            "2": [],
            "3": [],
            "4": []
        }
 
        return f, 200  

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        

    return error_response, 500


def zone_by_gps(position):
    try:
        f = {
            "status": "200 OK",
            "result": {
                "message": "success",
                "zone": 17,
                "lead_time": 10
            }
        }

        return f, 200
    except Exception as e:
        error_response ["result"] ["message"] = str(e) 

    return error_response , 500

def get_zonestatus(fleet_number):
    try:
        f = {
            "101": [ 0, 0  ],
            "102": [ 0, 0  ],
            "103": [ 0, 0  ],
            "104": [ 0, 0  ],
            "105": [ 0, 0  ],  
            "106": [ 0, 0  ], 
            "107": [ 0, 0  ], 
            "108": [ 0, 0  ],
            "109": [ 0, 0  ],
            "110": [ 0, 0  ],
            "111": [ 0, 0  ],
            "112": [ 0, 0  ],
            "113": [ 0, 0  ],
            "114": [ 0, 0  ],
            "115": [ 0, 0  ],
            "116": [ 0, 0  ],
            "117": [ 0, 0  ],
            "118": [ 0, 0  ],
            "119": [ 0, 0  ],
            "120": [ 0, 0  ],
            "121": [ 0, 0  ],
            "122": [ 0, 0  ],  
            "123": [ 0, 0  ],
            "124": [ 0, 0  ],
            "125": [ 0, 0  ],
            "126": [ 0, 0  ],
            "127": [ 0, 0  ],
            "128": [ 0, 0  ],
            "129": [ 0, 0  ],
            "201": [ 0, 0  ],
            "211": [ 0, 0  ],
            "221": [ 0, 0  ],
            "231": [ 0, 0  ],
            "241": [ 0, 0  ],
            "251": [ 0, 0  ],
            "261": [ 0, 0  ],
            "271": [ 0, 0  ],
            "281": [ 0, 0  ],
            "291": [ 0, 0  ],
            "301": [ 0, 0  ],
            "311": [ 0, 0  ],
            "321": [ 0, 0  ],
            "331": [ 0, 0  ],
            "341": [ 0, 0  ],
            "351": [ 0, 0  ],
            "361": [ 0, 0  ],
            "371": [ 0, 0  ],
            "381": [ 0, 0  ],
            "601": [ 0, 0  ],
            "602": [ 0, 0  ],
            "605": [ 0, 0  ],
            "895": [ 0, 0  ],
        }

        return f, 200  

    except Exception as e:
        error_response ["result"] ["message"] = str(e)
        return error_response, 500
    
    return error_response, 500




def mdt_check(fare):
    try:
        customer_number = fare["customer_number"]
        account_number  = fare["account_number"]
        f = {
            "status": "200 OK",
            "result": 
            {
                "message": "OK",
                "number_of_accounts": 1,
                "voucher": 0, 
                "active": 1, 
                "customer_number" : customer_number,
                "account_number"  : account_number  ,
                "account_name" : "SAMIRA",             
            }
        }

        return f , 200  
 
    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500    

def update_payment_type():
    try:
        return success_response , 200       

    except Exception as e:
        error_response ["result"] ["message"] = str(e)        
        return error_response, 500

    return error_response, 500  

def setup_logging():
   
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  
   

    handler = logging.FileHandler( LOG_FILE_NAME)
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger

def setup_logging_cfg(
    default_path='logging.json',
    default_level=logging.INFO,
    env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)

    logger = logging.getLogger()
    return logger


###############################
#
# To be moved elsewhere
#
################################

#logging.basicConfig(level=logging.INFO)


def init_db():
    try:
        conn = sqlite3.connect( DB_FILENAME )
        c = conn.cursor()
        return conn, c
    except Exception as e:
        logger.error ('init_db **** ERROR ...%s \n', str(e) )

def cleanup_db(db_cur, tables=[]):
    for t in tables:
        try:
            db_cur.execute ( 'DROP TABLE  {0}  IF EXIST  '.format ( t ) )
        except Exception as e:
            logger.error ('ERROR ...%s \n', str(e) )

def setup_db(db_cur):
    try:
        table_name = 'FARES'
        db_cur.execute ( 'CREATE TABLE {0} IF NOT EXISTS  (FareNumber TEXT PRIMARYKEY, Address  TEXT) '. format (table_name) )

    except Exception as e:
        logger.error ('setup_db *** ERROR ...%s \n', str(e) )

def insert_db(db_cur, farenum, address,  table_name='FARES'):
    try:
        res=True
        logger.info(  "INSERT INTO  {0} (FareNumber, Address) VALUES ( '{1}',  '{2}') ".format ( table_name, farenum, address))
        db_cur.execute ( "INSERT INTO  {0} (FareNumber, Address) VALUES ( '{1}',  '{2}') ".format ( table_name, farenum, address) )
        db_conn.commit()

    except Exception as e:
        logger.error  ('ERROR ...%s \n', str(e) )
        res=False

    return res

def update_db(db_cur, farenum, address,  table_name='FARES'):
    try:
        res=True
        logger.info( "UPDATE  {0} (Address) VALUES ( '{1}') WHERE FareNumber = '{2}' ".format ( table_name, address, farenum) )
        db_cur.execute ( "UPDATE {table} SET Address='{address}' WHERE FareNumber = '{farenum}' ".format ( table=table_name, address=address, farenum=farenum) )
        db_conn.commit()

    except Exception as e:
        logger.error  ('***update_db*** ERROR ...%s \n', str(e) )
        res=False

    return res

def find_in_db(db_cur, farenum,  table_name='FARES', limit=1):
    try:
        res = False
        l = []
        logger.info("SELECT * FROM  {0} WHERE FareNumber = '{1}' ".format ( table_name, farenum))
        l = db_cur.execute ("SELECT * FROM {0} WHERE FareNumber='{1}'".format ( table_name, farenum, limit) )

        if l:           
            my_row = db_cur.fetchone()
            if my_row is not None:
                logger.info ( " found {r} ".format ( r=my_row )) 
                res = True
            '''    
            for i in l:
                logger.info ( " *** found *** {0}".format ( i ) )
                res = True  
            '''  
           

    except Exception as e:
        logger.error  ('ERROR ...%s \n', str(e) )
        res=False

    return (res, my_row )

###############################



logger = setup_logging()

app = connexion.App(__name__)
app.add_api('cwebs.yaml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
db_conn, db_cur = init_db()

#  Remove DB 
# cleanup_db(db_cur, tables=['FARES'])

# Do not create tables ...
#setup_db(db_cur)

application = app.app

if __name__ == '__main__': 
    try:  
        # run our standalone gevent server
        app.run(port=PORT,  server='gevent')
    except Exception as e:
        logger.error('__main__ **** ERROR ...%s \n', str(e) )        
