
class ZbDiscoverState :
    SIMPLE = 0 ;
    BIND = 1 ;
    CONFIG_REPORT = 2 ;
    DONE = 3 ;

class ZbNode :
    def __init__(self, eui, nodeId, discover=ZbDiscoverState.SIMPLE) :
        self.m_eui = eui ;
        self.m_nodeId = nodeId ;
        self.m_discoverState = discover ;
        self.m_endpointArray = [] ;

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
