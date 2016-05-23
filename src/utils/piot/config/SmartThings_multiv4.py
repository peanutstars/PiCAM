

MfgId = 0x110A ;


def doInit(node) :
    print 'Init : %s' % __file__ ;
    print 'EUI : %s' % node.getEUI() ;
    return [] ;

def doConfig(node) :
    print 'Configuration : %s' % __file__ ;
    msgs = [] ;

    msgPower  = 'zdo bind %s 0x1 0x1 0x1 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
    msgPower += 'zcl global send-me-a-report 0x1 0x20 0x20 %d %d {%02X}\n' % (60, 10800, 1) ; # min, max, changable
    msgPower += 'send %s 1 1' % (hex(node.getId())) ;
    msgs.append(msgPower) ;

    msgTemp   = 'zdo bind %s 0x1 0x1 0x402 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
    msgTemp  += 'zcl global send-me-a-report 0x402 0x0 0x29 %d %d {%s}\n' % (60, 600, node.intToString(10, 4)) ; # min, max, changable
    msgTemp  += 'send %s 1 1' % (hex(node.getId())) ;
    msgs.append(msgTemp) ;

    msgAccel  = 'zdo bind %s 0x1 0x1 0xFC02 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
    msgAccel += 'zcl mfg-code %s\n' % hex(MfgId) ;
    msgAccel += 'zcl global send-me-a-report 0xFC02 0x10 0x18 %d %d {%s}\n' % (10, 3600, node.intToString(1, 2)) ; # min, max, changable
    msgAccel += 'send %s 1 1\n' % (hex(node.getId())) ;
    msgAccel += 'zcl mfg-code %s\n' % hex(MfgId) ;
    msgAccel += 'zcl global send-me-a-report 0xFC02 0x12 0x29 %d %d {%s}\n' % (1, 3600, node.intToString(1, 4)) ; # min, max, changable
    msgAccel += 'send %s 1 1\n' % (hex(node.getId())) ;
    msgAccel += 'zcl mfg-code %s\n' % hex(MfgId) ;
    msgAccel += 'zcl global send-me-a-report 0xFC02 0x13 0x29 %d %d {%s}\n' % (1, 3600, node.intToString(1, 4)) ; # min, max, changable
    msgAccel += 'send %s 1 1\n' % (hex(node.getId())) ;
    msgAccel += 'zcl mfg-code %s\n' % hex(MfgId) ;
    msgAccel += 'zcl global send-me-a-report 0xFC02 0x14 0x29 %d %d {%s}\n' % (1, 3600, node.intToString(1, 4)) ; # min, max, changable
    msgAccel += 'send %s 1 1' % (hex(node.getId())) ;
    msgs.append(msgAccel) ;

    return msgs ;

def doRefresh(node) :
    print 'Refresh : %s' % __file__ ;
    msgs = [] ;

    if node.hasCluster(0x1, 0x500) :
        # Read IAS Zone Attributes
        msgIAS  = 'zcl global read 0x500 0x0\n' ;
        msgIAS += 'send %s 0x1 0x1\n' % hex(node.getId()) ;
        msgIAS += 'zcl global read 0x500 0x2\n' ;
        msgIAS += 'send %s 0x1 0x1\n' % hex(node.getId()) ;
        msgIAS += 'zcl global read 0x500 0x11\n' ;
        msgIAS += 'send %s 0x1 0x1\n' % hex(node.getId()) ;
        msgs.append(msgIAS) ;

    return msgs ;
