from mysql_q_agent import QAgent
from mysql_storage_allocator import StorageAllocator
import time
import os
import numpy as np
import gym
import matplotlib.pyplot as plt
import random
import pandas as pd
import csv


def main():
    window_size = 10
    episode_count = 20
    df = "training_data_mysql"
    batch_size = 32
    
    agent = QAgent(window_size)
    allocator = StorageAllocator(window_size = window_size, dataset = df)
    
    cumulative_reward = 0
    start_time = time.time()

    # Note the rewards and downtime per episode
    with open(r'downtime_reward.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['rewards_per_episode', 'downtime_per_episode'])

    # Note disk_space every iteration
    with open(r'disk_space_training_model.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['timeslot', 'disk_space'])

    for e in range(episode_count + 1):
        print("Episode {0}/{1}".format(e, episode_count))
        agent.reset()
        state, disk_usage_data = allocator.reset()
        
        for t in range(allocator.last_data_index):
            action, allocated_disk_space = agent.get_action(state, disk_usage_data)
            
            next_state, next_disk_space, reward, done = allocator.get_next_state_reward(action, allocated_disk_space)
            agent.memory.append((state, action, reward, next_state, done))
            
            if len(agent.memory) > batch_size:
                agent.experience_replay(batch_size = batch_size)
            
            cumulative_reward += reward
            state = next_state
            disk_usage_data = next_disk_space
            
            with open(r'disk_space_training_model.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([t, allocated_disk_space])

            if done:
                print("-------------------------------------------------------------------------")
                print("Total cost incurred due to downtime: {0}".format(agent.get_total_downtime()))
                print("-------------------------------------------------------------------------")
                print("-------------------------------------------------------------------------")
                print("Total reward for this episode: {0}".format(cumulative_reward))
                print("-------------------------------------------------------------------------")
                with open(r'downtime_reward.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow([cumulative_reward, agent.get_total_downtime()])

                with open(r'disk_space_training_model.csv', 'a') as f:
                    writer = csv.writer(f)
                    writer.writerow(["-----------------------------------", "--------------------------------------" ])
            
    if not os.path.exists("models/rl_storage_allocator.h5"):
        try:
            os.mkdir("models")
        except FileExistsError:
            print("Models folder already exists")

        agent.model.save("models/rl_storage_allocator.h5")

    end_time = time.time()
    train_time = end_time - start_time
    print("Training time: {} seconds".format(train_time))
    

if __name__ == "__main__":
    main()

