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
        # None

    def setup_signals_connections(self):
        """ Connects the events of objects in the view (buttons, combobox, etc)
        to respective methods.
        """
        self.cb_ch1.toggled.connect(lambda x: self.emg_app.plotHandler.emg_bruto.set_visible(x))
        self.cb_ch2.toggled.connect(lambda x: self.emg_app.plotHandler.hilbert.set_visible(x))
        self.cb_ch3.toggled.connect(lambda x: self.emg_app.plotHandler.hilbert_retificado.set_visible(x))
        self.cb_ch4.toggled.connect(lambda x: self.emg_app.plotHandler.envoltoria.set_visible(x))

    def closeEvent(self, q_close_event):
        self.emg_app.stop()
        super(self.__class__, self).closeEvent(q_close_event)

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
