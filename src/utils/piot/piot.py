#!/usr/bin/env python

from lpiot.database import PiotDB ;

db = PiotDB() ;

db.zbAddDevice('FF0000', 0x64, 0) ;
db.zbAddDevice('FF0001', 0x64, 0) ;
db.zbAddDevice('FF0002', 0x64, 100) ;

db.zbAddDevice('FF0001', 0x100, 0) ;
db.zbAddDevice('FF0001', 0x200, 0) ;
db.zbAddDevice('FF0002', 0x300, 0) ;

db.zbDelDevice('000000') ;

db.dumpTable(['zb_device', 'zb_cl_attr']) ;
