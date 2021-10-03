'''A simple OPC UA client which reads values from the OPC UA server and publishes them to a MySQL'''

import logging
import mysql.connector
import time
from opcua import Client
import json
import sys
import os
from datetime import datetime
import threading
from queue import Queue
import _thread
from socket import error as socket_error
from mysql.connector import errorcode

# set log level
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

INSTANCE_NAME = os.environ.get('INSTANCE_NAME', 'dt-python-mysql')
OPCUA_SERVER = os.environ.get('OPCUA_SERVER', '0.0.0.0')
OPCUA_PORT = os.environ.get('OPCUA_PORT', '4840')
MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'my_database')
MYSQL_CLUSTERIP = os.environ.get('MYSQL_CLUSTERIP', '10.105.243.76')
MYSQL_USERNAME = os.environ.get('MYSQL_USERNAME', 'root')
PASSWORD = os.environ.get('$MYSQL_PASSWORD', 'ZfkHf9ovlk')
SLEEP_DURATION = os.environ.get('SLEEP_DURATION', '2') # seconds sleep after each update written to kafka
OUT_FILE = os.environ.get('OUT_FILE', 'response_time.json')

TABLE = 'mysql_table'
NUM_QUERIES = 10000
# file = open(OUT_FILE, "w")


if __name__== "__main__":

    try:
        # connect to opc ua server
        opcua_client = Client("opc.tcp://%s:%s/freeopcua/server/" % (OPCUA_SERVER, OPCUA_PORT))
        opcua_client.connect()
        print('*************************Connected to OPC UA server %s:%s****************************' % (OPCUA_SERVER, OPCUA_PORT))
        root = opcua_client.get_root_node()
        imms = root.get_child(["0:Objects", "2:IMMS"])
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            # not connection refused error? re-raise
            raise serr
        # connection refused error
        print('Connection refused on the given IP')

    # connect to My_SQL server and to the database
    # if the database doesn't exists, throw an exception and handle it by creating one
    try:

        mydb = mysql.connector.connect(
                host=MYSQL_CLUSTERIP,
                user=MYSQL_USERNAME,
                password=PASSWORD
                )
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
            # connect to MySQL server
            mydb = mysql.connector.connect(
                host=MYSQL_CLUSTERIP,
                user=MYSQL_USERNAME,
                password=PASSWORD
                )
            db_cursor = mydb.cursor()

            # create a database
            db_cursor.execute("CREATE DATABASE %s" % (MYSQL_DATABASE))
            log.debug("Database %s created" % (MYSQL_DATABASE))
            print("New Database created, connecting to the database {}".format(MYSQL_DATABASE))
            mydb = mysql.connector.connect(
                host=MYSQL_CLUSTERIP,
                user=MYSQL_USERNAME,
                password=PASSWORD,
                database=MYSQL_DATABASE
                )
            db_cursor = mydb.cursor() # keeping cursor updated
        else:
            print(err)
    db_cursor = mydb.cursor()
    db_cursor.execute("SHOW DATABASES")
    print(type(db_cursor))
    databases = list()
    for x in db_cursor:
        print(x[0])
        databases.append(x[0])
    if MYSQL_DATABASE in databases:
        print("%s exists" % MYSQL_DATABASE)
    else:
        db_cursor.execute("CREATE DATABASE %s" % (MYSQL_DATABASE))
        log.debug("Database %s created" % (MYSQL_DATABASE))
        print("New Database created, connecting to the database {}".format(MYSQL_DATABASE))
        mydb = mysql.connector.connect(
            host=MYSQL_CLUSTERIP,
            user=MYSQL_USERNAME,
            password=PASSWORD,
            database=MYSQL_DATABASE
            )
        db_cursor = mydb.cursor() # keeping cursor updated

    print('*****************************Connected to MySQL server %s and to database %s *******************************' % (MYSQL_CLUSTERIP, MYSQL_DATABASE))

    # available databases, if any
