
import re ;
from libps.psDebug import CliColor, DBG, ERR ;

class ZbDiscoverState :
    SIMPLE = 0 ;
    BIND = 1 ;
    CONFIG_REPORT = 2 ;
    DONE = 3 ;

class ZbNode :
    def __init__(self, eui, nodeId, discover=ZbDiscoverState.SIMPLE) :
        self.m_eui = eui ;
        self.m_nodeId = nodeId ;
        self.m_fgActivity = False ;
        self.m_discoverState = discover ;
        self.m_endpointArray = [] ;
    def setActivity(self, fgActivity=False) :
        self.m_fgActivity = fgActivity ;
    def getEndpoint(self, endpoint) :
        for ep in self.m_endpointArray :
            if ep.m_id == endpoint :
                return ep ;
        ep = ZbEndpoint(endpoint) ;
        self.m_endpointArray.append(ep) ;
        return ep ;
    def dumpNode(self, msg='') :
        msgnd = msg + ' %s %s %s' %(self.m_eui, hex(self.m_nodeId), str(self.m_fgActivity)) ;
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
    def getCluster(self, cluster) :
        for cl in self.m_clusterArray :
            if cl.m_id == cluster :
                return cl ;
        return None ;
    def addCluster(self, cluster) :
        for cl in self.m_clusterArray :
            if cl.m_id == cluster.m_id :
                DBG('Already exist cluster %s' % hex(cluster.m_id)) ;
                return ;
        self.m_clusterArray.append(cluster) ;
    def dumpEndpoint(self, msg='') :
        if len(self.m_clusterArray) > 0 :
            for cl in self.m_clusterArray :
                msgep = msg + ' ep[%d]' % self.m_id ;
                cl.dumpCluster(msgep) ;
        else :
            DBG(msg + ' ep[%d]' % self.m_id) ;

class ZbCluster :
    def __init__(self, clId, clDir) :
        self.m_id = clId ;
        self.m_dir = clDir ;
        self.m_attributeArray = [] ;
    def dumpCluster(self, msg='') :
        if len(self.m_attributeArray) > 0 :
            for at in self.m_attributeArray :
                msgcl = msg + ' %s %s' % (hex(self.m_id), str(self.m_dir)) ;
                at.dumpAttribute(msgcl) ;
        else :
            DBG(msg + ' %s %s' % (hex(self.m_id), str(self.m_dir))) ;

class ZbAttribute :
    def __init__(self, atId, atType, raw, value=None) :
        self.m_id = atId ;
        self.m_type = atType ;
        self.m_raw = raw ;
        self.m_value = value ;
    def dumpAttribute(self, msg='') :
        DBG(msg + ' %s %s %s %s' % (hex(self.m_id), hex(self.m_type), self.m_raw, str(self.m_value))) ;

class ZbHandler :
    def __init__(self, db) :
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
        for node in self.m_nodeArray :
            if node.m_nodeId == nodeId :
                return node ;
        return None ;

    def addChildNode(self, eui, nodeId) :
        node = ZbNode(eui, int(nodeId, 16)) ;
        node.setActivity(True) ;
        self.m_nodeArray.append(node) ;
        return node ;
    def addCluster(self, ep, clId, clDir) :
        ep.addCluster(ZbCluster(clId, clDir)) ;
