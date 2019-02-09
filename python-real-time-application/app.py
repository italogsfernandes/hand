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
from ArduinoOutputController import ArduinoOutputController

import sys
import os

import serial.tools.list_ports as serial_tools

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

        ##############
        # Serial Port Selection
        ##############
        serial_ports = serial_tools.comports()

        self.cb_in_serial_port.addItem("None")
        self.cb_out_serial_port.addItem("None")

        for s_port in serial_ports:
            self.cb_in_serial_port.addItem(str(s_port))
            self.cb_out_serial_port.addItem(str(s_port))

        self.cb_in_serial_port.selected = 0
        self.cb_out_serial_port.selected = 0
        #############

        #Output
        self.servo_controller = ArduinoOutputController()
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

        self.tabWidget.setCurrentIndex(5)

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
        self.btn_record_raw_emg.clicked.connect(self.btn_record_raw_emg_clicked)
        self.btn_generate_training_file.clicked.connect(self.btn_generate_training_file_clicked)
        #self.connect(self.cb_in_serial_port,SIGNAL('currentIndexChanged(int)'),self.cb_in_serial_port_changed)
        #self.connect(self.cb_out_serial_port,SIGNAL('currentIndexChanged(int)'),self.cb_out_serial_port_changed)
        self.btn_go.clicked.connect(self.btn_go_clicked)
        self.h_slider_1.valueChanged.connect(self.sliders_changed)
        self.h_slider_2.valueChanged.connect(self.sliders_changed)
        self.h_slider_3.valueChanged.connect(self.sliders_changed)
        self.h_slider_4.valueChanged.connect(self.sliders_changed)
        self.h_slider_5.valueChanged.connect(self.sliders_changed)
        self.btn_reset_position.clicked.connect(self.btn_reset_position_clicked)
        self.btn_send_position.clicked.connect(self.btn_send_position_clicked)

    def btn_send_position_clicked(self):
        f_values = [self.h_slider_1.value(),
                    self.h_slider_2.value(),
                    self.h_slider_3.value(),
                    self.h_slider_4.value(),
                    self.h_slider_5.value()]
        self.servo_controller.send_new_cmd(f_values)

    def btn_reset_position_clicked(self):
        self.h_slider_1.setValue(0)
        self.h_slider_2.setValue(0)
        self.h_slider_3.setValue(0)
        self.h_slider_4.setValue(0)
        self.h_slider_5.setValue(0)
        self.btn_send_position_clicked()

    def sliders_changed(self):
        self.groupBox_f1.setTitle(u'Finger 1: %dº' % self.h_slider_1.value())
        self.groupBox_f2.setTitle(u'Finger 2: %dº' % self.h_slider_2.value())
        self.groupBox_f3.setTitle(u'Finger 3: %dº' % self.h_slider_3.value())
        self.groupBox_f4.setTitle(u'Finger 4: %dº' % self.h_slider_4.value())
        self.groupBox_f5.setTitle(u'Finger 5: %dº' % self.h_slider_5.value())

    def btn_go_clicked(self):
        port_in_name = str(self.cb_in_serial_port.itemText(self.cb_in_serial_port.currentIndex()))
        port_out_name = str(self.cb_out_serial_port.itemText(self.cb_out_serial_port.currentIndex()))

        if port_out_name != "None":
            port_out_name = port_out_name.split()[0]
            self.servo_controller.open_port(port_out_name)
            self.tabWidget.setCurrentIndex(3)

        #0 90 30 40 50

    def cb_in_serial_port_changed(self, new_index):
        pass

    def cb_out_serial_port_changed(self, new_index):
        pass

    def btn_generate_training_file_clicked(self):
        #################################################
        # Selecting file
        #################################################
        fileName = QFileDialog.getOpenFileNames(self,
                        "Open Raw EMG Recording",
                        "",
                        "CSV files (*.csv)",
                        options = QFileDialog.DontUseNativeDialog)
        #################################################
        # Condition 2
        #################################################
        if not fileName:
            return

        #################################################
        # Updating interface
        #################################################
        if len(fileName) == 1:
            self.statusbar.showMessage("File selected: " + fileName[0].split('/')[-1])
        elif len(fileName) == 2:
            self.statusbar.showMessage("Files selected: " + fileName[0].split('/')[-1] + " and " + fileName[1].split('/')[-1])
        elif len(fileName) >= 3:
            self.statusbar.showMessage("Files selected: " + fileName[0].split('/')[-1] + " and others " + str(len(fileName) - 1) + " files.")
        #self.btn_record_raw_emg.setText("Stop Recording")

        #################################################
        # Starting recording process
        #################################################
        #self.emg_app.start_saving_to_file_routine(fileName)


    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if not event.isAutoRepeat():
                if self.emg_app.saving_to_file:
                    self.emg_app.move_output_value = event.text()
                    self.lbl_output_value.setText(event.text())
                    self.statusbar.showMessage("key pressed: " + str(event.text()))

    def keyReleaseEvent(self, event):
        if type(event) == QKeyEvent:
            if not event.isAutoRepeat():
                if self.emg_app.saving_to_file:
                    self.emg_app.move_output_value = "0"
                    self.lbl_output_value.setText("None")
                    self.statusbar.showMessage("key released: " + str(event.text()))

    def btn_record_raw_emg_clicked(self):
        """ Save values to a file.
        1. Select the file.
        2. Acquisition should be already running.
        3.
        """
        #################################################
        # Stop actual recording
        #################################################
        if self.emg_app.saving_to_file:
            self.emg_app.stop_saving_to_file_routine()
            self.label_file_name.setText("File: None")
            self.btn_record_raw_emg.setText("Start Recording")
        #################################################
        # Start a recording
        #################################################
        else:
            #################################################
            # Condition 1
            #################################################
            if not self.emg_app.started:
                ret = QMessageBox.critical(self, "Critical",
                      'Acquisition should be started before recording.',
                      QMessageBox.Ok)
                if ret == QMessageBox.Ok:
                    return
            #################################################
            # Selecting file
            #################################################
            fileName = QFileDialog.getSaveFileName(self,
                            "Save Raw EMG Recording",
                            "",
                            "CSV files (*.csv)",
                            options = QFileDialog.DontUseNativeDialog)
            #################################################
            # Condition 2
            #################################################
            if not fileName:
                return

            # Garanting compatibility between python 2 and 3
            if sys.version_info.major == 3:
                fileName = fileName[0]

            #################################################
            # Updating interface
            #################################################
            self.statusbar.showMessage("File selected: " + str(fileName))
            self.label_file_name.setText("File: " + fileName.split('/')[-1])
            self.btn_record_raw_emg.setText("Stop Recording")

            #################################################
            # Starting recording process
            #################################################
            self.emg_app.start_saving_to_file_routine(fileName)

    def tab_changed(self, tab_index):
        """ For every change in the visible tab, it disables the unused threads.
        And it enables the threads corresponding to the visible information.
        """
        if tab_index == 0:
            self.emg_app.plotHandler.enable()
        else:
            self.emg_app.plotHandler.disable()

        if tab_index == 1:
            self.emg_app.feature_plot_handler.enable()
        else:
            self.emg_app.feature_plot_handler.disable()


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
