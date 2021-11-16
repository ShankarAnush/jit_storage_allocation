import tensorflow
import csv
from tensorflow import keras
from tensorflow.keras import models
from tensorflow.keras.models import load_model

from cassandra_linear_q_agent import QAgent
from cassandra_linear_storage_allocator import StorageAllocator

import matplotlib.pyplot as plt

def main():
    test_file = "cassandra_testing_data"
    model_name = "cassandra_rl_storage_allocator.h5"

    model = load_model("./models/" + model_name)
    window_size = model.layers[0].input.shape.as_list()[1]

    agent = QAgent(window_size, True, model_name)
    storage_allocator = StorageAllocator(window_size, test_file)

    state, disk_usage_data = storage_allocator.reset()
    cumulative_reward = 0

    with open(r'rl_cassandra_l_downtime_reward.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['rewards', 'downtime'])

    with open(r'rl_cassandra_l_disk_space.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['timeslot', 'disk_space'])

    for t in range(storage_allocator.last_data_index):
        action, allocated_disk_space = agent.get_action(state, disk_usage_data)

        next_state, next_disk_space, reward, done = storage_allocator.get_next_state_reward(action, allocated_disk_space)
            
        cumulative_reward += reward
        state = next_state
        disk_usage_data = next_disk_space
        
        with open(r'rl_cassandra_l_disk_space.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([t, allocated_disk_space])

        with open(r'rl_cassandra_l_downtime_reward.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([cumulative_reward, agent.get_total_downtime()])

        if done:
            print("-------------------------------------------------------------------------")
            print("Total cost incurred due to downtime: {0}".format(agent.get_total_downtime()))
            print("-------------------------------------------------------------------------")
            print("-------------------------------------------------------------------------")
            print("Total reward for this episode: {0}".format(cumulative_reward))
            print("-------------------------------------------------------------------------")

            #with open(r'rl_cassandra_l_downtime_reward.csv', 'a') as f:
            #    writer = csv.writer(f)
            #    writer.writerow([cumulative_reward, agent.get_total_downtime()])
    plot(storage_allocator.data, agent.action_history, agent.get_total_downtime())



def plot(data, action_data, downtime):
    plt.plot(range(len(data)), data)
    plt.xlabel("time")
    plt.ylabel("disk_usage")
    
    print(len(data))
    print(data)
    print(len(action_data))
    print(action_data)
    increase, decrease = False, False
    for d in range(len(data) - 1):
        if action_data[d] == 1: #increase
            increase, = plt.plot(d, data[d], 'g*')
        elif action_data[d] == 2:
            decrease, = plt.plot(d,data[d], 'r+')
    if increase and decrease:
        plt.legend([increase, decrease], ["Increase", "Decrease"])
    plt.title("Total Disk Usage")
    plt.savefig("disk_allocation.pdf")


if __name__ == "__main__":
    main()
