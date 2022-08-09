# -*- coding: utf-8 -*-

# based on PyAGTUM_210216.py
# only show 2 cameras

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic

from AGTUMconfigparser import config

import sys
import os
import paintableqlabel
import cv2
import csv #EWH

import numpy as np
import time

import syringepump as Pump
import valuelogger as log


# https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv/44404713

application_path = os.path.dirname(__file__)

if sys.platform.startswith('win'):
    win=1
else:
    win=0

def moving_average(x, w,shape='same'):
    out=np.convolve(x, np.ones(w), shape) / w
    if x.__len__()<w and shape=='same':
        out=out[0:x.__len__()]
    return out

class Thread(log.valuelogger):
#    changePixmap = pyqtSignal(QImage)
    def Setup(self, label, parent=None):
        self.plabel = label
        self.parent=parent

    def run(self):
        if self.parent.unit_test == False:
            cap = cv2.VideoCapture(0)
        else: 
            video_name = "LeicaCamWater_Movie.mp4"
            video_path = os.path.join(application_path, video_name)
            cap = cv2.VideoCapture(video_path)
            starttime = time.time()
            
        while True:
            ret, frame = cap.read()
            nowtime = time.time()
            
            if self.parent.unit_test == True:
                if ret == False:
                    cap = cv2.VideoCapture(video_path)             
                    ret, frame = cap.read()
                    nowtime = time.time()
                
                    print("New Video Loop Started.")
            
                while (float(nowtime - starttime)) < float(self.parent.unit_test_LeicaCam_SPEED):
                    
                    ROIXbegin=min([self.plabel.begin.x(),self.plabel.end.x()])
                    ROIXend=max([self.plabel.begin.x(),self.plabel.end.x()])
                    ROIYbegin=min([self.plabel.begin.y(),self.plabel.end.y()])
                    ROIYend=max([self.plabel.begin.y(),self.plabel.end.y()])
                    self.parent.waterlevellog.waterlevel=np.mean(frame[ROIYbegin:ROIYend,ROIXbegin:ROIXend])
    
                    p = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
                    self.plabel.setPixmap(QtGui.QPixmap.fromImage(p))
                    # self.changePixmap.emit(p)
                    nowtime = time.time()
                    
                if (float(nowtime - starttime)) > float(self.parent.unit_test_LeicaCam_SPEED):
                    starttime = time.time()
            else:
                ROIXbegin=min([self.plabel.begin.x(),self.plabel.end.x()])
                ROIXend=max([self.plabel.begin.x(),self.plabel.end.x()])
                ROIYbegin=min([self.plabel.begin.y(),self.plabel.end.y()])
                ROIYend=max([self.plabel.begin.y(),self.plabel.end.y()])
                self.parent.waterlevellog.waterlevel=np.mean(frame[ROIYbegin:ROIYend,ROIXbegin:ROIXend])

                p = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
                self.plabel.setPixmap(QtGui.QPixmap.fromImage(p))
                # self.changePixmap.emit(p)
                
        




class waterlevellog(log.valuelogger):
    waterlevel=None
    waterwindow=20
    historylength=3000
    num_iters = 0
    first_hit= True
    slope = -1

    def updateVis(self):
        self.parent.ptwaterlevel.setData(self.timelog,moving_average(self.valuelog,self.waterwindow,'same'))
        self.parent.sldr_WaterThres.setMinimum(min(self.parent.pg_waterlevel.getAxis('left').range))
        self.parent.sldr_WaterThres.setMaximum(max(self.parent.pg_waterlevel.getAxis('left').range))
        
        #print(moving_average(self.valuelog,self.waterwindow,'same'))
        
        if np.isnan(np.average(self.valuelog[(-1*self.waterwindow):-1])):
            pass
        else:
            self.parent.DisplayCurrentLevel.setHtml(str(round(np.average(self.valuelog[(-1*self.waterwindow):-1]))))

            data = list(self.valuelog[(-1*self.waterwindow):-1])
            index = list(range(len(data)))
            
            if len(index) < 3:
                pass
            else:
                coeffs = np.polyfit(index, data, 1) #PROBLEM
                self.slope = coeffs[-2]
                #print(self.slope)
                
                if self.slope >= 0:
                    if self.first_hit == True:
                        self.num_iters += 1
                        self.parent.DisplayCurrentCount.setHtml(str(self.num_iters))
                        self.first_hit = False
                    else:
                        pass
                if self.slope < 0:
                    self.first_hit = True
                else:
                    pass

    def datacollector(self):
        self.updateLog(self.waterlevel)
        
        if self.parent.cbx_pumpOn.isChecked():
#            cycleduration = self.parent.sbx_CycleDurationSet.value()
#            period_start = time.time()
#            period_end = period_start + cycleduration
#            with open('C:\dev\logs\waterlevel.csv', 'a', newline='') as f: #EWH
#                writer = csv.writer(f) #EWH
#                writer.writerow(str(round(self.waterlevel,4))) #EWH 
            
            if np.average(self.valuelog[(-1*self.waterwindow):-1])<self.parent.sldr_WaterThres.value()-self.parent.sbx_WaterThresRange.value():
                if self.parent.unit_test == False:
                    Pump.trigger_pump()
                else:
                    pass
                        
                row = [1] #EWH
                with open('C:\dev\logs\waterpumps.csv', 'a', newline='') as f: #EWH
                    writer = csv.writer(f) #EWH
                    writer.writerow(row) #EWH
            else:
                row = [0] #EWH
                with open('C:\dev\logs\waterpumps.csv', 'a', newline='') as f: #EWH
                    writer = csv.writer(f) #EWH
                    writer.writerow(row) #EWH
                

