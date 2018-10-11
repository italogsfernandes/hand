# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layouts/config_processamento.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_windowConfig(object):
    def setupUi(self, windowConfig):
        windowConfig.setObjectName("windowConfig")
        windowConfig.resize(186, 390)
        self.centralwidget = QtWidgets.QWidget(windowConfig)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setObjectName("comboBox")
        self.verticalLayout.addWidget(self.comboBox)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        windowConfig.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(windowConfig)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 186, 28))
        self.menubar.setObjectName("menubar")
        windowConfig.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(windowConfig)
        self.statusbar.setObjectName("statusbar")
        windowConfig.setStatusBar(self.statusbar)

        self.retranslateUi(windowConfig)
        QtCore.QMetaObject.connectSlotsByName(windowConfig)

    def retranslateUi(self, windowConfig):
        _translate = QtCore.QCoreApplication.translate
        windowConfig.setWindowTitle(_translate("windowConfig", "Processamento"))
        self.label.setText(_translate("windowConfig", "Tipo:"))

