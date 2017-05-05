from gevent import monkey
monkey.patch_all()

import gevent
import sys
import struct

import sysv_ipc
import datetime
import traceback
import random


import webapi_conf as Config
import msgconf as msgconf

from entrycontainer import EntryContainer

base_fmt = 'I I I I I B B B B'


mykey=msgconf.CWEBS
mq=None
sleep_time=1
num_iterations=100



def gmsg_getq(k):

    mq = None
    try:        
        mq = sysv_ipc.MessageQueue(k, flags=sysv_ipc.IPC_CREAT, mode=666, max_message_size = 8064)   
    except sysv_ipc.PermissionsError as ex:
        print ('gmsg_init Permission Exception ', str(ex) )

        try:
            mq = sysv_ipc.MessageQueue(k, flags=sysv_ipc.IPC_CREX, mode=666, max_message_size = 8064)

        except sysv_ipc.ExistentialError as e:
            print ('gmsg_init Exception ALREADY EXISTS ', str(e) )

            try:
                mq = sysv_ipc.MessageQueue(k)
            except Exception as e:
                print ('gmsg_init Exception ', str(e) )

    except Exception as e:
        print ('gmsg_init Exception ', str(e) )
  
    return mq

def gmsg_send(data, data_size, dstid, scndid, mtype, ss, srcid=msgconf.CWEBS, mykey=msgconf.CWEBS):
    """ 
        Build msg to be sent. 
    """

    msg = ( srcid,             #  msg.msg_struct.ms_srcuid
            dstid,             #  msg.msg_struct.ms_dstuid
            scndid,            #  msg.msg_struct.ms_scnduid
            mtype,             #  msg.msg_struct.ms_msgtype
            data_size,         #  msg.msg_struct.ms_datasize
            0,                 #  msg.msg_struct.ms_srcmch
            0,                 #  msg.msg_struct.ms_dstmch
            1,                 #  msg.msg_struct.ms_priority
            10,                #  msg.msg_struct.ms_reserved
            data)              #  msg.msg_struct.ms_msgdata

    #print ( 'packet size ', data_size  )
    packed_msg = ss.pack(*msg)    

    try:
        mq = gmsg_getq(mykey)
     
    except Exception as e:
        print (' gmsg_send Exception ', str(e))
        return

    try:
        if mq != None:
            mq.send(packed_msg, block=False, type=msgconf.ROUT_PRI)
    except Exception as e:
        print ( 'gmsg_send Exception', str(e) )
    
    #print ( 'packet size ', data_size  )    
    return

