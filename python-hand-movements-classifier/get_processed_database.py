#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%% Importing the libraries
import pandas as pd # reading files
import numpy as np # handling numerical data
import matplotlib.pyplot as plt # Plotting
from scipy import signal

#########################
#%% Importing the dataset
#########################

volunteer_id = 1
dataset = pd.read_csv('datasets/volunteer_'+str(volunteer_id)+'.csv', sep=',',
 nrows=150000)

emg_channels = dataset.iloc[:, 1:-1].values
emg_out = dataset.iloc[:, -1].values

dataset = None

#########################
#%% Windowing
#########################
#TODO


###############################
#%% Optional: Plotting the data
###############################

# Here we use the matplotlib library to plot a small window of the signal
# And verify if everything is all right

fig = plt.figure()
axes = [None for i in range(4)]
for i in range(4):
    axes[i] = plt.subplot(4,1,i+1)
    plt.plot(emg_channels[:,i])
    plt.plot(emg_out[:]/10.0)
    plt.title('Ch ' + str(i+1))
    plt.ylim((-1,1))
    plt.grid()

axes[0].get_shared_x_axes().join(axes[0],axes[1],axes[2],axes[3])
axes[0].get_shared_y_axes().join(axes[0],axes[1],axes[2],axes[3])
axes[0].set_xticklabels([])
axes[1].set_xticklabels([])
axes[2].set_xticklabels([])
plt.show()
