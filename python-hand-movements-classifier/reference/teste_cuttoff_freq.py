#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%% Importing the libraries
import numpy as np # handling numerical data
import matplotlib.pyplot as plt # Plotting

Fs = 1000
T = 3
N = Fs*T
time = np.linspace(0,T,N)
freqs = np.arange(1,500)*0.333555703802535
all_freq_signal = np.zeros(N)
for freq in freqs:
    all_freq_signal = all_freq_signal + np.sin(2*np.pi*freq*time)

f = np.abs(np.fft.fft(all_freq_signal)) / len(time)
f = f[:int(len(f)/2)]*2
flabel = np.linspace(0,Fs/2, len(f))

filtered_signal = do_moving_average(all_freq_signal, 5)
ff = np.abs(np.fft.fft(filtered_signal)) / len(time)
ff = ff[:int(len(ff)/2)]*2

db = 10 * np.log10(ff/f)
#plt.figure()
#plt.plot(time, all_freq_signal)

plt.figure()
plt.plot(flabel,f)
plt.plot(flabel,ff)

plt.figure()
plt.plot(flabel, db)

plt.show()
