
import sqlite3 ;
from sensormodel import SensorMeta ;
from libps.psDebug import DBG, ERR ;
from error import SensorDBError ;

SENSOR_DB_PATH = 'sensor.sqlite3' ;
SENSOR_LOG_DB_PATH = 'sensorlog.sqlite3' ;

QUERY_JOURNAL_MODE = 'PRAGMA journal_mode = MEMORY ;' ;
QUERY_FOREIGN_KEYS_ENABLE = 'PRAGMA foreign_keys = ON ;' ;
QUERY_NODE_TABLE = \
'''CREATE TABLE IF NOT EXISTS sensor_node (eui char(20), stamp char(24), fuid char(16), type char(8), value varchar(64), extra varchar(256),
PRIMARY KEY(eui)) ;'''
QUERY_CLUSTER_TABLE = \
'''CREATE TABLE IF NOT EXISTS sensor_cluster(eui char(20), stamp char(24), fuid char(16), type char(8), value varchar(64), extra varchar(256),
PRIMARY KEY(eui, fuid),
FOREIGN KEY(eui) REFERENCES sensor_node(eui) ON DELETE CASCADE) ;'''
QUERY_ATTRIBUTE_TABLE = \
'''CREATE TABLE IF NOT EXISTS sensor_attribute(eui char(20), stamp char(24), fuid char(16), type char(8), value varchar(64), extra varchar(256),
PRIMARY KEY(eui, fuid),
FOREIGN KEY(eui) REFERENCES sensor_node(eui) ON DELETE CASCADE) ;'''

class BaseDB :
    def __init__(self, dbFile) :
        self.m_con = sqlite3.connect(dbFile, check_same_thread=False) ;
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
    def queryDeleteTable(self, table) :
        query = [] ;
        if isinstance(table, list) :
            for t in table :
                query.append('DROP TABLE IF EXISTS %s;' % t) ;
        else :
            query = 'DROP TABLE IF EXISTS %s;' % table ;
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


class SensorDB(BaseDB) :
    SubtypeTableMap = { SensorMeta.SEN_TYPE_ZB_NODE: 'sensor_node' ,
                        SensorMeta.SEN_TYPE_ZW_NODE: 'sensor_node' ,
                        SensorMeta.SEN_TYPE_ZB_CLUSTER: 'sensor_cluster' ,
                        SensorMeta.SEN_TYPE_ZW_CLASS: 'sensor_cluster' ,
                        SensorMeta.SEN_TYPE_ZB_ATTRIBUTE: 'sensor_attribute' ,
                        SensorMeta.SEN_TYPE_ZW_ATTRIBUTE: 'sensor_attribute' } ;
    EmptyField = [ 'null' , 'None' ] ;
    def __init__(self, dbFile=SENSOR_DB_PATH) :
        BaseDB.__init__(self, dbFile) ;
        self.__createTable() ;
    def __createTable(self) :
        self.queryUpdate([  QUERY_JOURNAL_MODE ,
                            QUERY_FOREIGN_KEYS_ENABLE ,
                            QUERY_NODE_TABLE ,
                            QUERY_CLUSTER_TABLE ,
                            QUERY_ATTRIBUTE_TABLE ]) ;
    def queryUpsert(self, notifyList) :
        query = [] ;
        for protoSubtype, payload in notifyList :
            if protoSubtype == 'SENSOR' :
                field = payload.split('|') ;
                if field[1] in SensorDB.SubtypeTableMap :
                    table = SensorDB.SubtypeTableMap[field[1]] ;
                    if len(field) != 6 :
                        ERR('Field length is 6 over, %s-%s.' % (protoSubtype, payload)) ;
                        continue ;
                    if table == 'sensor_node' :
                        query.append("INSERT OR IGNORE INTO %s (eui) VALUES ('%s') ;" % (table, field[2])) ;
                        query.append("UPDATE %s SET fuid='%s' WHERE eui='%s' ;" % (table, field[3], field[2])) ;
                        query.append("UPDATE %s SET stamp='%s' WHERE eui='%s' ;" % (table, field[0], field[2])) ;
                        query.append("UPDATE %s SET type='%s' WHERE eui='%s' ;" % (table, field[1], field[2])) ;
                        if field[4] not in SensorDB.EmptyField :
                            query.append("UPDATE %s SET value='%s' WHERE eui='%s' ;" % (table, field[4], field[2])) ;
                        if field[5] not in SensorDB.EmptyField :
                            query.append("UPDATE %s SET extra='%s' WHERE eui='%s' ;" % (table, field[5], field[2])) ;
                    else :
                        query.append("INSERT OR IGNORE INTO %s (eui, fuid) VALUES ('%s', '%s') ;" % (table, field[2], field[3])) ;
                        query.append("UPDATE %s SET stamp='%s' WHERE eui='%s' AND fuid='%s' ;" % (table, field[0], field[2], field[3])) ;
                        query.append("UPDATE %s SET type='%s' WHERE eui='%s' AND fuid='%s' ;" % (table, field[1], field[2], field[3])) ;
                        if field[4] not in SensorDB.EmptyField :
                            query.append("UPDATE %s SET value='%s' WHERE eui='%s' AND fuid='%s' ;" % (table, field[4], field[2], field[3])) ;
                        if field[5] not in SensorDB.EmptyField :
                            query.append("UPDATE %s SET extra='%s' WHERE eui='%s' AND fuid='%s' ;" % (table, field[5], field[2], field[3])) ;
                else :
                    ERR('Unknown subtype, %s-%s.' % (protoSubtype, payload)) ;
            else :
                DBG('Not supported portoSubtype, %s-%s.' % (protoSubtype, payload)) ;
        self.queryUpdate(query) ;
        del query ;
    def queryGetTable(self, table) :
        cur = self.queryScalar("SELECT * FROM %s ORDER BY 1 ;" % table) ;
        result = [] ;
        for row in cur.fetchall() :
            rowData = '' ;
            for col in row :
                rowData += '%s|' % col ;
            result.append(rowData) ;
        return result ;


class SensorLogDB(BaseDB) :
    def __init__(self, dbFile=SENSOR_LOG_DB_PATH) :
        BaseDB.__init__(self, dbFile) ;
