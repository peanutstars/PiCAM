#!/usr/bin/python

from lpiot.ipcpacket import IPDaemon, IPProcHandler ;
from lpiot.dbmanager import DBManager ;

IPDaemon(True).start() ;

ippHandle = IPProcHandler() ;
dbm       = DBManager(ippHandle) ;
