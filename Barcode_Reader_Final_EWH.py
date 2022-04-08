# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Barcode_Reader_Window.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import matlab.engine
import pandas as pd
import cv2
import numpy as np

#EWH: start the python matlab engine
eng = matlab.engine.start_matlab()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1165, 563)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.grid_image = QtWidgets.QLabel(self.centralwidget)
        self.grid_image.setGeometry(QtCore.QRect(10, 10, 621, 481))
        self.grid_image.setStyleSheet("background: rgb(255,255,255)")
        self.grid_image.setObjectName("grid_image")
        self.luxell_image_string_label = QtWidgets.QLabel(self.centralwidget)
        self.luxell_image_string_label.setGeometry(QtCore.QRect(640, 120, 161, 19))
        self.luxell_image_string_label.setObjectName("luxell_image_string_label")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(640, 280, 131, 19))
        self.label.setObjectName("label")
        self.textEdit_Luxell_file_location = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_Luxell_file_location.setGeometry(QtCore.QRect(810, 60, 341, 41))
        self.textEdit_Luxell_file_location.setObjectName("textEdit_Luxell_file_location")
        self.DisplayApertureNum = QtWidgets.QTextEdit(self.centralwidget)
        self.DisplayApertureNum.setGeometry(QtCore.QRect(790, 270, 161, 41))
        self.DisplayApertureNum.setObjectName("DisplayApertureNum")
        
        self.cbx_LuxellImages = QtWidgets.QCheckBox(self.centralwidget)
        self.cbx_LuxellImages.setGeometry(QtCore.QRect(650, 190, 141, 23))
        self.cbx_LuxellImages.setObjectName("cbx_LuxellImages")
        
        self.textEdit_Luxell_image_location_2 = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit_Luxell_image_location_2.setGeometry(QtCore.QRect(810, 110, 341, 41))
        self.textEdit_Luxell_image_location_2.setObjectName("textEdit_Luxell_image_location_2")
        self.luxell_image_string_label_2 = QtWidgets.QLabel(self.centralwidget)
        self.luxell_image_string_label_2.setGeometry(QtCore.QRect(640, 70, 161, 19))
        self.luxell_image_string_label_2.setObjectName("luxell_image_string_label_2")
        self.warning_image = QtWidgets.QLabel(self.centralwidget)
        
        self.warning_image.setGeometry(QtCore.QRect(980, 180, 151, 131))
        self.warning_image.setStyleSheet("background: rgb(255,255,255)")
        self.warning_image.setText("")
        #self.warning_image.setObjectName("warning_image")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1165, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.Barcode_Reader)
        self.timer.start()

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.grid_image.setText(_translate("MainWindow", "grid_image"))
        self.luxell_image_string_label.setText(_translate("MainWindow", "Luxell Image Location:"))
        self.label.setText(_translate("MainWindow", "Aperture Number:"))
        self.cbx_LuxellImages.setText(_translate("MainWindow", "Luxell Images"))
        self.luxell_image_string_label_2.setText(_translate("MainWindow", "Luxell File Location:"))


    def Barcode_Reader(self):
        
        #EWH: Running the matlab script in the python matlab engine
        eng.barcode_reader(nargout=0)
        
        #EWH: read the output file of the matlab barcode reader
        with open('C:/dev/data/barcode_file.txt', 'r') as f:
            barcode_num = f.readlines()
        
        #EWH: display the barcode number 
        if len(barcode_num) > 0:
            self.DisplayApertureNum.setHtml(str(barcode_num[0]))
        
        #EWH: check if Luxell Images is checked and then will pull up images from luxell. 
            if self.cbx_LuxellImages.isChecked():
                            
                barcode_num = int(barcode_num[0])
                #print(barcode_num)
                
                #EWH: only looking for info of the actual apertures
                if barcode_num < 199999:
                    
                    #EWH: setup necessary location, etc. 
                    path_to_luxell_file = self.textEdit_Luxell_file_location.toPlainText() 
                    path_to_luxell_images = self.textEdit_Luxell_image_location_2.toPlainText()
                    
                    wb = pd.read_csv(path_to_luxell_file, skiprows=13)
                    df = pd.DataFrame(wb, columns = ['Slot #', 'Wrinkle Code', 
                                                     'QA Code', 'Luxel R/N', 
                                                     'Thickness (nm)', 
                                                     'Comments'])
                    #print(df)
                    
