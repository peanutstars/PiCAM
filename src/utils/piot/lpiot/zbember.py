
import os ;
import signal ;
import sys ;
import subprocess ;
import threading ;
from libps.psDebug import CliColor, DBG, ERR ;

ENTER = '\n'

class ZbEmber :
    def __init__(self, cmd) :
        self.m_cmd = cmd ;
        self.m_fgRun = True ;
        self.m_thid = threading.Thread(target=self.emberMain);
        self.m_thid.start() ;

    def emberMain(self) :
        DBG(self.m_cmd) ;
        self.m_proc = subprocess.Popen(self.m_cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) ;
        while self.m_fgRun :
            line = self.m_proc.stdout.readline() ;
            DBG(CliColor.YELLOW + line.strip() + CliColor.NONE) ;
        self.m_proc.wait() ;
        DBG('End of emberMain') ;

    def quit(self) :
        self.m_fgRun = False ;
        os.killpg(os.getpgid(self.m_proc.pid), signal.SIGTERM) ;

    def sendMsg(self, msg) :
        self.m_proc.stdin.write(msg + ENTER) ;
