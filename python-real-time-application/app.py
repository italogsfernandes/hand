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
from ArduinoEMGPlotter import ArduinoEMGPlotter

import sys

# Including Libraries according to python version
if sys.version_info.major == 3:
    # PyQt5
    from PyQt5.QtWidgets import *
    from views import base_project_main_qt5 as base
    from PyQt5 import QtCore
elif sys.version_info.major == 2:
    # PyQt4
    from PyQt4.QtGui import *
    from views import base_project_main_qt4 as base
    from PyQt4 import QtCore
    from PyQt4.QtCore import SIGNAL
else:
    print("Python version not supported.")

# ------------------------------------------------------------------------------
# MAIN CLASS
# ------------------------------------------------------------------------------
class HandProjectApp(QMainWindow, base.Ui_MainWindow):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        # Configuring UI, seting up chart, etc:
        self.setupUi(self)
        # connections between buttons and methods:
        self.setup_signals_connections()

        # Object to acquire EMG signals and plot it (using the serial port).
        self.emg_app = ArduinoEMGPlotter(parent=self.centralwidget,label=self.lbl_status)

        ####################
        ###### Some Ui modifications
        ### Combo box features
        self.cb_features.addItems(("RMS - Root Mean Square",
                                   "ZC - Zero Crossing",
                                   "MAV - Mean Absolute Value",
                                   "VAR - Variance",
                                   "WL - Wave Length",
                                   "SSC - Slope Signal Change"))
        self.cb_features.currentIndex = 0

        #### Chart EMG
        # Adding object to a specific place in the layout
        self.verticalLayoutGraph.addWidget(self.emg_app.plotHandler.plotWidget)
        # for design reasons I put a label widged in the place, now I need to
        # remove it
        self.verticalLayoutGraph.removeWidget(self.label_replace)
        self.label_replace.setParent(None)

        #### Chart Features
        # Adding object to a specific place in the layout
        self.verticalLayoutGraph_features.addWidget(self.emg_app.feature_plot_handler.plotWidget)
        # for design reasons I put a label widged in the place, now I need to
        # remove it
        self.verticalLayoutGraph_features.removeWidget(self.label_replace_features)
        self.label_replace_features.setParent(None)

        # Setting up inicial conditions:
        self.cb_ch1.toggle() # enabling visibility of channel
        self.cb_ch2.toggle() # enabling visibility of channel
        self.cb_ch3.toggle() # enabling visibility of channel
        self.cb_ch4.toggle() # enabling visibility of channel

        self.emg_app.feature_plot_handler.series[0].set_visible(True) # 0.3
        self.emg_app.feature_plot_handler.series[1].set_visible(True) # 100.0
        self.emg_app.feature_plot_handler.series[2].set_visible(True) # 0.2
        self.emg_app.feature_plot_handler.series[3].set_visible(True) # 0.9
        self.emg_app.feature_plot_handler.series[4].set_visible(True) # 55.0
        self.emg_app.feature_plot_handler.series[5].set_visible(True) # 150.0

        # trying to start acquisition
        try:
            self.emg_app.start()
            self.actionStartAcquisition.setText("Stop Acquisition")
        except Exception as e:
            self.statusbar.showMessage("Not possible to automatically start. Please verify USB connection.")
            self.lbl_status.setText("Select Functions -> Start Acquisition for start.")

    def setup_signals_connections(self):
        """ Connects the events of objects in the view (buttons, combobox, etc)
        to respective methods.
        """
        self.actionStartAcquisition.triggered.connect(self.start_stop_acquisition)
        self.actionFind_Serial_Port.triggered.connect(self.find_serial_port)
        self.cb_ch1.toggled.connect(lambda x: self.emg_app.plotHandler.lines[0].set_visible(x))
        self.cb_ch2.toggled.connect(lambda x: self.emg_app.plotHandler.lines[1].set_visible(x))
        self.cb_ch3.toggled.connect(lambda x: self.emg_app.plotHandler.lines[2].set_visible(x))
        self.cb_ch4.toggled.connect(lambda x: self.emg_app.plotHandler.lines[3].set_visible(x))
        self.cb_chart_emg_on_off.toggled.connect(self.turn_chart_emg_on_off)
        self.cb_chart_features_on_off.toggled.connect(self.turn_chart_features_on_off)
        self.tabWidget.currentChanged.connect(self.tab_changed)

    def tab_changed(self, tab_index):
        """ For every change in the visible tab, it disables the unused threads.
        And it enables the threads corresponding to the visible information.
        """
        if tab_index == 0:
            self.emg_app.plotHandler.enable()
            print("enabled")
        else:
            self.emg_app.plotHandler.disable()
            print("disabled")

        if tab_index == 1:
            self.emg_app.feature_plot_handler.enable()
            print("enabled")
        else:
            self.emg_app.feature_plot_handler.disable()
            print("disabled")


    def find_serial_port(self):
        """ Try to find a active serial port.
        """
        bar_foo = self.emg_app.arduinoHandler.update_port_name()
        self.statusbar.showMessage(bar_foo)
        self.lbl_status.setText(bar_foo)

    def turn_chart_emg_on_off(self, cb_value):
        """ Enables and disables the emg chart.
        """
        if self.emg_app.plotHandler.is_enabled:
            self.emg_app.plotHandler.disable()
        else:
            self.emg_app.plotHandler.enable()

    def turn_chart_features_on_off(self, cb_value):
        """ Enables and disables the features chart.
        """
        if self.emg_app.feature_plot_handler.is_enabled:
            self.emg_app.feature_plot_handler.disable()
        else:
            self.emg_app.feature_plot_handler.enable()

    def closeEvent(self, q_close_event):
        """ Method called when the application is being closed.
        Closes the serial port before closing application.
        """
        self.emg_app.stop()
        super(self.__class__, self).closeEvent(q_close_event)

    def start_stop_acquisition(self):
        """ toggle the acquision.
        """
        if not self.emg_app.started:
            try:
                self.emg_app.start()
                self.actionStartAcquisition.setText("Stop Acquisition")
            except Exception as e:
                self.statusbar.showMessage("Not possible to start (" + str(e) +").")
        else:
            self.emg_app.stop()
            self.actionStartAcquisition.setText("Start Acquisition")

# ------------------------------------------------------------------------------
def main():
    """Main function
    Instantialize the objects and runs the app.
    """
    app = QApplication(sys.argv)
    form = HandProjectApp()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
