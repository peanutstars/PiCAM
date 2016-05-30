
import os ;
import socket ;
import threading ;
import time ;
from lpiot.sockuid import UIDDaemon, UIDClient ;
from lpiot.sockipc import IPCDaemon, IPCClient ;
from libps.psDebug import CliColor, DBG, ERR ;


class IPMeta :
    '''
    IP Packet Infomation.
    '''
    BASE_ADDRESS = '/tmp/picam'
    UID_ADDRESS = BASE_ADDRESS + '/socket_uid'
    UID_PORT = None ;
    UID_QUIT = 'uidquit\n' ;
    IPC_ADDRESS = BASE_ADDRESS + '/socket_ipc'
    IPC_PORT = None ;
    IPC_QUIT = 'ipcquit' ;
    TERMINATOR = '\n' ;

    NOTIFY       = 'N' ;
    REQUEST      = 'R' ;
    REPLY        = 'r' ;
    SEPARATOR    = '|' ;
    S_NOTIFY_S   = '|N|' ;
    S_REQUEST_S  = '|R|' ;
    S_REPLY_S    = '|r|' ;
    SIZE_SUBTYPE = 6 ;

    SUBTYPE_SYSTEM = 'SYSTEM' ;
    SUBTYPE_SENSOR = 'SENSOR' ;
    SUBTYPE_DB     = 'D    B' ;


class IPDaemon :
    '''
    IPC Packet Deamon
    '''
    def __init__(self, fgForce=False) :
        if fgForce :
            if not os.path.exists(IPMeta.BASE_ADDRESS) :
                os.mkdir(IPMeta.BASE_ADDRESS) ;
            if IPMeta.UID_PORT == None and os.path.exists(IPMeta.UID_ADDRESS) :
                os.remove(IPMeta.UID_ADDRESS) ;
            if IPMeta.IPC_PORT == None and os.path.exists(IPMeta.IPC_ADDRESS) :
                os.remove(IPMeta.IPC_ADDRESS) ;
    def start(self) :
        UIDDaemon(IPMeta.UID_ADDRESS, IPMeta.UID_PORT) ;
        IPCDaemon(IPMeta.IPC_ADDRESS, IPMeta.IPC_PORT) ;
        time.sleep(0.3) ;
    def stop(self) :
        time.sleep(0.3) ;
        IPCClient(IPMeta.IPC_ADDRESS, IPMeta.IPC_PORT).sendMsg(IPMeta.IPC_QUIT) ;
        UIDClient(IPMeta.UID_ADDRESS, IPMeta.UID_PORT).getUID(IPMeta.UID_QUIT) ;



class IPHandler(IPCClient) :
    '''
    IPC Packet Handler for communication between the client.
    '''
    # Packet Header :     XXXXXXXX(8)|Type(1)|SubType(6)|Payload
    # NOTIFY_SENSOR_HEAD  00000000|N|SENSOR|
    # REQUEST_DB_HEAD     12345678|R|DB    |
    # REPLY_DB_HEAD       12345678|r|DB    |
    # Callback Format : cbFunc(ID, SubType, Playload)
    def __init__(self, cbFunc=None) :
        IPCClient.__init__(self, IPMeta.IPC_ADDRESS, IPMeta.IPC_PORT, self.__receivedPacket) ;
        self.m_callback  = cbFunc ;
        self.m_queryPool = {} ;
        self.m_lock = threading.Lock() ;
    def __getUID(self) :
        return UIDClient(IPMeta.UID_ADDRESS, IPMeta.UID_PORT).getUID(IPMeta.TERMINATOR) ;
    def __receivedPacket(self, msg) :
        '''
        receivedPacket() is called by IPCClient thread.
        '''
        field     = msg[0:18].split('|') ;
        # print '@@', field
        if len(field) == 4 :
            fieldId   = field[0] ;
            fieldType = field[1] ;
            fieldSub  = field[2] ;
            payload = msg[18:] ;
            if int(fieldId,16) != 0 :
                if fieldType == IPMeta.REPLY :
                    # Caller of Request is only recevied Reply.
                    with self.m_lock :
                        try :
                            self.m_queryPool[fieldId][1] = payload ;
                            self.m_queryPool[fieldId][0].set() ;
                        except KeyError :
                            # Maybe, it is not mine.
                            pass ;
                elif fieldType == IPMeta.REQUEST :
                    if hasattr(self.m_callback, '__call__') :
                        self.m_callback(fieldId, fieldSub, payload) ;
            else :
                # Notify
                if hasattr(self.m_callback, '__call__') :
                    self.m_callback(fieldId, fieldSub, payload) ;
        elif msg == IPMeta.IPC_QUIT :
            DBG('Quit a IPC Client') ;
            with self.m_lock :
                for key in self.m_queryPool :
                    self.m_queryPool[key][0].set() ;

    def sendNotify(self, subType, payload) :
        assert (len(subType) == IPMeta.SIZE_SUBTYPE), 'subType length is not 6.'
        self.sendMsg('00000000'+IPMeta.S_NOTIFY_S + subType +IPMeta.SEPARATOR+ payload) ;
    def sendQueryRequest(self, subType, payload, timeout=0) :
        assert (len(subType) == IPMeta.SIZE_SUBTYPE), 'subType length is not 6.'
        event = threading.Event() ;
        try :
            fieldId = self.__getUID() ;
        except socket.error, e :
            DBG('Have Socket Errors : %s' % e) ;
            self.stop() ;
            return None ;
        self.sendMsg(fieldId+IPMeta.S_REQUEST_S + subType +IPMeta.SEPARATOR+ payload) ;
        with self.m_lock :
            self.m_queryPool[fieldId] = [event, None] ;
        event.wait(None if timeout==0 else timeout) ;
        with self.m_lock :
            reply = self.m_queryPool.pop(fieldId) ;
        if reply[1] == None :
            DBG('Query Timeout[%d] - %s, %s' % (timeout, subType, payload))
        return reply[1] ;
    def sendQueryReply(self, fieldId, subType, payload) :
        assert (len(subType) == IPMeta.SIZE_SUBTYPE), 'subType length is not 6.'
        self.sendMsg(fieldId+IPMeta.S_REPLY_R + subType +IPMeta.SEPARATOR+ payload) ;

