# -*- coding: utf-8 -*-

# based on PyAGTUM_210116
# remove un-used functions, remove cbx_synRetractSpeed
# 210223 remove 3rd camera, remove pump
# remove retract phase diff logs
# 210312 spring change on 210310


import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic

import sys
import os
from AGTUMconfigparser import config
from ximea import xiapi
import time
import nidaqmx
import serial
# import paintableqlabel
import cv2
import copy

import numpy as np
from scipy import stats, signal, fftpack
import leicaCmds as Leica
import atumCmds_2 as Atum
# import syringepump as Pump
import valuelogger as log

tape_speed_list = np.arange(0.27,0.33,0.01)

application_path = os.path.dirname(__file__)

if sys.platform.startswith('win'):
    win=1
else:
    win=0

def draw_str(dst, target, s):
    # copy from cv_samples.common
    x, y = target
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.LINE_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 1.0, (255, 255, 255), lineType=cv2.LINE_AA)

lk_params = dict( winSize  = (10, 10),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

feature_params = dict( maxCorners = 25,
                       qualityLevel = 0.6,
                       minDistance = 20,
                       blockSize = 20 )

class PreCamTimer(log.valuelogger):
    def setupCams(self, camSN, CamFrame):
        self.cam=xiapi.Camera()
        self.cam.open_device_by_SN(camSN)
            # settings
        self.cam.set_imgdataformat('XI_RGB24')
            #1028*1232*3*20*24
        self.cam.set_limit_bandwidth(750)
        self.cam.set_exposure(10000)
        self.cam.set_decimation_horizontal(2)
        self.cam.set_decimation_vertical(2)
        self.cam.set_framerate(10)
        self.cam.frame=CamFrame
 #           cam.name=self.CamFrames[icam].text()
        self.cam.image=xiapi.Image()
        self.cam.start_acquisition()

    def updateVis(self):
        #get data and pass them from camera to img
        try:
            self.cam.get_image(self.cam.image)
#                print('Image read from ' + cam.name)
            #cv2.imshow("XIMEA cams", img.get_image_data_numpy())

            npimg=self.cam.image.get_image_data_numpy()
            npimg=np.copy(npimg[::2,::2,:])
#            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))

            Qimg = QtGui.QImage(npimg,npimg.shape[1],npimg.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(Qimg)
            self.cam.frame.setPixmap(pix)
        except:
            print('Image skipped')

    def datacollector(self):
        self.updateVis()


class PostCamTimer(log.valuelogger):
    historylength = 4000
    def setupCams(self, camSN, CamFrame):
        self.cam=xiapi.Camera()
        self.cam.open_device_by_SN(camSN)
            # settings
        self.cam.set_imgdataformat('XI_RGB24')
            #1028*1232*3*20*24
        self.cam.set_limit_bandwidth(750)
        self.cam.set_exposure(10000)
        self.cam.set_decimation_horizontal(2)
        self.cam.set_decimation_vertical(2)
        self.cam.set_framerate(10)
        self.cam.frame=CamFrame
 #           cam.name=self.CamFrames[icam].text()
        self.cam.image=xiapi.Image()
        self.cam.start_acquisition()

        self.track_len = 20 # max number of locations of point to remember
        self.detect_interval = 10
        self.tracks = []
        self.frame_idx = 0
        self.speed = 0
        self.time = []
        self.speed_list = []

    def datacollector(self):
        #get data and pass them from camera to img
        try:
            self.cam.get_image(self.cam.image)
            t1 = time.time()
#                print('Image read from ' + cam.name)
            #cv2.imshow("XIMEA cams", img.get_image_data_numpy())

            npimg=self.cam.image.get_image_data_numpy()

            vis=np.copy(npimg[::2,::2,:])
#            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))
            if self.parent.cbx_TrackSpeed.isChecked():
                frame_gray = cv2.cvtColor(vis, cv2.COLOR_BGR2GRAY)
                if len(self.tracks) > 0:
                    img0, img1 = self.prev_gray, frame_gray
                    p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
                    p1, _st, _err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
                    p0r, _st, _err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
                    d = abs(p0-p0r).reshape(-1, 2).max(-1)
                    good = d < 1
                    new_tracks = []
                    t20 = []
                    for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
                        if not good_flag:
                            continue
                        tr.append((x, y))
                        if len(tr) > self.track_len:
                            del tr[0]
                            t20.append(tr[-1][0] - tr[0][0])
                        new_tracks.append(tr)
                        cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
                    self.tracks = new_tracks
                    cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
                    draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))
                    if self.frame_idx % 20 == 0:
                        self.time.append(t1)
                        if len(self.time) > 2:
                            self.speed = (sum(t20) / len(t20)) * 0.0136 / (self.time[-1] - self.time[-2])
                            del self.time[0]
                            self.updateLog(self.speed)
                            print('Cam Tape speed: %3f' % self.speed)
                            '''
                            self.speed_list.append(self.speed)
                            if len(self.speed_list) > 3:
                                s1 = sum(self.speed_list[-3:])/3
                                if s1 > 0.35:
                                    self.parent.setTapeSpeed(0.39)
                                    self.speed_list = []
                                elif s1 < 0.325:
                                    self.parent.setTapeSpeed(0.43)
                                    self.speed_list = []
                                else:
                                    self.parent.setTapeSpeed(0.41)
                                    del self.speed_list[0]
                             '''

                    # 0.0136mm per pixel
                    draw_str(vis, (20, 40), 'speed: %3f' % self.speed)

                if self.frame_idx % self.detect_interval == 0:
                    mask = np.zeros_like(frame_gray)
                    mask[:] = 255
                    for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
                        cv2.circle(mask, (x, y), 5, 0, -1)
                    p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
                    if p is not None:
                        for x, y in np.float32(p).reshape(-1, 2):
                            self.tracks.append([(x, y)])

                self.frame_idx += 1
                self.prev_gray = frame_gray
               # cv.imshow('lk_track', vis)

            Qimg = QtGui.QImage(vis, vis.shape[1], vis.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(Qimg)
            self.cam.frame.setPixmap(pix)
        except:
            print('Image skipped Post')


class ATUMcyledurationlog(log.valuelogger):
    historylength=500
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)

