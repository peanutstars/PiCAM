
from lpiot.sockuid import UIDDaemon, UIDClient ;
from lpiot.sockpid import IPCDaemon, IPCClient ;
from libps.psDebug import CliColor, DBG, ERR ;


class PacketDaemon :
    UID_ADDRESS = '/tmp/picam/socket_uid'
    UID_PORT = None ;
    UID_QUIT = 'uidquit' ;
    IPC_ADDRESS = '/tmp/picam/socket_ipc'
    IPC_PORT = None ;
    IPC_QUIT = 'ipcquit' ;
    TERMINATOR = '\n' ;
    def __init__(self) :
        pass ;
    def start(self) :
        UIDDaemon(UID_ADDRESS, UID_PORT) ;
        IPCDaemon(IPC_ADDRESS, IPC_PORT) ;
    def stop(self) :
        UIDClient(UID_ADDRESS, UID_PORT).getUID(UID_QUIT) ;
        IPCClient(IPC_ADDRESS, IPC_PORT).sendMsg(PID_QUIT) ;

class PacketHandler :
    def __init__(self) :
        self.m_ipc = IPCClient(IPC_ADDRESS, IPC_PORT, self.receivedPacket) ;
    def getUID(self) :
        return UIDClient(PacketDaemon.UID_ADDRESS, PacketDaemon.UID_PORT).getUID(PacketDaemon.TERMINATOR) ;
    def receivedPacket(self, msg) :
        pass ;
    def sendPacket(self, msg) :
        self.m_ipc.sendMsg(msg) ;
