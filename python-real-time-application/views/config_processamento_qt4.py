# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config_processamento.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_windowConfig(object):
    def setupUi(self, windowConfig):
        windowConfig.setObjectName(_fromUtf8("windowConfig"))
        windowConfig.resize(186, 390)
        self.centralwidget = QtGui.QWidget(windowConfig)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.comboBox = QtGui.QComboBox(self.centralwidget)
        self.comboBox.setObjectName(_fromUtf8("comboBox"))
        self.verticalLayout.addWidget(self.comboBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        windowConfig.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(windowConfig)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 186, 28))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        windowConfig.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(windowConfig)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        windowConfig.setStatusBar(self.statusbar)

        self.retranslateUi(windowConfig)
        QtCore.QMetaObject.connectSlotsByName(windowConfig)

    def retranslateUi(self, windowConfig):
        windowConfig.setWindowTitle(_translate("windowConfig", "Processamento", None))
        self.label.setText(_translate("windowConfig", "Tipo:", None))

