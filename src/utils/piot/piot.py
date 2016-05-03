#!/usr/bin/env python

from lpiot.database import PiotDB ;
from lpiot.zbember import ZbEmber ;
from lpiot.cli import Cli ;

db = PiotDB() ;
zbem = ZbEmber(db, 'zbember -n1 -p/dev/ttyUSB0') ;
cli = Cli(zbem) ;
