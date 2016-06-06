
import json ;
import datetime ;
from libps.psDebug import CliColor, DBG, ERR ;

class SensorMeta :
                                            # KEY
    SEN_TYPE_ZB_ATTRIBUTE   = 'ZbAttr' ;    # endpointId.clusterId.attributeId
    SEN_TYPE_ZB_CLUSTER     = 'ZbClus' ;    # endpointId.clusterId
    SEN_TYPE_ZB_NODE        = 'ZbNode' ;    # nodeId
    SEN_TYPE_ZW_ATTRIBUTE   = 'ZwAttr' ;    # classId.typeId
    SEN_TYPE_ZW_CLASS       = 'ZwClas' ;    # classId
    SEN_TYPE_ZW_NODE        = 'ZwNode' ;    # None

    VAL_TYPE_MMA_RAW_HOUR   = 'mMR' ;       # 0,0,1,1,1,0,0,0,0,0,...,0 - 60EA Temperature, Humidity, Battery ...
    VAL_TYPE_MMA_HOUR       = 'mMH' ;       # minValue,maxValue,averageValue - Temperature, Humidity, Battery ...
    VAL_TYPE_MMA_DAY        = 'mMD' ;       # minValue,maxValue,averageValue - Temperature, Humidity, Battery ...
    VAL_TYPE_MMA_MONTH      = 'mMM' ;       # minValue,maxValue,averageValue - Temperature, Humidity, Battery ...
    VAL_TYPE_EVENT_MINUTE   = 'ETm' ;       # 0,0,1,1,1,0,0,0,0,0,...,0 - 60EA OpenClose, PIR ...
    VAL_TYPE_EVENT_HOUR     = 'ETH' ;       # 0,0,1,1,1,0,0,0,0,0,...,0 - 60EA OpenClose, PIR ...
    VAL_TYPE_EVENT_DAY      = 'ETD' ;       # 0,0,1,1,1,0,0,0,0,0,...,0 - 24EA OpenClose, PIR ...
    VAL_TYPE_EVENT_MONTH    = 'ETM' ;       # 0,0,1,1,1,0,0,0,0,0,...,0 - 31EA OpenClose, PIR ...


class SensorEvent :
    def __init__(self, stype=None, uid=None, fuid=None, value=None, extra=None) :
        self.m_datetime = datetime.datetime.now() ;
        self.m_type = stype ;
        self.m_uid = uid ;
        self.m_fuid = fuid ;
        self.m_value = value ;
        self.m_extra = extra ;
    def setTimeStamp(self, datetime) :
        self.m_datetime = datetime ;
    def setType(self, stype) :
        self.m_type = stype ;
    def setUID(self, uid) :
        self.m_uid = uid ;
    def setKey(self, fuid) :
        self.m_fuid = fuid ;
    def setValue(self, value) :
        self.m_value = value ;
    def setExtra(self, extra) :
        self.m_extra = extra ;
    def toString(self) :
        toStr  = self.m_datetime.strftime('%Y.%m.%d.%H.%M.%S') ;
        toStr += '|%s|%s|%s|%s|%s' % (self.m_type, self.m_uid, self.m_fuid, str(self.m_value),
            json.dumps(self.m_extra, default=lambda o: o.__dict__) if self.m_extra else None) ;
        return toStr ;

class SensorDevice :
    def __init__(self, uid) :
        self.uid = uid ;
    def setName(self, name) :
        self.name = name ;
    def setManufacturer(self, manu) :
        self.manufacturer = manu ;
    def setModel(self, model) :
        self.model = model ;
    def setAppVersion(self, version) :
        self.appversion = version ;
    def setSwBuild(self, swbuild) :
        self.swbuild = swbuild ;
    def setBattery(self, battery) :
        self.battery = battery ;
    def setTemperature(self, temp) :
        self.temperature = temp ;
    def setHumidity(self, hum) :
        self.humidity = hum ;
    def setAccelActive(self, active) :
        if not hasattr(self, 'acceleration') :
            self.acceleration = {} ;
        self.acceleration['active'] = active ;
    def setAccelX(self, x) :
        if not hasattr(self, 'acceleration') :
            self.acceleration = {} ;
        self.acceleration['x'] = x ;
    def setAccelY(self, y) :
        if not hasattr(self, 'acceleration') :
            self.acceleration = {} ;
        self.acceleration['y'] = y ;
    def setAccelZ(self, z) :
        if not hasattr(self, 'acceleration') :
            self.acceleration = {} ;
        self.acceleration['z'] = z ;
    def setZoneStatus(self, zone) :
        self.zonestatus = zone ;
