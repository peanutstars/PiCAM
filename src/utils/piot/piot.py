#!/usr/bin/env python

from lpiot.database import PiotDB ;
from lpiot.zbember import ZbEmber ;
from lpiot.cli import Cli ;


zbem = ZbEmber('zbember -n1 -p/dev/ttyUSB0') ;
cli = Cli(zbem) ;
