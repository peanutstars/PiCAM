
import re ;
import subprocess ;
import threading ;
from lpiot.ipcpacket import IPMeta, IPDaemon ;
from libps.psDebug import CliColor, DBG, ERR ;

# raw_input() would be appended a  history function when import readline ;
try :
    import readline ;
except :
    pass ;

class Cli :
    PROMPT = 'picam >'
    CT_EMBER = 'ember' ;
    CT_PAIR = 'pair' ;
    CT_PRINT = 'print' ;
    def __init__(self, ippHandle, zbem) :
        self.m_ippHandle = ippHandle ;
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
                self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SYSTEM, 'quit') ;
                IPDaemon().stop() ;
            elif cmd[0] == Cli.CT_EMBER :
                if len(cmd) > 1 :
                    self.m_zbem.sendMsg(' '.join(cmd[1:])) ;
            elif cmd[0] == Cli.CT_PAIR :
                timeout = 60 if len(cmd) == 1 else int(re.sub('\D', '', '0'+cmd[1])) ;
                self.m_zbem.sendMsg('network pjoin %d' % timeout) ;
            elif cmd[0] == Cli.CT_PRINT :
                if cmd[1] == 'zigbee' :
                    self.m_zbem.dump() ;
                elif cmd[1] == 'db' :
                    queryList = [IPMeta.QUERY_DB_GET_NODE, IPMeta.QUERY_DB_GET_CLUSTER, IPMeta.QUERY_DB_GET_ATTRIBUTE] ;
                    for query in queryList :
                        print ('### DB : %s' % query) ;
                        reply = self.m_ippHandle.sendQueryRequest(IPMeta.SUBTYPE_DB, query) ;
                        if reply.success :
                            ii = 0 ;
                            for row in reply.value :
                                ii += 1 ;
                                print ('%3d, %s' % (ii, row)) ;

                else :
                    pass ;

        DBG('End of cliMain') ;
