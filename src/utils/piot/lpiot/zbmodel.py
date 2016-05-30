
import re ;
from zbenum import ZCLCluster, ZCLAttribute, ZCLAttributeType ;
from libps.psDebug import CliColor, DBG, ERR ;

class ZbJoinState :
    SIMPLE = 0 ;
    BASIC = 1 ;
    CONFIG = 2 ;
    DONE = 3 ;
    def __init__(self, state=SIMPLE) :
        self.m_state = state ;
        self.m_requestedReportCount = 0 ;
        self.m_responsedReportCount = 0 ;
    def setJoinState(self, state) :
        self.m_state = state ;
        if hasattr(self, 'm_extra') :
            self.m_extra.joinState = state ;
        if state == ZbJoinState.SIMPLE :
            self.m_requestedReportCount = 0 ;
            self.m_responsedReportCount = 0 ;
    def getJoinState(self) :
        return self.m_state ;
    def setRequestedCount(self, count) :
        self.m_requestedReportCount = count ;
    def increaseResponsedCount(self) :
        self.m_responsedReportCount += 1 ;
        return self.m_requestedReportCount == self.m_responsedReportCount ;
    def dump(self) :
        stringList = ['Simple', 'Basic', 'Config', 'Done'] ;
        if self.m_state < 0 or self.m_state > ZbJoinState.DONE :
            return 'UnKnown State' ;
        return stringList[self.m_state] ;

class ZbNode(ZbJoinState) :
    class Extra :
        def __init__(self, joinState) :
            self.mfgId = None ;
            self.capability = 0 ;
            self.activity = False ;
            self.joinState = joinState ;
    def __init__(self, eui, nodeId) :
        ZbJoinState.__init__(self) ;
        self.m_eui = eui ;
        self.m_id = nodeId ;
        self.m_extra = ZbNode.Extra(self.getJoinState()) ;
        self.m_endpointArray = [] ;
    def getEUI(self) :
        return self.m_eui ;
    def getSwapEUI(self, separator='') :
        return separator.join(reversed(re.findall('..', self.m_eui))) ;
    def getId(self) :
        return self.m_id ;
    def getExtra(self) :
        return self.m_extra ;
    def setCapability(self, capability) :
        self.m_extra.capability = capability ;
    def setActivity(self, fgActivity=False) :
        self.m_extra.activity = fgActivity ;
    def setMfgId(self, id) :
        self.m_extra.mfgId = id ;
    def getMfgId(self) :
        return self.m_extra.mfgId ;
    def getEndpoint(self, epId) :
        for ep in self.m_endpointArray :
            if ep.getId() == epId :
                return ep ;
        ep = ZbEndpoint(epId) ;
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
    def getValue(self, epId, clId, atId) :
        for ep in self.m_endpointArray :
            if ep.getId() == epId :
                cl = ep.getCluster(clId) ;
                if cl :
                    at = cl.getAttribute(atId) ;
                    if at :
                        return at.getValue() ;
        return None ;
    def hasCluster(self, epId, clId) :
        for ep in self.m_endpointArray :
            if ep.getId() == epId :
                cl = ep.getCluster(clId) ;
                if cl :
                    return True ;
        return False ;
    @staticmethod
    def intToString(value, digit) :
        fmt = '%%0%dX' % digit ;
        strValue = fmt % value ;
        return ''.join(reversed(re.findall('..', strValue)))
    def dump(self, msg='') :
        msgnd = msg + ' %s %s %s Mfg[%04X] Join.%s C%X' % (self.m_eui, hex(self.m_id), str(self.m_extra.activity), self.m_extra.mfgId, ZbJoinState.dump(self), self.m_extra.capability) ;
        if len(self.m_endpointArray) > 0 :
            for ep in self.m_endpointArray :
                ep.dump(msgnd) ;
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
    def getCluster(self, clId) :
        for cl in self.m_clusterArray :
            if cl.getId() == clId :
                return cl ;
        return None ;
    def addCluster(self, cluster) :
        for cl in self.m_clusterArray :
            if cl.getId() == cluster.getId() :
                DBG('Already exist cluster %s' % hex(cluster.getId())) ;
                return ;
        self.m_clusterArray.append(cluster) ;
    def getValue(self, clId, atId) :
        for cl in self.m_clusterArray :
            if cl.getId() == clId :
                at = cl.getAttribute(atId) ;
                if at :
                    return at.getValue() ;
        return None ;
    def dump(self, msg='') :
        if len(self.m_clusterArray) > 0 :
            for cl in self.m_clusterArray :
                msgep = msg + ' ep[%d]' % self.getId() ;
                cl.dump(msgep) ;
        else :
            DBG(msg + ' ep[%d]' % self.getId()) ;

class ZbCluster :
    def __init__(self, clId, clDir) :
        self.m_id = clId ;
        self.m_dir = clDir ;
        self.m_attributeArray = [] ;
    def getId(self) :
        return self.m_id ;
    def getAttribute(self, atId) :
        for at in self.m_attributeArray :
            if at.getId() == atId :
                return at ;
        return None ;
    # def addAttribute(self, attr) :
    #     for at in self.m_attributeArray :
    #         if at.getId() == attr.getId() :
    #             DBG('Already exist attribute %s' % hex(attr.getId())) ;
    #             return ;
    #     self.m_attributeArray.append(attr) ;
    def upsertAttribute(self, attr) :
        idx = 0 ;
        for at in self.m_attributeArray :
            if at.getId() == attr.getId() :
                if at.isEqual(attr) :
                    return False ;
                del self.m_attributeArray[idx] ;
                break ;
            idx += 1 ;
        self.m_attributeArray.append(attr) ;
        return True ;
    def getValue(self, atId) :
        for at in self.m_attributeArray :
            if at.getId() == atId :
                return at.getValue() ;
        return None ;
    def dump(self, msg='') :
        if len(self.m_attributeArray) > 0 :
            for at in self.m_attributeArray :
                msgcl = msg + ' C[%s %s]' % (hex(self.getId()), str(self.m_dir)) ;
                at.dump(msgcl) ;
        else :
            DBG(msg + ' %s %s' % (hex(self.getId()), str(self.m_dir))) ;

class ZbAttribute :
    def __init__(self, atId, atType, raw, value=None) :
        self.m_id = atId ;
        self.m_type = atType ;
        self.m_raw = str(raw) ;
        self.m_value = value ;
    def getId(self) :
        return self.m_id ;
    def isEqual(self, attr) :
        # if isinstance(attr, ZbAttribute) :
        return (self.m_id == attr.m_id and self.m_type == attr.m_type and self.m_value == attr.m_value) ;
    def getType(self) :
        return self.m_type ;
    def getValue(self) :
        return self.m_value ;
    def dump(self, msg='') :
        DBG(msg + ' A[%s %s %s %s]' % (hex(self.getId()), hex(self.m_type), str(self.m_value), self.m_raw)) ;
