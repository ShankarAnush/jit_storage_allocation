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

INSTANCE_NAME = os.environ.get('INSTANCE_NAME', 'MY-INSTACE')
OPCUA_SERVER = os.environ.get('OPCUA_SERVER', '0.0.0.0') # IP of the pod hosting digital twin
OPCUA_PORT = os.environ.get('OPCUA_PORT', '4840')
SLEEP_DURATION = os.environ.get('SLEEP_DURATION', '1') # seconds sleep after each update written to kafka
OUT_FILE = os.environ.get('OUT_FILE', 'response_time.json')
PASSWORD = os.environ.get('$CASSANDRA_PASSWORD', 'jit@upb123')
NUMBER_MESSAGES = os.environ.get('NUMBER_MESSAGES', 10)
KEYSPACE = "cassandra_testkeyspace"

def main():
    auth_provider = PlainTextAuthProvider(username='cassandra', password=PASSWORD)
    clstr = Cluster(['10.108.8.41'], auth_provider=auth_provider)
    session = clstr.connect()
    
    # create a KEYSPACE
    session.execute("""
            CREATE KEYSPACE %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '2'}
            """ % KEYSPACE)

    rows = session.execute("SELECT * FROM system-schema_keyspaces")
    if KEYSPACE in [row[0] for row in rows]:
        print(row[0])
        



if __name__ == "__main__":
    opcua_client = Client("opc.tcp://%s:%s/freeopcua/server/" % (OPCUA_SERVER, OPCUA_PORT))
    opcua_client.connect()
    print('Connected to OPC UA server %s:%s' % (OPCUA_SERVER, OPCUA_PORT))
    main()