def gmsg_rcv(block=False, mykey=msgconf.CWEBS):
    packed_msg=None
    try:

        try:
            rmq = gmsg_getq(mykey)
        except sysv_ipc.ExistentialError:
            sys.stdout.write("%s: EXIST ** \n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
            return None
        except sysv_ipc.InternalError:
            sys.stdout.write("%s: *** INTERNAL Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
            return None

        except Exception as e:
            #sys.stdout.write("%s: ***** Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
            return None

        if rmq == None:
            return

        packed_msg, t = rmq.receive( block=block, type= msgconf.ROUT_PRI)

        if t == msgconf.ROUT_PRI:
            data_size = len(packed_msg) - 24
          
            #print ' packed_msg_type=%d, packed_msg_len=%d \n' %(t, len(packed_msg))    

            if len(packed_msg)  > 0 :
                msg_format = 'I I I I I c c c c %ds' % data_size
                ss = struct.Struct(msg_format)
                # Structure of the message:
                # 0      | 1      | 2       | 3       | 4        | 5      | 6      | 7        | 8        | 9
                # srcuid | dstuid | scnduid | msgtype | datasize | srcmch | dstmch | priority | reserved | msgdata
                msg = ss.unpack(packed_msg)

                #print (' Unpacked Message: ', msg)

                #bother only about data content ...
                if  msg[4] > 0 :
                    if msg[3] == msgconf.MT_OP_ERR :                       
                        m = ()
                        # packed = 79, datalen=51.
                        # data len 9msg[4] = packed_len -28
                        if msg[4] in [22, 32, 58, 51, 42, 238 ]:
                            m_format = 'I I I I I c c c c %ds c c c c c'  % (msg[4] -1)
                            s = struct.Struct(m_format)
                            try:
                                m = s.unpack(packed_msg) 
                               
                                return m                            
                                
                            except Exception as e:
                                sys.stdout.write("%s: MT_OP_ERR Exception 1 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
                                return msg
                                  
                        else:
                            m_format = 'I I I I I c c c c H h 64s 10s 134s H'
                            s = struct.Struct(m_format)

                            print (' s.size ==> %d [%s]' % ( s.size, m_format) )
                            try:
                                m = s.unpack(packed_msg)
                                return m

                            except Exception as e:
                                sys.stdout.write("%s: MT_OP_ERR Exception 2 %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
                                return msg

                    #immediate data size = 272
                    if msg[3] == msgconf.MT_ENTER_CALL :
                       
                        #this is 272
                        m_format = 'I I I I I c c c c 8I 2f 7H 2c 33s 33s 33s 33s 2c H H H 64s 10s 3H'
                        if msg[4] == 192:
                            m_format = 'I I I I I c c c c 8I 2f 7H 2c 33s 33s 33s 33s 2c H H H '
                        s = struct.Struct(m_format)

                        
                        try:
                            m = s.unpack(packed_msg)  
                            return m

                        except Exception as e:
                            sys.stdout.write("%s: MT_ENTER_CALL Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
                            return msg

                    #FUTURE
                    # data size = 84, packed len = 112)
                    if msg[3] in [ msgconf.MT_NEWFARE, msgconf.MT_UPD_FARE, msgconf.MT_MODFAREINFO] :
                        #struct its_farenumber
                        m_format = 'I I I I I c c c c I h H 64s 10s I'
                        s = struct.Struct(m_format)
                        #print  ' s.size ==>' , s.size
                        try:
                            m = s.unpack(packed_msg)                             
                            return m

                        except Exception as e:
                            sys.stdout.write("%s: MT_NEWFARE/MT_UPD_FARE/MT_MODFAREINFO  Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    

                    if msg[3] == msgconf.MT_GET_ZONE_BY_LAT_LONG:
                        m_format = 'I I I I I c c c c 8I 2f 7H 2c 33s 33s 33s 33s 2c H H H 64s 10s 3H'
                        s = struct.Struct(m_format) 
                        #print  ' s.size ==>' , s.size
                        try:
                            m = s.unpack(packed_msg)                            
                            return m

                        except Exception as e:
                            sys.stdout.write("%s: MT_GET_ZONE_BY_LAT_LONG Exception %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    

                    if msg[3] == 1 and msg[4] == 8 :                                           
                        m_format = ''.join( [ base_fmt,'I I' ])
                        s = struct.Struct(m_format) 
                        try:
                            m = s.unpack(packed_msg)  
                            #print ( m)                          
                            return m
                        except Exception as e:
                            sys.stdout.write("%s: cabmsg.gmsg_rcv Exception *** %s\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e)))    
               
   

                if msg[3] == msgconf.MT_OP_ERR and msg[4] == 0 :                    
                    print (' cabmsg.gmsg_rcv Received error ....' )
                    return msg

                return packed_msg

    except (sysv_ipc.PermissionsError, sysv_ipc.ExistentialError):
        sys.stdout.write("%s: Message could not be received. Check if os queue exist and its permission\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
        #time.sleep(self.settings.OS_MQ_SLEEP) 
        gevent.sleep(self.settings.OS_MQ_SLEEP)        

    except sysv_ipc.BusyError:
        #sys.stdout.write("%s:Nothing is the Q\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))        
        return None

    except sysv_ipc.InternalError:
        sys.stdout.write("%s: A severe error ocurred in os message queue. Aborting...\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT)))
              
                
    except Exception as e:
        sys.stdout.write("%s: An unexpected error occurred.\nDetails:\n%s [%s]\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), traceback.format_exc() , str(e) ))
 
    return packed_msg




def gmsg_purge(num=1):
    try:
        for i in range(num):
            gmsg_rcv()
    except Exception as e:
        pass


def gmsg_main(mymap):
    while True:
        try:      
            
            m = gmsg_rcv()         
            if m != None:
                print ( m )
                mykey = m[10]                                           
                i = m[9]              
                val=(i, mykey)
                sys.stdout.write("%s: mt=%d key=%d, i=%d\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT),  m[3], mykey, i ))                
               
                if mymap != None:
                    mymap[str(mykey)] = val

                
                #print ( "gmsg_main ***", mymap )
           

            gevent.sleep(1)
        
        except Exception as e:            
            sys.stdout.write("%s: gmsg_main Exception [%s]\n" % (datetime.datetime.strftime(datetime.datetime.now(), Config.LOG_DATETIME_FORMAT), str(e) ))


#[] {}  " "  ' '

if __name__ == "__main__":

    try:
        mq = gmsg_getq(mykey)
    except Exception as e:
        print ('main gmsg_getq() error ....', str(e))
        sys.exit()

    if mq != None:
        try:
            mymap = {}
            for i in range(3, num_iterations):
                mt = 1
                mykey = i                
                val = (mt, i)               
               
                mymap[str(mykey)] = val

                #print ('inserting ... ', mykey, val )

                format_message='I I'
                dest = msgconf.CWEBS            
                data=(i, mykey)
                s = struct.Struct(format_message);
          
                packed_data = s.pack(*data)   
                ss = struct.Struct('I I I I I B B B B' + '%ds' % (  s.size ) )  
                #(data, data_size, dstid, scndid, mtype, ss, srcid=msgconf.CWEBS, mykey=msgconf.CWEBS)
                gmsg_send(packed_data, s.size, dest, 0, mt, ss)

                gevent.sleep(sleep_time)

        except Exception as e:
            print ('main gmsg_send error ....', str(e))


   