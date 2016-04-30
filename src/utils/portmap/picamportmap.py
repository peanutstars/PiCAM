#!/usr/bin/env python

import miniupnpc ;
import sys ;

from libps.psDebug import DBG, ERR ;

class Upnpc :
    def __init__(self) :
        self.m_portmap = [] ;
        self.m_ipaddr = None ;
        self.m_handle = miniupnpc.UPnP(discoverdelay=200, localport=0, minissdpdsocket=None, multicastif=None) ;
        self.doQueryGetPortmap() ;
    def __getHandle(self) :
        return self.m_handle ;
    def doQueryGetPortmap(self) :
        self.m_portmap = [] ;
        u = self.__getHandle() ;
        if u.discover() > 0 :
            try:
                u.selectigd() ;
            except Exception, e:
                ERR('Exception : %s', e) ;
            self.m_ipaddr = u.lanaddr ;
            i = 0 ;
            while True :
            	p = u.getgenericportmapping(i) ;
            	if p==None :
            		break ;
            	#(port, proto, (ihost,iport), desc, c, d, e) = p ;
                self.m_portmap.append(p) ;
            	i = i + 1 ;
    def doQueryAddPortmap(self, port, proto, innerport, name) :
        self.__getHandle().addportmapping(port, proto, self.m_ipaddr, innerport, name, '') ;
    def doQueryDelPortmap(self, port, proto) :
        self.__getHandle().deleteportmapping(port, proto) ;
    def dumpPortmap(self, query=False) :
        if query :
            self.doQueryGetPortmap() ;
        print('Port Lists ...') ;
        for item in self.m_portmap :
            print item ;
        return self ;

PICAM_PORT_LIST = [ 8554, 18554, 28554, 38554, 48554, 58554 ] ;
PICAM_PROTO = 'TCP'
class PicamPortmap(Upnpc) :
    def isPortmapped(self) :
        for item in self.m_portmap :
            if item[2][0] != self.m_ipaddr :
                continue ;
            if item[3].find('picam') != 0 or item[1] != PICAM_PROTO:
                continue ;
            if item[0] in PICAM_PORT_LIST :
                return True ;
        return False ;
    def getValidPort(self) :
        for port in PICAM_PORT_LIST :
            for item in self.m_portmap :
                if port == item[0] :
                    continue ;
                else :
                    return port ;
    def setPortmap(self) :
        if not self.isPortmapped() :
            port = self.getValidPort() ;
            self.doQueryAddPortmap(self.getValidPort(), PICAM_PROTO, 8554, 'picam') ;
            self.doQueryGetPortmap() ;
        return self ;
    def delPortmapAll(self) :
        if self.isPortmapped() :
            fgQuery = False ;
            for item in self.m_portmap :
                if item[2][0] != self.m_ipaddr :
                    continue ;
                if item[3].find('picam') != 0 or item[1] != PICAM_PROTO:
                    continue ;
                if item[0] in PICAM_PORT_LIST :
                    self.doQueryDelPortmap(item[0], item[1]) ;
                    fgQuery = True ;
            if fgQuery :
                self.doQueryGetPortmap() ;
        return self ;


def main(option) :
        if option == 'dumplist' :
            PicamPortmap().dumpPortmap() ;
        elif option == 'install' :
            PicamPortmap().setPortmap().dumpPortmap() ;
        elif option == 'remove' :
            PicamPortmap().delPortmapAll() ;
        else :
            ERR('Notthing to do about %s.' % option) ;

def usage(cmdName) :
    strUsage = '''
usage : %s [<install|remove|dumplist>]
    options :
        install     : set a port map of rtsp streaming for picam.
        remove      : unset a port map of rtsp streaming.
        dumplist    : print lists of port map.
'''
    print >> sys.stderr, strUsage % (cmdName) ;

if __name__ == '__main__':
    option = 'install'
    validOptions = [ 'install', 'remove', 'dumplist' ] ;
    if len(sys.argv) > 1 and sys.argv[1] not in validOptions :
        usage(sys.argv[0]) ;
    else :
        if len(sys.argv) > 1 and sys.argv[1] :
            option = sys.argv[1] ;
    main(option)
