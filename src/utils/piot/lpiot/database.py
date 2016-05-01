
import sqlite3 ;
from libps.psDebug import DBG, ERR ;
from error import PiotDatabaseError ;

PIOT_DB_PATH = 'piot.sqlite3'

QUERY_FOREIGN_KEYS_ENABLE = 'PRAGMA foreign_keys = ON;' ;
QUERY_JOURNAL_MODE = 'PRAGMA journal_mode = MEMORY' ;
QUERY_ZB_DEVICE_TABLE = \
'''CREATE TABLE IF NOT EXISTS zb_device (eui char(16), nodeId int, capability int,
PRIMARY KEY (eui));'''
QUERY_ZB_CLUSTER_TABLE = \
'''CREATE TABLE IF NOT EXISTS zb_cluster (eui char(16), endpointId int, profileId int, clusterId int,
PRIMARY KEY (eui, endpointId, clusterId), FOREIGN KEY (eui) REFERENCES zb_device(eui) ON DELETE CASCADE);'''
QUERY_ZB_ATTRIBUTE_TABLE = \
'''CREATE TABLE IF NOT EXISTS zb_attribute (eui char(16), endpointId int, clusterId int, attributeId int, attributeType int, attributeData varchar(64),
PRIMARY KEY (eui, endpointId, clusterId, attributeId),
FOREIGN KEY (eui) REFERENCES zb_device(eui) ON DELETE CASCADE,
FOREIGN KEY (eui, endpointId, clusterId) REFERENCES zb_cluster(eui, endpointId, clusterId) ON DELETE CASCADE);'''


