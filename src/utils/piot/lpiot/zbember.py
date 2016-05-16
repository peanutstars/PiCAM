
import os ;
import re ;
import signal ;
import sys ;
import subprocess ;
import threading ;
from lpiot.zbenum import ZCLCluster, ZCLAttribute, ZCLCommandId ;
from lpiot.zbmodel import ZbJoinState ;
from lpiot.zbhandler import ZbHandler ;
from libps.psDebug import CliColor, DBG, ERR ;

ENTER = '\n'

class ZbEmber :
    PROMPT = 'zbember>' ;
    def __init__(self, db, cmd) :
        self.m_cmd = cmd ;
        self.m_fgRun = True ;
        self.m_sentMsg = None ;
        self.m_thid = threading.Thread(target=self.emberMain);
        self.m_thid.start() ;
        self.m_zbHandler = ZbHandler(db) ;

    def emberMain(self) :
        DBG(self.m_cmd) ;
        self.m_proc = subprocess.Popen(self.m_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid) ;
        while self.m_fgRun :
            line = self.m_proc.stdout.readline().strip() ;
            if len(line) == 0 :
                continue ;
            if line == self.m_sentMsg :
                self.m_sentMsg = None ;
                continue ;
            # self.m_sentMsg = None ;
            if self.processMessage(line) :
                DBG(CliColor.GREEN + line + CliColor.NONE) ;
                continue ;
            DBG(CliColor.YELLOW + line + CliColor.NONE) ;

        self.m_proc.wait() ;
        DBG('End of emberMain') ;

    def quit(self) :
        self.m_fgRun = False ;
        os.killpg(os.getpgid(self.m_proc.pid), signal.SIGTERM) ;
    def dump(self) :
        self.m_zbHandler.dump() ;
    def dbdump(self) :
        self.m_zbHandler.dbdump() ;
    @staticmethod
    def _sendMsg(param) :
        zbem = param[0] ;
        msg = param[1] ;
        DBG(CliColor.BLUE + msg + CliColor.NONE) ;
        zbem.m_proc.stdin.write(msg + ENTER) ;
        zbem.m_sentMsg = ZbEmber.PROMPT + msg ;
    def sendMsg(self, msg, sec=0.0) :
        if sec == 0.0 :
            ZbEmber._sendMsg([self, msg]) ;
        else :
            threading.Timer(sec, ZbEmber._sendMsg, [[self, msg]]).start() ;

    def processMessage(self, msg) :
        RegxPool = (
            ( self.rxOnMessage,   r'T(.+):nodeId\[0x([0-9a-fA-F]+)\] RX len ([0-9a-fA-F]+), ep ([0-9a-fA-F]+), clus 0x([0-9a-fA-F]+) \((.+)\) mfgId ([0-9a-fA-F]+) FC ([0-9a-fA-F]+) seq ([0-9a-fA-F]+) cmd ([0-9a-fA-F]+) payload\[(.+)\]') ,
            ( self.rxOnZoneNotification, r'emberAfIasZoneClusterZoneStatusChangeNotificationCallback@nodeId<0x([0-9a-fA-F]+)> zoneStatus<0x([0-9a-fA-F]+)> extStatus<0x([0-9a-fA-F]+)> zoneId<0x([0-9a-fA-F]+)> delay<([0-9]+)>') ,
            # It brings up automatically by Device-Query-Service plugin for sending a simple descriptor request.
            # ( self.rxOnSimple,    r'Device-Query-Service EP\[([0-9a-fA-F]+)\] : found for 0x([0-9a-fA-F]+)') ,
            ( self.rxOnNewJoin,   r'emberAfTrustCenterJoinCallback@newNodeId<0x([0-9a-fA-F]+)> newNodeEui64<([0-9a-fA-F]+)> parentOfNewNode<0x([0-9a-fA-F]+)> EmberDeviceUpdate<(.*)> EmberJoinDecision<(.*)>') ,
            ( self.rxOnCluster,   r'Device-Query-Service (in|out) cluster 0x([0-9a-fA-F]+) for ep\[([0-9a-fA-F]+)\] of 0x([0-9a-fA-F]+) (.*)') ,
            ( self.rxOnBasic,     r'Device-Query-Service All endpoints discovered for 0x([0-9a-fA-F]+)') ,
            ( self.rxOnCoInfo,    r'node \[\(>\)([0-9a-fA-F]+)\] chan \[([0-9]+)\] pwr \[([0-9a-fA-F]+)\]') ,
            ( self.rxOnInfo,      r'EMBER_NETWORK_UP 0x0000' ) ,
            ) ;
        # Remove prompt word
        if ZbEmber.PROMPT == msg[0:8] :
            msg = msg[8:] ;
        for func, rstr in RegxPool :
            mo = re.match(rstr, msg)
            if mo :
                DBG(mo.groups()) ;
                return func(mo) ;

    def rxOnInfo(self, mo) :
        self.sendMsg('info') ;
        return True ;
    def rxOnNewJoin(self, mo) :
        rv = False ;
        node = self.m_zbHandler.getNodeWithEUI(mo.group(2)) ;
        if mo.group(4).find(' left') >= 0 :
            DBG('Device left, but keeping device data.') ;
            if node :
                self.m_zbHandler.setActivity(node, False) ;

        elif mo.group(4).find(' rejoin') >= 0 :
            # TODO :
            # It should be to read basic cluster attributes for firmware version and others ...
            # Or to write IAS Zone's CIB Address for Notification because some device could be forgot the coordinator's endpoint. But it is not mandotory.
            pass ;
        elif mo.group(4).find(' join') >= 0 :
            rv = True ;
            if node is None :
                node = self.m_zbHandler.addNode(mo.group(2), mo.group(1)) ;
            else :
                # It could be changed nodeId, in case of joinning again after end-device leaved network by user.
                node.setNodeId(mo.group(1)) ;
            # self.sendMsg('zdo active %s' % hex(node.m_nodeId), 0.01) ;
        else :
            DBG(CliColor.RED + 'Unknown State' + CliColor.NONE) ;
        return rv ;
    def rxOnCoInfo(self, mo) :
        self.m_zbHandler.setCoordinator(mo.group(1), int(mo.group(2)), int(mo.group(3))) ;
        return True ;
    def rxOnSimple(self, mo) :
        self.sendMsg('zdo simple 0x%s %s' % (mo.group(2), mo.group(1)), 0.01) ;
        return True ;
    def rxOnCluster(self, mo) :
        node = self.m_zbHandler.getNode(mo.group(4)) ;
        if node :
            ep = node.getEndpoint(int(mo.group(3))) ;
            if ep and ep.getCluster(int(mo.group(2),16)) is None :
                self.m_zbHandler.addCluster(node, ep, int(mo.group(2),16), True if mo.group(1) == 'in' else False) ;
            return True ;
        else :
            return False ;
    def rxOnBasic(self, mo) :
        rv = False ;
        node = self.m_zbHandler.getNode(mo.group(1)) ;
        if node :
            self.sendMsg(self.m_zbHandler.getMessageToReadBasicAttribute(node).strip(), 0.01) ;
            node.setJoinState(ZbJoinState.BASIC) ;
            rv = True ;
        return rv ;
    def rxOnZoneNotification(self, mo) :
        nodeId = int(mo.group(1),16) ;
        status = int(mo.group(2),16) ;
        ext    = int(mo.group(3),16) ;
        zoneId = int(mo.group(4),16) ;
        delay  = int(mo.group(5)) ;
        return self.m_zbHandler.setZoneNotification(nodeId, status, ext, zoneId, delay) ;
    def rxOnMessage(self, mo) :
        cmdPool = (
            ( None, ZCLCluster.ZCL_OTA_BOOTLOAD_CLUSTER_ID, -1) ,
            # ( self.rxOnMsgChangedNotification, ZCLCluster.ZCL_IAS_ZONE_CLUSTER_ID, ZCLCommandId.ZCL_ZONE_STATUS_CHANGE_NOTIFICATION_COMMAND_ID) ,
            ( self.rxOnIasZoneEnrollRequest,   ZCLCluster.ZCL_IAS_ZONE_CLUSTER_ID, ZCLCommandId.ZCL_ZONE_ENROLL_REQUEST_COMMAND_ID) ,
            ( self.rxOnConfigResponse, -1, ZCLCommandId.ZCL_CONFIGURE_REPORTING_RESPONSE_COMMAND_ID) ,
            ( self.rxOnMsgReportAttribute, -1, ZCLCommandId.ZCL_REPORT_ATTRIBUTES_COMMAND_ID) ,
            ( self.rxOnMsgReadAttribute, -1, ZCLCommandId.ZCL_READ_ATTRIBUTES_RESPONSE_COMMAND_ID) ,
        ) ;
        node = self.m_zbHandler.getNode(mo.group(2)) ;
        rv = False ;
        if node :
            ep = node.findEndpoint(int(mo.group(4), 16)) ;
            if ep :
                cl = ep.getCluster(int(mo.group(5),16)) ;
                if cl :
                    clusterId = cl.getId() ;
                    cmdId = int(mo.group(10), 16) ;
                    for item in cmdPool :
                        if item[1] == clusterId and item[2] == cmdId :
                            return item[0](node, ep, cl, mo.group(11)) ;
                        if item[1] == clusterId and item[2] == -1 :
                            # This cluster and command is passing.
                            return False ;
                        if item[1] == -1 :
                            if item[2] == cmdId :
                                return item[0](node, ep, cl, mo.group(11)) ;
        return rv ;
    def rxOnMsgReportAttribute(self, node, ep, cl, payload) :
        fgDirty = False ;
        for a in self.m_zbHandler.doReportPayload(payload) :
            fgDirty |= cl.upsertAttribute(a) ;
        if fgDirty :
            DBG('Changed Attribute') ;
        if node.getJoinState() == ZbJoinState.BASIC :
            if payload.find('00 40 ') == 0 :
                self.m_zbHandler.doConfiguration(self, node) ;
        return True ;
    def rxOnMsgReadAttribute(self, node, ep, cl, payload) :
        if self.m_zbHandler.upsertAttribute(node, ep, cl, self.m_zbHandler.doReadPayload(payload)) :
            DBG('Attribute Updated') ;
        if node.getJoinState() == ZbJoinState.BASIC :
            if payload.find('00 40 ') == 0 :
                self.m_zbHandler.doConfiguration(self, node) ;
        return True ;
    # def rxOnMsgChangedNotification(self, node, ep, cl, payload) :
    #     return True ;
    def rxOnConfigResponse(self, node, ep, cl, payload) :
        if self.m_zbHandler.updateConfigurationResponse(node) :
            self.m_zbHandler.doRefresh(self, node) ;
        return True ;
    def rxOnIasZoneEnrollRequest(self, node, ep, cl, payload) :
        if self.m_zbHandler.setNodeXInfo(node, payload) == False :
            return self.rxOnMsgReadAttribute(node, ep, cl, payload)
        return True ;