class IPProcHandler(IPHandler) :
    def __init__(self) :
        IPHandler.__init__(self, self.onReceivedPacket) ;
        # self.m_lock = threading.Lock() ;
        self.m_funcPool = [] ;

    def onReceivedPacket(self, ipId, ipSType, ipPayload) :
        with self.m_lock :
            for st, cb in self.m_funcPool :
                if st == ipSType and hasattr(cb, '__call__') :
                    cb(ipId, ipSType, ipPayload) ;

    def register(self, subType, cbFunc) :
        with self.m_lock :
            self.m_funcPool.append([subType, cbFunc]) ;
    def unregister(self, subType, cbFunc) :
        with self.m_lock :
            self.m_funcPool = [ x for x in self.m_funcPool if not x == [subType, cbFunc]] ;


if __name__ == '__main__':
    import sys ;

    class Handler(IPHandler) :
        def __init__(self, second, fgReply=False) :
            IPHandler.__init__(self, self.onReceived) ;
            self.m_fgReply = fgReply ;
            self.m_second = second ;
        def onReceived(self, packetId, subType, payload) :
            if int(packetId,16) == 0 :
                print 'Notify [%s] %s' % (subType, payload) ;
            elif int(packetId,16) != 0 and self.m_fgReply :
                # Send a reply.
                print 'Received [%s:%s] %s' % (packetId, subType, payload) ;
                if self.m_second != 0 :
                    time.sleep(self.m_second) ;
                    payload = 'Reply after %f seconds' % float(self.m_second) ;
                else :
                    payload = 'Reply immediately'
                self.sendQueryReply(packetId, subType, payload) ;
        def doRequest(self, timeout=0) :
            return self.sendQueryRequest('SUBTYP', 'Request', timeout) ;
        def doNotify(self, msg='') :
            self.sendNotify('subtyp', 'Notify %s' % msg) ;
        def doNotifyQuit(self) :
            self.sendNotify(IPMeta.SUBTYPE_SYSTEM, 'quit') ;

    if len(sys.argv) == 1 :
        print 'usage : %s <notify|request|reply|quit> [<timesec> <server> <loop>]' ;
        raise SystemExit ;

    fgServer = 'server' in sys.argv ;
    fgLoop = 'loop' in sys.argv ;

    if fgServer :
        IPDaemon(True).start() ;
    if sys.argv[1] == 'quit' :
        IPDaemon(False).stop() ;
        raise SystemExit ;

    # Make time parameter
    try :
        timesec = float(sys.argv[2]) ;
    except ValueError :
        timesec = 0 ;
    except IndexError :
        timesec = 0 ;

    if fgServer and fgLoop :
        Handler(timesec, False) ;
    else :
        fgReply = False ;
        if 'reply' in sys.argv[1] :
            fgReply = True ;
            fgLoop = True ;

        h = Handler(timesec, fgReply) ;
        if sys.argv[1] == 'request' :
            rv = h.doRequest(timesec) ;
            while fgLoop and h.isAlive():
                DBG('Replied : %s' % rv) ;
                time.sleep(timesec) ;
                rv = h.doRequest(timesec) ;

        if sys.argv[1] == 'notify' :
            if sys.argv[2] == 'quit' :
                h.doNotifyQuit() ;
            else :
                h.doNotify() ;
                while fgLoop and h.isAlive():
                    time.sleep(timesec) ;
                    h.doNotify(str(timesec)) ;

        if not fgLoop and not fgReply:
            h.stop() ;
