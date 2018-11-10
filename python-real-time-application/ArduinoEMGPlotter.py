# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# FEDERAL UNIVERSITY OF UBERLANDIA
# Faculty of Electrical Engineering
# Biomedical Engineering Lab
# ------------------------------------------------------------------------------
# Author: Italo Gustavo Sampaio Fernandes
# Contact: italogsfernandes@gmail.com
# Git: www.github.com/italogsfernandes
# ------------------------------------------------------------------------------
# Description:
# ------------------------------------------------------------------------------
from EMGPlotHandler import EMGPlotHandler
from libraries.QtArduinoPlotter import QtArduinoPlotter
from libraries.ArduinoHandler import ArduinoHandler
# ------------------------------------------------------------------------------
import numpy as np
import scipy.fftpack as fftpack
from scipy.signal import butter, lfilter, freqz, filtfilt
from collections import deque
# ------------------------------------------------------------------------------


class EMGProcessing:
    def __init__(self):
        """
        Routines for processing a emg raw data.
        """
        self.window_size = 256
        self.fs = 1000
        self.filter_params = dict()

        [b, a] = EMGProcessing.design_butter_lowpass(7, self.fs, 2)
        self.filter_params['b'] = b
        self.filter_params['a'] = a

        self.buffer = deque(maxlen=self.window_size)
        self.hilbert = np.zeros(self.window_size, dtype='float')
        self.hilbert_retificado = np.zeros(self.window_size, dtype='float')
        self.window = 100

    def update_values(self):
        """
        Removes the points of the emg buffer, process it
        """
        points_to_add = len(self.buffer)
        if points_to_add > 0:
            for n in range(points_to_add):  # obtains the new values
                num = self.buffer.popleft()
                self.emg_bruto.append(num)
                self.emg_bruto.pop(0)
            self.do_process()

    def do_process(self):
        """
        Process the data
        """
        #self.hilbert = fftpack.hilbert(self.emg_bruto)#+self.emg_bruto[::-1])
        self.hilbert = self.emg_bruto - EMGProcessing.do_moving_average(self.emg_bruto, 5) #+self.emg_bruto[::-1])
        self.hilbert_retificado = np.abs(self.hilbert)

        self.envoltoria = \
            filtfilt(self.filter_params['b'], self.filter_params['a'], self.hilbert_retificado,
                     #method='gust') * 3.8
                     padtype='even', padlen=128) * 3.8
        #self.envoltoria = \
        #    EMGProcessing.do_moving_average(self.hilbert_retificado, 128)*3.8
        #self.envoltoria = \
        #    np.convolve(self.hilbert_retificado, self.weights, 'same') * 3.8
        # self.envoltoria = EMGProcessing.do_moving_average(self.hilbert_retificado,100)
        self.detection_sites = self.envoltoria > self.threshold

        #self.hilbert = self.hilbert[0: self.window_size]
        #self.hilbert_retificado = self.hilbert_retificado[0: self.window_size]
        #self.envoltoria = self.envoltoria[0: self.window_size]
        #self.detection_sites = self.detection_sites[0: self.window_size]


    @staticmethod
    def do_moving_average(values, window):
        weights = np.repeat(1.0, window) / window
        sma = np.convolve(values, weights, 'same')
        return sma

    @staticmethod
    def design_butter_lowpass(cutoff, fs, order=5):
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq
        [b, a] = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a


