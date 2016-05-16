

def doInit(node) :
    print 'Init : %s' % __file__ ;
    print 'EUI : %s' % node.getEUI() ;
    return [] ;

def doConfig(node) :
    print 'Configuration : %s' % __file__ ;
    msgs = [] ;
    if node.hasCluster(0x1, 0x500) :
        msgIAS  = 'zcl global write 0x500 0x10 0xf0 {IASCIE}\n' ;
        msgIAS += 'send %s 0x1 0x1\n' % hex(node.getId()) ;
        msgs.append(msgIAS) ;

    # for battery
    if node.hasCluster(0x1, 0x1) :
        msgPower  = 'zdo bind %s 0x1 0x1 0x1 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
        msgPower += 'zcl global send-me-a-report 0x1 0x20 0x20 %d %d {%02X}\n' % (60, 10800, 1) ; # min, max, changable - 0.1 voltage
        msgPower += 'send %s 1 1' % (hex(node.getId())) ;
        msgs.append(msgPower) ;

    # for temperature
    if node.hasCluster(0x1, 0x402) :
        msgTemp   = 'zdo bind %s 0x1 0x1 0x402 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
        msgTemp  += 'zcl global send-me-a-report 0x402 0x0 0x29 %d %d {%s}\n' % (60, 3600, node.intToString(10, 4)) ; # min, max, changable - 0.1 degree
        msgTemp  += 'send %s 1 1' % (hex(node.getId())) ;
        msgs.append(msgTemp) ;

    # for humidity
    if node.hasCluster(0x1, 0x405) :
        msgHum   = 'zdo bind %s 0x1 0x1 0x402 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
        msgHum  += 'zcl global send-me-a-report 0x405 0x0 0x21 %d %d {%s}\n' % (60, 3600, node.intToString(10, 4)) ; # min, max, changable - 1 percent
        msgHum  += 'send %s 1 1' % (hex(node.getId())) ;
        msgs.append(msgHum) ;

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
