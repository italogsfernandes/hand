# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
# FEDERAL UNIVERSITY OF UBERLANDIA
# Faculty of Electrical Engineering
# Biomedical Engineering Lab
# ------------------------------------------------------------------------------
# Author: Italo Gustavo Sampaio Fernandes
# Contact: italogsfernandes@gmail.com
# Git: www.github.com/italogfernandes
# ------------------------------------------------------------------------------
# Description:
# ------------------------------------------------------------------------------
from .ThreadHandler import ThreadHandler, InfiniteTimer
from .ArduinoHandler import ArduinoHandler
from .PyQtGraphHandler import PyQtGraphHandler
# ------------------------------------------------------------------------------


class QtArduinoPlotter:
    def __init__(self, parent, app=None, label=None):
        """
        Initializes all the objects for a arduino acquisition and plotting.
        It has:
        plotHandler: Handles the continuous plot.
        arduinoHandler: Handles the arduino acquisition.
        consumerThread: Redirects the acquire data from the arduinoHandler to the plotHandler.

        See the code of the test function in this file for an example.
        :param parent: The parent to be passed to the pyqtPlotWidget.
        :param app: If it is set, it will be passed to the plotwidget to be updated with every plot update.
        :param label: If it is set as a QtLabel, this label will be updated with the status of the buffers.
        """
        self.plotHandler = None
        self.label = label
        self._init_plotHandler(parent, app)
        self.arduinoHandler = ArduinoHandler()
        self.consumerThread = ThreadHandler(self.consumer_function)
        self.timerStatus = InfiniteTimer(0.05, self.print_buffers_status)
        self.started = False
    
    def _init_plotHandler(self, parent, app):
        """
        Only initializes the plotHandler object. It is set as a method to allow override.
        """
        self.plotHandler = PyQtGraphHandler(qnt_points=5000, parent=parent, y_range=(0, 5), app=app)

    def consumer_function(self):
        """
        This method is called automatically by the consumerThread. Do not call by yourself.
        It redirects the read value to the plotter buffers.
        Override if you want to do some processing in the data before plotting.
        """
        if self.arduinoHandler.data_waiting:
            self.plotHandler.series.buffer.put(self.arduinoHandler.buffer_acquisition.get()*5.0/1024.0)

    def get_buffers_status(self, separator):
        """
        Returns a string like:
            Serial:    4/1024 - Acq:    1/1024 - Plot:  30/1024
        :param separator: Separates the strings, example ' - ', ' | ', '\n'
        :return: A string containing the status of all the buffers involved in the acquisition and plotting.
        """
        return self.arduinoHandler.get_buffers_status(separator) + separator +\
               self.plotHandler.series.get_buffers_status()

    def print_buffers_status(self):
        """
        Prints the buffer status of send it to the Label if it is defined.
        See get_buffers_status for more information.
        """
        if self.label is None:
            print(self.get_buffers_status(" - "))
        else:
            self.label.setText(self.arduinoHandler.serial_tools_obj.description +
                               "\tBuffers: " + self.get_buffers_status(" - "))

    def start(self):
        """
        Set a started flag to True and starts the following tasks: (in this order)
        timerStatus : for updating the status label.
        plotHandler : timer for updating the plot.
        consumerThread : for redirect the data from the arduino to the plotter.
        arduinoHandler : serial port acquisition with a thread.
        """
        self.started = True
        self.timerStatus.start()
        self.plotHandler.timer.start(0)
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


def test():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)  # Creates a new PyQt Application
    form = QtGui.QMainWindow()  # Creates a new empty MainWindow
    form.resize(800, 600)  # Set its size for a nice one

    central_widget = QtGui.QWidget(form)  # Defines the parent of all others widgets
    vertical_layout = QtGui.QVBoxLayout(central_widget)  # Adds a vertical Layout

    harry_plotter = QtArduinoPlotter(parent=central_widget)  # Creates a QtArduinoPlotter Object
    vertical_layout.addWidget(harry_plotter.plotHandler.plotWidget)  # Adds to the layout
    harry_plotter.start()  # and starts the acquisition and plotting

    form.setCentralWidget(central_widget)  # Assigns the central widget to the form
    form.show()  # Shows the form window
    app.exec_()  # Executes the QtApplication
    harry_plotter.stop()  # Remember to close the serial and stop all thread at the close event.

if __name__ == '__main__':
    test()
