import sys
import os
import json
import csv
import time
import logging
from datetime import datetime


if __name__ == "__main__":


    header = ['Time', 'Disk_Usage']
    with open('rabbitmq_disk_usage_uncompressed_3.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(header)
    
    command = "kubectl exec jit-rabbitmq-0 -- rabbitmqctl list_queues --vhost sample_virtual_host message_bytes_persistent| awk 'FNR == 4 {print $0}'"
    write_counter = 0
    while True:
        try:
            disk_usage = os.popen(command).read()
            print("*************{}".format(disk_usage))
            print("Current Disk Usage {}".format(disk_usage))
            with open('rabbitmq_disk_usage_uncompressed_3.csv', 'a', encoding='UTF8') as f:
               writer = csv.writer(f)
               data = [int(time.time()), int(disk_usage)]
               writer.writerow(data)
            time.sleep(1)
            write_counter += 1
            print("Write Counter ---> {}".format(write_counter))
        except KeyboardInterrupt:
            # log.debug("Terminating program")
            p.terminate()
            sys.exit()
        except Exception as e:
            print("got an exception --> {}".format(e))


