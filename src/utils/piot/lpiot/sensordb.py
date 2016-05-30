
import sqlite3 ;
from libps.psDebug import DBG, ERR ;
from error import SensorDBError ;

SENSOR_DB_PATH = 'sensor.sqlite3' ;
SENSOR_LOG_DB_PATH = 'sensorlog.sqlite3' ;

QUERY_FOREIGN_KEYS_ENABLE = 'PRAGMA foreign_keys = ON ;' ;
QUERY_JOURNAL_MODE = 'PRAGMA journal_mode = MEMORY ;' ;
QUERY_NODE_TABLE = \
'''CREATE TABLE IF NOT EXIST sensor_node (eui char(20), fuid char(16), type char(8), value varchar(64), extra varchar(128),
PRIMARY KEY(eui)) ;'''
QUERY_CLUSTER_TABLE = \
'''CREATE TABLE IF NOT EXIST sensor_cluster(eui char(20), fuid char(16), type char(8), value varchar(64), extra varchar(128),
PRIMARY KEY(eui, fuid),
FOREIGN KEY(eui) REFERENCES sensor_node(eui) ON DELETE CASCADE) ;'''
QUERY_ATTRIBUTE_TABLE = \
'''CREATE TABLE IF NOT EXIST sensor_attribute(eui char(20), fuid char(16), type char(8), value varchar(64), extra varchar(128),
PRIMARY KEY(eui, fuid),
FOREIGN KEY(eui) REFERENCES sensor_node(eui) ON DELETE CASCADE) ;'''

class SensorDB :
    def __init__(self, dbFile=SENSOR_DB_PATH) :
        pass ;

class SensorLogDB :
    def __init__(self, dbFile=SENSOR_LOG_DB_PATH) :
        pass ;
