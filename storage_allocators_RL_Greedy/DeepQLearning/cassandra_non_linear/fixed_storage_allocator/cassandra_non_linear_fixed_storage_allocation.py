import pickle
import csv
import math
import pandas as pd
import numpy as np


if __name__ == "__main__":
    #model = load_model('./models/Kafka_Model.h5')
    df = pd.read_csv('../raw_data/cassandra_non_linear_testing_data.csv')
    disk_usage = df['cassandra_non_linear_model'].tolist()
    current_allocated_disk_space = 0
    required_disk_space = 0
    unused_allocated_disk_space = 0
    total_downtime = 0
    disk_difference = 0
    counter = 0

    # Note the allocated disk space, unused allocated disk space and downtime
    with open(r'cassandra_non_linear_fixed_storage_allocation.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['current_allocated_disk_space', 'unused_allocated_disk_space', 'total_downtime', 'original_value'])

    # Note the unused allocated disk space for that instant and do not take the cumulative unused disk space
    for i in range(0,len(disk_usage)):
        if i == 0:
            current_allocated_disk_space = disk_usage[i]
            required_disk_space = disk_usage[i]
        else:
            required_disk_space = disk_usage[i]

        # print("current_allocated_disk_space: {0}, required_disk_space: {1}". format(current_allocated_disk_space, required_disk_space))

        disk_difference = required_disk_space - current_allocated_disk_space

        if disk_difference > 0:
            current_allocated_disk_space += 5 # 5 MB, scaling in case of cassandra_non_linear
            unused_allocated_disk_space = disk_difference
            total_downtime += 1 
            
        elif disk_difference < 0:
            if disk_difference < -10: # 8 MB between rise and fall of the disk usage
                pass
            
            unused_allocated_disk_space = (-1 * disk_difference)
            # when the disk difference is less than 0, 
            # application has more allocated disk compared to the required disk space
            # so no disk space allocation required. hence, no downtime
            # but there is allocated but unused disk space

        else:
            pass   # disk space remains to be constant

        with open(r'cassandra_non_linear_fixed_storage_allocation.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([current_allocated_disk_space, unused_allocated_disk_space, total_downtime, disk_usage[i] ])

        
        print("{0}--------------{1}-----------{2}----------{3}".format(current_allocated_disk_space, unused_allocated_disk_space, total_downtime, disk_usage[i]))



