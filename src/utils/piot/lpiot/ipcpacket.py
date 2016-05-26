
import os ;
import threading ;
from lpiot.sockuid import UIDDaemon, UIDClient ;
from lpiot.sockipc import IPCDaemon, IPCClient ;
from libps.psDebug import CliColor, DBG, ERR ;


class PacketDaemon :
    BASE_ADDRESS = '/tmp/picam'
    UID_ADDRESS = BASE_ADDRESS + '/socket_uid'
    UID_PORT = None ;
    UID_QUIT = 'uidquit\n' ;
    IPC_ADDRESS = BASE_ADDRESS + '/socket_ipc'
    IPC_PORT = None ;
    IPC_QUIT = 'ipcquit' ;
    TERMINATOR = '\n' ;
    def __init__(self, fgForce=False) :
        if fgForce :
            if not os.path.exists(PacketDaemon.BASE_ADDRESS) :
                os.mkdir(PacketDaemon.BASE_ADDRESS) ;
            if os.path.exists(PacketDaemon.UID_ADDRESS) :
                os.remove(PacketDaemon.UID_ADDRESS) ;
            if os.path.exists(PacketDaemon.IPC_ADDRESS) :
                os.remove(PacketDaemon.IPC_ADDRESS) ;
    def start(self) :
        UIDDaemon(PacketDaemon.UID_ADDRESS, PacketDaemon.UID_PORT) ;
        IPCDaemon(PacketDaemon.IPC_ADDRESS, PacketDaemon.IPC_PORT) ;
    def stop(self) :
        IPCClient(PacketDaemon.IPC_ADDRESS, PacketDaemon.IPC_PORT).sendMsg(PacketDaemon.IPC_QUIT) ;
        UIDClient(PacketDaemon.UID_ADDRESS, PacketDaemon.UID_PORT).getUID(PacketDaemon.UID_QUIT) ;

NOTIFY       = 'N' ;
REQUEST      = 'R' ;
REPLY        = 'r' ;
SEPARATOR    = '|' ;
SIZE_SUBTYPE = 6

class PacketHandler :
    # Packet Header :     XXXXXXXX(8)|Type(1)|SubType(6)|Payload
    # NOTIFY_SENSOR_HEAD  00000000|N|SENSOR|
    # REQUEST_DB_HEAD     12345678|R|DB    |
    # REPLY_DB_HEAD       12345678|r|DB    |
    def __init__(self, cbFunc=None) :
        self.m_ipc       = IPCClient(PacketDaemon.IPC_ADDRESS, PacketDaemon.IPC_PORT, self.__receivedPacket) ;
        # Callback Format : ID, SubType, Playload
        self.m_callback  = cbFunc ;
        self.m_queryPool = {} ;
        self.m_lock = threading.Lock() ;
    def getUID(self) :
        return UIDClient(PacketDaemon.UID_ADDRESS, PacketDaemon.UID_PORT).getUID(PacketDaemon.TERMINATOR) ;
    def __receivedPacket(self, msg) :
        '''
        receivedPacket() is called by IPCClient thread.
        '''
        field     = msg[0:18].split('|') ;
        print '@@', field
        if len(field) == 4 :
            fieldId   = field[0] ;
            fieldType = field[1] ;
            fieldSub  = field[2] ;
            if hasattr(self.m_callback, '__call__') :
                payload = msg[18:] ;
                if int(fieldId,16) != 0 :
                    if fieldType == REPLY :
                        with self.m_lock :
                            try :
                                self.m_queryPool[fieldId][1] = payload ;
                                self.m_queryPool[fieldId][0].set() ;
                            except KeyError :
                                # Maybe, it is not mine.
                                pass ;
                    elif fieldType == REQUEST :
                        self.m_callback(fieldId, fieldSub, payload) ;
                else :
                    self.m_callback(fieldId, fieldSub, payload) ;
    def sendNotify(self, subType, payload) :
        assert (len(subType) == SIZE_SUBTYPE), 'subType length is not 6.'
        self.m_ipc.sendMsg('00000000'+SEPARATOR+NOTIFY+SEPARATOR + subType +SEPARATOR+ payload) ;
    def sendQueryRequest(self, subType, payload, timeout=0) :
        assert (len(subType) == SIZE_SUBTYPE), 'subType length is not 6.'
        event = threading.Event() ;
        fieldId = self.getUID() ;
        self.m_ipc.sendMsg(fieldId+SEPARATOR+REQUEST+SEPARATOR + subType +SEPARATOR+ payload) ;
        with self.m_lock :
            self.m_queryPool[fieldId] = [event, None] ;
        event.wait(None if timeout==0 else timeout) ;
        with self.m_lock :
            reply = self.m_queryPool.pop(fieldId) ;
        if reply[1] == None :
            DBG('Query Timeout[%d] - %s, %s' % (timeout, subType, payload))
        return reply[1] ;
    def sendQueryReply(self, fieldId, subType, payload) :
        assert (len(subType) == SIZE_SUBTYPE), 'subType length is not 6.'
        self.m_ipc.sendMsg(fieldId+SEPARATOR+REPLY+SEPARATOR + subType +SEPARATOR+ payload) ;

if __name__ == '__main__':
    import sys ;
    class Handler :
        def __init__(self, fgDoReply=False) :
            self.m_handle = PacketHandler(self.onReceived) ;
            self.m_fgDoReply = fgDoReply ;
        def onReceived(self, packetId, subType, payload) :
            if int(packetId,16) == 0 :
                print 'Notify [%s] %s' % (subType, payload) ;
            elif int(packetId,16) != 0 and self.m_fgDoReply :
                print 'Reply[%s:%s] %s' % (packetId, subType, payload) ;
                self.m_handle.sendQueryReply(packetId, subType, 'Reply') ;
        def doRequest(self, timeout=0) :
            return self.m_handle.sendQueryRequest('SUBTYP', 'Request', timeout) ;
        def doNotify(self) :
            self.m_handle.sendNotify('subtyp', 'Notify') ;

    if len(sys.argv) == 1 :
        print 'usage : %s <notify|request|reply|quit> [<timeout> <server>]' ;
        raise SystemExit ;
    if 'server' in sys.argv :
        PacketDaemon(True).start() ;
    if sys.argv[1] == 'quit' :
        PacketDaemon(False).stop() ;
        raise SystemExit ;

    h = Handler(True if sys.argv[1] == 'reply' else False) ;
    if sys.argv[1] == 'request' :
        try :
            timeout = int(sys.argv[2]) ;
        except ValueError :
            timeout = 0 ;
        except IndexError :
            timeout = 0 ;
        rv = h.doRequest(timeout) ;
        DBG('Replied : %s' % rv) ;
    if sys.argv[1] == 'notify' :
        h.doNotify() ;
