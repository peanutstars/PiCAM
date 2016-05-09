
import re ;
from zbdefine import ZCLCluster, ZCLAttribute ;
from libps.psDebug import CliColor, DBG, ERR ;

class ZbDiscoverState :
    SIMPLE = 0 ;
    BIND = 1 ;
    CONFIG_REPORT = 2 ;
    DONE = 3 ;

class ZbNode :
    def __init__(self, eui, nodeId, discover=ZbDiscoverState.SIMPLE) :
        self.m_eui = eui ;
        self.m_id = nodeId ;
        self.m_fgActivity = False ;
        self.m_discoverState = discover ;
        self.m_endpointArray = [] ;
    def getId(self) :
        return self.m_id ;
    def setActivity(self, fgActivity=False) :
        self.m_fgActivity = fgActivity ;
    def getEndpoint(self, endpoint) :
        for ep in self.m_endpointArray :
            if ep.getId() == endpoint :
                return ep ;
        ep = ZbEndpoint(endpoint) ;
        self.m_endpointArray.append(ep) ;
        return ep ;
    def findEndpoint(self, epId) :
        for ep in self.m_endpointArray :
            if ep.getId() == epId :
                return ep ;
        return None ;
    def getEndpointId(self) :
        count = len(self.m_endpointArray) ;
        if count == 0 :
            ERR('Empty Endpoint') ;
            return 0 ;
        elif count == 1 :
            return self.m_endpointArray[0].getId() ;
        else :
            for epid in range(1, 256) :
                ep = self.findendpoint(epid) ;
                if ep :
                    return ep.getId() ;

    def setNodeId(self, nodeId) :
        if isinstance(nodeId, basestring) :
            self.m_id = int(nodeId, 16) ;
        elif isinstance(nodeId, int) :
            self.m_id = nodeId ;
    def dumpNode(self, msg='') :
        msgnd = msg + ' %s %s %s' %(self.m_eui, hex(self.m_id), str(self.m_fgActivity)) ;
        if len(self.m_endpointArray) > 0 :
            for ep in self.m_endpointArray :
                ep.dumpEndpoint(msgnd) ;
        else :
            DBG(msgnd) ;

class ZbEndpoint :
    def __init__(self, id) :
        self.m_id = id ;
        # self.m_profileId = profileId ;
        # self.m_deviceId = deviceId ;
        self.m_clusterArray = [] ;
    def getId(self) :
        return self.m_id ;
    def getCluster(self, cluster) :
        for cl in self.m_clusterArray :
            if cl.getId() == cluster :
                return cl ;
        return None ;
    def addCluster(self, cluster) :
        for cl in self.m_clusterArray :
            if cl.getId() == cluster.getId() :
                DBG('Already exist cluster %s' % hex(cluster.getId())) ;
                return ;
        self.m_clusterArray.append(cluster) ;
    def dumpEndpoint(self, msg='') :
        if len(self.m_clusterArray) > 0 :
            for cl in self.m_clusterArray :
                msgep = msg + ' ep[%d]' % self.getId() ;
                cl.dumpCluster(msgep) ;
        else :
            DBG(msg + ' ep[%d]' % self.getId()) ;

class ZbCluster :
    def __init__(self, clId, clDir) :
        self.m_id = clId ;
        self.m_dir = clDir ;
        self.m_attributeArray = [] ;
    def getId(self) :
        return self.m_id ;
    def dumpCluster(self, msg='') :
        if len(self.m_attributeArray) > 0 :
            for at in self.m_attributeArray :
                msgcl = msg + ' %s %s' % (hex(self.getId()), str(self.m_dir)) ;
                at.dumpAttribute(msgcl) ;
        else :
            DBG(msg + ' %s %s' % (hex(self.getId()), str(self.m_dir))) ;

class ZbAttribute :
    def __init__(self, atId, atType, raw, value=None) :
        self.m_id = atId ;
        self.m_type = atType ;
        self.m_raw = raw ;
        self.m_value = value ;
    def getId(self) :
        return self.m_id ;
    def dumpAttribute(self, msg='') :
        DBG(msg + ' %s %s %s %s' % (hex(self.getId()), hex(self.m_type), self.m_raw, str(self.m_value))) ;

class ZbHandler :
    def __init__(self, db) :
        self.m_epId = 1 ;
        self.m_db = db
        self.m_nodeArray = [] ;
    def dump(self) :
        index = 1 ;
        for node in self.m_nodeArray :
            node.dumpNode('%2d' % index) ;
            index += 1 ;
    def getSwapEUI64(self, nodeId) :
        return ''.join(reversed(re.findall('..', nodeId))) ;
    def getNodeWithEUI(self, eui) :
        for node in self.m_nodeArray :
            if node.m_eui == eui :
                return node ;
        return None ;
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
