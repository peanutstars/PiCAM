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

PICAM_PORT_LIST = [ 554, 10554, 20554, 30554, 40554, 50554, 60554 ] ;
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
            self.doQueryAddPortmap(self.getValidPort(), PICAM_PROTO, 554, 'picam') ;
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
            if fqQuery :
                self.doQueryGetPortmap() ;
        return self ;


def main() :
        # PicamPortmap().delPortmapAll().dumpPortmap().setPortmap().dumpPortmap() ;
        PicamPortmap().setPortmap().dumpPortmap() ;

if __name__ == '__main__':
    main()

    # u.addportmapping(10554, 'TCP', u.lanaddr, 554, 'picam', '' ) ;

#print u.addportmapping(64000, 'TCP',
#                       '192.168.1.166', 63000, 'port mapping test', '')
#print u.deleteportmapping(64000, 'TCP')
