
import asynchat ;
import asyncore ;
import select ;
import socket ;
import threading ;
from libps.psDebug import CliColor, DBG, ERR ;

_ipc_room = {} ;
IPC_TERMINATOR = '\n' ;
IPC_QUIT = 'ipcquit' ;

class IPCHandler(asynchat.async_chat):
    def __init__(self, sock):
        asynchat.async_chat.__init__(self, sock=sock, map=_ipc_room)
        self.set_terminator(IPC_TERMINATOR)
        self.buffer = []
    def collect_incoming_data(self, data):
        self.buffer.append(data)
    def found_terminator(self):
        msg = ''.join(self.buffer)
        self.buffer = []
        # DBG('@S %s' % _ipc_room) ;
        for handler in _ipc_room.itervalues():
            if handler == self :
                # Skip a push operation in case oneself.
                continue ;
            if hasattr(handler, 'push'):
                handler.push(msg + IPC_TERMINATOR)
        if msg == IPC_QUIT :
            self.push(msg + IPC_TERMINATOR) ;
            raise asyncore.ExitNow('IPC Server is quitting') ;

class IPCServer(asyncore.dispatcher):
    def __init__(self, host, port=None):
        asyncore.dispatcher.__init__(self, map=_ipc_room)
        if isinstance(port, int) :
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
            self.bind((host, port))
        else :
            self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM) ;
            self.bind(host) ;
        self.listen(5)
    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            handler = IPCHandler(sock)

class IPCDaemon(threading.Thread) :
    def __init__(self, host, port) :
        threading.Thread.__init__(self) ;
        self.server = IPCServer(host, port) ;
        self.start() ;
    def run(self) :
        try :
            asyncore.loop(map=_ipc_room) ;
        except asyncore.ExitNow, e :
            DBG(e) ;

class IPCClient(threading.Thread) :
    def __init__(self, host, port=None, cbfunc=None) :
        threading.Thread.__init__(self) ;
        if isinstance(port, int) :
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) ;
            self.sock.connect((host,port)) ;
        else :
            self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) ;
            self.sock.connect(host) ;
        self.fgAlive = True ;
        self.buffer = [] ;
        self.cbfunc = cbfunc ;
        self.start() ;
    def __doPollIn(self) :
        rv = False ;
        tmp = self.sock.recv(1) ;
        if tmp != IPC_TERMINATOR :
            self.buffer.append(tmp) ;
        else :
            msg = ''.join(self.buffer).strip() ;
            self.buffer = [] ;
            if self.cbfunc :
                assert(hasattr(self.cbfunc, '__call__')) ;
                self.cbfunc(msg) ;
            if msg == IPC_QUIT :
                rv = True ;
        return rv ;
    def run(self) :
        poll = select.poll() ;
        poll.register(self.sock, select.POLLIN | select.POLLHUP) ;
        pollc = 1 ;
        try :
            sockFd = self.sock.fileno() ;
            while self.fgAlive and pollc > 0 :
                fgUnregister = False ;
                events = poll.poll(1) ;
                for event in events :
                    (rfd, event) = event ;
                    if event & select.POLLIN :
                        if rfd == sockFd :
                            fgUnregister = self.__doPollIn() ;
                    if fgUnregister or event & select.POLLHUP :
                        poll.unregister(rfd) ;
                        pollc -= 1 ;
            if pollc > 0 :
                poll.unregister(sockFd) ;
                pollc -= 1 ;
        except :
            DBG('Have Socket Errors') ;
            self.stop() ;
        finally :
            del poll ;
            self.sock.close() ;
    def stop(self) :
        self.fgAlive = False ;
    def sendMsg(self, msg) :
        try :
            self.sock.sendall(msg + IPC_TERMINATOR) ;
        except socket.error, e :
            DBG('Have Socket Errors : %s' % e) ;
            self.stop() ;
    def isAlive(self) :
        return self.fgAlive ;



# class IPCClient(asynchat.async_chat, threading.Thread) :
#     def __init__(self, host, port=None, cbfunc=None) :
#         asynchat.async_chat.__init__(self) ;
#         threading.Thread.__init__(self) ;
#         if isinstance(port, int) :
#             self.create_socket(socket.AF_INET, socket.SOCK_STREAM) ;
#             self.connect((host,port)) ;
#         else :
#             self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM) ;
#             self.connect(host) ;
#         self.set_terminator(IPC_TERMINATOR) ;
#         self.buffer = [] ;
#         self.cbfunc = cbfunc ;
#         self.fgAlive = True ;
#         self.start() ;
#     def collect_incoming_data(self, data) :
#         self.buffer.append(data) ;
#     def found_terminator(self) :
#         msg = ''.join(self.buffer).strip() ;
#         self.buffer = [] ;
#         if len(msg) > 0 and self.cbfunc and hasattr(self.cbfunc, '__call__'):
#             print '#', msg ;
#             self.cbfunc(msg) ;
#         if msg == IPC_QUIT :
#             self.close() ;
#             self.fgAlive = False ;
#             raise asyncore.ExitNow('IPC Client is quitting') ;
#     def run(self) :
#         while self.fgAlive :
#             try :
#                 asyncore.loop(1, count=1) ;
#             except asyncore.ExitNow, e :
#                 DBG(e) ;
#     def stop(self) :
#         self.close() ;
#         self.fgAlive = False ;
#
#     def sendMsg(self, msg) :
#         self.push(msg + IPC_TERMINATOR) ;

if __name__ == '__main__':
    import sys ;

    ipcHost = 'localhost' ;
    ipcPort = None ; # 50001 ;

    def receivedMsg(msg) :
        if msg == IPC_QUIT :
            return ;
        print ('R: %s' % msg) ;

    def doServer() :
        IPCDaemon(ipcHost, ipcPort) ;

    def doClient() :
        client = IPCClient(ipcHost, ipcPort, receivedMsg) ;
        while client.fgAlive :
            msg = raw_input('> ').strip() ;
            client.sendMsg(msg) ;

    def main(mode) :
        if mode[0] == 'server' :
            doServer() ;
        elif mode[0] == 'client' :
            doClient() ;

    if len(sys.argv) == 1 :
        DBG('usage : %s <server|client>' % sys.argv[0]) ;
        raise SystemExit ;

    main(sys.argv[1:])
