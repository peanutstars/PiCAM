#!/usr/bin/env python

import asynchat
import asyncore
import socket


_ipc_room = {}
IPC_TERMINATOR = '\n'
IPC_QUIT = 'ipcquit'

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
        for handler in _ipc_room.itervalues():
            if hasattr(handler, 'push'):
                handler.push(msg + IPC_TERMINATOR)
        if msg == IPC_QUIT :
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

class IPCClient(asynchat.async_chat) :
    def __init__(self, host, port=None) :
        asynchat.async_chat.__init__(self) ;
        if isinstance(port, int) :
            self.create_socket(socket.AF_INET, socket.SOCK_STREAM) ;
            self.connect((host,port)) ;
        else :
            self.create_socket(socket.AF_UNIX, socket.SOCK_STREAM) ;
            self.connect(host) ;
        self.set_terminator(IPC_TERMINATOR) ;
        self.buffer = [] ;
        self.run = True ;
    def collect_incoming_data(self, data) :
        self.buffer.append(data) ;
    def found_terminator(self) :
        msg = ''.join(self.buffer) ;
        self.buffer = [] ;
        print 'Received:', msg ;
        if msg == IPC_QUIT :
            self.close() ;
            self.run = False ;

if __name__ == '__main__':
    import sys ;
    import threading ;

    ipcHost = 'localhost' ;
    ipcPort = None ; # 50001 ;

    def doServer() :
        server = IPCServer(ipcHost, ipcPort) ;
        try :
            asyncore.loop(map=_ipc_room) ;
        except asyncore.ExitNow, e :
            print e ;

    def doClient(fgTerminator) :
        client = IPCClient(ipcHost, ipcPort) ;
        comm = threading.Thread(target=asyncore.loop) ;
        comm.daemon = True ;
        comm.start() ;

        while client.run :
            msg = raw_input('> ').strip() ;
            if fgTerminator :
                client.push(msg + IPC_TERMINATOR) ;
            else :
                client.push(IPC_TERMINATOR if msg == 'enter' else msg) ;

    def main(mode) :
        if mode[0] == 'server' :
            doServer() ;
        elif mode[0] == 'client' :
            doClient(True if len(mode) == 1 else False) ;

    if len(sys.argv) == 1 :
        print 'usage : %s <server|client> [test]' % sys.argv[0] ;
        raise SystemExit ;

    main(sys.argv[1:])