class ATUMslotdurationlog(log.valuelogger):
    historylength=500
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)

class ATUMinterslotdurationlog(log.valuelogger):
    historylength=500
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)


class TapeSpeedDifflog(log.valuelogger):
    historylength=500
  #  def updateVis(self): self.parent.ptTapeSpeedDiff.setData(self.timelog,self.valuelog)

    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)

class ATUMchopperlog(log.valuelogger):
    historylength=2000
    upStateStart=[]
    downStateStart=[]

    atum_idx = 0

    def updateVis(self):
        self.parent.ptsyncATUM_chopper.setData(self.timelog,self.valuelog)

    def datacollector(self):
        chopperSignal=int(self.parent.syncATUM_chopper.read())
        #invert chopper signal
        if chopperSignal==1:
            chopperSignal=0
        elif chopperSignal==0:
            chopperSignal=1

        self.updateLog(chopperSignal)
        if self.valuelog.__len__()<2:
            return
        if self.valuelog[-1]==1 and self.valuelog[-2]==0: #slot phase starts
            
            print("atum_idx : {}".format(self.atum_idx))

            if self.atum_idx % 20 == 0 and int(self.atum_idx / 20) < len(tape_speed_list):
                speed = tape_speed_list[int(self.atum_idx / 20)]
                self.parent.setTapeSpeed(speed)
                
                print("speed changed to: {}".format(speed))
                
            self.atum_idx += 1

            self.upStateStart.append(self.timelog[-1])
            if self.downStateStart.__len__()>0:
                interslotDuration=self.upStateStart[-1]-self.downStateStart[-1]
                self.parent.ATUMinterslotdurationlog.datacollector(interslotDuration)
            if self.upStateStart.__len__()>1:
                ATUMcycle=np.diff(self.upStateStart[-2:])
                self.parent.ATUMcyledurationlog.datacollector(ATUMcycle[-1])
                print("ATUM cycle: {}, actual tape speed: {}".format(round(ATUMcycle[-1],2), round(6/ATUMcycle[-1],3)))
                print("tape tension: {}".format(round(Atum.gTT(),2)))

        if self.valuelog[-2]==1 and self.valuelog[-1]==0: #inter-slot phase starts
            self.downStateStart.append(self.timelog[-1])
            if self.upStateStart.__len__()>0:
                slotDuration=self.downStateStart[-1]-self.upStateStart[-1]
                self.parent.ATUMslotdurationlog.datacollector(slotDuration)
        del self.upStateStart[:-3]
        del self.downStateStart[:-3]


