#!/usr/bin/python

from lpiot.database import PiotDB ;
from lpiot.zbember import ZbEmber ;
from lpiot.cli import Cli ;
from lpiot.ipcpacket import IPProcHandler ;


db        = PiotDB() ;
ippHandle = IPProcHandler() ;
zbem      = ZbEmber(ippHandle, db, 'zbember -n1 -p/dev/ttyUSB0') ;
cli       = Cli(ippHandle, zbem) ;
