
import json ;
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
    PROMPT =    'picam >'
    CT_EMBER =  'ember' ;
    CT_PAIR =   'pair' ;
    CT_PRINT =  'print' ;
    def __init__(self, ippHandle, zbem) :
        self.m_ippHandle = ippHandle ;
        self.m_zbem = zbem ;
        self.m_fgRun = True ;
        self.m_thid = threading.Thread(target=self.cliMain);
        self.m_thid.start() ;
        self.command = {
            'quit' :        self.__cmdQuit ,
            Cli.CT_EMBER :  self.__cmdEmber ,
            Cli.CT_PAIR :   self.__cmdPair ,
            Cli.CT_PRINT :  self.__cmdPrint ,
        } ;
        self.commandPrint = {
            "db" :          self.__cmdPrintDatabase ,
            "zigbee" :      self.__cmdPrintZigbee ,
            "device" :      self.__cmdPrintSensorDevice ,
        } ;

    def __cmdQuit(self, argv) :
        self.m_fgRun = False ;
        self.m_zbem.quit() ;
        self.m_ippHandle.sendNotify(IPMeta.SUBTYPE_SYSTEM, 'quit') ;
        IPDaemon().stop() ;
    def __cmdEmber(self, argv) :
        self.m_zbem.sendMsg(' '.join(argv)) ;
    def __cmdPair(self, argv) :
        timeout = int(re.sub('\D', '', '0'+argv[0])) if argv else 60 ;
        self.m_zbem.sendMsg('network pjoin %d' % timeout) ;
    def __cmdPrintZigbee(self, argv) :
        self.m_zbem.dump() ;
    def __cmdPrintDatabase(self, argv) :
        queries = [IPMeta.QUERY_DB_GET_NODE, IPMeta.QUERY_DB_GET_CLUSTER, IPMeta.QUERY_DB_GET_ATTRIBUTE] ;
        for query in queries :
            print ('### DB : %s' % query) ;
            reply = self.m_ippHandle.sendQueryRequest(IPMeta.SUBTYPE_DB, query) ;
            if reply.success :
                ii = 0 ;
                for row in reply.value :
                    ii += 1 ;
                    print ('%3d, %s' % (ii, row)) ;
    def __cmdPrintSensorDevice(self, argv) :
        print ('### Sensor Device Lists') ;
        print json.dumps(self.m_zbem.m_zbHandle.queryGetDevice(), indent=2, default=lambda o: o.__dict__) ;
    def __cmdPrint(self, argv) :
        try :
            self.commandPrint[argv[0]](None if len(argv)==1 else argv[1:]) ;
        except KeyError :
            ERR('Unknown Print Command, %s' % ' '.join(argv)) ;
    def cliMain(self) :
        DBG('Start of cliMain') ;
        while self.m_fgRun :
            cmd = raw_input(Cli.PROMPT).strip().split() ;
            # DBG('CMD%s' % cmd)
            if cmd == [] :
                continue ;
            try :
                self.command[cmd[0]](None if len(cmd)==1 else cmd[1:]) ;
            except KeyError :
                ERR('Unknown Command, %s' % cmd)
        DBG('End of cliMain') ;
