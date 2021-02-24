# -*- coding: utf-8 -*-

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic

import sys
import os
from AGTUMconfigparser import config
from ximea import xiapi
import time
import nidaqmx
import serial
import paintableqlabel
import cv2
import copy

import numpy as np
from scipy import stats, signal, fftpack
import leicaCmds as Leica
import atumCmds_2 as Atum
import syringepump as Pump
import valuelogger as log

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

def next_power_of2(x):
    return 1<<(x-1).bit_length()

class CamTimer(log.valuelogger):
    def updateVis(self):
        self.parent.CamCaptureFrame()
        
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
    
class RetractPhaseDifflog(log.valuelogger):    
    historylength=500
    def updateVis(self):
        self.parent.ptRetractPhaseDiff.setData(self.timelog,self.valuelog)
                
    def datacollector(self,value=None):
        if value is None:
           return 
        self.updateLog(value)

class TapeSpeedDifflog(log.valuelogger):    
    historylength=500
    def updateVis(self):
        self.parent.ptTapeSpeedDiff.setData(self.timelog,self.valuelog)
                
    def datacollector(self,value=None):
        if value is None:
           return 
        self.updateLog(value)

class LEICAchopperlog(log.valuelogger):    
    historylength=2000
    upStateStart=[]
    downStateStart=[]
    def updateVis(self):
        self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)
        
    def datacollector(self):
        chopperSignal=int(self.parent.syncLEICA_chopper.read())
        self.updateLog(chopperSignal)
        if self.valuelog.__len__()<2:
            return
        
        if self.valuelog[-1]==1 and self.valuelog[-2]==0: #cutting phase starts
            self.upStateStart.append(self.timelog[-1])
            if self.downStateStart.__len__()>0 and self.upStateStart.__len__()>0:
                retractDuration=self.upStateStart[-1]-self.downStateStart[-1]
                self.parent.LEICAretractdurationlog.datacollector(retractDuration)
                if self.parent.LEICAretractdurationlog.valuelog.__len__()>0 and self.parent.ATUMinterslotdurationlog.valuelog.__len__()>0:
                    RetractPhaseDiff=self.parent.LEICAretractdurationlog.valuelog[-1]-self.parent.ATUMinterslotdurationlog.valuelog[-1]
                    self.parent.RetractPhaseDifflog.datacollector(RetractPhaseDiff)
                    if self.parent.cbx_synRetractSpeed.isChecked() and self.parent.retractspeedlog.valuelog.__len__()>0:
                        durationRatio=\
                            self.parent.LEICAretractdurationlog.valuelog[-1]/self.parent.ATUMinterslotdurationlog.valuelog[-1]                          
                        currentRetractSpeed=np.float(self.parent.retractspeedlog.valuelog[-1])
                        newRetractSpeed=int(max(300,min(5000,currentRetractSpeed+\
                           self.parent.sbx_retractFactor.value()*(durationRatio-1.0)*currentRetractSpeed)))
                        if not (currentRetractSpeed==newRetractSpeed):                
                            Leica.setReturnSpeed(newRetractSpeed)
                        
            offset=0.0
            if self.upStateStart.__len__()>1 and self.parent.ATUMchopperlog.upStateStart.__len__()>0:
                ATUMup=self.parent.ATUMchopperlog.upStateStart[-1]
                offset1=self.upStateStart[-1]-ATUMup
                offset2=self.upStateStart[-2]-ATUMup
                if abs(offset1)<abs(offset2):
                    offset=offset1
                else:
                    offset=offset2
            if self.parent.LEICAretractdurationlog.valuelog.__len__()>0 and self.parent.retractspeedlog.valuelog.__len__()>0:
                durationRatio=(self.parent.sbx_targetretractphase.value()-offset)/self.parent.LEICAretractdurationlog.valuelog[-1]
                currentRetractSpeed=np.float(self.parent.retractspeedlog.valuelog[-1])
                factor=-durationRatio/(1.0+durationRatio)
                newRetractSpeed=int(max(300,min(5000,currentRetractSpeed+\
                   self.parent.sbx_retractFactor.value()*factor*currentRetractSpeed)))
                print("offset:{0}, factor:{1}, new retract speed:{2}".format(offset,factor,newRetractSpeed))
                if self.parent.cbx_PhaseLock.isChecked() and not (currentRetractSpeed==newRetractSpeed):                
                    Leica.setReturnSpeed(newRetractSpeed)

        if self.valuelog[-2]==1 and self.valuelog[-1]==0: #retraction phase starts
            self.downStateStart.append(self.timelog[-1])
            if self.upStateStart.__len__()>0 and self.downStateStart.__len__()>0:
                cutDuration=self.downStateStart[-1]-self.upStateStart[-1]
                self.parent.LEICAcutdurationlog.datacollector(cutDuration)


            if self.parent.cbx_synCutting.isChecked() and self.parent.ATUMcyledurationlog.valuelog.__len__()>0:
                CycleTime=self.parent.ATUMcyledurationlog.valuelog[-1]
                TargetCycleTime=(self.parent._DistanceBetweenSlots/self.parent.sbx_targetCycleSpeed.value())
                TapeSpeedDiff=CycleTime-TargetCycleTime
                self.parent.TapeSpeedDifflog.datacollector(TapeSpeedDiff)
                durationRatio=CycleTime/TargetCycleTime                     
                if self.parent.tapespeedlog.valuelog.__len__()>0:
                    currentTapeSpeed=np.float(self.parent.tapespeedlog.valuelog[-1])
                    newTapeSpeed=max(0.0,min(5.0,currentTapeSpeed+\
                       self.parent.sbx_cycleFactor.value()*(durationRatio-1.0)*currentTapeSpeed))
                    if not (currentTapeSpeed==newTapeSpeed):                
                        Atum.sTS(newTapeSpeed)

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
        self.parent.sbx_tapeSpeed.setValue(self.valuelog[-1])
    