#                    #####checks 
#                    Slot_nums = df['Slot #']
#                    slot_number = Slot_nums[barcode_num]
#                    print(slot_number)
#                    
                    
                    #EWH: looking up the qulaity code number for that section
                    QA_code = df['QA Code']
                    QA_code_aperture = QA_code[barcode_num]
                    
                    is_it_a_string = isinstance(QA_code_aperture, float)
                    
                    #print(is_it_a_string)
                    #print(QA_code_aperture)
                    
                    #EWH: if it is NaN then it is a good section (no error codes)
                    if is_it_a_string: 
                        QA_code_NaN = 0
                        self.warning_image.setFont(QFont('Times', 20))
                        self.warning_image.setStyleSheet("background-color: green; border: 1px solid black;")
                        self.warning_image.setText(str(QA_code_NaN))
                        self.set_Aperture_Image(path_to_luxell_images, barcode_num)
                        
                    
                    #EWH: anything else is either yellow if a minor error, or red for major
                    else: 
                        
                        QA_code_aperture_int = int(QA_code_aperture)
                        
                        if QA_code_aperture_int <= 10:
                            self.warning_image.setFont(QFont('Times', 20))
                            self.warning_image.setStyleSheet("background-color: yellow; border: 1px solid black;")
                            self.warning_image.setText(str(QA_code_aperture))
                            #EWH: add the image of the window
                            self.set_Aperture_Image(path_to_luxell_images, barcode_num)
                        
                        if QA_code_aperture_int == 11:
                            self.warning_image.setFont(QFont('Times', 20))
                            self.warning_image.setStyleSheet("background-color: red; border: 1px solid black;")
                            self.warning_image.setText(str(QA_code_aperture))
                            self.set_Aperture_Image(path_to_luxell_images, barcode_num)
                    
                else: 
                    #EWH: change the warning image to yellow if it is leader / trailer
                    self.warning_image.setStyleSheet("background-color: yellow; border: 1px solid black;")
                    #self.warning_image.text('Leading or Trailing Tape')
                    
    def set_Aperture_Image(self, path, barcode_number):
        #EWH: purpose is to populate the Qlabel (grid_image) of the specific image from luxel
        
        #EWH: setting up name for files to get from folder
        if barcode_number <= 9:
            barcode_image_file = f'/000{barcode_number}.jpg'
        if 10 <= barcode_number <= 99:
            barcode_image_file = f'/00{barcode_number}.jpg'
        if 100 <= barcode_number <= 999:
            barcode_image_file = f'/0{barcode_number}.jpg'
        if 1000 <= barcode_number <= 9999:
            barcode_image_file = f'/{barcode_number}.jpg'
                
        path = path + barcode_image_file
        
        Qimg = cv2.imread(path)
        
        Qimg_cropped = Qimg[300:1050, 750:1700]
        
        #EWH: honestly I do not know what is going on here... I would think the 
        #warping could be avoided somehow though with this... 
        
        Qimg_cropped = np.copy(Qimg_cropped[::,::,::])
        
        Q_image = QtGui.QImage(Qimg_cropped,Qimg_cropped.shape[1],Qimg_cropped.shape[0], QtGui.QImage.Format_RGB888)
        pix = QtGui.QPixmap(Q_image)
        
        self.grid_image.setPixmap(pix)  
        

#FOR TESTING: C:/Users/jprice/Downloads/Spool#1050-250 QA Datasheet 4-1-2021 (sample of current milling quality).csv
#Test Images: C:/Users/jprice/Downloads/Spool#1050-250 Inspection 4-1-2021-20220120T154213Z-001/Spool#1050-250 Inspection 4-1-2021
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

#EWH: stopping the python matlab engine
eng.quit()