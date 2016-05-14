

MfgId = 0x110A ;

def doInit(node) :
    print 'Init : %s' % __file__ ;
    print 'EUI : %s' % node.getEUI() ;
    return [] ;

def doConfig(node) :
    print 'Configuration : %s' % __file__ ;
    msgs = [] ;
    # if node.hasCluster(0x1, 0x500) :
    #     msgIAS  = 'zcl global write 0x500 0x10 0xf0 {COEUI}\n' ;
    #     msgIAS += 'send %s 0x1 0x1\n' % hex(node.getId()) ;
    #     msgs.append(msgIAS) ;

    # msgPower  = 'zdo bind %s 0x1 0x1 0x1 {%s} {COEUI}\n' % (hex(node.getId()), node.getSwapEUI(' ')) ;
    msgPower  = 'zdo bind %s 0x1 0x1 0x1 {%s} {COEUI}\n' % (hex(node.getId()), node.getEUI()) ;
    msgPower += 'zcl global send-me-a-report 0x1 0x20 0x20 %d %d {%02X}\n' % (60, 60, 1) ; # min, max, changable
    msgPower += 'send %s 1 1' % (hex(node.getId())) ;
    msgs.append(msgPower) ;

    return msgs ;

def doRefresh(node) :
    print 'Refresh : %s' % __file__ ;
    return [] ;