class PiotDB :
    def __init__(self, pathDB=None) :
        fileDB = pathDB if pathDB else PIOT_DB_PATH ;
        self.m_con = sqlite3.connect(fileDB) ;
        self.queryCreateTable() ;
    def __del__(self) :
        if self.m_con :
            self.m_con.close() ;
    def queryUpdate(self, query) :
        try :
            cur = self.m_con.cursor() ;
            if isinstance(query, list) :
                for q in query :
                    cur.execute(q) ;
            else :
                cur.execute(query) ;
            self.m_con.commit() ;
        except sqlite3.Error, e :
            self.m_con.rollback() ;
            DBG('DB Error, %s: %s' % (e.args, query)) ;
            # raise PiotDatabaseError(e.args[0]) ;
    def queryScalar(self, query) :
        try :
            cur = self.m_con.cursor() ;
            cur.execute(query) ;
            return cur ;
        except sqlite3.Error, e :
            DBG('DB Error, %s: %s' % (e.args, query)) ;
        return None ;
    def queryCreateTable(self) :
        self.queryUpdate([  QUERY_JOURNAL_MODE,
                            QUERY_FOREIGN_KEYS_ENABLE,
                            QUERY_ZB_DEVICE_TABLE ,
                            QUERY_ZB_CLUSTER_TABLE ,
                            QUERY_ZB_ATTRIBUTE_TABLE ]) ;
    def queryDeleteTable(self, table) :
        query = [] ;
        if isinstance(table, list) :
            for t in table :
                query.append('drop table if exists %s;' % t) ;
        else :
            query = 'drop table if exists %s;' % table ;
        self.queryUpdate(query) ;
    def _dumpContentTable(self, table) :
        cur = self.queryScalar('PRAGMA TABLE_INFO(%s);' % table) ;
        if cur :
            schema = '' ;
            for row in cur.fetchall() :
                schema += '%s , ' % row[1] ;
            cur = self.queryScalar('SELECT * FROM %s ORDER BY 1;' % table) ;
            DBG('Schema : %s' % schema)
            idx = 0 ;
            for row in cur.fetchall() :
                rowData = '' ;
                idx += 1 ;
                for col in row :
                    rowData += '%s , ' % col ;
                DBG('%6d : %s' % (idx, rowData)) ;
    def dumpTable(self, table) :
        if isinstance(table, list) :
            for t in table :
                self._dumpContentTable(t) ;
        else :
            self._dumpContentTable(table) ;

    # Functions for zb_device table.
    def zbIsExistDevice(self, eui) :
        return (len(self.queryScalar("SELECT * FROM zb_device WHERE eui='%s'" % eui).fetchall()) > 0) ;
    def zbAddDevice(self, eui, nodeId, capability) :
        query = [] ;
        if self.zbIsExistDevice(eui) :
            if capability != 0 :
                query.append("UPDATE zb_device SET capability=%d WHERE eui='%s' AND capability!=%d;" % (capability, eui, capability)) ;
            query.append("UPDATE zb_device SET nodeId=%d WHERE eui='%s' AND nodeId!=%d;" % (nodeId, eui, nodeId)) ;
        else :
            query = "INSERT OR IGNORE INTO zb_device (eui, nodeId, capability) VALUES ('%s', %d, %d);" % (eui, nodeId, capability) ;
        self.queryUpdate(query) ;
    def zbDelDevice(self, eui) :
        self.queryUpdate("DELETE FROM zb_device WHERE eui='%s';" % eui) ;

    # Functions for zb_cluster table.
    def zbIsExistCluster(self, eui, endpointId, clusterId) :
        return (len(self.queryScalar("SELECT * FROM zb_cluster WHERE eui='%s' AND endpointId=%d AND clusterId=%d;" % (eui, endpointId, clusterId)).fetchall()) > 0) ;
    def zbAddCluster(self, eui, endpointId, profileId, clusterId) :
        if not self.zbIsExistCluster(eui, endpointId, clusterId) :
            query = "INSERT OR IGNORE INTO zb_cluster (eui, endpointId, profileId, clusterId) VALUES ('%s', %d, %d, %d);" % (eui, endpointId, profileId, clusterId) ;
            self.queryUpdate(query) ;
    def zbDelCluster(self, eui, endpointId, clusterId) :
        self.queryUpdate("DELETE FROM zb_cluster WHERE eui='%s' AND endpointId=%d AND clusterId=%d;" % (eui, endpointId, clusterId)) ;

    # Function for zb_attribute table.
    def zbIsExistAttribute(self, eui, endpointId, clusterId, attributeId) :
        return (len(self.queryScalar("SELECT * FROM zb_attribute WHERE eui='%s' AND endpointId=%d AND clusterId=%d AND attributeId=%d;" % (eui, endpointId, clusterId, attributeId)).fetchall()) > 0) ;
    def zbAddAttribute(self, eui, endpointId, clusterId, attributeId, attributeType, attributeData) :
        query = '' ;
        if self.zbIsExistAttribute(eui, endpointId, clusterId, attributeId) :
            query = "UPDATE zb_attribute SET attributeData='%s' WHERE eui='%s' AND endpointId=%d AND clusterId=%d AND attributeId=%d;" % (attributeData, eui, endpointId, clusterId, attributeId) ;
        else :
            query = "INSERT OR IGNORE INTO zb_attribute (eui, endpointId, clusterId, attributeId, attributeType, attributeData) " + \
                    "VALUES ('%s', %d, %d, %d, %d, '%s');" % (eui, endpointId, clusterId, attributeId, attributeType, attributeData) ;
        self.queryUpdate(query) ;
    def zbDelAttribute(self, eui, endpointId, clusterId, attributeId) :
        self.queryUpdate("DELETE FROM zb_attribute WHERE eui='%s' AND endpointId=%d AND clusterId=%d AND attributeId=%d;" % (eui, endpointId, clusterId, attributeId)) ;


