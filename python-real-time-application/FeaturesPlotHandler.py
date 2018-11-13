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


class BarGraphSeries:
    def __init__(self, parent=None, pen=(0, 0, 255), name="Curve"):
        """
        Initializes a custom BarGraphCurve
        :param parent: The parent, it should contains a PyQtPlotWidget that will own this curve.
        :param pen: The RGB color of the curve. Default is blue.
        :param name: The name of the curve. Default is 'Curve'
        """
        self.parent = parent  # Save the parent in a attribute.
        self.values = np.zeros(self.parent.qnt_channels)  # Initilizes a zero-filled vector
        # Creates and adds the curve to the plotwidget.
        self.curve = pg.BarGraphItem(x=np.arange(1,self.parent.qnt_channels+1),
                                     height=self.values, width=0.3, pen=pen)
                                     #NOTE: talvez trocar pen por brush='r'
        self.visible = True

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
        self.curve.setData(self.values)

    def get_buffers_status(self):
        """
        Returns a string like:
            Plot:    4/1024
        :return: A string containing the status of the plot buffer for this curve.
        """
        return "Plot: %4d" % (self.buffer.qsize()) + '/' + str(self.buffer.maxsize)


class PyQtGraphHandler:
    def __init__(self, qnt_channels=4, parent=None, app=None):
        self.app = app
        self.qnt_channels = qnt_channels

        self.plotWidget = pg.PlotWidget(parent)

        self.series = [None] * 6 # amount of features = 6
        self.series[0] = BarGraphSeries(self, (0, 0, 255), "Values")
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


def example1():
    """
    Simple example using BarGraphItem
    """
    import pyqtgraph as pg
    from pyqtgraph.Qt import QtCore, QtGui
    import numpy as np

    win = pg.plot()
    win.setWindowTitle('pyqtgraph example: BarGraphItem')

    x = np.arange(10)
    y1 = np.sin(x)
    y2 = 1.1 * np.sin(x+1)
    y3 = 1.2 * np.sin(x+2)

    bg1 = pg.BarGraphItem(x=x, height=y1, width=0.3, brush='r')
    bg2 = pg.BarGraphItem(x=x+0.33, height=y2, width=0.3, brush='g')
    bg3 = pg.BarGraphItem(x=x+0.66, height=y3, width=0.3, brush='b')

    win.addItem(bg1)
    win.addItem(bg2)
    win.addItem(bg3)


    # Final example shows how to handle mouse clicks:
    class BarGraph(pg.BarGraphItem):
        def mouseClickEvent(self, event):
            print("clicked")


    bg = BarGraph(x=x, y=y1*0.3+2, height=0.4+y1*0.2, width=0.8)
    win.addItem(bg)

    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

def test():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    plot_handler = FeaturesPlotHandler(parent=central_widget)
    plot_handler.series[0].plot(np.random.normal(0,1,4))
    plot_handler.series[1].plot(np.random.normal(0,1,4))
    plot_handler.series[2].plot(np.random.normal(0,1,4))
    plot_handler.series[3].plot(np.random.normal(0,1,4))
    plot_handler.series[4].plot(np.random.normal(0,1,4))
    plot_handler.series[5].plot(np.random.normal(0,1,4))

    plot_handler.timer.start(0)

    vertical_layout.addWidget(plot_handler.plotWidget)
    form.setCentralWidget(central_widget)
    form.show()
    app.exec_()

    plot_handler.timer.stop()

if __name__ == '__main__':
    example1()
