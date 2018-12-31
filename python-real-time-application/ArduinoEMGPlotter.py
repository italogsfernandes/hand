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
from FeaturesPlotHandler import FeaturesPlotHandler
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
        self.feature_plot_handler = FeaturesPlotHandler(qnt_channels=4,
                                                        parent=parent,
                                                        app=app)
        self.plotHandler.lines[0].set_visible(True)
        self.plotHandler.lines[1].set_visible(False)
        self.plotHandler.lines[2].set_visible(False)
        self.plotHandler.lines[3].set_visible(False)
        self.emg_values = [0] * 4

        self.saving_to_file = False
        self.file_obj = None

        #################################################
        #NOTE: Put it in another place, only for testing:
        #################################################
        self.mva_window_size = 500
        self.ch1_mva_window = np.zeros(self.mva_window_size, dtype='float')
        self.ch2_mva_window = np.zeros(self.mva_window_size, dtype='float')
        self.ch3_mva_window = np.zeros(self.mva_window_size, dtype='float')
        self.ch4_mva_window = np.zeros(self.mva_window_size, dtype='float')

        self.noise_vector = np.random.normal(-1,1,100)
        self.noise_index = 0

        self.features_window_size = 200
        self.features_window_index = 0
        self.features_window_overlap = 20 # 10% of 200
        self.ch1_features_window = np.zeros(self.features_window_size, dtype='float')
        self.ch2_features_window = np.zeros(self.features_window_size, dtype='float')
        self.ch3_features_window = np.zeros(self.features_window_size, dtype='float')
        self.ch4_features_window = np.zeros(self.features_window_size, dtype='float')

        self.ch1_features = {}
        self.ch2_features = {}
        self.ch3_features = {}
        self.ch4_features = {}

        self.division_factors = [0.3, 100.0, 0.2, 0.9, 55.0, 150.0]
        ######################################################
        #NOTE: Put it in another place, only for testing [END]
        ######################################################

    def start_saving_to_file_routine(self, file_name):
        # Open file
        self.file_obj = open(file_name, mode='w+')
        # Write Header
        self.file_obj.write("CH1,CH2,CH3,CH4,OUTPUT\n")
        # Adding Flag
        self.saving_to_file = True

    def stop_saving_to_file_routine(self):
        # Stopping Flag
        self.saving_to_file = False
        # Closing file
        self.file_obj.close()

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

    def start(self):
        """
        Set a started flag to True and starts the following tasks: (in this order)
        timerStatus : for updating the status label.
        plotHandler : timer for updating the plot.
        consumerThread : for redirect the data from the arduino to the plotter.
        arduinoHandler : serial port acquisition with a thread.
        """
        self.arduinoHandler.open()
        if self.arduinoHandler.serialPort.isOpen():
            self.started = True
            self.timerStatus.start()
            self.plotHandler.timer.start(0)
            self.feature_plot_handler.start_update()
            self.consumerThread.start()
            self.arduinoHandler.start_acquisition()

    def stop(self):
        """
        Set a started flag to False and stops the following tasks: (in this order)
        arduinoHandler : serial port acquisition with a thread.
        consumerThread : for redirect the data from the arduino to the plotter.
        timerStatus : for updating the status label.
        plotHandler : timer for updating the plot.
        """
        self.started = False
        self.arduinoHandler.stop_acquisition()
        self.consumerThread.stop()
        self.timerStatus.stop()
        self.plotHandler.timer.stop()
        self.feature_plot_handler.stop_update()
        self.stop_saving_to_file_routine()


    #NOTE: I will put the process found inside the counsumer function inside this fuctions:
    # def add_to_mva_window(self, input_number, actual_mva_window):
    # def apply_moving_average_high_pass_filter(self, input_array, window_size):
    # def apply_ajusts_for_simulation(self, raw_emg_values)

    @staticmethod
    def get_rms_feature(input_array):
        return np.sqrt(np.mean(np.square(
           input_array)))

    @staticmethod
    def get_zc_feature(input_array):
        s3= np.sign(
         input_array)
        s3[s3==0] = -1     # replace zeros with -1
        return (np.where(np.diff(s3)))[0].shape[0]

    @staticmethod
    def get_mav_feature(input_array):
        return np.mean(np.abs(
                input_array))

    @staticmethod
    def get_var_feature(input_array):
        return np.var(
                input_array)

    @staticmethod
    def get_wl_feature(input_array):
        return np.sum(np.abs(np.diff(
                input_array)))

    @staticmethod
    def get_ssc_feature(input_array):
        return np.where(np.diff(np.sign(np.diff(
                input_array))))[0].shape[0]

    def apply_feature_extraction(self):

        ########
        # RMS
        self.ch1_features['rms'] = ArduinoEMGPlotter.get_rms_feature(self.ch1_features_window)
        self.ch2_features['rms'] = ArduinoEMGPlotter.get_rms_feature(self.ch2_features_window)
        self.ch3_features['rms'] = ArduinoEMGPlotter.get_rms_feature(self.ch3_features_window)
        self.ch4_features['rms'] = ArduinoEMGPlotter.get_rms_feature(self.ch4_features_window)
        ########
        # ZC
        self.ch1_features['zc'] = ArduinoEMGPlotter.get_zc_feature(self.ch1_features_window)
        self.ch2_features['zc'] = ArduinoEMGPlotter.get_zc_feature(self.ch2_features_window)
        self.ch3_features['zc'] = ArduinoEMGPlotter.get_zc_feature(self.ch3_features_window)
        self.ch4_features['zc'] = ArduinoEMGPlotter.get_zc_feature(self.ch4_features_window)
        ########
        # MAV
        self.ch1_features['mav'] = ArduinoEMGPlotter.get_mav_feature(self.ch1_features_window)
        self.ch2_features['mav'] = ArduinoEMGPlotter.get_mav_feature(self.ch2_features_window)
        self.ch3_features['mav'] = ArduinoEMGPlotter.get_mav_feature(self.ch3_features_window)
        self.ch4_features['mav'] = ArduinoEMGPlotter.get_mav_feature(self.ch4_features_window)
        ########
        # VAR
        self.ch1_features['var'] = ArduinoEMGPlotter.get_var_feature(self.ch1_features_window)
        self.ch2_features['var'] = ArduinoEMGPlotter.get_var_feature(self.ch2_features_window)
        self.ch3_features['var'] = ArduinoEMGPlotter.get_var_feature(self.ch3_features_window)
        self.ch4_features['var'] = ArduinoEMGPlotter.get_var_feature(self.ch4_features_window)
        ########
        # WL
        self.ch1_features['wl'] = ArduinoEMGPlotter.get_wl_feature(self.ch1_features_window)
        self.ch2_features['wl'] = ArduinoEMGPlotter.get_wl_feature(self.ch2_features_window)
        self.ch3_features['wl'] = ArduinoEMGPlotter.get_wl_feature(self.ch3_features_window)
        self.ch4_features['wl'] = ArduinoEMGPlotter.get_wl_feature(self.ch4_features_window)
        ########
        # SSC
        self.ch1_features['ssc'] = ArduinoEMGPlotter.get_ssc_feature(self.ch1_features_window)
        self.ch2_features['ssc'] = ArduinoEMGPlotter.get_ssc_feature(self.ch2_features_window)
        self.ch3_features['ssc'] = ArduinoEMGPlotter.get_ssc_feature(self.ch3_features_window)
        self.ch4_features['ssc'] = ArduinoEMGPlotter.get_ssc_feature(self.ch4_features_window)

    def send_features_to_plot(self):
        if self.feature_plot_handler.is_enabled:
            ########
            # RMS
            if self.feature_plot_handler.series[0].visible:
                self.feature_plot_handler.series[0].plot(np.array([self.ch1_features['rms'],
                                                          self.ch2_features['rms'],
                                                          self.ch3_features['rms'],
                                                          self.ch4_features['rms']])/self.division_factors[0])
            if self.feature_plot_handler.series[1].visible:
                self.feature_plot_handler.series[1].plot(np.array([self.ch1_features['zc'],
                                                          self.ch2_features['zc'],
                                                          self.ch3_features['zc'],
                                                          self.ch4_features['zc']])/self.division_factors[1])
            if self.feature_plot_handler.series[2].visible:
                self.feature_plot_handler.series[2].plot(np.array([self.ch1_features['mav'],
                                                          self.ch2_features['mav'],
                                                          self.ch3_features['mav'],
                                                          self.ch4_features['mav']])/self.division_factors[2])
            if self.feature_plot_handler.series[3].visible:
                self.feature_plot_handler.series[3].plot(np.array([self.ch1_features['var'],
                                                          self.ch2_features['var'],
                                                          self.ch3_features['var'],
                                                          self.ch4_features['var']])/self.division_factors[3])
            if self.feature_plot_handler.series[4].visible:
                self.feature_plot_handler.series[4].plot(np.array([self.ch1_features['wl'],
                                                          self.ch2_features['wl'],
                                                          self.ch3_features['wl'],
                                                          self.ch4_features['wl']])/self.division_factors[4])
            if self.feature_plot_handler.series[5].visible:
                self.feature_plot_handler.series[5].plot(np.array([self.ch1_features['ssc'],
                                                          self.ch2_features['ssc'],
                                                          self.ch3_features['ssc'],
                                                          self.ch4_features['ssc']])/self.division_factors[5])
    def consumer_function(self):
        """ If there are some data in the queue, add this to the plot.
        """
        ################################
        #TODO: to plot features
        #TODO: On/off button in chart
        #TODO: record raw data
        #TODO: screen for saving a "coleta", to be used as a dataset
        #TODO: Screen for design a RNA and save it
        #TODO: Training screen
        #TODO: Options checkbox for what is included in the pre processing and processing
        ################################
        if self.arduinoHandler.data_waiting:
            self.emg_values = np.array(self.arduinoHandler.buffer_acquisition.get(), dtype=float)
            self.emg_values = self.emg_values * 5.0/1024.0 - 2.5

            ####################################################
            ## Only for simulation: Ajusting some values
            self.noise_index = self.noise_index + 1 if self.noise_index < 99 else 0
            self.emg_values[self.emg_values == 0] += (-0.045 + self.noise_vector[self.noise_index] * 0.0075)
            ####################################################

            ####################################################
            # Creating windows for pre processing
            self.ch1_mva_window[:-1] = self.ch1_mva_window[1:]
            self.ch1_mva_window[-1] = self.emg_values[0]

            self.ch2_mva_window[:-1] = self.ch2_mva_window[1:]
            self.ch2_mva_window[-1] = self.emg_values[1]

            self.ch3_mva_window[:-1] = self.ch3_mva_window[1:]
            self.ch3_mva_window[-1] = self.emg_values[2]

            self.ch4_mva_window[:-1] = self.ch4_mva_window[1:]
            self.ch4_mva_window[-1] = self.emg_values[3]
            ####################################################

            ####################################################
            # Applying high-pass mva filter to remove offset
            self.emg_values[0] -= np.mean(self.ch1_mva_window)
            self.emg_values[1] -= np.mean(self.ch2_mva_window)
            self.emg_values[2] -= np.mean(self.ch3_mva_window)
            self.emg_values[3] -= np.mean(self.ch4_mva_window)
            ####################################################

            ####################################################
            # Creating windows for extraction of features
            #BUG: I don't know if this will work, but I hope so. I'm still have to test it
            # Adding values to window
            self.ch1_features_window[self.features_window_index] = self.emg_values[0]
            self.ch2_features_window[self.features_window_index] = self.emg_values[1]
            self.ch3_features_window[self.features_window_index] = self.emg_values[2]
            self.ch4_features_window[self.features_window_index] = self.emg_values[3]
            #
            # 0 1 2 3 4 5 6 7 8 9 10
            # 0 1 2 3 4
            #         4 5 6 7
            #               7 8 9 1
            # incrementing index
            self.features_window_index = self.features_window_index + 1
            if self.features_window_index >= self.features_window_size:
                self.features_window_index = self.features_window_overlap
                self.ch1_features_window[:self.features_window_overlap] = self.ch1_features_window[-self.features_window_overlap:]
                self.ch2_features_window[:self.features_window_overlap] = self.ch2_features_window[-self.features_window_overlap:]
                self.ch3_features_window[:self.features_window_overlap] = self.ch3_features_window[-self.features_window_overlap:]
                self.ch4_features_window[:self.features_window_overlap] = self.ch4_features_window[-self.features_window_overlap:]
            ####################################################

            ####################################################
            # Extracting features
            if self.features_window_index == self.features_window_overlap:
                # if I had completed a window and i'm ready to start the next one
                self.apply_feature_extraction()
                self.send_features_to_plot()
            ####################################################


            ####################################################
            # Applying some adjusts to allow a good plot
            for n in range(4):
                self.emg_values[n] = self.emg_values[n] + n
            ####################################################

            ####################################################
            # Sending data to chart
            if self.plotHandler.is_enabled:
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
