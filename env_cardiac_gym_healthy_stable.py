# -*- coding: utf-8 -*-
"""Cardiac_gym.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12FzY4Cm-PAkiyY81FQhjNp_qKNWMYi_r

# Loading the trained TCN model
"""

from stable_baselines.common import set_global_seeds

# import keras
# 20000000 steps, change setpoint every 500 episodes
# 60000000 steps, change setpoint every 600 episodes


alg = "PPO"

if alg == "PPO":
    from stable_baselines import PPO2
    from stable_baselines.common.policies import FeedForwardPolicy, MlpPolicy
elif alg == "SAC":
    from stable_baselines.sac.policies import MlpPolicy
    from stable_baselines.sac import FeedForwardPolicy
    from stable_baselines.common.policies import MlpLstmPolicy,LstmPolicy
    from stable_baselines import sacc_Model
    
elif alg == "DDPG":
    from stable_baselines.ddpg.policies import MlpPolicy
    from stable_baselines.ddpg import DDPG#, FeedForwardPolicy




import pandas as pd

# Commented out IPython magic to ensure Python compatibility.
# import ddeint
import numpy as np
import gym
#from pilco.models import PILCO
#from pilco.controllers import RbfController, LinearController
#from pilco.rewards_cardiac import ExponentialReward, LinearReward


import tensorflow.compat.v1 as tf
print(tf.__version__)



# %matplotlib inline
import matplotlib
import matplotlib.pyplot as plt
np.random.seed(10) #0
from utils_cardiac_TCN import rollout, policy
import numpy as np
from gym import spaces
from gym.core import Env
import os

import random


import sys
import os
from utils_tcn import *






# import time
sys.path.append(os.path.abspath("./Updated_Rat_Models_healthy_stable"))



df_save_name = "./Healthy_500samples"




PATH_to_MAT = "./Updated_Rat_Models_healthy_stable/"

filenames = ["Openloop_Healthy_Simulation_23-Jan-2022_08-39-53_15000.mat"]
mat_dict = loadmat(PATH_to_MAT + filenames[0], squeeze_me=True)

# PC_VNSx is pulse current (mA) at VNS location x.
# Freq_VNSx is pulse frequency (Hz) at VNS location x.
PC_VNS1 = []
PC_VNS2 = []
PC_VNS3 = []
Freq_VNS1 = []
Freq_VNS2 = []
Freq_VNS3 = []
HR = []
MAP = []

for index in range(mat_dict['u'].shape[-1]):
    
    PC_VNS1.append(mat_dict['u'][3,:,index] * mat_dict['u'][0,:,index])
    PC_VNS2.append(mat_dict['u'][5,:,index] * mat_dict['u'][1,:,index])
    PC_VNS3.append(mat_dict['u'][7,:,index] * mat_dict['u'][2,:,index])
    
    Freq_VNS1.append(mat_dict['u'][4,:,index] * mat_dict['u'][0,:,index])
    Freq_VNS2.append(mat_dict['u'][6,:,index] * mat_dict['u'][1,:,index])
    Freq_VNS3.append(mat_dict['u'][8,:,index] * mat_dict['u'][2,:,index])
    
    MAP.append(mat_dict['y'][0,:,index])
    HR.append(mat_dict['y'][1,:,index])

PC_VNS1 = np.array(PC_VNS1).flatten()
PC_VNS2 = np.array(PC_VNS2).flatten()
PC_VNS3 = np.array(PC_VNS3).flatten()
Freq_VNS1 = np.array(Freq_VNS1).flatten()
Freq_VNS2 = np.array(Freq_VNS2).flatten()
Freq_VNS3 = np.array(Freq_VNS3).flatten()

MAP = np.array(MAP).flatten()
HR = np.array(HR).flatten()


max_ori_MAP = max(MAP)
min_ori_MAP = min(MAP)
max_ori_HR = max(HR)
min_ori_HR = min(HR)
print('max MAP: ', max_ori_MAP)
print('min MAP: ', min_ori_MAP)
print('max HR: ', max_ori_HR)
print('min HR: ', min_ori_HR)





df = pd.DataFrame()
df["PC_VNS1"] = PC_VNS1
df["Freq_VNS1"] = Freq_VNS1
df["PC_VNS2"] = PC_VNS2
df["Freq_VNS2"] = Freq_VNS2
df["PC_VNS3"] = PC_VNS3
df["Freq_VNS3"] = Freq_VNS3

df["HR"] = HR
df["MAP"] = MAP

pick_end_cycle = False  # whether use the whole cycle or only the end point.

if pick_end_cycle:
    df = df.iloc[::30, :].reset_index(drop=True)  # Sample every 30 cycles

print(f"\nWhole data lenght is: {len(df)}")

cycle_length = 30  # How many cycles is each trial (we should know this a priori)

