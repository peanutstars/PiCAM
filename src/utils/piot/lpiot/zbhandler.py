
import imp ;
import os ;
import re ;
import struct ;
import threading ;
import time ;
from error import * ;
from ipcpacket import IPMeta ;
from sensormodel import SensorMeta, SensorEvent, SensorDevice ;
from zbenum import ZCLCluster, ZCLAttribute, ZCLAttributeType ;
from zbmodel import ZbJoinState, ZbNode, ZbEndpoint, ZbCluster, ZbAttribute ;
from libps.psJson import PSJson ;
from libps.psDebug import CliColor, DBG, ERR ;

class ZbParse :
    @staticmethod
    def getSizeOfAttributeType(attrType, plarr) :
        if attrType > ZCLAttributeType.ZCL_ENUM16_ATTRIBUTE_TYPE :
            if attrType == ZCLAttributeType.ZCL_CHAR_STRING_ATTRIBUTE_TYPE or attrType == ZCLAttributeType.ZCL_OCTET_STRING_ATTRIBUTE_TYPE :
                return int(plarr[0],16), plarr[1:] ;
            else :
                raise PiotZBParseError('Unknown Type') ;
        else :
            return ZCLAttributeType.SIZE[attrType], plarr ;
    @staticmethod
    def convertRawtoValue(attrType, arr, raw) :
        attrValue = None ;
        if attrType == ZCLAttributeType.ZCL_CHAR_STRING_ATTRIBUTE_TYPE or attrType == ZCLAttributeType.ZCL_OCTET_STRING_ATTRIBUTE_TYPE :
            attrValue = ''.join(chr(int(x,16)) for x in arr) ;
        elif attrType <= ZCLAttributeType.ZCL_ENUM16_ATTRIBUTE_TYPE :
            if attrType < ZCLAttributeType.ZCL_INT8S_ATTRIBUTE_TYPE  or attrType >= ZCLAttributeType.ZCL_ENUM8_ATTRIBUTE_TYPE :
                at = attrType & 0x07 ;
                if at == 0 :
                    attrValue = struct.unpack('<B', raw.decode('hex'))[0] ;
                elif at == 1 :
                    attrValue = struct.unpack('<H', raw.decode('hex'))[0] ;
                elif at == 2 :
                    _raw = '00' + raw ;
                    attrValue = struct.unpack('<I', _raw.decode('hex'))[0] >> 8 ;
                elif at == 3 :
                    attrValue = struct.unpack('<I', raw.decode('hex'))[0] ;
                elif at == 4 :
                    _raw = '000000' + raw ;
                    attrValue = struct.unpack('<Q', _raw.decode('hex'))[0] >> 24 ;
                elif at == 5 :
                    _raw = '0000' + raw ;
                    attrValue = struct.unpack('<Q', _raw.decode('hex'))[0] >> 16 ;
                elif at == 6 :
                    _raw = '00' + raw ;
                    attrValue = struct.unpack('<Q', _raw.decode('hex'))[0] >> 8 ;
                else :
                    attrValue = struct.unpack('<Q', raw.decode('hex'))[0] ;
            else :
                if attrType == ZCLAttributeType.ZCL_INT8S_ATTRIBUTE_TYPE :
                    attrValue = struct.unpack('<b', raw.decode('hex'))[0] ;
                elif attrType == ZCLAttributeType.ZCL_INT16S_ATTRIBUTE_TYPE :
                    attrValue = struct.unpack('<h', raw.decode('hex'))[0] ;
                elif attrType == ZCLAttributeType.ZCL_INT24S_ATTRIBUTE_TYPE :
                    _raw = '00' + raw ;
                    attrValue = struct.unpack('<i', _raw.decode('hex'))[0] >> 8 ;
                elif attrType == ZCLAttributeType.ZCL_INT32S_ATTRIBUTE_TYPE :
                    attrValue = struct.unpack('<i', raw.decode('hex'))[0] ;
                elif attrType == ZCLAttributeType.ZCL_INT40S_ATTRIBUTE_TYPE :
                    _raw = '000000' + raw ;
                    attrValue = struct.unpack('<q', _raw.decode('hex'))[0] >> 24 ;
                elif attrType == ZCLAttributeType.ZCL_INT48S_ATTRIBUTE_TYPE :
                    _raw = '0000' + raw ;
                    attrValue = struct.unpack('<q', _raw.decode('hex'))[0] >> 16 ;
                elif attrType == ZCLAttributeType.ZCL_INT56S_ATTRIBUTE_TYPE :
                    _raw = '00' + raw ;
                    attrValue = struct.unpack('<q', _raw.decode('hex'))[0] >> 8 ;
                elif attrType == ZCLAttributeType.ZCL_INT56S_ATTRIBUTE_TYPE :
                    attrValue = struct.unpack('<q', raw.decode('hex'))[0] ;
        return attrValue ;
    @staticmethod
    def doReportPayload(payload) :
        attrList = [] ;
        arr = payload.strip().split() ;
        while len(arr) > 3 :
            attrId = int(arr[1] + arr[0], 16) ;
            attrType = int(arr[2], 16) ;
            arr = arr[3:] ;
            try :
                length, arr = ZbParse.getSizeOfAttributeType(attrType, arr) ;
            except PiotZBParseError as e:
                raise PiotZBParseError(e) ;
            raw = ''.join(str(x) for x in arr[0:length]) ;
            attrList.append(ZbAttribute(attrId, attrType, raw, ZbParse.convertRawtoValue(attrType, arr, raw))) ;
            arr = arr[length:] ;
        return attrList ;
    @staticmethod
    def doReadPayload(payload) :
        attrList = [] ;
        arr = payload.strip().split() ;
        while len(arr) > 4 :
            attrId = int(arr[1] + arr[0], 16) ;
            state = int(arr[2], 16);
            attrType = int(arr[3], 16) ;
            arr = arr[4:] ;
            try :
                length, arr = ZbParse.getSizeOfAttributeType(attrType, arr) ;
            except PiotZBParseError as e:
                raise PiotZBParseError(e) ;
            if state == 0 :
                raw = ''.join(str(x) for x in arr[0:length]) ;
                attrList.append(ZbAttribute(attrId, attrType, raw, ZbParse.convertRawtoValue(attrType, arr, raw))) ;
            arr = arr[length:] ;
        return attrList ;
    @staticmethod
    def doZoneChangedNotification(payload) :
        # Payload : ZoneStatus0 ZoneStatus1 ExtendedStatus2 ZoneId3 Delay4 Delay5
        attrList = [] ;
        arr = payload.strip().split() ;
        if len(arr) == 6 :
            attrList.append(ZbAttribute(ZCLAttribute.ZCL_ZONE_STATUS_ATTRIBUTE_ID, ZCLAttributeType.ZCL_BITMAP16_ATTRIBUTE_TYPE, arr[0]+arr[1], int(arr[1]+arr[0],16))) ;
            attrList.append(ZbAttribute(ZCLAttribute.ZCL_ZONE_ID_ATTRIBUTE_ID,     ZCLAttributeType.ZCL_INT8U_ATTRIBUTE_TYPE, arr[3], int(arr[3],16))) ;
        return attrList ;
    @staticmethod
    def doIasZoneEnrollRequest(payload) :
        # payload : ZoneType0 ZoneType1 MfgCode2 MfgCode3
        attrList = [] ;
        arr = payload.strip().split() ;
        if len(arr) == 4 :
            attrList.append(ZbAttribute(ZCLAttribute.ZCL_ZONE_TYPE_ATTRIBUTE_ID, ZCLAttributeType.ZCL_ENUM16_ATTRIBUTE_TYPE, arr[0]+arr[1], int(arr[1]+arr[0],16))) ;
        return attrList ;