class retractspeedlog(log.valuelogger):
    historylength=500        
    def datacollector(self):        
        [RetractionSpeed,resstr]=Leica.getReturnSpeed()
        if RetractionSpeed>=0:
            self.updateLog(RetractionSpeed)
            self.parent.sbx_retractionSpeed.blockSignals(True)
            self.parent.sbx_retractionSpeed.setValue(RetractionSpeed)
            self.parent.sbx_retractionSpeed.blockSignals(False)
        return
     
class waterlevellog(log.valuelogger):
    waterlevel=None 
    waterwindow=20
    
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
    _CameraSNs=['CICAU1641091','CICAU1914024','CICAU1914041']
    Cameras=[]
    CamFrames=[]
    CamTimer=QtCore.QTimer()
    _CamFrameRate=10;
    _syncATUM_chopperPort="Dev1/pfi0"
    _syncLEICA_chopperPort="Dev1/pfi1"
    _logpath='C:\dev\PyAGTUM\logs'
    _DistanceBetweenSlots=6.0#mm
    
    def __init__(self,uifile):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        myconfig.LoadConfig(self,"pyAGTUM")
               
        self.setupATUMsync()
        self.ConnectGUISlots()
        
        self.SetupHardware()
        
        if hasattr(self,'_StartPosition'):
            if self._StartPosition.__len__()>3:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setGeometry(self._StartPosition[0],self._StartPosition[1],self._StartPosition[2],self._StartPosition[3])
        self.UpdateWindowTitle()
        self.SetupGUIState(self)
        
        self.paintableCam=paintableqlabel.paintableqlabel(self.cam_knife)
        self.show()

    def setupATUMsync(self):
        self.ptsyncLEICA_chopper = self.pg_sync.plot(pen=(0, 255, 200, 200))
        self.ptsyncATUM_chopper = self.pg_sync.plot(pen=(255, 0, 20, 200)) 
        self.ptwaterlevel=self.pg_waterlevel.plot(pen=(0, 255, 200, 200))
        self.ptwaterthres=pg.InfiniteLine(pen=(255, 0, 0, 200),angle=0,movable=False)
        self.pg_waterlevel.addItem(self.ptwaterthres)
        self.ptRetractPhaseDiff=self.pg_phasediff.plot(pen=(0, 255, 200, 200))
        self.ptTapeSpeedDiff =  self.pg_phasediff.plot(pen=(255, 0, 20, 200)) 
        
        self.waterlevellog=waterlevellog();
        self.waterlevellog.initiateTimer(1000,self._logpath,'waterlevel',parent=self)
        
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
        
        self.RetractPhaseDifflog=RetractPhaseDifflog()
        self.RetractPhaseDifflog.initiateTimer(1000,self._logpath,'RetractPhaseDiff',parent=self)
        self.TapeSpeedDifflog=TapeSpeedDifflog()
        self.TapeSpeedDifflog.initiateTimer(1000,self._logpath,'TapeSpeedDiff',parent=self)

        self.ATUMcyledurationlog=ATUMcyledurationlog()
        self.ATUMcyledurationlog.initiateTimer(1000,self._logpath,'ATUMcyleduration',parent=self)

         
    def SetupHardware(self):
        self.cbx_pumpOn.setChecked(0)
        self.cbx_synRetractSpeed.setChecked(0)
        if not self._cam_presection in self.CamFrames:
            self.CamFrames.append(self._cam_presection)
        if not self._cam_postsection in self.CamFrames:
            self.CamFrames.append(self._cam_postsection)
        if not self.cam_knife in self.CamFrames:
            self.CamFrames.append(self.cam_knife)
        
        for icam,camSN in enumerate(self._CameraSNs):
            cam=xiapi.Camera()
            cam.open_device_by_SN(camSN)        
            # settings
            cam.set_imgdataformat('XI_RGB24')
            #1028*1232*3*20*24
            cam.set_limit_bandwidth(750)
            cam.set_exposure(10000)
            cam.set_decimation_horizontal(2)
            cam.set_decimation_vertical(2)
            cam.set_framerate(self._CamFrameRate)            
            cam.frame=self.CamFrames[icam]
            cam.name=self.CamFrames[icam].text()
            cam.image=xiapi.Image()
            self.Cameras.append(cam)

        for cam in self.Cameras:
            cam.start_acquisition()
            
        self.CamTimer=CamTimer()
        self.CamTimer.initiateTimer(1000./self._CamFrameRate,None,None,parent=self)
        self.CamTimer.start()        

        self.syncATUM_chopper=nidaqmx.Task()      
        self.syncATUM_chopper.di_channels.add_di_chan(self._syncATUM_chopperPort)
        self.syncLEICA_chopper=nidaqmx.Task()      
        self.syncLEICA_chopper.di_channels.add_di_chan(self._syncLEICA_chopperPort)
            
    def CamCaptureFrame(self):
        for cam in self.Cameras:
            #get data and pass them from camera to img
            try:
                cam.get_image(cam.image)
