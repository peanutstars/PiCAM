#!/usr/bin/python

from lpiot.zbember import ZbEmber ;
from lpiot.cli import Cli ;
from lpiot.ipcpacket import IPProcHandler ;


ippHandle = IPProcHandler() ;
zbem      = ZbEmber(ippHandle, 'zbember -n1 -p/dev/ttyUSB0') ;
cli       = Cli(ippHandle, zbem) ;