#    databases = db_cursor.execute("SHOW DATABASES")
#    print(db_cursor.execute("SHOW DATABASES"))
#    print(type(databases))
#    if MYSQL_DATABASE in databases:
#        print("Database {} exists".format(MYSQL_DATABASE))
#        mydb = mysql.connector.connect(
#        host="10.99.72.39",
#        user=MYSQL_USERNAME,
#        password=PASSWORD,
#        database=MYSQL_DATABASE
#        )
#        db_cursor = mydb.cursor() # keeping cursor updated
##    else:
#        db_cursor.execute("CREATE DATABASE %s" % (MYSQL_DATABASE))
#        log.debug("Database %s created" % (MYSQL_DATABASE))
#        print("New Database created, connecting to the database {}".format(MYSQL_DATABASE))
#        mydb = mysql.connector.connect(
#        host="10.99.72.39",
#        user=MYSQL_USERNAME,
#        password=PASSWORD,
#        database=MYSQL_DATABASE
#        )
#        db_cursor = mydb.cursor() # keeping cursor updated

    # Use the database
    db_cursor.execute("USE %s" % MYSQL_DATABASE)
    # get available tables, if any
    db_cursor.execute("SHOW TABLES")
    print(db_cursor.fetchall())
    # check if table exists
    print("Table {} exists, dropping it".format(TABLE))
    db_cursor.execute("DROP TABLE IF EXISTS %s" % (TABLE))
    # after dropping the table, create a new one
    log.debug("Creating Table")
    db_cursor.execute("""
            CREATE TABLE %s (
            date float,
            time TEXT,
            ATActSimPara1 float,
            ATActSimPara2 float,
            ActCntCyc float,
            ActCntPrt float,
            ActStsMach text,
            ActTimCyc float,
            SetCntMld float,
            SetCntPrt float,
            SetTimCyc float,
            InstanceName TEXT,
            TimestampSent TIMESTAMP(6) PRIMARY KEY) TABLESPACE ts2 ROW_FORMAT=COMPRESSED KEY_BLOCK_SIZE=8""" % (TABLE))


    # insert values into table
    while True:
        try:
            db_cursor.execute("""INSERT INTO mysql_table (date, time, ATActSimPara1, ATActSimPara2, ActCntCyc, ActCntPrt, ActStsMach, ActTimCyc, SetCntMld, SetCntPrt, SetTimCyc, InstanceName, TimestampSent) VALUES (%(date)s, %(time)s, %(ATActSimPara1)s, %(ATActSimPara2)s, %(ActCntCyc)s, %(ActCntPrt)s, %(ActStsMach)s, %(ActTimCyc)s, %(SetCntMld)s, %(SetCntPrt)s, %(SetTimCyc)s, %(InstanceName)s, %(TimestampSent)s)""",
            {
                "date": float(imms.get_variables()[0].get_value()),
                "time": str(imms.get_variables()[1].get_value()),
                "ATActSimPara1": float(imms.get_variables()[2].get_value()),
                "ATActSimPara2": float(imms.get_variables()[3].get_value()),
                "ActCntCyc": float(imms.get_variables()[4].get_value()),
                "ActCntPrt": float(imms.get_variables()[5].get_value()),
                "ActStsMach": str(imms.get_variables()[6].get_value()),
                "ActTimCyc": float(imms.get_variables()[7].get_value()),
                "SetCntMld": float(imms.get_variables()[8].get_value()),
                "SetCntPrt": float(imms.get_variables()[9].get_value()),
                "SetTimCyc": float(imms.get_variables()[10].get_value()),
                "InstanceName": INSTANCE_NAME,
                "TimestampSent": datetime.now()
            })

            print(datetime.now())

            mydb.commit()
            print('Values inserted into table %s' % TABLE)
            # time.sleep(float(SLEEP_DURATION))
        except KeyboardInterrupt:
            try:
                opcua_client.disconnect()
            except Exception:
                pass
            finally:
                # print("Writing response times to", OUT_FILE)
                # file.write(json.dumps(list(q.queue)))
                # file.close()
                sys.exit()