class ZbConfig :
    DEFAUT_CONFIG = 'zigbee_common' ;
    @staticmethod
    def _doVerify(configFile) :
        if os.path.exists(configFile) :
            # TODO : checking config file - syntax and import ....
            return configFile ;
        DBG('File Not Exist : %s - Using a default config file.' % configFile) ;
        return 'config/%s.py' % ZbConfig.DEFAUT_CONFIG
    @staticmethod
    def _doSendMessage(zbem, msgs, node=None) :
        if type(msgs) is list :
            coEUI = zbem.m_zbHandle.getSwapEUI() ;
            swapCoEUI = zbem.m_zbHandle.getEUI() ;
            # print msgs ;
            countReport = 0 ;
            for msg in msgs :
                msg = msg.replace('IASCIE', swapCoEUI) ;
                msg = msg.replace('COEUI', coEUI) ;
                zbem.sendMsg(msg) ;
                countReport += msg.count('send-me-a-report') ;
                time.sleep(0.1) ;
            if node :
                node.setRequestedCount(countReport) ;
    @staticmethod
    def _getModule(name, path) :
        try :
            module = imp.load_source(name, path) ;
        except SyntaxError, err :
            ERR('Syntax Error : %s' % path) ;
            DBG(err) ;
            module = None ;
        except Exception, err :
            ERR('Exception Error : %s' % path)
            DBG(err) ;
            module = None ;
        return module ;
    @staticmethod
    def doConfiguration(zbem, node) :
        def target(zbem, node) :
            moduleName = '%s_%s' % (node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID),
                                    node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID)) ;
            configFile = 'config/%s.py' % moduleName ;
            DBG('Configuration : %s' % configFile) ;
            configFile = ZbConfig._doVerify(configFile) ;
            module = ZbConfig._getModule(moduleName, configFile) ;
            if module :
                if hasattr(module, 'doInit') :
                    instInit = getattr(module, 'doInit') ;
                    ZbConfig._doSendMessage(zbem, instInit(node)) ;
                if hasattr(module, 'doConfig') :
                    instConfig = getattr(module, 'doConfig') ;
                    ZbConfig._doSendMessage(zbem, instConfig(node), node) ;
                    zbem.m_zbHandle.setJoinState(node, ZbJoinState.CONFIG) ;
                del module ;
        threading.Timer(1, target, [zbem, node]).start() ;

    @staticmethod
    def _doMethod(zbem, node, method) :
        moduleName = '%s_%s' % (node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID),
                                node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID)) ;
        configFile = 'config/%s.py' % moduleName ;
        configFile = ZbConfig._doVerify(configFile) ;
        module = ZbConfig._getModule(moduleName, configFile) ;
        if module :
            if hasattr(module, method) :
                inst = getattr(module, method) ;
                ZbConfig._doSendMessage(zbem, inst(node), node) ;
            del module ;
    @staticmethod
    def doRefresh(zbem, node) :
        zbem.m_zbHandle.setJoinState(node, ZbJoinState.DONE) ;
        threading.Timer(1, ZbConfig._doMethod, [zbem, node, 'doRefresh']).start() ;

