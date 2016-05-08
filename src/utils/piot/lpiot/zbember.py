
import os ;
import re ;
import signal ;
import sys ;
import subprocess ;
import threading ;
from lpiot.zbmodel import ZbHandler ;
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
        pass ;
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
            ( self.rxOnInfo,      r'EMBER_NETWORK_UP 0x0000' ) ,
            ( self.rxOnNewJoin,   r'emberAfTrustCenterJoinCallback@newNodeId<0x([0-9a-fA-F]+)> newNodeEui64<([0-9a-fA-F]+)> parentOfNewNode<0x([0-9a-fA-F]+)> EmberDeviceUpdate<(.*)> EmberJoinDecision<(.*)>') ,
            # ( self.rxOnSimple,    r'Device-Query-Service EP\[([0-9a-fA-F]+)\] : found for 0x([0-9a-fA-F]+)') ,
            ( self.rxOnCluster,   r'Device-Query-Service (in|out) cluster 0x([0-9a-fA-F]+) for ep\[([0-9a-fA-F]+)\] of 0x([0-9a-fA-F]+) (.*)') ,
            ( self.rxOnBind,      r'Device-Query-Service All endpoints discovered for 0x([0-9a-fA-F]+)') ,
            ) ;
        # Remove prompt word
        if ZbEmber.PROMPT == msg[0:8] :
            msg = msg[8:] ;
        for func, rstr in RegxPool :
            mo = re.match(rstr, msg)
            if mo :
                return func(mo) ;

    def rxOnInfo(self, mo) :
        self.sendMsg('info') ;
        return True ;
    def rxOnNewJoin(self, mo) :
        DBG('%s %s %s %s %s' % (mo.group(1), mo.group(2), mo.group(3), mo.group(4), mo.group(5))) ;
        rv = False ;
        node = self.m_zbHandler.getNodeWithEUI(mo.group(2)) ;
        if mo.group(4).find(' left') >= 0 :
            DBG('Device left, but keeping device data.') ;
            if node :
                node.setActivity(False) ;
            self.sendMsg('plugin device-database device erase {%s}' % self.m_zbHandler.getSwapEUI64(mo.group(2))) ;
        elif mo.group(4).find(' rejoin') >= 0 :
            # TODO :
            # It should be to read basic cluster attributes for firmware version and others ...
            # Or to write IAS Zone's CIB Address for Notification because some device could be forgot the coordinator's endpoint. But it is not mandotory.
            pass ;
        elif mo.group(4).find(' join') >= 0 :
            rv = True ;
            if node is None :
                node = self.m_zbHandler.addChildNode(mo.group(2), mo.group(1)) ;
            # self.sendMsg('zdo active %s' % hex(node.m_nodeId), 0.01) ;
        else :
            DBG(CliColor.RED + 'Unknown State' + CliColor.NONE) ;
        return rv ;
    def rxOnSimple(self, mo) :
        DBG('%s %s' % (mo.group(1), mo.group(2))) ;
        self.sendMsg('zdo simple 0x%s %s' % (mo.group(2), mo.group(1)), 0.01) ;
        return True ;
    def rxOnCluster(self, mo) :
        DBG('%s %s %s %s %s' %(mo.group(1), mo.group(2), mo.group(3), mo.group(4), mo.group(5))) ;
        node = self.m_zbHandler.getNode(int(mo.group(4),16)) ;
        ep = node.getEndpoint(int(mo.group(3))) ;
        if ep and ep.getCluster(int(mo.group(2),16)) is None :
            self.m_zbHandler.addCluster(ep, int(mo.group(2),16), True if mo.group(1) == 'in' else False) ;
        return True ;
