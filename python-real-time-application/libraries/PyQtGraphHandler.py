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
from pyqtgraph.Qt import QtCore
import pyqtgraph as pg
from pyqtgraph.ptime import time
from numpy import clip

import sys
if sys.version_info.major == 3:
    from queue import Queue
    from PyQt5.QtGui import QBrush, QColor, QPen
elif sys.version_info.major == 2:
    from Queue import Queue
    from PyQt4.QtGui import QBrush, QColor, QPen

# ------------------------------------------------------------------------------


class PyQtGraphSeries:
    def __init__(self, parent=None, pen=(0, 0, 255), name="Curve"):
        """
        Initializes a custom PyQtGraphCurve with a auxiliary vector of values and a buffer.
        :param parent: The parent, it should contains a PyQtPlotWidget that will own this curve.
        :param pen: The RGB color of the curve. Default is blue.
        :param name: The name of the curve. Default is 'Curve'
        """
        self.parent = parent  # Save the parent in a attribute.
        self.values = [0] * self.parent.qnt_points  # Initilizes a zero-filled vector
        # Creates and adds the curve to the plotwidget.
        self.curve = self.parent.plotWidget.plot(self.values, pen=pen, name=name)
        self.visible = True
        self.buffer = Queue(self.parent.qnt_points)

    def set_visible(self, visible):
        """
        Adds or removes the curve of the parent plot widget.
        :param visible: Boolean telling that the curve should appear (True) or hide (False).
        """
        self.visible = visible  # Save the argument as as attribute
        if not self.visible:
            self.parent.plotWidget.removeItem(self.curve)
        else:
            self.parent.plotWidget.addItem(self.curve)

    def update_values(self):
        """
        This method is called automatically, you should not call it by yourself.

        It verifies how many points are in the buffer,
        then remove one by one, and add to the auxiliary vector.
        This auxiliary vector is set as the data source of the curve in the plot.
        """
        points_to_add = self.buffer.qsize()
        if points_to_add > 0:
            for n in range(points_to_add):  # obtains the new values
                num = self.buffer.get()
                self.values.append(num)
                if len(self.values) > self.parent.qnt_points:
                    self.values.pop(0)
        if self.visible:
            self.curve.setData(self.values)

    def get_buffers_status(self):
        """
        Returns a string like:
            Plot:    4/1024
        :return: A string containing the status of the plot buffer for this curve.
        """
        return "Plot: %4d" % (self.buffer.qsize()) + '/' + str(self.buffer.maxsize)


class PyQtGraphHandler:
    def __init__(self, qnt_points=10, parent=None, y_range=(-1, 1), app=None):
        """
        Handles a plotwidget (library: PyQtGraph) as a continuous plot.
        It allows a simple way to plot points as if they where scrolling in the screen.

        See the code of the test function in this file for an example.
        :param qnt_points: The amount of points that your plot will have.
        :param parent: The parent of the plotwidget (QObject).
        :param y_range: A tuple telling the minimum and maximum value for the y-axis.
        :param app: The QAplication that holds this widget - Not essential, but if it's defined, it
        will try to force a update in the whole window every plot interaction.
        """
        self.app = app
        self.__y_range = y_range
        self.qnt_points = qnt_points

        self.plotWidget = pg.PlotWidget(parent)
        # self.plotWidget = pg.MultiPlotWidget(parent)

        self.series = PyQtGraphSeries(self, (0, 0, 255), "Values")
        self.configure_plot()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)

        self.show_fps = True
        self.lastTime = 0
        self.fps = 0
        # 1) Simplest approach -- update data in the array such that plot appears to scroll
        # 2) Allow data to accumulate. In these examples, the array doubles in length
        #    whenever it is full.

    def update(self):
        """
        This method is called automatically, you should not call it by yourself.

        It removes the values of the curve buffers, and updates the curves.
        If defined it can show the refresh rate (fps) in the plot title.
        If defined it can force the app to update every time that this method runs.
        """
        self.series.update_values()

        if self.show_fps:
            self.calculate_fps()
            self.plotWidget.setTitle('<font color="red">%0.2f fps</font>' % self.fps)

        if self.app is not None:
            self.app.processEvents()

    def calculate_fps(self):
        """
        If defined, it this method is called automatically by the update function.
        Updating the value of the fps attribute.
        """
        now = time()
        dt = now - self.lastTime
        self.lastTime = now
        if self.fps is None:
            self.fps = 1.0 / dt
        else:
            s = clip(dt * 3., 0, 1)
            self.fps = self.fps * (1 - s) + (1.0 / dt) * s

    def configure_plot(self):
        """
        Configure the plot to:
            Show a X,Y grid.
            Sets the colors to a white background theme.
            Sets the axis range and labels.
        And set the title of the chart.
        """
        self.configure_area()
        self.configure_title("Graph")

    def configure_area(self, x_title='Index', x_unit='',  y_title='Values', y_unit=''):
        """
        Configure the plot to:
            Show a X,Y grid.
            Sets the colors to a white background theme.
            Sets the axis range and labels.
        :param x_title: The x axis label.
        :param x_unit: The unit names of the x values.
        :param y_title: The y axis label.
        :param y_unit: The unit names of the y axis.
        """
        self.plotWidget.showGrid(True, True)
        # Colors:
        self.plotWidget.setBackgroundBrush(QBrush(QColor.fromRgb(255, 255, 255)))
        self.plotWidget.getAxis('left').setPen(QPen(QColor.fromRgb(0, 0, 0)))
        self.plotWidget.getAxis('bottom').setPen(QPen(QColor.fromRgb(0, 0, 0)))
        self.plotWidget.getAxis('left').setPen(QPen(QColor.fromRgb(0, 0, 0)))
        self.plotWidget.getAxis('bottom').setPen(QPen(QColor.fromRgb(0, 0, 0)))
        # Axis:
        self.plotWidget.setXRange(0, self.qnt_points)
        self.plotWidget.setYRange(self.__y_range[0], self.__y_range[1])
        self.plotWidget.setLabel('bottom', x_title, units=x_unit)
        self.plotWidget.setLabel('left', y_title, units=y_unit)

    def configure_title(self, title="Graph"):
        """
        Sets the title of the plot.
        :param title: String to be showed in the title of this plot.
        """
        self.plotWidget.setTitle('<font color="black"> %s </font>' % title)


