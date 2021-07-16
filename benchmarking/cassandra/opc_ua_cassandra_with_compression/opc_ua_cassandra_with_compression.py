'''A simple OPC UA client which reads values from the OPC UA server and publishes them to a Cassandra'''

import logging
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra import ConsistencyLevel
from cassandra.query import SimpleStatement
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

# set log level
log = logging.getLogger()
log.setLevel('INFO')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

INSTANCE_NAME = os.environ.get('INSTANCE_NAME', 'dt-imms-opcua-0')
OPCUA_SERVER = os.environ.get('OPCUA_SERVER', '0.0.0.0')
OPCUA_PORT = os.environ.get('OPCUA_PORT', '4840')
CASSANDRA_KEYSPACE = os.environ.get('CASSANDRA_KEYSPACE', 'sample_keyspace')
CASSANDRA_CLUSTERIP = os.environ.get('CASSANDRA_CLUSTERIP', '10.108.8.41')
PASSWORD = os.environ.get('$CASSANDRA_PASSWORD', 'jit@upb123')
SLEEP_DURATION = os.environ.get('SLEEP_DURATION', '2') # seconds sleep after each update written to kafka
OUT_FILE = os.environ.get('OUT_FILE', 'response_time.json')

TABLE = 'sample_table'
NUM_QUERIES = 10000
# file = open(OUT_FILE, "w")


if __name__== "__main__":

    try:
        # connect to opc ua server
        opcua_client = Client("opc.tcp://%s:%s/freeopcua/server/" % (OPCUA_SERVER, OPCUA_PORT))
        opcua_client.connect()
        print('**************************************************Connected to OPC UA server %s:%s*****************************************' % (OPCUA_SERVER, OPCUA_PORT))
        root = opcua_client.get_root_node()
        imms = root.get_child(["0:Objects", "2:IMMS"])
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED:
            # not connection refused error? re-raise
            raise serr
        # connection refused error
        print('Connection refused on the given IP')
    
    # connect to Cassandra
    auth_provider = PlainTextAuthProvider(username='cassandra', password=PASSWORD)
    clstr = Cluster([CASSANDRA_CLUSTERIP], auth_provider=auth_provider)
    session = clstr.connect()
    print('***********************************************Connected to Cassandra %s************************************************' % (CASSANDRA_CLUSTERIP))

    # check for existing keyspace
    rows = session.execute("SELECT * FROM system_schema.keyspaces")
    if CASSANDRA_KEYSPACE in [row[0] for row in rows]:
        log.debug("dropping existing keyspace...")
        session.execute("DROP KEYSPACE " + CASSANDRA_KEYSPACE)
        print('******************************************************Existing keyspace dropped***********************************************')

    log.debug("Creating keyspace...")
    session.execute("""
            CREATE KEYSPACE %s 
            WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '2'}
            """ % CASSANDRA_KEYSPACE)

    log.debug("Setting keyspace...")
    session.set_keyspace(CASSANDRA_KEYSPACE)

    log.debug("Creating table...")
    qry = ("""
    create table %s(
        date float,
        time text,
        ATActSimPara1 float,
        ATActSimPara2 float,
        ActCntCyc float,
        ActCntPrt float,
        ActStsMach text,
        ActTimCyc float,
        SetCntMld float,
        SetCntPrt float,
        SetTimCyc float,
        InstanceName text,
        TimestampSent timestamp,
        primary key(TimestampSent)
    ) WITH compression = {'class': 'LZ4Compressor'}""" % TABLE)
    session.execute(qry)

    # insert values into table
    while True:
        try:
            session.execute("""INSERT INTO sample_keyspace.sample_table (date, time, ATActSimPara1, ATActSimPara2, ActCntCyc, ActCntPrt, 
                    ActStsMach, ActTimCyc, SetCntMld, SetCntPrt, SetTimCyc, InstanceName, TimestampSent)
                    VALUES (%(date)s, %(time)s, %(ATActSimPara1)s, %(ATActSimPara2)s, %(ActCntCyc)s, %(ActCntPrt)s, %(ActStsMach)s, %(ActTimCyc)s, 
                    %(SetCntMld)s, %(SetCntPrt)s, %(SetTimCyc)s, %(InstanceName)s, %(TimestampSent)s)""",
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

            log.debug("Sleeping for two seconds...")
            print('Values inserted into table %s' % TABLE)
            time.sleep(float(SLEEP_DURATION))
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
