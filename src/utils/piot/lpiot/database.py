
import sqlite3 ;
from libps.psDebug import DBG, ERR ;
from error import PiotDatabaseError ;

PIOT_DB_PATH = 'piot.sqlite3'

QUERY_ZB_DEVICE_TABLE   = 'CREATE TABLE IF NOT EXISTS zb_device (eui char(16), nodeId int, capability int, primary key (eui));'
QUERY_ZB_CLUSTER_ATTRIBUTE_TABLE = 'CREATE TABLE IF NOT EXISTS zb_cl_attr (eui char(16), profileId int, endpointId int, clusterId int, direction int, attributeId int, attributeType int, attributeData varchar(64), primary key (eui, endpointId, clusterId, attributeId), foreign key (eui) references zb_device(eui) on delete cascade)'


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
        self.queryUpdate([ QUERY_ZB_DEVICE_TABLE ,
                           QUERY_ZB_CLUSTER_ATTRIBUTE_TABLE ]) ;
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
        return len(self.queryScalar("SELECT * FROM zb_device WHERE eui='%s'" % eui).fetchall()) ;
    def zbAddDevice(self, eui, nodeId, capability) :
        query = [] ;
        if self.zbIsExistDevice(eui) :
            if capability != 0 :
                query.append("UPDATE zb_device SET capability=%d WHERE eui='%s' AND capability!=%d" % (capability, eui, capability)) ;
            query.append("UPDATE zb_device SET nodeId=%d WHERE eui='%s' AND nodeId!=%d" % (nodeId, eui, nodeId)) ;
        else :
            query = "INSERT OR IGNORE INTO zb_device (eui, nodeId, capability) VALUES ('%s', %d, %d)" % (eui, nodeId, capability) ;
        self.queryUpdate(query) ;
    def zbDelDevice(self, eui) :
        self.queryUpdate("DELETE FROM zb_device where eui='%s'" % eui) ;
    # Functions for zb_cl_attr table.
    def zbIsExistClAttr(nodeId, endpointId, clusterId, )
