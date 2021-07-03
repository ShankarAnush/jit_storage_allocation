FROM ubuntu:18.04
LABEL maintainer="ashankar@campus.uni-paderborn.de"

ENV SQUID_VERSION=4.15

ARG TRUST_CERT=

RUN if [ ! -z "$TRUST_CERT" ]; then \
        echo "$TRUST_CERT" > /usr/local/share/ca-certificates/build-trust.crt ; \
        update-ca-certificates ; \
    fi

RUN cat /etc/apt/sources.list | grep -v '^#' | sed /^$/d > sources.tmp.1 && \
    cat /etc/apt/sources.list | sed s/deb\ /deb-src\ /g | grep -v '^#' | sed /^$/d > sources.tmp.2 && \
    cat sources.tmp.1 sources.tmp.2 | sort -u > /etc/apt/sources.list && \
    rm -f sources.tmp.1 sources.tmp.2

RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get build-dep -y squid \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y wget tar xz-utils libssl-dev nano

RUN mkdir /src \
    && cd /src \
    && wget http://www.squid-cache.org/Versions/v4/squid-$SQUID_VERSION.tar.xz \
    && mkdir squid \
    && tar -C squid --strip-components=1 -xvf squid-$SQUID_VERSION.tar.xz

RUN cd /src/squid && \
    ./configure \
        --prefix=/usr \
        --datadir=/usr/share/squid4 \
		--sysconfdir=/etc/squid4 \
		--localstatedir=/var \
		--mandir=/usr/share/man \
		--enable-inline \
		--enable-async-io=8 \
		--enable-storeio="ufs,aufs,diskd,rock" \
		--enable-removal-policies="lru,heap" \
		--enable-delay-pools \
		--enable-cache-digests \
		--enable-underscores \
		--enable-icap-client \
		--enable-follow-x-forwarded-for \
		--enable-auth-basic="DB,fake,getpwnam,LDAP,NCSA,NIS,PAM,POP3,RADIUS,SASL,SMB" \
		--enable-auth-digest="file,LDAP" \
		--enable-auth-negotiate="kerberos,wrapper" \
		--enable-auth-ntlm="fake" \
		--enable-external-acl-helpers="file_userip,kerberos_ldap_group,LDAP_group,session,SQL_session,unix_group,wbinfo_group" \
		--enable-url-rewrite-helpers="fake" \
		--enable-eui \
		--enable-esi \
		--enable-icmp \
		--enable-zph-qos \
		--with-openssl \
		--enable-ssl \
		--enable-ssl-crtd \ 
		--disable-translation \
		--with-swapdir=/var/spool/squid4 \
		--with-logdir=/var/log/squid4 \
		--with-pidfile=/var/run/squid4.pid \
		--with-filedescriptors=65536 \
		--with-large-files \
		--with-default-user=proxy \
        --disable-arch-native \
        --disable-ipv6

RUN wget -O /usr/local/bin/p2 \
    https://github.com/wrouesnel/p2cli/releases/download/r1/p2 && \
    chmod +x /usr/local/bin/p2

ENV HTTP_PORT=3128 \
    ICP_PORT= \
    HTCP_PORT= \
    VISIBLE_HOSTNAME=docker-squid4 \
    MAX_CACHE_SIZE=40000 \
    MAX_OBJECT_SIZE="1536 MB" \
    MEM_CACHE_SIZE="128 MB"

ENV http_proxy=http://172.17.0.1:3128 \
    https_proxy=http://172.17.0.1:3128 \
    ftp_proxy=http://172.17.0.1:3128

COPY entrypoint.sh /sbin/entrypoint.sh
RUN chmod 755 /sbin/entrypoint.sh

EXPOSE 3128/tcp

ENTRYPOINT ["/sbin/entrypoint.sh"]

