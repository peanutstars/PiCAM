
import asyncore ;
import socket ;
import threading ;
from libps.psDebug import CliColor, DBG, ERR ;

UID_QUIT = 'uidquit'
UID_TOKEN = '\n'

uidCount = 0 ;
uidLock = threading.Lock() ;

class UIDServer(asyncore.dispatcher) :
    def __init__(self, host, port) :
        asyncore.dispatcher.__init__(self) ;
        if isinstance(port, int) :
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM) ;
            self.bind((host, port)) ;
        else :
            self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM) ;
            self.bind(host) ;
        self.listen(1) ;
    def handle_accept(self) :
        sock, address = self.accept() ;
        UIDHandler(sock) ;

class UIDHandler(asyncore.dispatcher_with_send) :
    def handle_read(self) :
        buffer = self.recv(16) ;
        if buffer == UID_TOKEN :
            self.out_buffer = self.getUID() ;
        elif buffer == UID_QUIT :
            raise asyncore.ExitNow('UID Server is quitting') ;
        if not self.out_buffer :
            self.close() ;
    def getUID(self) :
        global uidCount ;
        with uidLock :
            uidCount += 1 ;
            uidCount &= 0xFFFFFFFF ;
            if uidCount == 0 :
                uidCount = 1 ;
            return '%08X' % uidCount ;

class UIDDaemon(threading.Thread) :
    def __init__(self, host, port) :
        threading.Thread.__init__(self) ;
        self.server = UIDServer(host, port) ;
        self.start() ;
    def run(self) :
        try :
            asyncore.loop() ;
        except asyncore.ExitNow, e :
            DBG(e) ;

class UIDClient :
    def __init__(self, host, port) :
        if isinstance(port, int) :
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ;
            self.sock.connect((host,port)) ;
        else :
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) ;
            self.sock.connect(host) ;
    def getUID(self, msg=UID_TOKEN) :
        try :
            self.sock.sendall(msg) ;
            uid = self.sock.recv(16) ;
        finally :
            self.sock.close() ;
        return uid ;


if __name__ == '__main__':
    import sys ;
    uidHost = 'uidport' ;
    uidPort = None ;

    def main(argv) :
        if argv[0] == 'server' :
            UIDDaemon(uidHost, uidPort) ;
        elif argv[0] == 'client' :
            DBG(UIDClient(uidHost, uidPort).getUID('\n' if len(argv) == 1 else argv[1])) ;

    if len(sys.argv) == 1 :
        DBG('usage : %s <server|client> [message]' % sys.argv[0]) ;
        raise SystemExit ;

    main(sys.argv[1:]) ;
