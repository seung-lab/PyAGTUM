# -*- coding: utf-8 -*-

# based on PyAGTUM_210216.py
# only show 2 cameras

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic

import sys
import os
import paintableqlabel
import cv2

import numpy as np

import syringepump as Pump
import valuelogger as log

# https://stackoverflow.com/questions/44404349/pyqt-showing-video-stream-from-opencv/44404713

application_path = os.path.dirname(__file__)

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
        cap = cv2.VideoCapture(0)
        while True:
            ret, frame = cap.read()

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
    historylength=2000

    def updateVis(self):
        self.parent.ptwaterlevel.setData(self.timelog,moving_average(self.valuelog,self.waterwindow,'same'))
        self.parent.sldr_WaterThres.setMinimum(min(self.parent.pg_waterlevel.getAxis('left').range))
        self.parent.sldr_WaterThres.setMaximum(max(self.parent.pg_waterlevel.getAxis('left').range))

    def datacollector(self):
        self.updateLog(self.waterlevel)
        if self.parent.cbx_pumpOn.isChecked():
            if np.average(self.valuelog[(-1*self.waterwindow):-1])<self.parent.sldr_WaterThres.value()-self.parent.sbx_WaterThresRange.value():
                Pump.trigger_pump()

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

        self.setWindowTitle("LeicaCam")

#        cbx_pumpOn = False
#        _StartPosition = 222, 332, 2564, 1273

        self.paintableCam=paintableqlabel.paintableqlabel(self.cam_knife)
        print("Show GUI...")

#        th.changePixmap.connect(self.setImage)
        self.CamTh.start()
        self.show()

    def WaterThresholdChanged(self):
        newValue=self.sldr_WaterThres.value()
        self.ptwaterthres.setValue(newValue)
        print("Threshold updated: {0}".format(newValue))

    def ConnectGUISlots(self):
        self.btn_StartCams.clicked.connect(self.StartCams)
        self.btn_StopCams.clicked.connect(self.StopCams)
        self.sldr_WaterThres.valueChanged.connect(self.WaterThresholdChanged)

    def SetupWaterLog(self):
        self.ptwaterlevel=self.pg_waterlevel.plot(pen=(0, 255, 200, 200))
        self.ptwaterthres=pg.InfiniteLine(pen=(255, 0, 0, 200),angle=0,movable=False)
        self.pg_waterlevel.addItem(self.ptwaterthres)

        self.waterlevellog=waterlevellog();
        self.waterlevellog.initiateTimer(50,self._logpath,'LeicaCamWaterLevel',parent=self)

    def StartCams(self):
        print("start log")
        self.waterlevellog.start()
    
    def StopCams(self):
        print("stop log")
        self.waterlevellog.stopLog()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    print("Loading main GUI...")
    window = mainGUI(os.path.join(application_path,"LeicaCam_Window_210215.ui"))

    sys.exit(app.exec_())
