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
# import sys
# sys.path.append('../libraries')
import pyqtgraph as pg
from libraries.PyQtGraphHandler import PyQtGraphHandler, PyQtGraphSeries
# ------------------------------------------------------------------------------
# Processing:
import numpy as np
import scipy.fftpack as fftpack
from scipy.signal import butter, lfilter, freqz, filtfilt
# ------------------------------------------------------------------------------

class EMGPlotHandler(PyQtGraphHandler):
    def __init__(self, qnt_points=2000, parent=None, y_range=(-1, 1), app=None):
        """
        Handles a plotwidget (library: PyQtGraph) as a continuous plot.
        It allows a simple way to plot points as if they where scrolling in the screen.
        It has all the emg series needed.
        See the code of the test function in this file for an example.
        :param qnt_points: The amount of points that your plot will have.
        :param parent: The parent of the plotwidget (QObject).
        :param y_range: A tuple telling the minimum and maximum value for the y-axis.
        :param app: The QAplication that holds this widget - Not essential, but if it's defined, it
        will try to force a update in the whole window every plot interaction.
        """
        PyQtGraphHandler.__init__(self, qnt_points, parent, y_range, app)

        self.plotWidget.removeItem(self.series.curve)
        self.lines = [None] * 4
        self.lines[0] = PyQtGraphSeries(self, pen=(0, 0, 255), name="CH 1")
        self.lines[1] = PyQtGraphSeries(self, pen=(90, 200, 90), name="CH 2")
        self.lines[2] = PyQtGraphSeries(self, pen=(30, 100, 10), name="CH 3")
        self.lines[3] = PyQtGraphSeries(self, pen=(255, 0, 0), name="CH 4")

    def update(self):
        """
        This method is called automatically, you should not call it by yourself.

        It verifies how many points are in the buffer,
        then remove one by one, and add to the auxiliary vector.
        This auxiliary vector is set as the data source of the curve in the plot.
        """
        self.lines[0].update_values()
        self.lines[1].update_values()
        self.lines[2].update_values()
        self.lines[3].update_values()

        if self.show_fps:
            self.calculate_fps()
            self.plotWidget.setTitle('<font color="red">%0.2f fps</font>' % self.fps)

def test():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    plot_handler = EMGPlotHandler(qnt_points=5000, parent=central_widget, y_range=[-2.5, 2.5])
    plot_handler.lines[0].visible = True
    plot_handler.lines[1].visible = False
    plot_handler.lines[2].visible = False
    plot_handler.lines[3].visible = False
    from datetime import datetime
    import numpy as np

    def generate_point():
        agr = datetime.now()
        y_value = agr.microsecond / 1000000.0
        emg_bruto = np.sin(2*np.pi*y_value)+0.4*np.sin(20*2*np.pi*y_value)
        plot_handler.lines[0].buffer.put(emg_bruto+1)

    from libraries.ThreadHandler import InfiniteTimer
    timer = InfiniteTimer(0.001, generate_point)
    timer.start()

    plot_handler.timer.start(0)

    vertical_layout.addWidget(plot_handler.plotWidget)
    form.setCentralWidget(central_widget)
    form.show()
    app.exec_()

    timer.stop()
    plot_handler.timer.stop()

if __name__ == '__main__':
    test()
