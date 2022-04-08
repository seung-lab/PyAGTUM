






# -*- coding: utf-8 -*-

# based on PyAGTUM_210216.py
# only show 2 cameras
import os
import matlab.engine
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QMainWindow, QMessageBox)


ui_path = 'C:/dev/PyAGTUM/PyAGTUM_mainwindow_210302_EWH.ui'




#
#application_path = os.path.dirname(__file__)
#
#class Window(QtWidgets.QMainWindow):
#    def __init__(self, parent=None):
#        super().__init__(parent)
#        self.setupUi(self)
#        self.connectSignalsSlots()
#
#    def connectSignalsSlots(self):
#        self.btn_Barcode.clicked.connect(self.Matlab_Read_Barcode())
#
#    def Matlab_Read_Barcode(self):
#        eng = matlab.engine.start_matlab()
#        eng.barcode_reader(nargout=0)
#        eng.quit()
#        
#        with open('C:/dev/data/barcode_file.txt', 'r') as f:
#            barcode_num = f.readlines()
# 
# 
#        self.DisplayApertureNum.setHtml(barcode_num)
#
#
#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    print("Loading main GUI...")
#    window = Window(os.path.join(application_path,"PyAGTUM_mainwindow_210302_EWH.ui"))
#    window.show()
#    sys.exit(app.exec())
    
