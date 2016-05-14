
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
    def doPayload(payload) :
        attrList = [] ;
        arr = payload.strip().split() ;
        while len(arr) > 4 :
            attrId = int(arr[1] + arr[0], 16) ;
            state = int(arr[2], 16);
            attrType = int(arr[3], 16) ;
            attrValue = None ;
            arr = arr[4:] ;
            try :
                length, arr = ZbParse.getSizeOfAttributeType(attrType, arr) ;
            except PiotZBParseError as e:
                raise PiotZBParseError(e) ;
            if state == 0 :
                raw = ''.join(str(x) for x in arr[0:length]) ;
                if attrType == ZCLAttributeType.ZCL_CHAR_STRING_ATTRIBUTE_TYPE or attrType == ZCLAttributeType.ZCL_OCTET_STRING_ATTRIBUTE_TYPE :
                    attrValue = ''.join(chr(int(x,16)) for x in arr) ;
                elif attrType < ZCLAttributeType.ZCL_ENUM8_ATTRIBUTE_TYPE :
                    if attrType < ZCLAttributeType.ZCL_INT8S_ATTRIBUTE_TYPE :
                        at = attrType & 0x07 ;
                        if at == 0 :
                            attrValue = struct.unpack('>B', raw.decode('hex'))[0] ;
                        elif at == 1 :
                            attrValue = struct.unpack('>H', raw.decode('hex'))[0] ;
                        elif at == 2 :
                            raw = '00' + raw ;
                            attrValue = struct.unpack('>I', raw.decode('hex'))[0] >> 8 ;
                        elif at == 3 :
                            attrValue = struct.unpack('>I', raw.decode('hex'))[0] ;
                        elif at == 4 :
                            raw = '000000' + raw ;
                            attrValue = struct.unpack('>Q', raw.decode('hex'))[0] >> 24 ;
                        elif at == 5 :
                            raw = '0000' + raw ;
                            attrValue = struct.unpack('>Q', raw.decode('hex'))[0] >> 16 ;
                        elif at == 6 :
                            raw = '00' + raw ;
                            attrValue = struct.unpack('>Q', raw.decode('hex'))[0] >> 8 ;
                        else :
                            attrValue = struct.unpack('>Q', raw.decode('hex'))[0] ;
                    else :
                        if attrType == ZCLAttributeType.ZCL_INT8S_ATTRIBUTE_TYPE :
                            attrValue = struct.unpack('>b', raw.decode('hex'))[0] ;
                        elif attrType == ZCLAttributeType.ZCL_INT16S_ATTRIBUTE_TYPE :
                            attrValue = struct.unpack('>h', raw.decode('hex'))[0] ;
                        elif attrType == ZCLAttributeType.ZCL_INT24S_ATTRIBUTE_TYPE :
                            raw = '00' + raw ;
                            attrValue = struct.unpack('>i', raw.decode('hex'))[0] >> 8 ;
                        elif attrType == ZCLAttributeType.ZCL_INT32S_ATTRIBUTE_TYPE :
                            attrValue = struct.unpack('>i', raw.decode('hex'))[0] ;
                        elif attrType == ZCLAttributeType.ZCL_INT40S_ATTRIBUTE_TYPE :
                            raw = '000000' + raw ;
                            attrValue = struct.unpack('>q', raw.decode('hex'))[0] >> 24 ;
                        elif attrType == ZCLAttributeType.ZCL_INT48S_ATTRIBUTE_TYPE :
                            raw = '0000' + raw ;
                            attrValue = struct.unpack('>q', raw.decode('hex'))[0] >> 16 ;
                        elif attrType == ZCLAttributeType.ZCL_INT56S_ATTRIBUTE_TYPE :
                            raw = '00' + raw ;
                            attrValue = struct.unpack('>q', raw.decode('hex'))[0] >> 8 ;
                        elif attrType == ZCLAttributeType.ZCL_INT56S_ATTRIBUTE_TYPE :
                            attrValue = struct.unpack('>q', raw.decode('hex'))[0] ;
                attrList.append(ZbAttribute(attrId, attrType, raw, attrValue)) ;
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
    def doSendMessage(zbem, msgs) :
        if type(msgs) is list :
            coEUI = zbem.m_zbHandler.coordinator.getSwapEUI(' ') ;
            # print msgs ;
            for msg in msgs :
                msg = msg.replace('COEUI', coEUI) ;
                print '@', msg ;
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
                if hasattr(module, 'doConfig') :
                    instConfig = getattr(module, 'doConfig') ;
                    ZbConfig.doSendMessage(zbem, instConfig(node)) ;
                    node.setJoinState(ZbJoinState.CONFIG) ;
                del module ;
    @staticmethod
    def doMethod(zbem, node, method) :
        moduleName = '%s_%s' % (node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MANUFACTURER_NAME_ATTRIBUTE_ID),
                                node.getValue(1, ZCLCluster.ZCL_BASIC_CLUSTER_ID, ZCLAttribute.ZCL_MODEL_IDENTIFIER_ATTRIBUTE_ID)) ;
        configFile = 'config/%s.py' % moduleName ;
        if ZbConfig.doVerify(configFile):
            module = ZbConfig.getModule(moduleName, configFile) ;
            if module :
                if hasattr(module, method) :
                    inst = getattr(module, method) ;
                    inst(node) ;
                del module ;

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
