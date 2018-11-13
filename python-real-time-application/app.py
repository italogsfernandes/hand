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
    print("Versao do python nao suportada")
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
        # Adding object to a specific place in the layout
        self.verticalLayoutGraph.addWidget(self.emg_app.plotHandler.plotWidget)
        # for design reasons I put a label widged in the place, now I need to
        # remove it
        self.verticalLayoutGraph.removeWidget(self.label_replace)
        self.label_replace.setParent(None)

        # Setting up inicial conditions:
        self.cb_ch1.toggle() # enabling visibility of channel
        self.cb_ch2.toggle() # enabling visibility of channel
        self.cb_ch3.toggle() # enabling visibility of channel
        self.cb_ch4.toggle() # enabling visibility of channel

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
        self.tabWidget.currentChanged.connect(self.tab_changed)

    def tab_changed(self, tab_index):
        print("tab changed: " + str(tab_index))
        
    def find_serial_port(self):
        bar_foo = self.emg_app.arduinoHandler.update_port_name()
        self.statusbar.showMessage(bar_foo)
        self.lbl_status.setText(bar_foo)

    def turn_chart_emg_on_off(self, cb_value):
        if self.emg_app.plotHandler.is_enabled:
            self.emg_app.plotHandler.disable()
        else:
            self.emg_app.plotHandler.enable()

    def closeEvent(self, q_close_event):
        self.emg_app.stop()
        super(self.__class__, self).closeEvent(q_close_event)

    def start_stop_acquisition(self):
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