class mainGUI(QtWidgets.QMainWindow):
    #gui elements whose value/state is saved in the configuration file.
    #gui elements whose name starts with '_' are excluded.
    GUIElements=[QtWidgets.QSlider,QtWidgets.QRadioButton,QtWidgets.QCheckBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox,QtWidgets.QComboBox,QtWidgets.QLineEdit]
    _StartPosition=[]
    _logpath='C:\dev\logs'

    def __init__(self,uifile):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        
        self.unit_test = bool(myconfig["pyAGTUM"]["_unit_test"])
        self.unit_test_LeicaCam_SPEED = myconfig["pyAGTUM"]["_unit_test_LeicaCamWater_SPEED"]

        print("Setup water level log...")
        self.SetupWaterLog()
        print("Connect GUI slots...")
        self.ConnectGUISlots()

        print("Setup camera...")
        self.cbx_pumpOn.setChecked(0)
        self.CamTh = Thread(self)
        self.CamTh.Setup(self.cam_knife, parent=self)


        if hasattr(self,'_StartPosition'):
            if self._StartPosition.__len__()>3:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setGeometry(self._StartPosition[0],self._StartPosition[1],self._StartPosition[2],self._StartPosition[3])

        self.UpdateWindowTitle()

#        cbx_pumpOn = False
#        _StartPosition = 222, 332, 2564, 1273

        self.paintableCam=paintableqlabel.paintableqlabel(self.cam_knife)
        print("Show GUI...")

#        th.changePixmap.connect(self.setImage)
        
        self.CamTh.start()
        self.show()
        
    def setCycleDuration(self,value=None):
        if value is None:
            value=self.sbx_CycleDurationSet.value()
        else:
            self.sbx_CycleDurationSet.blockSignals(True)
            self.sbx_CycleDurationSet.setValue(value)
            self.sbx_CycleDurationSet.blockSignals(False)

    def WaterThresholdChanged(self):
        newValue=self.sldr_WaterThres.value()
        self.ptwaterthres.setValue(newValue)
        #print("Threshold updated: {0}".format(newValue))
        
    def WaterUpperLimChanged(self):
        newValue = self.sbx_WaterLevelUpperLim.value()
        self.ptwaterupperlim.setValue(newValue)
        #print("Upper Limit updated: {0}".format(newValue))
        
    def WaterLowerLimChanged(self):
        newValue = self.sbx_WaterLevelLowerLim.value()
        self.ptwaterlowerlim.setValue(newValue)
        #print("Upper Limit updated: {0}".format(newValue))

    def ConnectGUISlots(self):
        self.btn_StartCams.clicked.connect(self.StartCams)
        self.btn_StopCams.clicked.connect(self.StopCams)
        self.sldr_WaterThres.valueChanged.connect(self.WaterThresholdChanged)

        self.sbx_WaterLevelUpperLim.valueChanged.connect(self.WaterUpperLimChanged)
        self.sbx_WaterLevelLowerLim.valueChanged.connect(self.WaterLowerLimChanged)

    def SetupWaterLog(self):
        self.ptwaterlevel=self.pg_waterlevel.plot(pen=(0, 255, 200, 200))
        self.ptwaterthres=pg.InfiniteLine(pen=(255, 0, 0, 200),angle=0,movable=False)
        self.ptwaterupperlim=pg.InfiniteLine(angle=0, movable=False)
        self.ptwaterlowerlim=pg.InfiniteLine(angle=0, movable=False)
        self.pg_waterlevel.addItem(self.ptwaterupperlim)
        self.pg_waterlevel.addItem(self.ptwaterlowerlim)
        self.pg_waterlevel.addItem(self.ptwaterthres)

        self.waterlevellog=waterlevellog();
        self.waterlevellog.initiateTimer(50,self._logpath,'LeicaCamWaterLevel',parent=self)

    def StartCams(self):
        print("start log")
        self.waterlevellog.start()
    
    def StopCams(self):
        print("stop log")
        self.waterlevellog.stopLog()
        
    def UpdateWindowTitle(self):
        if self.unit_test == False:
            Title="Leica Cam"
            self.setWindowTitle(Title)
        else:
            Title="Leica Cam - VIRTUAL MODE"
            self.setWindowTitle(Title)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    print("Loading main GUI...")

    #Loading default configuration
    if win:
        config_name = 'DefaultConfig_win-3rdCam_-Water.cfg'
    else:
        config_name = 'DefaultConfig.cfg'

    configfile = os.path.join(application_path, config_name)
    
    if not os.path.isfile(configfile):
        QtWidgets.QMessageBox.warning(None,"Error",
            "Configuration file missing:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)
        sys.exit()

    try:
        print("Loading configuration...")
        myconfig = config(configfile)
                
    except:
        QtWidgets.QMessageBox.warning(None, "Error",
            "Configuration file corrupted:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)
        sys.exit()
        
    window = mainGUI(os.path.join(application_path,"LeicaCam_Window_210215_EWH.ui"))

    sys.exit(app.exec_())
