#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 17 16:06:46 2018

@author: italo
"""
#%% Importing the libraries
import pandas as pd # reading files
import numpy as np # handling numerical data
import matplotlib.pyplot as plt # Plotting
from scipy import signal

###############################
#%% Adding the path to datasets
###############################

# Description of the analysed movements:
# Movement Number - Movement Name
# 1 -> Supinar
# 2 -> Pronar
# 3 -> Pinçar
# 4 -> Fechar
# 5 -> Estender
# 6 -> Flexionar
# This should be the output of the classifier. It should classify each moviment
# in one of this classes.
HAND_MOVIMENTS_NAMES = ["Supinar", "Pronar", "Pinçar", "Fechar", "Estender", "Flexionar"]

#########################
#%% Importing the dataset
#########################

# The file name refering to the folder where this script is located
#   - emg-movements-classifier
#       - datasets
#           - coletas
#               - Eber
#               - LH
#               - Miguel... etc
#       - python-hand_moviments-classifier
#           - app_procedimentos
#               - app_procedures.py

# Opening a file and reading it to a dataFrame object
# sep means separator, the files have no headers
# After reading it, we add the names of each column in the dataset.
# At end, we select the 4 channels as a numpy vector and we save it in
# emg_channels.
# The trigger is saved in emg_trigger.
volunteer_id = 'Eber/Eber'
dataset_pt11 = pd.read_table('datasets/coletas/'+volunteer_id+'11-Final.txt', sep=';', header=None)
dataset_pt11.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
dataset_pt12 = pd.read_table('datasets/coletas/'+volunteer_id+'12-Final.txt', sep=';', header=None)
dataset_pt12.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
dataset_pt13 = pd.read_table('datasets/coletas/'+volunteer_id+'13-Final.txt', sep=';', header=None)
dataset_pt13.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
dataset_pt14 = pd.read_table('datasets/coletas/'+volunteer_id+'14-Final.txt', sep=';', header=None)
dataset_pt14.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()

dataset_pt21 = pd.read_table('datasets/coletas/'+volunteer_id+'21-Final.txt', sep=';', header=None)
dataset_pt21.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
dataset_pt22 = pd.read_table('datasets/coletas/'+volunteer_id+'22-Final.txt', sep=';', header=None)
dataset_pt22.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
dataset_pt23 = pd.read_table('datasets/coletas/'+volunteer_id+'23-Final.txt', sep=';', header=None)
dataset_pt23.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()
dataset_pt24 = pd.read_table('datasets/coletas/'+volunteer_id+'24-Final.txt', sep=';', header=None)
dataset_pt24.columns = 'CH1 CH2 CH3 CH4 Trigger None'.split()

dt_frames = [dataset_pt11, dataset_pt12, dataset_pt13, dataset_pt14,
          dataset_pt21, dataset_pt22, dataset_pt23, dataset_pt24]
dataset = pd.concat(dt_frames)


emg_channels = dataset.iloc[:, :-2].values
emg_trigger = dataset.iloc[:, -2].values

dataset_pt11 = None
dataset_pt12 = None
dataset_pt13 = None
dataset_pt14 = None
dataset_pt21 = None
dataset_pt22 = None
dataset_pt23 = None
dataset_pt24 = None
dt_frames = None
dataset = None
# Here we do the same for obtaining a numpy vector with the movements
# executed in each peek of the trigger.
# targets contains the moviments as a number from 1 to 6
# and targets_str as a string(name)
targets_pt11 = pd.read_table('datasets/coletas/'+volunteer_id+'11-Resposta.txt', header=None)
targets_pt12 = pd.read_table('datasets/coletas/'+volunteer_id+'12-Resposta.txt', header=None)
targets_pt13 = pd.read_table('datasets/coletas/'+volunteer_id+'13-Resposta.txt', header=None)
targets_pt14 = pd.read_table('datasets/coletas/'+volunteer_id+'14-Resposta.txt', header=None)

targets_pt21 = pd.read_table('datasets/coletas/'+volunteer_id+'21-Resposta.txt', header=None)
targets_pt22 = pd.read_table('datasets/coletas/'+volunteer_id+'22-Resposta.txt', header=None)
targets_pt23 = pd.read_table('datasets/coletas/'+volunteer_id+'23-Resposta.txt', header=None)
targets_pt24 = pd.read_table('datasets/coletas/'+volunteer_id+'24-Resposta.txt', header=None)

targets_frames = [targets_pt11, targets_pt12, targets_pt13, targets_pt14,
                  targets_pt21, targets_pt22, targets_pt23, targets_pt24]

targets = pd.concat(targets_frames)

targets_pt11 = None
targets_pt12 = None
targets_pt13 = None
targets_pt14 = None
targets_pt21 = None
targets_pt22 = None
targets_pt23 = None
targets_pt24 = None
targets_frames = None

targets = targets.iloc[:, :].values.ravel()
targets_str = []
for target in targets:
    targets_str.append(HAND_MOVIMENTS_NAMES[target-1])

#####################
#%% Signal constants
#####################

# The empirical delay time between the signal saying to execute a movement and
# the start of some movement by the volunteer.
# We guess a time of 250ms, this means 500 data points at a sampling frequency
# of 2 kHz
# This s a dalay time in the TRIGGER necessary to sync the TRIGGER with the SIGNAL
delay_trigger = 500 # amount of points to delay
fs = 2000  # Sampling frequency in Hz

#########################
#%% Correcting the triger
#########################

# representation of why there are the necessity of syncing the signals
# Before correction:
#     emg signal: __________. .||||||||-.._____________
#                            ''||||||||-''
# trigger signal:       ________________
#                 _____|               |_____________
#
# After Correction:
#     emg signal: __________. .||||||||-.._____________
#                            ''||||||||-''
# trigger signal:           ________________
#                 _________|               |_____________
#

# append concatenates some values in a array.
# Here we insert a array of zeros at the beggining of the trigger
# objectiving to deslocate the signal
# We also exclude the last 'delay_trigger' points of the signal
# to garant that the new array will have the same size of the emg_trigger
emg_trigger_corrected = np.append(arr = np.zeros(delay_trigger),
                                  values = emg_trigger[:-delay_trigger])

###########################
#%% downsampling to 1000Hz
###########################
emg_channels = emg_channels[range(0,len(emg_channels),2),:]
emg_trigger = emg_trigger[range(0,len(emg_trigger),2)]
emg_trigger_corrected = emg_trigger_corrected[range(0,len(emg_trigger_corrected),2)]

###########################
#%% Normalizing
###########################
maximum = max([abs(emg_channels.max()), abs(emg_channels.min())])
emg_channels = emg_channels / maximum
emg_trigger = np.array(emg_trigger > 0.7, dtype=np.uint8)
emg_trigger_corrected = np.array(emg_trigger_corrected > 0.7, dtype=np.uint8)

#####################
#%% Contraction sites
#####################
np.where(np.diff(np.sign(np.diff(
                emg_trigger_corrected
                ))))[0]

s3= np.array(emg_trigger_corrected, dtype=np.int8)
s3[s3==0] = -1     # replace zeros with -1
s4=np.where(np.diff(s3))[0]+1
contractions_onsets = s4[np.arange(0,len(s4),2)]
contractions_offsets = s4[np.arange(1,len(s4),2)]

###############################
#%% OUPUT SIGNAL
###############################
output_signal = emg_trigger_corrected
contractions_lenght = contractions_offsets - contractions_onsets
for n in range(len(contractions_onsets)):
    cont_index = np.arange(contractions_onsets[n],contractions_offsets[n])
    cont_values = targets[n] * np.ones(contractions_lenght[n])
    output_signal[cont_index] = cont_values

###############################
#%% creating new file
###############################
output_data_frame = pd.DataFrame(columns=['CH1', 'CH2', 'CH3', 'CH4', 'OUTPUT'])

output_data_frame['CH1'] = emg_channels[:,0]
output_data_frame['CH2'] = emg_channels[:,1]
output_data_frame['CH3'] = emg_channels[:,2]
output_data_frame['CH4'] = emg_channels[:,3]
output_data_frame['OUTPUT'] = output_signal

file_name_output = 'datasets/volunteer_1.csv'
output_data_frame.to_csv(path_or_buf=file_name_output,header=True)

# TODO: add SQLAlchemy support

###############################
#%% Optional: Plotting the data
###############################

# Here we use the matplotlib library to plot a small window of the signal
# And verify if everything is all right

fig = plt.figure()
axes = [None for i in range(4)]
for i in range(4):
    axes[i] = plt.subplot(4,1,i+1)
    plt.plot(emg_channels[12000:80000,i])
    plt.plot(output_signal[12000:80000]/10.0)
    plt.title('Ch ' + str(i+1))
    plt.ylim((-1,1))
    plt.grid()

axes[0].get_shared_x_axes().join(axes[0],axes[1],axes[2],axes[3])
axes[0].get_shared_y_axes().join(axes[0],axes[1],axes[2],axes[3])
axes[0].set_xticklabels([])
axes[1].set_xticklabels([])
axes[2].set_xticklabels([])
plt.show()
