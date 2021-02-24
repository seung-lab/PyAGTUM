# -*- coding: utf-8 -*-
"""
Created on Sat Oct 12 08:13:41 2019

@author: jprice
"""

import sys
from PyQt5 import QtWidgets, QtCore, QtGui

# This is our window from QtCreator

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(102, 144)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.btnStart = QtWidgets.QPushButton(self.centralwidget)
        self.btnStart.setObjectName("btnStart")
        self.verticalLayout.addWidget(self.btnStart)
        self.btnStop = QtWidgets.QPushButton(self.centralwidget)
        self.btnStop.setObjectName("btnStop")
        self.verticalLayout.addWidget(self.btnStop)
        self.lblAction = QtWidgets.QLabel(self.centralwidget)
        self.lblAction.setObjectName("lblAction")
        self.verticalLayout.addWidget(self.lblAction)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 102, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnStart.setText(_translate("MainWindow", "btnStart"))
        self.btnStop.setText(_translate("MainWindow", "btnStop"))
        self.lblAction.setText(_translate("MainWindow", "lblAction"))


class DataCaptureThread(QtCore.QThread):
    def collectProcessData(self):
        print ("Collecting Process Data")

    def __init__(self, *args, **kwargs):
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.dataCollectionTimer = QtCore.QTimer()
        self.dataCollectionTimer.moveToThread(self)
        self.dataCollectionTimer.timeout.connect(self.collectProcessData)

    def run(self):
        self.dataCollectionTimer.start(1000)
        loop = QtCore.QEventLoop()
        loop.exec_()


class MainWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.setupUi(self) # gets defined in the UI file
        self.btnStart.clicked.connect(self.pressedStartBtn)
        self.btnStop.clicked.connect(self.pressedStopBtn)

    def pressedStartBtn(self):
        self.lblAction.setText("STARTED")
        self.dataCollectionThread = DataCaptureThread()
        self.dataCollectionThread.start()
    def pressedStopBtn(self):
        self.lblAction.setText("STOPPED")
        self.dataCollectionThread.terminate()


def main():
     # a new app instance
     app = QtWidgets.QApplication(sys.argv)
     form = MainWindow()
     form.show()
     sys.exit(app.exec_())

if __name__ == "__main__":
     main()