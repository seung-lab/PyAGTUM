# -*- coding: utf-8 -*-

# based on PyAGTUM_210116
# remove un-used functions, remove cbx_synRetractSpeed
# 210223 not use the 3rd camera, remove pump
# remove retract phase diff log
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

application_path = os.path.dirname(__file__)

if sys.platform.startswith('win'):
    win=1
else:
    win=0

class CamTimer(log.valuelogger):
    CameraSNs=[]
    Cameras=[]
    CamFrames=[]
    CamFrameRate=10
    def setupCams(self):
        for icam,camSN in enumerate(self.CameraSNs):
            cam=xiapi.Camera()
            cam.open_device_by_SN(camSN)
            # settings
            cam.set_imgdataformat('XI_RGB24')
            #1028*1232*3*20*24
            cam.set_limit_bandwidth(750)
            cam.set_exposure(10000)
            cam.set_decimation_horizontal(2)
            cam.set_decimation_vertical(2)
            cam.set_framerate(self.CamFrameRate)
            cam.frame=self.CamFrames[icam]
            cam.name=self.CamFrames[icam].text()
            cam.image=xiapi.Image()
            self.Cameras.append(cam)

        for cam in self.Cameras:
            cam.start_acquisition()

    def updateVis(self):
        for cam in self.Cameras:
            #get data and pass them from camera to img
            try:
                cam.get_image(cam.image)
#                print('Image read from ' + cam.name)
                #cv2.imshow("XIMEA cams", img.get_image_data_numpy())

                npimg=cam.image.get_image_data_numpy()
                npimg=np.copy(npimg[::2,::2,:])
    #            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))

                Qimg = QtGui.QImage(npimg,npimg.shape[1],npimg.shape[0], QtGui.QImage.Format_RGB888)
                pix = QtGui.QPixmap.fromImage(Qimg)
                cam.frame.setPixmap(pix)
            except:
                print('Image skipped for ' + cam.name)

    def datacollector(self):
        self.updateVis()

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

class LEICAretractdurationlog(log.valuelogger):
    historylength=500
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)

class LEICAcutdurationlog(log.valuelogger):
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


class Offsetlog(log.valuelogger):
    historylength=500
    def updateVis(self):
        self.parent.ptOffset.setData(self.timelog,self.valuelog)

    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)

