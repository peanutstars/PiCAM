
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

class ZbEndpoint :
    def __init__(self, id, profileId, deviceId) :
        self.m_id = id ;
        self.m_profileId = profileId ;
        self.m_deviceId = deviceId ;
        self.m_clusterArray = [] ;

class ZbCluster :
    def __init__(self, id, dir) :
        self.m_id = id ;
        self.m_dir = dir ;
        self.m_attributeArray = [] ;

class ZbAttribute :
    def __init__(self, id, type, raw, value=None) :
        self.m_id = id ;
        self.m_type = type ;
        self.m_raw = raw ;
        self.m_value = value ;

class ZbHandler :
    def __init__(self, db) :
        self.m_db = db
        self.m_nodeArray = [] ;
    def dumpNode(self) :
        index = 1 ;
        for node in self.m_nodeArray :
            DBG('%2d %s %s %s' %(index, node.m_eui, node.m_nodeId, str(node.m_fgActivity))) ;
            index += 1 ;
    def getSwapEUI64(self, nodeId) :
        return ''.join(reversed(re.findall('..', nodeId))) ;
    def getNode(self, eui, nodeId) :
        for node in self.m_nodeArray :
            if node.m_eui == eui :
                if node.m_nodeId != nodeId :
                    node.m_nodeId = nodeId ;
                return node ;
        return None ;
    def addChildNode(self, eui, nodeId) :
        node = ZbNode(eui, nodeId) ;
        node.setActivity(True) ;
        self.m_nodeArray.append(node) ;
        return node ;