class ArduinoEMGPlotter(QtArduinoPlotter):
    def __init__(self, parent, app=None, label=None):
        QtArduinoPlotter.__init__(self, parent, app, label)
        self.arduinoHandler = ArduinoHandler(qnt_ch=4)
        self.process = EMGProcessing()
        self.plotHandler.lines[0].set_visible(True)
        self.plotHandler.lines[1].set_visible(False)
        self.plotHandler.lines[2].set_visible(False)
        self.plotHandler.lines[3].set_visible(False)
        self.emg_values = [0] * 4
        #################################################
        #NOTE: Put it in another place, only for testing:
        #################################################
        self.window_size = 500
        self.ch1_window = np.zeros(self.window_size, dtype='float')
        self.ch2_window = np.zeros(self.window_size, dtype='float')
        self.ch3_window = np.zeros(self.window_size, dtype='float')
        self.ch4_window = np.zeros(self.window_size, dtype='float')
        self.noise_vector = np.random.normal(-1,1,100)
        self.noise_index = 0

    def get_buffers_status(self, separator):
        """
        Returns a string like:
            Serial:    4/1024 - Acq:    1/1024 - Plot:  30/1024
        :param separator: Separates the strings, example ' - ', ' | ', '\n'
        :return: A string containing the status of all the buffers involved in the acquisition and plotting.
        """
        return self.arduinoHandler.get_buffers_status(separator) + separator + \
               self.plotHandler.lines[0].get_buffers_status()

    def _init_plotHandler(self, parent, app):
        """
        Only initializes the plotHandler object. It is set as a method to allow override.
        """
        self.plotHandler = EMGPlotHandler(qnt_points=4096, parent=parent, y_range=(-0.3, 3.3),
                                          app=app)

    #NOTE: I will put the process found inside the counsumer function inside this fuctions:
    # def add_to_window(self, input_number, actual_window):
    # def apply_moving_average_high_pass_filter(self, input_array, window_size):
    # def apply_ajusts_for_simulation(self, raw_emg_values)

    def consumer_function(self):
        """ If there are some data in the queue, add this to the plot.
        """
        if self.arduinoHandler.data_waiting:
            self.emg_values = np.array(self.arduinoHandler.buffer_acquisition.get(), dtype=float)
            self.emg_values = self.emg_values * 5.0/1024.0 - 2.5

            ####################################################
            ## Only for simulation: Ajusting some values
            self.noise_index = self.noise_index + 1 if self.noise_index < 99 else 0
            self.emg_values[self.emg_values == 0] += (-0.045 + self.noise_vector[self.noise_index] * 0.0075)
            ####################################################

            ####################################################
            # Creating windows
            self.ch1_window[:-1] = self.ch1_window[1:]
            self.ch1_window[-1] = self.emg_values[0]

            self.ch2_window[:-1] = self.ch2_window[1:]
            self.ch2_window[-1] = self.emg_values[1]

            self.ch3_window[:-1] = self.ch3_window[1:]
            self.ch3_window[-1] = self.emg_values[2]

            self.ch4_window[:-1] = self.ch4_window[1:]
            self.ch4_window[-1] = self.emg_values[3]
            ####################################################

            ####################################################
            # Applying high-pass mva filter to remove offset
            self.emg_values[0] -= np.mean(self.ch1_window)
            self.emg_values[1] -= np.mean(self.ch2_window)
            self.emg_values[2] -= np.mean(self.ch3_window)
            self.emg_values[3] -= np.mean(self.ch4_window)
            ####################################################

            ####################################################
            # Applying some adjusts to allow a good plot
            for n in range(4):
                self.emg_values[n] = self.emg_values[n] + n
            ####################################################

            ####################################################
            # Sending data to chart
            self.plotHandler.lines[0].buffer.put(self.emg_values[0])
            self.plotHandler.lines[1].buffer.put(self.emg_values[1])
            self.plotHandler.lines[2].buffer.put(self.emg_values[2])
            self.plotHandler.lines[3].buffer.put(self.emg_values[3])
            ####################################################


def test():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    harry_plotter = ArduinoEMGPlotter(parent=central_widget)#, app=app)
    harry_plotter.start()

    vertical_layout.addWidget(harry_plotter.plotHandler.plotWidget)
    form.setCentralWidget(central_widget)
    form.show()
    app.exec_()
    harry_plotter.stop()

if __name__ == '__main__':
    test()
