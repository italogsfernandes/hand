#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%% Importing the libraries
import pandas as pd # reading files
import numpy as np # handling numerical data
import matplotlib.pyplot as plt # Plotting
from scipy import signal

def do_moving_average(raw_signal, window_size):
    wd = np.ones(window_size)
    mva_signal = np.convolve(raw_signal, wd, mode='valid') / window_size
    signal_with_delay = np.zeros(window_size - 1)
    signal_with_delay = np.append(signal_with_delay, mva_signal)
    return signal_with_delay

def do_high_pass_mva(raw_signal, window_size):
    filtered_signal = raw_signal - do_moving_average(raw_signal, window_size)
    return filtered_signal

def do_band_pass_mva(raw_signal, window_low_size, window_high_size):
    higher_freqs = do_high_pass_mva(raw_signal, window_low_size)
    lower_freqs = do_moving_average(higher_freqs, window_high_size)
    return lower_freqs

def do_band_stop_mva(raw_signal, window_low_size, window_high_size):
    stop_freqs = do_band_pass_mva(raw_signal, window_low_size, window_high_size)
    filtered_signal = raw_signal - stop_freqs
    return filtered_signal
