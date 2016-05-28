#!/usr/bin/python

from lpiot.database import PiotDB ;
from lpiot.zbember import ZbEmber ;
from lpiot.cli import Cli ;
from lpiot.ipcpacket import IPHandler ;


db       = PiotDB() ;
ipHandle = IPHandler() ;
zbem     = ZbEmber(ipHandle, db, 'zbember -n1 -p/dev/ttyUSB0') ;
cli      = Cli(ipHandle, zbem) ;
