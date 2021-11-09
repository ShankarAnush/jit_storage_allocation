import pickle
import csv


if __name__ == "__main__":
    load_model = pickle.load(open('./models/mysql_custom_model.sav', 'rb'))
    current_allocated_disk_space = 0
    required_disk_space = 0
    unused_allocated_disk_space = 0
    total_downtime = 0

    # Note the allocated disk space, unused allocated disk space and downtime
    with open(r'fixed_storage_allocation.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['current_allocated_disk_space', 'unused_allocated_disk_space', 'total_downtime'])

    for i in range(0,14000):
        if i == 0:
            current_allocated_disk_space = load_model.predict([[i]])
            required_disk_space = load_model.predict([[i]])
        else:
            required_disk_space = load_model.predict([[i]])

        disk_difference = required_disk_space - current_allocated_disk_space

        if disk_difference > 0 and disk_difference <= 100:
            current_allocated_disk_space += 100
            unused_allocated_disk_space += 100 - disk_difference
            total_downtime += disk_difference * (1/5000)
        elif disk_difference > 100:
            current_allocated_disk_space += disk_difference + 100
            unused_allocated_disk_space += 100
            total_downtime += (disk_difference + 100) * (1/5000)
        else:
            pass   # disk space remains to be constant

        with open(r'fixed_storage_allocation.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([current_allocated_disk_space, unused_allocated_disk_space, total_downtime])

        
        print("{0}--------------{1}-----------{2}----------{3}".format(current_allocated_disk_space, unused_allocated_disk_space, total_downtime, load_model.predict([[i]])))