if __name__ == '__main__':
    db = PiotDB() ;

    # Test zb_device table.
    db.zbAddDevice('FF0000', 0x64, 0) ;
    db.zbAddDevice('FF0001', 0x64, 0) ;
    db.zbAddDevice('FF0002', 0x64, 100) ;
    db.zbAddDevice('FF0003', 0x400, 3) ;

    db.zbAddDevice('FF0001', 0x100, 0) ;
    db.zbAddDevice('FF0001', 0x200, 0) ;
    db.zbAddDevice('FF0002', 0x300, 0) ;

    db.zbDelDevice('000000') ;

    # Test zb_cluster
    db.zbAddCluster('FF0000', 1, 0x104, 0x0000) ;
    db.zbAddCluster('FF0000', 1, 0x104, 0x0001) ;
    db.zbAddCluster('FF0000', 1, 0x104, 0x0003) ;
    db.zbAddCluster('FF0000', 1, 0x104, 0x0019) ;
    db.zbAddCluster('FF0000', 1, 0x104, 0x0020) ;
    db.zbAddCluster('FF0000', 1, 0x104, 0x0500) ;
    db.zbAddCluster('FF0000', 1, 0x104, 0xFC00) ;

    db.zbAddCluster('FF0001', 1, 0x104, 0x0000) ;
    db.zbAddCluster('FF0001', 1, 0x104, 0x0001) ;
    db.zbAddCluster('FF0001', 1, 0x104, 0x0003) ;
    db.zbAddCluster('FF0001', 1, 0x104, 0x0019) ;
    db.zbAddCluster('FF0001', 1, 0x104, 0x0500) ;

    db.zbAddCluster('FF0002', 1, 0x104, 0x0000) ;
    db.zbAddCluster('FF0002', 1, 0x104, 0x0001) ;
    db.zbAddCluster('FF0002', 1, 0x104, 0x0003) ;
    db.zbAddCluster('FF0002', 1, 0x104, 0x0019) ;
    db.zbAddCluster('FF0002', 1, 0x104, 0x0500) ;

    db.zbAddCluster('FF0003', 1, 0x104, 0x0000) ;
    db.zbAddCluster('FF0003', 1, 0x104, 0x0001) ;
    db.zbAddCluster('FF0003', 1, 0x104, 0x0003) ;
    db.zbAddCluster('FF0003', 1, 0x104, 0x0019) ;
    db.zbAddCluster('FF0003', 1, 0x104, 0x0500) ;

    print '------------------------------------'
    db.dumpTable(['zb_device', 'zb_cluster', 'zb_attribute']) ;

    # Test zb_attribute
    db.zbAddAttribute('FF0000', 1, 0x0000, 0x0002, 0x20, 'SmartThings') ;
    db.zbAddAttribute('FF0000', 1, 0x0000, 0x0003, 0x20, 'Arrival') ;
    db.zbAddAttribute('FF0001', 1, 0x0000, 0x0002, 0x20, 'SmartThings') ;
    db.zbAddAttribute('FF0001', 1, 0x0000, 0x0003, 0x20, 'Motion') ;
    db.zbAddAttribute('FF0002', 1, 0x0000, 0x0002, 0x20, 'SmartThings') ;
    db.zbAddAttribute('FF0002', 1, 0x0000, 0x0003, 0x20, 'WaterLeak') ;
    db.zbAddAttribute('FF0003', 1, 0x0000, 0x0002, 0x20, 'SmartThings') ;
    db.zbAddAttribute('FF0003', 1, 0x0000, 0x0003, 0x20, 'Multi') ;

    db.zbAddAttribute('FF0000', 1, 0x0001, 0x0020, 0x03, '2.5')
    db.zbAddAttribute('FF0001', 1, 0x0001, 0x0020, 0x03, '3.1')
    db.zbAddAttribute('FF0002', 1, 0x0001, 0x0020, 0x03, '2.9')
    db.zbAddAttribute('FF0003', 1, 0x0001, 0x0020, 0x03, '2.0')

    print '------------------------------------'
    db.zbDelCluster('FF0003', 1, 0x0000) ;
    db.dumpTable(['zb_device', 'zb_cluster', 'zb_attribute']) ;

    # Test
    print '------------------------------------'
    db.zbDelDevice('FF0000') ;
    db.dumpTable(['zb_device', 'zb_cluster', 'zb_attribute']) ;
