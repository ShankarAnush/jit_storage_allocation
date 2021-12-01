#!/bin/bash

set -e

pod=$1
logfile=$2

echo "Monitoring pod: $pod", writing benchmarked results into "$logfile"
rm -f -- "$logfile"
echo "Date_time,CPU,Memory_Bytes,Disk_Usage" >> $logfile

while true
do
	date +%s | tr '\n' ',' >> $logfile
	kubectl exec $pod -- bash -c "cat /sys/fs/cgroup/cpu/cpuacct.usage | tr '\n' ','; cat /sys/fs/cgroup/memory/memory.usage_in_bytes | tr '\n' ','; du -sh /bitnami/cassandra/data | awk '{print \$1}'" >> $logfile
	sleep 20
	echo "+20 seconds"
done

exit 0