train_df, val_df, test_df, num_features, column_indices, train_end, valid_end = split_data(
    df, cycle_length)

print(f"\nNumber of trials in training data is: {len(train_df)/cycle_length}")
print(f"\nNumber of trials in validation data is: {len(val_df)/cycle_length}")
print(f"\nNumber of trials in test data is: {len(test_df)/cycle_length}")
print(f"\nNumber of features in data is: {num_features}")
train_df, val_df, test_df, train_mean, train_max, train_min = minmax_data(train_df, val_df, test_df)


print('PC')
print(np.min(train_df['PC_VNS1'])) # -0.268
print(np.max(train_df['PC_VNS1'])) # 0.732

print(np.min(train_df['PC_VNS2'])) # -0.208
print(np.max(train_df['PC_VNS2'])) # 0.792

print(np.min(train_df['PC_VNS3'])) # -0.167
print(np.max(train_df['PC_VNS3'])) # 0.833


print('Freq')
print(np.min(train_df["Freq_VNS1"])) #-0.258
print(np.max(train_df["Freq_VNS1"])) # 0.742

print(np.min(train_df["Freq_VNS2"])) # -0.19
print(np.max(train_df["Freq_VNS2"])) # 0.81

print(np.min(train_df["Freq_VNS3"])) # -0.158
print(np.max(train_df["Freq_VNS3"])) # 0.842

print('HR')

print(np.min(train_df["HR"])) # -0.485
print(np.max(train_df["HR"])) # 0.515




print('MAP')

print(np.min(train_df["MAP"])) # -0.359
print(np.max(train_df["MAP"])) # 0.641



input_width = 1
sequence_stride = 1

w = WindowGenerator(input_width=input_width,
                    label_width=1,
                    shift=1,
                    train_df=train_df,
                    val_df=val_df,
                    test_df=test_df,
                    sequence_stride=sequence_stride,
                    label_columns=["HR", "MAP"],
                    cycle_length=cycle_length)


loaded_models = dict()
predictions_HR = dict()
predictions_MAP = dict()
prediction_time = []



for model in ["TCN"]:
    saved_model_name = df_save_name + "/" + 'TCN' + "_" + str(input_width)
    print(f"Load model from {saved_model_name}")
    
    start = time.perf_counter()
    
    loaded_models[model] = tf.keras.models.load_model(saved_model_name)
    predictions_HR[model] = loaded_models[model].predict(w.test)[:, :, 0].flatten() * (train_max["HR"] - train_min["HR"]) + train_mean["HR"]
    predictions_MAP[model] = loaded_models[model].predict(w.test)[:, :, 1].flatten() * (train_max["MAP"] - train_min["MAP"]) + train_mean["MAP"]
    
    elapsed = time.perf_counter() - start
    print("\nElapsed %.3f seconds for prediction." % elapsed)
    prediction_time.append(elapsed)


"""# Implementing the model as an openai gym env"""


tcn_model = tf.keras.models.load_model(saved_model_name)













# initial state: 138, 408