class LEICAchopperlog(log.valuelogger):
    historylength=2000
    upStateStart=[]
    downStateStart=[]
    prev_offset=0
    state='none'

    def updateVis(self):
        self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)

    def datacollector(self):
        chopperSignal=int(self.parent.syncLEICA_chopper.read())
        self.updateLog(chopperSignal)
        if self.valuelog.__len__()<2:
            return

        if self.valuelog[-1]==1 and self.valuelog[-2]==0: #cutting phase starts
            self.upStateStart.append(self.timelog[-1])
            rs,_ = Leica.getReturnSpeed()

            print("retract speed: {}".format(rs))

                        # 210118 _zz_ use retract speed to keep phase offset
             # sbx_retractFactor (default 0.5, which mean 100 +/-)
            if self.parent.cbx_synOffset.isChecked():
                delta = self.parent.Offsetlog.valuelog[-1] - self.parent.sbx_targetphase.value()
              #  LEICAcycle = self.parent.LEICAcutdurationlog.valuelog[-1] + self.parent.LEICAretractdurationlog.valuelog[-1]
                ATUMcycle = self.parent.ATUMcyledurationlog.valuelog[-1]
                sp = int((-217)*(ATUMcycle) + 4756)
                if abs(delta) <= 0.3:
                    self.parent.setReturnSpeed(sp)
                    print("in sync {}".format(sp))
                elif abs(delta) <= 0.8:
                    newRetractSpeed=int(max(450,min(1400,sp + delta*100)))
                    self.parent.setReturnSpeed(newRetractSpeed)
                    if delta > 0:
                        print("speedup to {}".format(newRetractSpeed))
                    else:
                        print("slowdown to {}".format(newRetractSpeed))
                else:
                    # diff = round(delta/0.1,2)*2
                    newRetractSpeed=int(max(450,min(1400,sp + delta*200)))
                    self.parent.setReturnSpeed(newRetractSpeed)
                    if delta > 0:
                        print("speedup to {}".format(newRetractSpeed))
                    else:
                        print("slowdown to {}".format(newRetractSpeed))


            if self.downStateStart.__len__()>0 and self.upStateStart.__len__()>0:
                retractDuration=self.upStateStart[-1]-self.downStateStart[-1]
                self.parent.LEICAretractdurationlog.datacollector(retractDuration)

        if self.valuelog[-2]==1 and self.valuelog[-1]==0: #retraction phase starts
            self.downStateStart.append(self.timelog[-1])
            if self.upStateStart.__len__()>0 and self.downStateStart.__len__()>0:
                cutDuration=self.downStateStart[-1]-self.upStateStart[-1]
                self.parent.LEICAcutdurationlog.datacollector(cutDuration)
                if self.parent.LEICAretractdurationlog.valuelog.__len__()>0:
                    LEICAcycle = cutDuration + self.parent.LEICAretractdurationlog.valuelog[-1]
                    print("LEICA cycle: {}s".format(round(LEICAcycle,2)))


            if self.parent.ATUMcyledurationlog.valuelog.__len__()>0:
                CycleTime=self.parent.ATUMcyledurationlog.valuelog[-1]
                TargetCycleTime=(self.parent._DistanceBetweenSlots/self.parent.sbx_targetCycleSpeed.value())
                TapeSpeedDiff=CycleTime-TargetCycleTime
                self.parent.TapeSpeedDifflog.datacollector(TapeSpeedDiff)

                if self.parent.tapespeedlog.valuelog.__len__()>0:
                    currentTapeSpeed=np.float(self.parent.tapespeedlog.valuelog[-1])
                    if self.parent.cbx_synCutting.isChecked():
                        durationRatio=CycleTime/TargetCycleTime
                        newTapeSpeed=max(0.0,min(5.0,currentTapeSpeed+\
                           self.parent.sbx_cycleFactor.value()*(durationRatio-1.0)*currentTapeSpeed))
                        if not (currentTapeSpeed==newTapeSpeed):
                            self.parent.setTapeSpeed(newTapeSpeed)

                    if self.upStateStart.__len__()>1 and self.parent.ATUMchopperlog.upStateStart.__len__()>0:
                        offset=self.upStateStart[-1]-self.parent.ATUMchopperlog.upStateStart[-1]

                        # 210130 ZZ adjust tape speed for each cycle
                        if self.parent.cbx_synTS.isChecked():
                            cdelta = offset - self.parent.sbx_targetphase.value()

                            # offset Leica - ATUM
                            # offset < 0 -> Leica happened then ATUM
                            # more minus -> ATUM later than leica too much

                            OffsetDiff = abs(self.parent.Offsetlog.valuelog[-1]) - abs(offset)

                            # ATUMcycle = np.mean(self.parent.ATUMcyledurationlog.valuelog[-2:])
                            # cdelta = ATUMcycle - LEICAcycle
                           # BaseSpeed = self.parent.sbx_targetCycleSpeed.value()

                            if abs(cdelta) < 0.4:
                                self.parent.setTapeSpeed(self.parent.sbx_targetCycleSpeed.value())
                                print("tape in sync")
                            elif OffsetDiff < 0:
                                # not getting better
                                if cdelta < 0:
                                    f = 0.02
                                    print("tape speed up")
                                else:
                                    f = -0.02
                                    print("tape slow down")
                                self.parent.setTapeSpeed(currentTapeSpeed + f)
                            else:
                                print("adjusting")
                        print("offset:{}".format(round(offset, 2)))
                        self.parent.Offsetlog.datacollector(offset)
        del self.upStateStart[:-3]
        del self.downStateStart[:-3]

class ATUMchopperlog(log.valuelogger):
    historylength=2000
    upStateStart=[]
    downStateStart=[]
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
            self.upStateStart.append(self.timelog[-1])
            if self.downStateStart.__len__()>0:
                interslotDuration=self.upStateStart[-1]-self.downStateStart[-1]
                self.parent.ATUMinterslotdurationlog.datacollector(interslotDuration)
            if self.upStateStart.__len__()>1:
                ATUMcycle=np.diff(self.upStateStart[-2:])
                self.parent.ATUMcyledurationlog.datacollector(ATUMcycle[-1])
                print("ATUM cycle: {}, actual tape speed: {}".format(round(ATUMcycle[-1],2), round(6/ATUMcycle[-1],2)))
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