class tapespeedlog(log.valuelogger):
    historylength=500
    def datacollector(self,value=None):
        if (value is None):
            value=Atum.gTS()
        self.updateLog(value)
        #print("Tension: {0}".format(Atum.gTT()))



class mainGUI(QtWidgets.QMainWindow):
    #gui elements whose value/state is saved in the configuration file.
    #gui elements whose name starts with '_' are excluded.
    GUIElements=[QtWidgets.QSlider,QtWidgets.QRadioButton,QtWidgets.QCheckBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox,QtWidgets.QComboBox,QtWidgets.QLineEdit]
    _StartPosition=[]
    _CameraSNs=['CICAU1641091','CICAU1914024']
    # _CameraSNs=['CICAU1641091','CICAU1914024','CICAU1914041']
    _syncATUM_chopperPort="Dev1/pfi0"
    _syncLEICA_chopperPort="Dev1/pfi1"
    _logpath='C:\dev\PyAGTUM\logs'
    _DistanceBetweenSlots=6.0#mm

    def __init__(self,uifile):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        print("Loading GUI config...")
        myconfig.LoadConfig(self,"pyAGTUM")

        print("Setup ATUM sync...")
        self.setupATUMsync()
        print("Connect GUI slots...")
        self.ConnectGUISlots()

        print("Setup hardware...")
        self.SetupHardware()

        if hasattr(self,'_StartPosition'):
            if self._StartPosition.__len__()>3:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setGeometry(self._StartPosition[0],self._StartPosition[1],self._StartPosition[2],self._StartPosition[3])

        print("Setup GUI state...")
        self.UpdateWindowTitle()
        self.SetupGUIState(self)

        print("Show GUI...")
        self.show()

    def setTapeSpeed(self,value=None):
        if value is None:
            value=self.sbx_tapeSpeed.value()
        else:
            self.sbx_tapeSpeed.blockSignals(True)
            self.sbx_tapeSpeed.setValue(value)
            self.sbx_tapeSpeed.blockSignals(False)
        Atum.sTS(value)

    def setReturnSpeed(self,value=None):
        if value is None:
            value=self.sbx_retractionSpeed.value()
        else:
            self.sbx_retractionSpeed.blockSignals(True)
            self.sbx_retractionSpeed.setValue(value)
            self.sbx_retractionSpeed.blockSignals(False)
        Leica.setReturnSpeed(value)

    def setupATUMsync(self):
        self.ptsyncATUM_chopper = self.pg_sync.plot(pen=(255, 0, 20, 200))
        self.ptOffset = self.pg_phasediff.plot(pen=(255, 0, 20, 200))

        self.tapespeedlog=tapespeedlog();
        self.tapespeedlog.initiateTimer(1000,self._logpath,'tapespeed',parent=self)

        self.ATUMchopperlog=ATUMchopperlog();
        self.ATUMchopperlog.initiateTimer(50,self._logpath,'ATUMchopper',parent=self)

        self.ATUMslotdurationlog=ATUMslotdurationlog()
        self.ATUMslotdurationlog.initiateTimer(1000,self._logpath,'ATUMslotduration',parent=self)
        self.ATUMinterslotdurationlog=ATUMinterslotdurationlog()
        self.ATUMinterslotdurationlog.initiateTimer(1000,self._logpath,'ATUMinterslotduration',parent=self)

        self.TapeSpeedDifflog=TapeSpeedDifflog()
        self.TapeSpeedDifflog.initiateTimer(1000,self._logpath,'TapeSpeedDiff',parent=self)

        self.ATUMcyledurationlog=ATUMcyledurationlog()
        self.ATUMcyledurationlog.initiateTimer(1000,self._logpath,'ATUMcyleduration',parent=self)


    def SetupHardware(self):
        self.PreCamTimer = PreCamTimer()
        self.PreCamTimer.setupCams(self._CameraSNs[0], self._cam_presection)
        self.PreCamTimer.initiateTimer(100, None, None, parent=self)
        self.PreCamTimer.start()

        self.PostCamTimer = PostCamTimer()
        self.PostCamTimer.setupCams(self._CameraSNs[1], self._cam_postsection)
        self.PostCamTimer.initiateTimer(100, self._logpath,'CamTapeSpeed', parent=self)
        self.PostCamTimer.start()

        self.syncATUM_chopper=nidaqmx.Task()
        self.syncATUM_chopper.di_channels.add_di_chan(self._syncATUM_chopperPort)

    def StartCams(self):

        Atum.Start()

        print("start cameras")

 #       v=self.sbx_tapeSpeed.value()
 #       self.setTapeSpeed(1)
 #       self.sbx_tapeSpeed.setValue(v)
        self.setTapeSpeed()

        self.ATUMchopperlog.start()

        self.ATUMslotdurationlog.start()
        self.ATUMinterslotdurationlog.start()

        self.tapespeedlog.start()
        self.TapeSpeedDifflog.start()

        self.ATUMcyledurationlog.start()

    def StopCams(self):
        print("stopped cameras")
        Atum.Stop()
        self.ATUMchopperlog.stopLog()

        self.ATUMslotdurationlog.stopLog()
        self.ATUMinterslotdurationlog.stopLog()

        self.tapespeedlog.stopLog()
        self.TapeSpeedDifflog.stopLog()
        self.ATUMcyledurationlog.stopLog()


    def StopHardware(self):
        self.PreCamTimer.stopLog()
        self.PostCamTimer.stopLog()
        self.PreCamTimer.cam.stop_acquisition()
        self.PostCamTimer.cam.stop_acquisition()
        self.PreCamTimer.cam.close_device()
        self.PostCamTimer.cam.close_device()
        self.StopCams()

        self.syncATUM_chopper.close()

        print("done closing hardware")


    def closeEvent(self, event):
        self.StopHardware()

        tempGeometry=self.geometry()
        self._StartPosition=\
            [tempGeometry.x(),tempGeometry.y(),tempGeometry.width(),tempGeometry.height()]

        if not "GUIstate" in myconfig:
            myconfig["GUIstate"]={}
        for element in self.GUIElements:
            children=self.findChildren(element)
            for child in children:
                childName=child.objectName()
                if not isinstance(childName, str):
                    childName=str(childName,"utf-8")
                if childName.startswith("_") or childName.startswith("qt_") or childName=="":
                    continue
                if hasattr(child,'value'):
                    value=child.value()
                elif hasattr(child,'isChecked'):
                    value=child.isChecked()
                elif hasattr(child,'currentIndex'):
                    value=child.currentIndex()
                elif hasattr(child,'text'):
                    value=child.text()
                else:
                    continue
                myconfig["GUIstate"][childName]=value

        myconfig.SaveConfig(self,"pyAGTUM")
        myconfig.write()
        event.accept()

    def SetupGUIState(self,GUIobj):
        if not "GUIstate" in myconfig:
            return
        if not hasattr(GUIobj,'findChildren'):
            return
        for element in self.GUIElements:
            children=GUIobj.findChildren(element)
            for child in children:
                childName=child.objectName()
                if not isinstance(childName, str):
                    childName=str(childName,"utf-8")
                if childName.startswith("_"):
                    continue
                if not childName in myconfig["GUIstate"]:
                    continue
                if hasattr(child,'value'):
                    template=child.value()
                    child.setValue(myconfig.Cast(myconfig["GUIstate"][childName],template))
                elif hasattr(child,'isChecked'):
                    template=child.isChecked()
                    child.setChecked(myconfig.Cast(myconfig["GUIstate"][childName],template))
                elif hasattr(child,'currentIndex'):
                    template=child.currentIndex()
                    child.setCurrentIndex(myconfig.Cast(myconfig["GUIstate"][childName],template))
                elif hasattr(child,'text'):
                    template=child.text()
                    child.setText(myconfig.Cast(myconfig["GUIstate"][childName],template))

    def ConnectGUISlots(self):
        self.btn_StartCams.clicked.connect(self.StartCams)
        self.btn_StopCams.clicked.connect(self.StopCams)
        self.sbx_tapeSpeed.valueChanged.connect(self.setTapeSpeed)
        self.btn_TapeStart.clicked.connect(self.TapeStart)
        self.btn_TapeStop.clicked.connect(self.TapeStop)

    def TapeStart(self):
        if self.radiobtn_forward.isChecked():
            Atum.Start()
        else:
            Atum.Reverse()

    def TapeStop(self):
        Atum.Stop()

    def UpdateWindowTitle(self):
        Title="AGTUM"
        self.setWindowTitle(Title)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

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

    print("Loading main GUI...")
    window = mainGUI(os.path.join(application_path,"PyAGTUM_mainwindow_210302.ui"))

    sys.exit(app.exec_())