#                print('Image read from ' + cam.name)
                #cv2.imshow("XIMEA cams", img.get_image_data_numpy())
            except:
                print('Image skipped for ' + cam.name)
                       
            npimg=cam.image.get_image_data_numpy()
            npimg=np.copy(npimg[::2,::2,:])
#            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))         

            if cam.name=='knife cam':
                ROIXbegin=min([cam.frame.begin.x(),cam.frame.end.x()])
                ROIXend=max([cam.frame.begin.x(),cam.frame.end.x()])
                ROIYbegin=min([cam.frame.begin.y(),cam.frame.end.y()])
                ROIYend=max([cam.frame.begin.y(),cam.frame.end.y()])
                self.waterlevellog.waterlevel=np.mean(npimg[ROIYbegin:ROIYend,ROIXbegin:ROIXend])
                
            Qimg = QtGui.QImage(npimg,npimg.shape[1],npimg.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(Qimg)
            cam.frame.setPixmap(pix)
#        print("captured frame")

    def StartCams(self):
        Atum.sTT(int(30))
        Atum.sTS(1.0)
        Atum.Start()

        print("start cameras")
        Atum.sTS(0.5)
        Leica.setReturnSpeed(self.sbx_retractionSpeed.value())
        
        self.waterlevellog.start()
        self.retractspeedlog.start()
        self.ATUMchopperlog.start()
        self.LEICAchopperlog.start()  
        
        self.ATUMslotdurationlog.start()  
        self.ATUMinterslotdurationlog.start()  
        self.LEICAretractdurationlog.start()  
        self.LEICAcutdurationlog.start()  
        self.RetractPhaseDifflog.start()
        
        self.tapespeedlog.start()
        self.TapeSpeedDifflog.start()
        self.ATUMcyledurationlog.start()

    def StopCams(self):
        print("stopped cameras")
        Atum.Stop()
        if self.retractspeedlog.valuelog.__len__()>0:
            self.sbx_retractionSpeed.blockSignals(True)
            self.sbx_retractionSpeed.setValue(self.retractspeedlog.valuelog[-1])
            self.sbx_retractionSpeed.blockSignals(False)
            
        self.waterlevellog.stopLog()
        self.retractspeedlog.stopLog()
        self.ATUMchopperlog.stopLog()
        self.LEICAchopperlog.stopLog()   
        
        self.ATUMslotdurationlog.stopLog()  
        self.ATUMinterslotdurationlog.stopLog()  
        self.LEICAretractdurationlog.stopLog()  
        self.LEICAcutdurationlog.stopLog()  
        self.RetractPhaseDifflog.stopLog()

        self.tapespeedlog.stopLog()
        self.TapeSpeedDifflog.stopLog()
        self.ATUMcyledurationlog.stopLog()
        
    def WaterThresholdChanged(self):
        newValue=self.sldr_WaterThres.value()
        self.ptwaterthres.setValue(newValue)
        print("Threshold updated: {0}".format(newValue))
            
    def StopHardware(self):
        self.CamTimer.stopLog()
        for cam in self.Cameras:
            cam.stop_acquisition()

        self.StopCams()

        for cam in self.Cameras:
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
        self.sldr_WaterThres.valueChanged.connect(self.WaterThresholdChanged)
        self.sbx_retractionSpeed.valueChanged.connect(self.SetRetractSpeed)

    def SetRetractSpeed(self):
        Leica.setReturnSpeed(self.sbx_retractionSpeed.value())

    def UpdateWindowTitle(self):
        Title="AGTUM"      
        self.setWindowTitle(Title)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    #Loading default configuration
    if win:
        config_name = 'DefaultConfig_win.cfg'    
    else:
        config_name = 'DefaultConfig.cfg'    

    configfile = os.path.join(application_path, config_name)
    if not os.path.isfile(configfile):
        QtWidgets.QMessageBox.warning(None,"Error",
            "Configuration file missing:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)        
        sys.exit()            

    try:
        myconfig = config(configfile)
    except:
        QtWidgets.QMessageBox.warning(None, "Error",
            "Configuration file corrupted:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)
        sys.exit()

    window = mainGUI(os.path.join(application_path,"PyAGTUM_mainwindow.ui"))

    sys.exit(app.exec_())