FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
    python3-pip \
    vim \
    net-tools \
    iproute2 \
    iputils-ping \
    libsnappy-dev

ENV LC_ALL C.UTF-8

RUN pip3 install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

ENV OPCUA_SERVER 0.0.0.0
ENV OPCUA_PORT 4840
ENV CASSANDRA_KEYSPACE sample_keyspace
ENV CASSANDRA_CLUSTERIP 10.108.8.41
ENV PASSWORD jit@upb123
ENV SLEEP_DURATION 2
ENV OUT_FILE /respone_time_measurements/response
#ENV COMPRESSION snappy

COPY opc_ua_cassandra_with_compression.py opc_ua_cassandra_with_compression.py
COPY start.sh start.sh
RUN chmod +x start.sh
CMD /start.sh
