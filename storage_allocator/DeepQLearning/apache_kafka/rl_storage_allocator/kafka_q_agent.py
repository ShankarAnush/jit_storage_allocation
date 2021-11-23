import numpy as np
import gym
import matplotlib.pyplot as plt
import random
import pandas as pd
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam
from collections import deque


class QAgent:
    def __init__(self, state_size, is_eval = False, model_name = ""):
        self.__available_disk = []
        self.__total_downtime = 0.00
        self.action_history = []
        self.allocated_disk_space = 0

        self.state_size = state_size
        self.action_size = 3 #hold, increase, decrease
        self.memory = deque(maxlen = 1000)
        self.model_name = model_name
        self.is_eval = is_eval

        self.gamma = 0.95
        self.epsilon = 1.0
        self.min_epsilon = 0.01
        self.decay_rate = 0.995

        self.model = load_model("models/" + model_name) if is_eval else self.create_model()
        self.dqn = load_model("../../../../prediction_models/Kafka_Model.h5")


    def create_model(self):
        model = Sequential()
        model.add(Dense(units = 32, input_dim = self.state_size, activation = "relu"))
        model.add(Dense(units=8, activation = "relu"))
        model.add(Dense(units = self.action_size, activation = "linear"))
        model.compile(loss = "mse", optimizer = Adam(lr=0.001))
        return model

    def reset(self):
        self.__available_disk = []
        self.__total_downtime = 0
        self.action_history = []

    def get_action(self, state, disk_usage_data):
        if not self.is_eval and np.random.rand() <= self.epsilon:
            action = random.randrange(self.action_size)
        else:
            actions = self.model.predict(state)
            action = np.argmax(actions[0])
        #print("Printing state")
        #print(self.model.predict(state))


        if action  == 0: # do nothing
            print("No change")
            self.action_history.append(action)
        elif action == 1: # increase
            print("Increasing disk space ... ")
            self.increase(disk_usage_data)
            self.action_history.append(action)
        elif action == 2 and self.has_available_disk(): # decrease
            print("decreasing disk space ... ")
            self.allocated_disk_space =self.decrease(disk_usage_data)
            self.action_history.append(action)
        else:
            self.action_history.append(0)

        return action, self.allocated_disk_space


    def increase(self, disk_usage_data):
        self.__available_disk.append(disk_usage_data)
        disk_difference = disk_usage_data - self.dqn.predict([[[self.allocated_disk_space]]]).item()
        print(self.dqn.predict([[[self.allocated_disk_space]]]).item())
        self.allocated_disk_space += disk_difference
        print("Increase in the disk space: {}".format(disk_difference))
        if disk_difference > 0:
            self.__total_downtime += 1  # downtime is a fixed value for whatever the increase is in disk usage
        else:
            #Ignoring this possibility
            pass
            # print("less than 0 in Increase")
            # self.__total_downtime += -disk_difference * (3/500) # convert negative to positive
        print("Downtime: {}".format(self.__total_downtime))
        print("Increase : {}".format(self.allocated_disk_space))
     #   return self.allocated_disk_space

    def decrease(self, disk_usage_data):
        self.__available_disk.pop(0)
        disk_difference = disk_usage_data - self.dqn.predict([[[self.allocated_disk_space]]]).item()
        print(self.dqn.predict([[[self.allocated_disk_space]]]).item())
        self.allocated_disk_space -= disk_difference
        print("Decrease in the disk space: {}".format(disk_difference))
        self.__total_downtime += 40 # 40 seconds of downtime during transition from retention size to segment size
        print("Downtime: {}".format(self.__total_downtime))
        print("Decrease : {}".format(self.allocated_disk_space))
        return self.allocated_disk_space

    def get_total_downtime(self):
        return self.__total_downtime

    def has_available_disk(self):
        return len(self.__available_disk) > 0

    def experience_replay(self, batch_size):
        mini_batch = []
        l = len(self.memory)
        for i in range(l-batch_size + 1, l):
            mini_batch.append(self.memory[i])

        for state, action, reward, next_state, done in mini_batch:
            if done:
                target = reward
            else:
                next_q_values = self.model.predict(next_state)[0]
                target = reward + self.gamma * np.amax(next_q_values)
            predicted_target = self.model.predict(state)
            predicted_target[0][action] = target
            self.model.fit(state, predicted_target, epochs = 1, verbose = 0)

        if self.epsilon > self.min_epsilon:
            self.epsilon *= self.decay_rate


