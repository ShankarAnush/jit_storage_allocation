#!/bin/bash

# Setup the ssl_cert directory
if [ ! -d /etc/squid4/ssl_cert ]; then
	mkdir /etc/squid4/ssl_cert
fi

chown -R proxy:proxy /etc/squid4
chmod 700 /etc/squid4/ssl_cert

# Setup the squid cache directory
if [ ! -d /var/cache/squid4 ]; then
	mkdir -p /var/cache/squid4
fi
chown -R proxy: /var/cache/squid4
chmod -R 750 /var/cache/squid4

chown proxy: /dev/stdout
chown proxy: /dev/stderr

# Initialize the certificates database
/usr/libexec/security_file_certgen -c -s /var/spool/squid4/ssl_db -M 4MB
chown -R proxy: /var/spool/squid4/ssl_db

# Set the configuration
if [ "$CONFIG_DISABLE" != "yes" ]; then
	p2 -t /squid.conf.p2 > /etc/squid4/squid.conf

	# Parse the cache peer lines from the environment and add them to the
	# configuration
	echo '# CACHE PEERS FROM DOCKER' >> /etc/squid4/squid.conf
	env | grep 'CACHE_PEER' | sort | while read cacheline; do
		echo "# $cacheline " >> /etc/squid4/squid.conf
		line=$(echo $cacheline | cut -d'=' -f2-)
		echo "cache_peer $line" >> /etc/squid4/squid.conf
	done

	# Parse the extra config lines and append them to the configuration
	echo '# EXTRA CONFIG FROM DOCKER' >> /etc/squid4/squid.conf
	env | grep 'EXTRA_CONFIG' | sort | while read extraline; do
		echo "# $extraline " >> /etc/squid4/squid.conf
		line=$(echo $extraline | cut -d'=' -f2-)
		echo "$line" >> /etc/squid4/squid.conf
	done
else
	echo "/etc/squid4/squid.conf: CONFIGURATION TEMPLATING IS DISABLED."
fi

if [ ! -e /etc/squid4/squid.conf ]; then
    echo "ERROR: /etc/squid4/squid.conf does not exist. Squid will not work."
    exit 1
fi
