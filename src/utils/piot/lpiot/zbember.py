
import os ;
import re ;
import signal ;
import sys ;
import subprocess ;
import threading ;
from libps.psDebug import CliColor, DBG, ERR ;

ENTER = '\n'

class ZbEmber :
    PROMPT = 'zbember>' ;
    def __init__(self, db, cmd) :
        self.m_db = db ;
        self.m_cmd = cmd ;
        self.m_fgRun = True ;
        self.m_sentMsg = None ;
        self.m_thid = threading.Thread(target=self.emberMain);
        self.m_thid.start() ;
        self.m_nodeArray = [] ;

    def emberMain(self) :
        DBG(self.m_cmd) ;
        self.m_proc = subprocess.Popen(self.m_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, preexec_fn=os.setsid) ;
        while self.m_fgRun :
            line = self.m_proc.stdout.readline().strip() ;
            if line == self.m_sentMsg :
                self.m_sentMsg = None ;
                continue ;
            self.m_sentMsg = None ;
            if self.processMessage(line) :
                DBG(CliColor.GREEN + line + CliColor.NONE) ;
                continue ;
            DBG(CliColor.YELLOW + line + CliColor.NONE) ;

        self.m_proc.wait() ;
        DBG('End of emberMain') ;

    def quit(self) :
        self.m_fgRun = False ;
        os.killpg(os.getpgid(self.m_proc.pid), signal.SIGTERM) ;

    def sendMsg(self, msg) :
        DBG(CliColor.BLUE + msg + CliColor.NONE) ;
        self.m_proc.stdin.write(msg + ENTER) ;
        self.m_sentMsg = ZbEmber.PROMPT + msg ;

    def processMessage(self, msg) :
        RegxPool = (
            ( self.rxOnInfo,      r'EMBER_NETWORK_UP 0x0000' ) ,
            ( self.rxOnNewJoin,   r'emberAfTrustCenterJoinCallback@newNodeId<0x([0-9a-fA-F]+)> newNodeEui64<([0-9a-fA-F]+)> parentOfNewNode<0x([0-9a-fA-F]+)> EmberDeviceUpdate<(.*)> EmberJoinDecision<(.*)>') ,
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
        if mo.group(4).find('left') >= 0 :
            DBG('Device left, but keeping device data.) ;
        elif mo.group(4).find(' rejoin') >= 0 :
            # TODO :
            # It should be to read basic cluster attributes for firmware version and others ...
            # Or to write IAS Zone's CIB Address for Notification because some device could be forgot the coordinator's endpoint. But it is not mandotory.
            pass ;
        elif mo.group(4).find(' join') >= 0 :
            pass ;
        else :
            DBG(CliColor.RED + 'Unknown State' + CliColor.NONE) ;
        return True ;
