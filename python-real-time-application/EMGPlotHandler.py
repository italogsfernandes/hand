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
# import sys
# sys.path.append('../libraries')
import pyqtgraph as pg
from libraries.PyQtGraphHandler import PyQtGraphHandler, PyQtGraphSeries
# ------------------------------------------------------------------------------
# Processing:
import numpy as np
import scipy.fftpack as fftpack
from scipy.signal import butter, lfilter, freqz, filtfilt


def butter_lowpass(cutoff, fs, order=5):
    """
    Generates the params of a digital low-pass filter with butterworth response.
    :param cutoff: Cutoff frequency in [Hz]. This frequency will be at -3db.
    :param fs: Sampling frequency, necessary for the nyquist.
    :param order: The order of the filter.
    :return: The denominator and numerator values of the transfer function as a tuple (b,a).
    """
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

# ------------------------------------------------------------------------------


class EMGPlotHandler(PyQtGraphHandler):
    def __init__(self, qnt_points=2000, parent=None, y_range=(-1, 1), app=None, proc=None):
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
        :param proc: Must be 'hbt+env' or 'mva' or None.
        If defined, the emg data will be processed in plotter thread.
        """
        PyQtGraphHandler.__init__(self, qnt_points, parent, y_range, app)

        self.plotWidget.removeItem(self.series.curve)
        self.emg_bruto = PyQtGraphSeries(self, pen=(0, 0, 255), name="EMG Bruto")
        self.hilbert = PyQtGraphSeries(self, pen=(90, 200, 90), name="Hilbert")
        self.hilbert_retificado = PyQtGraphSeries(self, pen=(30, 100, 10), name="Hilbert Retificado")
        self.envoltoria = PyQtGraphSeries(self, pen=(255, 0, 0), name="Envoltoria")
        self.threshold = PyQtGraphSeries(self, pen=(255, 150, 0), name="Limiar")

        self.set_threshold(2.5)

        self.contraction_region = pg.LinearRegionItem([0, 1], movable=False)
        self.contraction_region.setZValue(10)
        self.plotWidget.addItem(self.contraction_region)

        self.proc = proc
        if self.proc is not None:
            self.process_in_plotter = True
        else:
            self.process_in_plotter = False

        # Processing:
        self.detection_sites = []
        self.b, self.a = butter_lowpass(7, 1000, order=2)

    def set_detection_visible(self, visible):
        """
        Adds or removes the curve of the parent plot widget.
        :param visible: Boolean telling that the curve should appear (True) or hide (False).
        """
        if not visible:
            self.plotWidget.removeItem(self.contraction_region)
        else:
            self.plotWidget.addItem(self.contraction_region)

    def set_threshold(self, th_value):
        """
        Sets a new threshold value.
        :param th_value:
        """
        self.threshold.values = [th_value] * self.qnt_points

    def update(self):
        """
        This method is called automatically, you should not call it by yourself.

        It verifies how many points are in the buffer,
        then remove one by one, and add to the auxiliary vector.
        This auxiliary vector is set as the data source of the curve in the plot.
        """
        self.emg_bruto.update_values()
        if self.process_in_plotter:
            self.process_data()
        self.hilbert.update_values()
        self.hilbert_retificado.update_values()
        self.envoltoria.update_values()
        self.threshold.update_values()

        if self.show_fps:
            self.calculate_fps()
            self.plotWidget.setTitle('<font color="red">%0.2f fps</font>' % self.fps)

    def process_data(self):
        """
        If the flag process in plotter is set to True.
        This function is called every plot update.
        It will process the data stored in the emg_bruto curve aiming to obtain all the other curves.
        """
        if 'hbt+' in self.proc:  # Filter the emg with Hilbert
            self.hilbert.values = fftpack.hilbert(self.emg_bruto.values)
        elif 'mva+' in self.proc:  # Or with subtracting the average
            self.hilbert.values =\
                self.emg_bruto.values -\
                np.convolve(self.emg_bruto.values,
                            np.repeat(1, 100) / (100.0 / 2.0),
                            'same')
        else:  # Or simply do not filter the emg
            self.hilbert.values = self.emg_bruto

        # With the filtered emg, calculates the its absolute value
        self.hilbert_retificado.values = np.abs(self.hilbert.values)

        if '+btr' in self.proc:  # Obtains the env by a low pass filter with butter response
            self.envoltoria.values = filtfilt(self.b, self.a, self.hilbert_retificado.values)
        elif '+ham_conv' in self.proc:  # Obtains the env by a convolution with a hamming window
            self.envoltoria.values = np.convolve(self.hilbert_retificado.values,
                                                 np.hamming(100) / (100.0 / 2.0),
                                                 'same')
        elif '+mva' in self.proc:  # Obtains the env by a convolution with a square window (moving average)
            self.envoltoria.values = np.convolve(self.hilbert_retificado.values,
                                                 np.repeat(1, 100) / (100.0 / 2.0),
                                                 'same')
        # Calculo dos locais em contração:
        self.detection_sites = self.envoltoria.values > self.threshold.values[0]
        time_inicio = self.qnt_points - 1
        for n in range(1, self.qnt_points):
            #subida
            if self.detection_sites[n] and not self.detection_sites[n-1]:
                time_inicio = n # Armazena o indes de inicio da contracao
            if not self.detection_sites[n] and self.detection_sites[n - 1]:
                time_end = n
                self.contraction_region.setRegion([time_inicio, time_end])
        # Converte de np.array para list para garantir compatibilidade com outros metodos de processamento
        self.envoltoria.values = list(self.envoltoria.values)
        self.hilbert_retificado.values = list(self.hilbert_retificado.values)
        self.hilbert.values = list(self.hilbert.values)


def test():
    import sys
    from PyQt4 import QtGui
    app = QtGui.QApplication(sys.argv)
    form = QtGui.QMainWindow()
    form.resize(800, 600)
    central_widget = QtGui.QWidget(form)
    vertical_layout = QtGui.QVBoxLayout(central_widget)

    plot_handler = EMGPlotHandler(qnt_points=5000, parent=central_widget, y_range=[-2.5, 2.5])
    plot_handler.process_in_plotter = False
    plot_handler.emg_bruto.visible = True
    plot_handler.hilbert.visible = False
    plot_handler.hilbert_retificado.visible = False
    from datetime import datetime
    import numpy as np

    def generate_point():
        agr = datetime.now()
        y_value = agr.microsecond / 1000000.0
        emg_bruto = np.sin(2*np.pi*y_value)+0.4*np.sin(20*2*np.pi*y_value)
        plot_handler.emg_bruto.buffer.put(emg_bruto+1)

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
