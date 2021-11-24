import numpy as np
import gym
import matplotlib.pyplot as plt
import random
import pandas as pd


class StorageAllocator(gym.Env):

    def __init__(self, window_size, dataset):

        self.data = self.get_data(dataset)
        self.states = self.get_all_window(self.data, window_size)
        self.index = -1
        self.last_data_index = len(self.data) - 1

    def get_data(self, dataset):
        vec = []
        lines = open("../raw_data/" + dataset + ".csv","r").read().splitlines()
        for l in lines[1:]:
            vec.append(float(l.split(',')[0]))
        return vec


    def get_all_window(self, data, window_size):
        processed_data = []
        for t in range(len(data)):
            state = self.get_state(data, t, window_size + 1)
            processed_data.append(state)
        return processed_data


    def get_state(self, data, t, n):
        d = t - n + 1
        block = data[d:t+1] if d>= 0 else -d * [data[0]] + data[0:t+1]
        res = []
        for i in range(n-1):
            res.append(block[i+1] - block[i])
        return np.array([res])

    def reset(self):
        self.index = -1
        return self.states[0], self.data[0]

    def get_next_state_reward(self, action, allocated_disk_space = None):
        self.index += 1
        if self.index > self.last_data_index:
            self.index = 0
        next_state = self.states[self.index+1]
        next_disk_space =  self.data[self.index+1]

        current_disk_space = self.data[self.index]
        reward = 0
        
        print("Actual_disk_space: {}".format(current_disk_space))
        print("allocated_disk_space: {}".format(allocated_disk_space))
        diff = current_disk_space - allocated_disk_space
        
        if diff >= 0 and diff < 5000:
            if action == 0 and allocated_disk_space is not None: # no difference in disk space
                reward = 0 # 1€ 
            elif action == 1 and allocated_disk_space is not None: # +ve difference in disk space
                reward = 1 # 1€
            elif action == 2 and allocated_disk_space is not None: # -ve difference in disk space
                reward = -10 # -10€
            else:
                reward = -10 # -10€
        # the difference between the allocated and required could be -ve in case Kafka reaches the retention size
        # this difference will be minimum of -800,000 KB. I.e., approximately 800 MB
        elif diff < 0:
            # When there is a transition from retention to segment size, no chance for action 0 or action 1
            if action == 0 and allocated_disk_space is not None: # no difference in disk space
                reward = -10 # -10€
            elif action == 1 and allocated_disk_space is not None: # +ve difference in disk space
                reward = -10 # -10€
            elif action == 2 and allocated_disk_space is not None: # -ve difference in disk space
                reward = 1 # -10€
            else:
                reward = -10 # -10€
        else:
            reward = -10 # -10€


        done = True if self.index == self.last_data_index - 1 else False
        return next_state, next_disk_space, reward, done

