
import re ;
import subprocess ;
import threading ;
from libps.psDebug import CliColor, DBG, ERR ;

class Cli :
    PROMPT = 'picam >'
    CT_ZB = 'zb' ;
    CT_DB = 'db' ;
    CT_PAIR = 'pair'
    def __init__(self, zbem) :
        self.m_zbem = zbem ;
        self.m_fgRun = True ;
        self.m_thid = threading.Thread(target=self.cliMain);
        self.m_thid.start() ;

    def cliMain(self) :
        while self.m_fgRun :
            cmd = raw_input(Cli.PROMPT).strip().split() ;
            # DBG('CMD%s' % cmd)
            if cmd == [] :
                continue ;
            if cmd[0] == 'quit' :
                self.m_fgRun = False ;
                self.m_zbem.quit() ;
            elif cmd[0] == Cli.CT_ZB :
                if len(cmd) > 1 :
                    self.m_zbem.sendMsg(' '.join(cmd[1:])) ;
            elif cmd[0] == Cli.CT_PAIR :
                timeout = 60 if len(cmd) == 1 else int(re.sub('\D', '', '0'+cmd[1])) ;
                self.m_zbem.sendMsg('network pjoin %d' % timeout) ;

        DBG('End of cliMain') ;
