#!/usr/bin/env python3
import connexion
import datetime
import logging
import random

from connexion import NoContent

##

# our memory-only fare storage
FARES = {

}


def get_version():
    return "VERSION 0.1"

def get_all_fares():
    return [f for f in FARES.values() ]

def get_fares(limit, fare_type=None):
    return [f for f in FARES.values() if not fare_type or f['fare_type'] == fare_type][:limit]

def get_fare(fare_number):
    f = FARES.get(fare_number)
    return f or ('Not found', 404)

def create_fare(fare):
    logger.info('Received ...')
    
    f = {
        "status": "200 OK",
        "result": {
        "message": "success",
        "zone": 17,
        "job_number": "9825",
        "fare_type": "future"
        }
    }
    print ( f)
    return f, 200

def send_msg(driver_msg=None, vehicle_msg=None, fleet_msg=None):
    try:
        if driver_msg is not None:
            return send_driver_msg  (driver_msg = driver_msg)
        if vehicle_msg is not None:
            return send_vehicle_msg  (vehicle_msg = vehicle_msg)
        if fleet_msg is not None:
            return send_fleet_msg  (fleet_msg = fleet_msg)
    except Exception as e:
        print ( " Exception {}". format ( str(e)) )


def send_driver_msg(driver_msg=None):
    try:
        #print ( "*** Received {}". format ( driver_msg ) )
        driver_id = driver_msg['driver_id']
        cnt = 'Received driver_id=' + str( driver_id)
        if driver_id <= 0:
            return ( cnt , 400)          
        return cnt, 200
    except Exception as e:
        print (' Exception ....', e)
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
        print (' Exception ....', e)
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
        print (' Exception ....', e)
    return NoContent, 200

def post_fare(fare, fare_id=None):
    if fare_id:
        exists = fare_id in FARES
        fare['id'] = fare_id
        if exists:
            logging.info('Updating fare %s..', fare_id)
            FARES[fare_id].update(fare)
            return NoContent, (200)            
    else:
        fare_id = '201722' + str(random.randint(0,100))

    logging.info('Creating fare %s..', fare_id)
    fare['created'] = datetime.datetime.utcnow()
    FARES[fare_id] = fare
    return NoContent, (200 if exists else 201)


def cancel_fare(fare):
    fare_number = fare['fare_number']
    if fare_number in FARES:
        logging.info('Canceling fare %s..', fare_number)
        del FARES[fare_number]
        return NoContent, 204
    else:
        return NoContent, 404

def modify_fare(fare):
    fare_id = fare['fare_number']
    if fare_id in FARES:
        logging.info('Modifying fare %s..', fare_id)
        del FARES[fare_id]
        return NoContent, 204
    else:
        return NoContent, 404


def update_fare(fare):
    fare_id = fare['fare_number']
    if fare_id in FARES:
        logging.info('Deleting fare %s..', fare_id)
        del FARES[fare_id]
        return NoContent, 204
    else:
        return NoContent, 404

def setup_logging():
   
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)  
   

    handler = logging.FileHandler('/var/log/supervisor/cwebs_api.log')
    handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


import os
import json
import logging.config

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


#logging.basicConfig(level=logging.INFO)
logger = setup_logging()
app = connexion.App(__name__)
app.add_api('cwebs.yaml')
# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
application = app.app

if __name__ == '__main__':
   
    # run our standalone gevent server
    app.run(port=8080, server='gevent')