class retractspeedlog(log.valuelogger):
    historylength=500
    def datacollector(self):
        [RetractionSpeed,resstr]=Leica.getReturnSpeed()
        if RetractionSpeed>=0:
            self.updateLog(RetractionSpeed)
        return


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
        self.ptsyncLEICA_chopper = self.pg_sync.plot(pen=(0, 255, 200, 200))
        self.ptsyncATUM_chopper = self.pg_sync.plot(pen=(255, 0, 20, 200))
        self.ptOffset = self.pg_phasediff.plot(pen=(255, 0, 20, 200))


        self.retractspeedlog=retractspeedlog();
        self.retractspeedlog.initiateTimer(1000,self._logpath,'retractspeed',parent=self)

        self.tapespeedlog=tapespeedlog();
        self.tapespeedlog.initiateTimer(1000,self._logpath,'tapespeed',parent=self)

        self.ATUMchopperlog=ATUMchopperlog();
        self.ATUMchopperlog.initiateTimer(50,self._logpath,'ATUMchopper',parent=self)

        self.LEICAchopperlog=LEICAchopperlog();
        self.LEICAchopperlog.initiateTimer(50,self._logpath,'LEICAchopper',parent=self)

        self.ATUMslotdurationlog=ATUMslotdurationlog()
        self.ATUMslotdurationlog.initiateTimer(1000,self._logpath,'ATUMslotduration',parent=self)
        self.ATUMinterslotdurationlog=ATUMinterslotdurationlog()
        self.ATUMinterslotdurationlog.initiateTimer(1000,self._logpath,'ATUMinterslotduration',parent=self)
        self.LEICAretractdurationlog=LEICAretractdurationlog()
        self.LEICAretractdurationlog.initiateTimer(1000,self._logpath,'LEICAretractduration',parent=self)
        self.LEICAcutdurationlog=LEICAcutdurationlog()
        self.LEICAcutdurationlog.initiateTimer(1000,self._logpath,'LEICAcutduration',parent=self)

        self.TapeSpeedDifflog=TapeSpeedDifflog()
        self.TapeSpeedDifflog.initiateTimer(1000,self._logpath,'TapeSpeedDiff',parent=self)

        self.Offsetlog=Offsetlog()
        self.Offsetlog.initiateTimer(1000,self._logpath,'Offset',parent=self)

        self.ATUMcyledurationlog=ATUMcyledurationlog()
        self.ATUMcyledurationlog.initiateTimer(1000,self._logpath,'ATUMcyleduration',parent=self)


    def SetupHardware(self):
        self.cbx_synRetractSpeed.setChecked(0)

        self.CamTimer=CamTimer()
        self.CamTimer.CameraSNs=self._CameraSNs

        if not self._cam_presection in self.CamTimer.CamFrames:
            self.CamTimer.CamFrames.append(self._cam_presection)
        if not self._cam_postsection in self.CamTimer.CamFrames:
            self.CamTimer.CamFrames.append(self._cam_postsection)

        self.CamTimer.setupCams()
        self.CamTimer.initiateTimer(100,None,None,parent=self)
        self.CamTimer.start()

        self.syncATUM_chopper=nidaqmx.Task()
        self.syncATUM_chopper.di_channels.add_di_chan(self._syncATUM_chopperPort)
        self.syncLEICA_chopper=nidaqmx.Task()
        self.syncLEICA_chopper.di_channels.add_di_chan(self._syncLEICA_chopperPort)

    def StartCams(self):

        Atum.Start()

        print("start cameras")
        newTapeSpeed=0.4
        self.setTapeSpeed(newTapeSpeed)

        self.setReturnSpeed()

        self.retractspeedlog.start()
        self.ATUMchopperlog.start()
        self.LEICAchopperlog.start()

        self.ATUMslotdurationlog.start()
        self.ATUMinterslotdurationlog.start()
        self.LEICAretractdurationlog.start()
        self.LEICAcutdurationlog.start()

        self.tapespeedlog.start()
        self.TapeSpeedDifflog.start()
        self.Offsetlog.start()
        self.ATUMcyledurationlog.start()

    def StopCams(self):
        print("stopped cameras")
        Atum.Stop()
        self.retractspeedlog.stopLog()
        self.ATUMchopperlog.stopLog()
        self.LEICAchopperlog.stopLog()

        self.ATUMslotdurationlog.stopLog()
        self.ATUMinterslotdurationlog.stopLog()
        self.LEICAretractdurationlog.stopLog()
        self.LEICAcutdurationlog.stopLog()

        self.tapespeedlog.stopLog()
        self.TapeSpeedDifflog.stopLog()
        self.Offsetlog.stopLog()
        self.ATUMcyledurationlog.stopLog()


    def StopHardware(self):
        self.CamTimer.stopLog()
        for cam in self.CamTimer.Cameras:
            cam.stop_acquisition()

        self.StopCams()

        for cam in self.CamTimer.Cameras:
            cam.close_device()

        self.syncATUM_chopper.close()
        self.syncLEICA_chopper.close()

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
        self.sbx_retractionSpeed.valueChanged.connect(self.setReturnSpeed)
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
    window = mainGUI(os.path.join(application_path,"PyAGTUM_mainwindow_210223_-3rdCam_-Water.ui"))

    sys.exit(app.exec_())