def test():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    plot_handler = PyQtGraphHandler(qnt_points=5000, parent=central_widget)

    plot_handler.plotWidget.setYRange(-1, 1)

    from datetime import datetime
    import numpy as np

    def generate_point():
        agr = datetime.now()
        y_value = agr.microsecond / 1000000.0
        plot_handler.series.buffer.put(np.sin(2 * np.pi * y_value))

    from ThreadHandler import InfiniteTimer
    timer = InfiniteTimer(0.001, generate_point)
    timer.start()

    plot_handler.timer.start(0)

    vertical_layout.addWidget(plot_handler.plotWidget)
    form.setCentralWidget(central_widget)
    form.show()
    app.exec_()

    timer.stop()
    plot_handler.timer.stop()


def test2():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    plot_handler = PyQtGraphHandler(qnt_points=5000, parent=central_widget)
    plot_handler.plotWidget.setYRange(-1, 1)

    plot_handler2 = PyQtGraphHandler(qnt_points=5000, parent=central_widget)
    plot_handler2.plotWidget.setYRange(-1, 1)

    from datetime import datetime
    import numpy as np

    def generate_point():
        agr = datetime.now()
        y_value = agr.microsecond / 1000000.0
        plot_handler.series.buffer.put(np.sin(2 * np.pi * y_value))
        plot_handler2.series.buffer.put(np.sin(2 * np.pi * y_value + np.pi))

    from ThreadHandler import InfiniteTimer
    timer = InfiniteTimer(0.001, generate_point)
    timer.start()

    plot_handler.timer.start(0)
    plot_handler2.timer.start(0)

    vertical_layout.addWidget(plot_handler.plotWidget)
    vertical_layout.addWidget(plot_handler2.plotWidget)
    form.setCentralWidget(central_widget)
    form.show()
    app.exec_()

    timer.stop()
    plot_handler.timer.stop()
    plot_handler2.timer.stop()


def test3():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    plot_handler = PyQtGraphHandler(qnt_points=5000, parent=central_widget)
    plot_handler.plotWidget.setYRange(-1, 1)

    plot_handler2 = PyQtGraphHandler(qnt_points=5000, parent=central_widget)
    plot_handler2.plotWidget.setYRange(-1, 1)

    plot_handler3 = PyQtGraphHandler(qnt_points=5000, parent=central_widget)
    plot_handler3.plotWidget.setYRange(-1, 1)

    from datetime import datetime
    import numpy as np

    def generate_point():
        agr = datetime.now()
        y_value = agr.microsecond / 1000000.0
        plot_handler.series.buffer.put(np.sin(2 * np.pi * y_value))
        plot_handler2.series.buffer.put(np.sin(2 * np.pi * y_value + np.pi/3))
        plot_handler3.series.buffer.put(np.sin(2 * np.pi * y_value + 2*np.pi/3))

    from ThreadHandler import InfiniteTimer
    timer = InfiniteTimer(0.001, generate_point)
    timer.start()

    plot_handler.timer.start(0)
    plot_handler2.timer.start(0)
    plot_handler3.timer.start(0)

    vertical_layout.addWidget(plot_handler.plotWidget)
    vertical_layout.addWidget(plot_handler2.plotWidget)
    vertical_layout.addWidget(plot_handler3.plotWidget)
    form.setCentralWidget(central_widget)
    form.show()
    app.exec_()

    timer.stop()
    plot_handler.timer.stop()
    plot_handler2.timer.stop()
    plot_handler3.timer.stop()


if __name__ == '__main__':
    test3()