class CardiacModel_Env(Env):
    
    
    
    def __init__(self):
        

        self.action_space = spaces.Box(np.array([-1,-1,-1,-1,-1,-1]), np.array([1,1,1,1,1,1]))
        self.min_HR = -0.49
        self.max_HR = 0.51
        self.min_MAP = -0.36
        self.max_MAP = 0.64




        low = np.array([self.min_HR, self.min_MAP, self.min_HR, self.min_MAP], dtype=np.float32)
        high = np.array([self.max_HR, self.max_MAP, self.max_HR, self.max_MAP], dtype=np.float32)

        # low = np.array([self.min_HR, self.min_MAP], dtype=np.float32)
        # high = np.array([self.max_HR, self.max_MAP], dtype=np.float32)
        self.observation_space = spaces.Box(low=low, high=high, dtype=np.float32)



        self.sp_list = [np.array([0.074, -0.37]), np.array([-0.355, 0.108]), np.array([0.064, -0.16])]
       
        self.setpoints = self.sp_list[1] 

   



        self.initial_state = np.array([0.3, 0.25])

        self.total_reward = []



        ################### reset ###############3

        self.consider_sp =  True
        self.ep_length = 500

        self.done = False

        self.current_step = 0
        self.current_reward = 0

        self.num_episode = 0


        self.listhistory = []#np.zeros((12))

        self.num_history = 1


    def save_current_state(self, state):

        self.listhistory+=(list(state.flatten()))

        if (len(self.listhistory) /2) > self.num_history:
            self.listhistory.pop(0)
            self.listhistory.pop(0) 




    def reset_history(self, state):
        self.listhistory = list(state.flatten())

        while (len(self.listhistory) / 2) < self.num_history:
            self.listhistory+=(list(state.flatten()))




    
    def history_state(self, state, setpoint):
      

        if self.current_step < 1:

            while len(self.historystates) < 4:#10

             
            self.historystates += list(state.flatten()
        
        else:

            self.historystates.pop(0)
            self.historystates.pop(0)

            self.historystates.append(state.flatten())
          
        
        
        
    def step(self, u):
        u[0] = u[0] /2 + 0.23
        u[1] = u[1] /2 + 0.24
        u[2] = u[2] /2 + 0.29
        u[3] = u[3] /2 + 0.31
        u[4] = u[4] /2 + 0.33
        u[5] = u[5] /2 + 0.34
        

        in_TCN = np.concatenate((u, self.state), axis=0).reshape(1,1,8)

        
    
        
        
        

        
        self.state = tcn_model.predict(in_TCN)[0][0]


        self.save_current_state(self.state)

        rew = self.reward(self.state, self.setpoints)




        self.current_step += 1
        self.done = self.current_step >= self.ep_length

        self.current_reward += rew


        if self.consider_sp:
            hist = (np.array(self.listhistory+ list(self.setpoints.flatten()))).reshape(1, -1).flatten()
        
            

            return hist, rew, self.done, {} # self.state
        
        else:




            return np.array(self.listhistory), rew, self.done, {} # self.state


    def reward(self, state, setpoint):


        return np.exp(-1*np.sum(np.power((state-setpoint),2)*10))

    def reset(self):

        self.num_episode += 1
        self.state = self.initial_state


        print('set point: ', self.setpoints)

        print('initial states: ', self.initial_state)
        print('new w/o exercise, healthy')
       

        # self.setpoints = np.array([random.uniform(-0.49, 0.51), random.uniform(-0.36, 0.64)])

        
        
        # self.state = np.array([random.uniform(-0.49, 0.51), random.uniform(-0.36, 0.64)])


        rand_sample = np.random.rand(2,2)

        self.setpoints = np.array([rand_sample[0,0] - 0.49, rand_sample[0,1] - 0.36])
        self.state = np.array([rand_sample[1,0] - 0.49, rand_sample[1,1] - 0.36])
        




        self.reset_history(self.state)





        self.total_reward.append(self.current_reward)

        # if len(self.total_reward) % 10000 == 0:
        dict = {'reward ': self.total_reward}

        df = pd.DataFrame(dict)
        # df.to_csv('sac_len500_new_healthy_stable_s0_64_0lr0005_tau00001_gamma08.csv')
        df.to_csv('ppo_len500_new_healthy_stable_s0_32_0r002_clip02_gamma095_vf1_ent0005_new.csv')


        


        rew = self.reward(self.state, self.setpoints)


        self.current_step = 0

      
        self.current_reward = 0


    
        if self.consider_sp:

            hist = (np.array(self.listhistory+ list(self.setpoints.flatten()))).reshape(1, -1).flatten()

        

            return hist
        
        else:

  

            return np.array(self.listhistory)
       

    def render(self):
        pass

# """# Example usage of the model:

# actions are be in [-1.0, 1.0] range  
# states are in [-0.7,0.3] range
# # """

class Custompolicy(MlpPolicy):
    def __init__(self, *args, **kwargs):
        super(Custompolicy, self).__init__(*args, **kwargs, layers = [32]) # 128, 128



env = CardiacModel_Env()
env.reset()




# sp1: 103, 393  sp2: 144, 348, sp3: 121, 392   #385 0
[hr, map] = np.array([0.25, 0.05])  #env.step(u)[0] # initial state


sp1 = np.array([0.074, -0.37]) # sp1: 103, 393 
sp2 = np.array([-0.355, 0.108]) # sp2: 144, 348, 
sp3 = np.array([0.064, -0.16]) # sp3: 121, 392 




import time

seed = 0#50

start = time.time()
env.seed(seed)



from stable_baselines.common.vec_env import DummyVecEnv



# model = sacc_Model(Custompolicy, env, verbose = 1, learning_rate = 0.0005, tau = 0.0001, gamma = 0.9 )
# model.learn(7000000, save_path = 'trained_model/sac_len500_new_healthy_stable_s0_64_0lr0005_tau00001_gamma09_new') #7000000
# model.save('trained_model/sac_len500_new_healthy_stable_s0_64_0lr0005_tau00001_gamma09_new')




model = PPO2(Custompolicy, env, verbose = 1, learning_rate = 0.002, gamma = 0.95, cliprange = 0.2, vf_coef =1, ent_coef = 0.005 )
model.learn(7000000, save_path = 'trained_model/ppo_len500_new_healthy_stable_s0_32_0r002_clip02_gamma095_vf1_ent0005_new') #12000000
model.save('trained_model/ppo_len500_new_healthy_stable_s0_32_0r002_clip02_gamma095_vf1_ent0005_new')





print('finish learning')
print('running time: ', time.time() - start)