class ZbCoordinator :
    def __init__(self) :
        self.m_eui = ''
        self.m_channel = 0 ;
        self.m_power = 0 ;
    def setCoordinator(self, eui, ch, pwr) :
        self.m_eui = ''.join(reversed(re.findall('..', eui))) ;
        self.m_channel = ch ;
        self.m_power = pwr ;
    def getEUI(self) :
        return self.m_eui ;
    def getSwapEUI(self, separator='') :
        return separator.join(reversed(re.findall('..', self.m_eui))) ;
    def getChannel(self) :
        return self.m_channel ;
    def getPower(self) :
        return self.m_power ;
    def dump(self) :
        return 'EUI:%s ch:%s pwr:%s' % (self.m_eui, self.m_channel, self.m_power) ;


class ZbHandler(ZbParse, ZbConfig, ZbCoordinator) :
    def __init__(self, ippHandle) :
        ZbCoordinator.__init__(self) ;
        self.m_epId = 1 ;
        self.m_ippHandle = ippHandle ;
        self.m_nodeArray = [] ;
        self.initNodeFromDB() ;
    def dump(self) :
        DBG(ZbCoordinator.dump(self)) ;
        index = 1 ;
        for node in self.m_nodeArray :
            node.dump('%2d' % index) ;
            index += 1 ;
    def initNodeFromDB(self) :
        reply = self.m_ippHandle.sendQueryRequest(IPMeta.SUBTYPE_DB, IPMeta.QUERY_DB_GET_NODE, 10) ;
        if reply.success :
            for row in reply.value :
                arr = row.split('|') ;
                if arr[3] == SensorMeta.SEN_TYPE_ZB_NODE :
                    node = self.addNode(arr[0], hex(int(arr[2]))) ;
                    node.setExtra(PSJson.toOBJ2(arr[5])) ;
        reply = self.m_ippHandle.sendQueryRequest(IPMeta.SUBTYPE_DB, IPMeta.QUERY_DB_GET_CLUSTER, 10) ;
        if reply.success :
            for row in reply.value :
                arr = row.split('|') ;
                if arr[3] == SensorMeta.SEN_TYPE_ZB_CLUSTER :
                    node = self.getNodeWithEUI(arr[0]) ;
                    arrId = arr[2].split('.') ;
                    if node and len(arrId) == 2 :
                        ep = node.getEndpoint(int(arrId[0])) ;
                        if ep :
                            ep.addCluster(ZbCluster(int(arrId[1]), True if arr[4] == 'True' else False)) ;
        reply = self.m_ippHandle.sendQueryRequest(IPMeta.SUBTYPE_DB, IPMeta.QUERY_DB_GET_ATTRIBUTE, 10) ;
        if reply.success :
            for row in reply.value :
                arr = row.split('|') ;
                if arr[3] == SensorMeta.SEN_TYPE_ZB_ATTRIBUTE :
                    node = self.getNodeWithEUI(arr[0]) ;
                    arrId = arr[2].split('.') ;
                    if node and len(arrId) == 3 :
                        ep = node.getEndpoint(int(arrId[0])) ;
                        if ep :
                            cl = ep.getCluster(int(arrId[1])) ;
                            if cl :
                                extra = PSJson.toOBJ2(arr[5]) ;
                                # cl.upsertAttribute(ZbAttribute(int(arrId[2]), extra.type, extra.raw, arr[4])) ;
                                self.upsertAttribute(node, ep, cl, [ZbAttribute(int(arrId[2]), extra.type, extra.raw, arr[4])], False) ;

    def getNodeWithEUI(self, eui) :
        for node in self.m_nodeArray :
            if node.m_eui == eui :
                return node ;
        return None ;
    def setCoordinator(self, eui, channel, power) :
        ZbCoordinator.setCoordinator(self, eui, channel, power) ;
    def getNode(self, nodeId) :
        if isinstance(nodeId, basestring) :
            nodeId = int(nodeId, 16) ;
        for node in self.m_nodeArray :
            if node.getId() == nodeId :
                return node ;
        return None ;
    def addNode(self, eui, nodeId) :
        node = ZbNode(eui, int(nodeId, 16)) ;
        node.setSensorDevice(SensorDevice(eui)) ;
        node.setActivity(True) ;
        self.m_nodeArray.append(node) ;
        self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
            SensorEvent(SensorMeta.SEN_TYPE_ZB_NODE, eui, node.getId(), None, None).toString()) ;
        return node ;
    def updateNode(self, node, nodeId) :
        node.setActivity(True) ;
        node.setNodeId(nodeId) ;
        self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
            SensorEvent(SensorMeta.SEN_TYPE_ZB_NODE, node.getEUI(), node.getId(), None, None).toString()) ;
    def setCapability(self, node, capability) :
        node.setCapability(capability) ;
        # self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
        #     SensorEvent(SensorMeta.SEN_TYPE_ZB_NODE, node.getEUI(), node.getId(), None, node.getExtra()).toString()) ;
    def setActivity(self, node, activity) :
        node.setActivity(activity) ;
        self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
            SensorEvent(SensorMeta.SEN_TYPE_ZB_NODE, node.getEUI(), node.getId(), None, node.getExtra()).toString()) ;
    def setJoinState(self, node, joinState) :
        node.setJoinState(joinState) ;
        self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
            SensorEvent(SensorMeta.SEN_TYPE_ZB_NODE, node.getEUI(), node.getId(), None, node.getExtra()).toString()) ;
    def getJoinState(self, node) :
        return node.getJoinState() ;
    def setNodeExtraInfo(self, node, payload) :
        arr = payload.split() ;
        if len(arr) == 4 :
            node.setMfgId(int(arr[3]+arr[2],16)) ;
            # self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
            #     SensorEvent(SensorMeta.SEN_TYPE_ZB_NODE, node.getEUI(), node.getId(), None, node.getExtra()).toString()) ;
            return True ;
        return False ;
    def addCluster(self, node, ep, clId, clDir) :
        ep.addCluster(ZbCluster(clId, clDir)) ;
        self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
            SensorEvent(SensorMeta.SEN_TYPE_ZB_CLUSTER, node.getEUI(), '%s.%s' % (ep.getId(), clId), clDir, None).toString()) ;
    # deprecated function
    # def addAttribute(self, node, epId, clId, attr) :
    #     ep = node.getEndpoint(epId) ;
    #     if ep :
    #         cl = ep.getCluster(clId) ;
    #         if cl :
    #             at = cl.getAttribute(attr.getId()) ;
    #             if at is None or at.isEqual(attr) :
    #                 DBG('Changed %s:%s:%s %s' % (hex(epId), hex(clId), hex(attr.getId()), str(attr.getValue()))) ;
    #             cl.upsertAttribute(attr) ;
    def __updateSensorDevice(self, sensordevice, node, cl, attr) :
        if sensordevice :
            if cl.getId() < ZCLCluster.ZCL_SAMPLE_MFG_SPECIFIC_CLUSTER_ID :
                funcPool = (
                    (ZCLCluster.ZCL_BASIC_CLUSTER_ID, (
                        (ZCLAttribute.ZCL_APPLICATION_VERSION_ATTRIBUTE_ID,             SensorDevice.setAppVersion) ,
                        (ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID,               SensorDevice.setManufacturer) ,
                        (ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID,                SensorDevice.setModel) ,
                        (ZCLAttribute.ZCL_SW_BUILD_ID_ATTRIBUTE_ID,                     SensorDevice.setSwBuild))) ,
                    (ZCLCluster.ZCL_POWER_CONFIG_CLUSTER_ID, (
                        (ZCLAttribute.ZCL_BATTERY_VOLTAGE_ATTRIBUTE_ID,                 SensorDevice.setBattery))) ,
                    (ZCLCluster.ZCL_IAS_ZONE_CLUSTER_ID, (
                        (ZCLAttribute.ZCL_ZONE_STATUS_ATTRIBUTE_ID,                     SensorDevice.setZoneStatus))) ,
                    (ZCLCluster.ZCL_TEMP_MEASUREMENT_CLUSTER_ID, (
                        (ZCLAttribute.ZCL_TEMP_MEASURED_VALUE_ATTRIBUTE_ID,             SensorDevice.setTemperature))) ,
                    (ZCLCluster.ZCL_RELATIVE_HUMIDITY_MEASUREMENT_CLUSTER_ID, (
                        (ZCLAttribute.ZCL_RELATIVE_HUMIDITY_MEASURED_VALUE_ATTRIBUTE_ID,SensorDevice.setHumidity))) ,
                ) ;
                for clpool in funcPool :
                    if clpool[0] == cl.getId() :
                        for item in clpool[1] :
                            if item[0] == attr.getId() :
                                item[1](sensordevice, attr.getValue()) ;
                                return ;
            else :
                funcPool = (
                    ( 0x110A, (0xFC02, ((0x0010, SensorDevice.setAccelActive) ,
                                        (0x0012, SensorDevcie.setAccelX) ,
                                        (0x0013, SensorDevcie.setAccelY) ,
                                        (0x0014, SensorDevice.setAccelZ)))) ,
                    ( 0x1002, (0xFC00, ((0x0010, SensorDevice.setAccelActive) ,
                                        (0x0012, SensorDevcie.setAccelX) ,
                                        (0x0013, SensorDevcie.setAccelY) ,
                                        (0x0014, SensorDevice.setAccelZ)))) ,
                ) ;
                for mfgPool in funcPool :
                    if mfgPool[0] == node.getMfgId() :
                        for clpool in mfgPool[1] :
                            if clpool[0] == cl.getId() :
                                for item in clpool[1] :
                                    if item[0] == attr.getId() :
                                        item[1](sensordevice, attr.getValue()) ;
                                        return ;

    def upsertAttribute(self, node, ep, cl, attrList, notify=True) :
        fgChanged = False ;
        for a in attrList :
            if cl.upsertAttribute(a) :
                self.__updateSensorDevice(node.getSensorDevice(), node, cl, a) ;
                if notify :
                    self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SENSOR,
                        SensorEvent(SensorMeta.SEN_TYPE_ZB_ATTRIBUTE, node.getEUI(), '%s.%s.%s' % (ep.getId(), cl.getId(), a.getId()), a.getValue(), a.getExtra()).toString()) ;
                fgChanged = True ;
        return fgChanged ;
    def setZoneNotification(self, nodeId, status, ext, zoneId, delay) :
        node = self.getNode(nodeId) ;
        if node :
            node.setZoneStatus(status, ext, zoneId, delay) ;
            return True ;
        return False ;
    def getMessageToReadBasicAttribute(self, node) :
        attrList = [ ZCLAttribute.ZCL_APPLICATION_VERSION_ATTRIBUTE_ID ,
                     ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID ,
                     ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID ,
                     ZCLAttribute.ZCL_APPLICATION_PROFILE_VERSION_ATTRIBUTE_ID ,
                     ZCLAttribute.ZCL_SW_BUILD_ID_ATTRIBUTE_ID ] ;
        msg = '' ;
        for attr in attrList :
            msg += 'zcl global read %s %s\n' % (hex(ZCLCluster.ZCL_BASIC_CLUSTER_ID), hex(attr)) ;
            msg += 'send %s %s %s\n' % (hex(node.getId()), hex(self.m_epId), hex(node.getEndpointId())) ;

        if node.hasCluster(0x1, ZCLCluster.ZCL_IAS_ZONE_CLUSTER_ID) :
            msg += 'zcl global write 0x500 0x10 0xf0 {%s}\n' % self.getEUI() ;
            msg += 'send %s 0x1 0x1\n' % hex(node.getId()) ;

        return msg ;
    def updateConfigurationResponse(self, node) :
        return node.increaseResponsedCount() ;

    # Query
    def queryGetDevice(self, uid=None) :
        devList = [] ;
        for node in self.m_nodeArray :
            if uid == None :
                devList.append(node.m_sensorDevice) ;
            elif uid == node.getId() :
                devList.append(node.m_sensorDevice) ;
        return devList ;
