
import imp ;
import os ;
import struct ;
from error import * ;
from zbenum import ZCLCluster, ZCLAttribute, ZCLAttributeType ;
from zbmodel import ZbJoinState, ZbCoordinator, ZbNode, ZbEndpoint, ZbCluster, ZbAttribute ;
from libps.psDebug import CliColor, DBG, ERR ;

class ZbParse :
    @staticmethod
    def getSizeOfAttributeType(attrType, plarr) :
        if attrType >= ZCLAttributeType.ZCL_ENUM8_ATTRIBUTE_TYPE :
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
        elif attrType < ZCLAttributeType.ZCL_ENUM8_ATTRIBUTE_TYPE :
            if attrType < ZCLAttributeType.ZCL_INT8S_ATTRIBUTE_TYPE :
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


class ZbConfig :
    @staticmethod
    def doVerify(configFile) :
        if os.path.exists(configFile) :
            # TODO : checking config file - syntax and import ....
            return True ;
            DBG('File Not Exist : %s' % configFile) ;
        return False ;
    @staticmethod
    def doSendMessage(zbem, msgs, node=None) :
        if type(msgs) is list :
            coEUI = zbem.m_zbHandler.coordinator.getSwapEUI() ;
            swapCoEUI = zbem.m_zbHandler.coordinator.getEUI() ;
            # print msgs ;
            countReport = 0 ;
            for msg in msgs :
                msg = msg.replace('IASCIE', swapCoEUI) ;
                msg = msg.replace('COEUI', coEUI) ;
                zbem.sendMsg(msg) ;
                countReport += msg.count('send-me-a-report') ;
            if node :
                node.m_joinState.setRequestedCount(countReport) ;

    @staticmethod
    def getModule(name, path) :
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
        rv = False ;
        moduleName = '%s_%s' % (node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID),
                                node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID)) ;
        configFile = 'config/%s.py' % moduleName ;
        DBG('Configuration : %s' % configFile) ;
        if ZbConfig.doVerify(configFile):
            module = ZbConfig.getModule(moduleName, configFile) ;
            if module :
                if hasattr(module, 'doInit') :
                    instInit = getattr(module, 'doInit') ;
                    ZbConfig.doSendMessage(zbem, instInit(node)) ;
                    rv |= True ;
                if hasattr(module, 'doConfig') :
                    instConfig = getattr(module, 'doConfig') ;
                    ZbConfig.doSendMessage(zbem, instConfig(node), node) ;
                    node.setJoinState(ZbJoinState.CONFIG) ;
                    rv |= True ;
                del module ;
        return rv ;
    @staticmethod
    def doMethod(zbem, node, method) :
        rv = False ;
        moduleName = '%s_%s' % (node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID),
                                node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID)) ;
        configFile = 'config/%s.py' % moduleName ;
        if ZbConfig.doVerify(configFile):
            module = ZbConfig.getModule(moduleName, configFile) ;
            if module :
                if hasattr(module, method) :
                    inst = getattr(module, method) ;
                    inst(node) ;
                    rv = True ;
                del module ;
        return rv ;
    @staticmethod
    def doRefresh(zbem, node) :
        node.setJoinState(ZbJoinState.DONE) ;
        return ZbConfig.doMethod(zbem, node, 'doRefresh') ;

class ZbHandler :
    def __init__(self, db) :
        self.m_epId = 1 ;
        self.m_db = db
        self.coordinator = None ;
        self.m_nodeArray = [] ;
    def dump(self) :
        if self.coordinator :
            DBG(self.coordinator.dump()) ;
        index = 1 ;
        for node in self.m_nodeArray :
            node.dump('%2d' % index) ;
            index += 1 ;
    def getNodeWithEUI(self, eui) :
        for node in self.m_nodeArray :
            if node.m_eui == eui :
                return node ;
        return None ;
    def setCoordinator(self, eui, channel, power) :
        self.coordinator = ZbCoordinator(eui, channel, power) ;
    def getNode(self, nodeId) :
        if isinstance(nodeId, basestring) :
            nodeId = int(nodeId, 16) ;
        for node in self.m_nodeArray :
            if node.getId() == nodeId :
                return node ;
        return None ;
    def addChildNode(self, eui, nodeId) :
        node = ZbNode(eui, int(nodeId, 16)) ;
        node.setActivity(True) ;
        self.m_nodeArray.append(node) ;
        return node ;
    def setNodeXInfo(self, node, payload) :
        arr = payload.split() ;
        node.setZoneType(int(arr[1]+arr[0],16)) ;
        node.setMfgId(int(arr[3]+arr[2],16)) ;
    def addCluster(self, ep, clId, clDir) :
        ep.addCluster(ZbCluster(clId, clDir)) ;
    def addAttribute(self, node, epId, clId, attr) :
        ep = node.getEndpoint(epId) ;
        if ep :
            cl = ep.getCluster(clId) ;
            if cl :
                at = cl.getAttribute(attr.getId()) ;
                if at is None or at.isEqual(attr) :
                    DBG('Changed %s:%s:%s %s' % (hex(epId), hex(clId), hex(attr.getId()), str(attr.getValue()))) ;
                cl.upsertAttribute(attr) ;
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
        return msg ;
    def updateConfigurationResponse(self, node) :
        return node.m_joinState.increaseResponsedCount() ;
