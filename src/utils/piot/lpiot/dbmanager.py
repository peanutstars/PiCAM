
import threading ;
import time ;
from lpiot.ipcpacket import IPMeta ;
from lpiot.sensormodel import SensorMeta ;
from lpiot.sensordb import SensorDB, SensorLogDB ;
from libps.psDebug import DBG, ERR ;

class DBManager(threading.Thread) :
    def __init__(self, ippHandle) :
        threading.Thread.__init__(self) ;
        self.m_ipphandle = ippHandle ;
        self.m_sdb = SensorDB() ;
        self.m_ldb = SensorLogDB() ;
        self.m_ipphandle.register(IPMeta.SUBTYPE_SYSTEM, self.receivedSystemEvent) ;
        self.m_ipphandle.register(IPMeta.SUBTYPE_SENSOR, self.receivedSensorEvent) ;
        self.fgRun = True ;
        self.start() ;
    def receivedSystemEvent(self, ipId, ipSType, ipPayload) :
        DBG('[SYSTEM EVENT] %s %s %s' % (ipId, ipSType, ipPayload)) ;
        if ipId == '00000000' and ipSType == IPMeta.SUBTYPE_SYSTEM :
            if ipPayload == 'quit' :
                self.stop() ;
    def receivedSensorEvent(self, ipId, ipSType, ipPayload) :
        DBG('[SENSOR EVENT] %s %s %s' % (ipId, ipSType, ipPayload)) ;
    def run(self) :
        DBG('Start of DBManager') ;
        while self.fgRun :
            time.sleep(1) ;
        DBG('End of DBManager') ;
    def stop(self) :
        self.fgRun = False ;
