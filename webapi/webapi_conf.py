#MONGO=True # DEV only usage

BOTTLE_DEBUG = True
BOTTLE_AUTO_RELOAD = False
BOTTLE_SERVER = 'gevent'

SECRET = "I_L@VE_BEE!"
AP_SECRET = "T!?_asF"
DRIVER_MID_SUSPEND_LIST="/data/drivsuspmid.fl"
DRIVER_SUSPEND_LIST = "/data/drivsusp.fl"

SERVER_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
DateFormat_SaveOrder_Input = '%Y-%m-%d %H:%M'
LOG_DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

SocketTimeoutDic = {"default": 30}
QueueTimeoutDic =  { "default" : 3 }

lUseUTF8Encoder = True

lDebugTrace = True

APPNAME = "WEBS"

SHUTDOWN_TIMEOUT = 10
DATA_PREFIX = 'fares'

LOGGING = True
LOG_FILENAME = '/var/log/webapi/webapi_log.out'


