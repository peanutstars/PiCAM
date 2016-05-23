
import imp ;
import os ;
import re ;
import struct ;
import threading ;
import time ;
from error import * ;
from zbenum import ZCLCluster, ZCLAttribute, ZCLAttributeType ;
from zbmodel import ZbJoinState, ZbNode, ZbEndpoint, ZbCluster, ZbAttribute ;
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
            coEUI = zbem.m_zbHandler.getSwapEUI() ;
            swapCoEUI = zbem.m_zbHandler.getEUI() ;
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
                    zbem.m_zbHandler.setJoinState(node, ZbJoinState.CONFIG) ;
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
        zbem.m_zbHandler.setJoinState(node, ZbJoinState.DONE) ;
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
    def __init__(self, db) :
        ZbCoordinator.__init__(self) ;
        self.m_epId = 1 ;
        self.m_db = db
        self.m_nodeArray = [] ;
        self.initNodeFromDB() ;
    def dump(self) :
        DBG(ZbCoordinator.dump(self)) ;
        index = 1 ;
        for node in self.m_nodeArray :
            node.dump('%2d' % index) ;
            index += 1 ;
    def dbdump(self) :
        self.m_db.dumpTableAll() ;
    def initNodeFromDB(self) :
        for n in self.m_db.zbLoadDevice() :
            node = self.addNode(n[0], hex(n[1])) ;
            node.setCapability(n[2] if n[2] else -1) ;
            node.setActivity(True if n[3] != 0 else False) ;
            node.setJoinState(n[4]) ;
            node.setMfgId(n[5])
        for ec in self.m_db.zbLoadCluster() :
            node = self.getNodeWithEUI(ec[0]) ;
            if node :
                ep = node.getEndpoint(ec[1]) ;
                if ep :
                    ep.addCluster(ZbCluster(ec[2], ec[3])) ;
        for at in self.m_db.zbLoadAttribute() :
            node = self.getNodeWithEUI(at[0]) ;
            if node :
                ep = node.getEndpoint(at[1]) ;
                if ep :
                    cl = ep.getCluster(at[2]) ;
                    if cl :
                        cl.upsertAttribute(ZbAttribute(at[3], at[4], 0, at[5])) ;
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
        node.setActivity(True) ;
        self.m_nodeArray.append(node) ;
        self.m_db.zbAddDevice(eui, node.getId()) ;
        return node ;
    def updateNode(self, node, nodeId) :
        node.setActivity(True) ;
        node.setNodeId(nodeId) ;
        self.m_db.zbAddDevice(node.getEUI(), node.getId()) ;
    def setCapability(self, node, capability) :
        node.setCapability(capability) ;
        self.m_db.zbCapability(node.getEUI(), capability) ;
    def setActivity(self, node, activity) :
        node.setActivity(activity) ;
        self.m_db.zbActivity(node.getEUI(), activity) ;
    def setJoinState(self, node, state) :
        node.setJoinState(state) ;
        self.m_db.zbJoinState(node.getEUI(), state) ;
    def getJoinState(self, node) :
        return node.getJoinState() ;
    def setNodeExtraInfo(self, node, payload) :
        arr = payload.split() ;
        if len(arr) == 4 :
            node.setMfgId(int(arr[3]+arr[2],16)) ;
            self.m_db.zbMfgId(node.getEUI(), node.getMfgId()) ;
            return True ;
        return False ;
    def addCluster(self, node, ep, clId, clDir) :
        ep.addCluster(ZbCluster(clId, clDir)) ;
        self.m_db.zbAddCluster(node.getEUI(), ep.getId(), 0, clId, clDir) ;
    def addAttribute(self, node, epId, clId, attr) :
        ep = node.getEndpoint(epId) ;
        if ep :
            cl = ep.getCluster(clId) ;
            if cl :
                at = cl.getAttribute(attr.getId()) ;
                if at is None or at.isEqual(attr) :
                    DBG('Changed %s:%s:%s %s' % (hex(epId), hex(clId), hex(attr.getId()), str(attr.getValue()))) ;
                cl.upsertAttribute(attr) ;
    def upsertAttribute(self, node, ep, cl, attrList) :
        query = [] ;
        for a in attrList :
            if cl.upsertAttribute(a) :
                query.append(self.m_db.zbGetQueryAddAttribute(node.getEUI(), ep.getId(), cl.getId(), a.getId(), a.getType(), a.getValue())) ;
        if len(query) :
            self.m_db.queryUpdate(query) ;
            return True ;
        return False ;
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
                     ZCLAttribute.ZCL_SW_BUILD_ID_ATTRIBUTE_ID
                     ] ;
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
