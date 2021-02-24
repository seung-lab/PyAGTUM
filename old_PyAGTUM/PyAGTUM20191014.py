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
        
        
class LEICAretractdurationlog(log.valuelogger):    
    historylength=2000
    def updateVis(self):
        self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)
        
    def datacollector(self):
    

class LEICAchopperlog(log.valuelogger):    
    historylength=2000
    upStateStart=None
    downStateStart=None
    def updateVis(self):
        self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)
        
    def datacollector(self):
        self.updateLog(int(self.parent.syncLEICA_chopper.read()))
        if self.valuelog.__len__()<2:
            return
        
        if self.valuelog[-1]==1 and self.valuelog[-2]==0:
            self.upStateStart=timelog[-1]
        if self.valuelog[-2]==1 and self.valuelog[-1]==0:
            self.downStateStart=timelog[-1]
        

class FreqShiftlog(log.valuelogger):    
    historylength=30
    def datacollector(self):
        freqratio=self.parent.FrequencyRatio()
        self.updateLog(freqratio)

class ATUMchopperlog(log.valuelogger):    
    historylength=2000
    def updateVis(self):
        self.parent.ptsyncATUM_chopper.setData(self.timelog,self.valuelog)
        
    def datacollector(self):
        self.updateLog(int(self.parent.syncATUM_chopper.read()))

class retractspeedlog(log.valuelogger):
    historylength=500        
    def datacollector(self):        
        [OldSpeed,resstr]=Leica.getReturnSpeed()
        if OldSpeed>=0:
            self.updateLog(OldSpeed)
            if self.parent.FreqShiftlog.valuelog.__len__()<self.parent.FreqShiftlog.historylength:
                return
            freqShift=self.parent.FreqShiftlog.valuelog[-1]
            if freqShift is None:
                return
            NewSpeed=int(max(10,min(5000,OldSpeed*freqShift)))
            if not OldSpeed==NewSpeed:                
                Leica.setReturnSpeed(NewSpeed)
                print("New speed:{0}, old speed:{1}, freqShift".format(NewSpeed,OldSpeed,freqShift))        
                self.parent.FreqShiftlog.timelog=[]
                self.parent.FreqShiftlog.valuelog=[]
                print("reset freq shift log: {0}".format(self.parent.FreqShiftlog.valuelog.__len__()))
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
    
    def __init__(self,uifile):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        myconfig.LoadConfig(self,"pyAGTUM")
               
        self.ConnectGUISlots()
        
        self.SetupHardware()
        
        if hasattr(self,'_StartPosition'):
            if self._StartPosition.__len__()>3:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setGeometry(self._StartPosition[0],self._StartPosition[1],self._StartPosition[2],self._StartPosition[3])
        self.UpdateWindowTitle()
        
        self.paintableCam=paintableqlabel.paintableqlabel(self.cam_knife)
        self.setupATUMsync()
        self.show()

    def FrequencyRatio(self):
        x=self.ATUMchopperlog.valuelog;
        x_times=self.ATUMchopperlog.timelog;
        y=self.LEICAchopperlog.valuelog;
        y_times=self.LEICAchopperlog.timelog;
        
        historythres=min(x_times[-1],y_times[-1])-30; #only consider the past 30 seconds
        try:
            x_startind=next(i for i,v in enumerate(x_times) if v>historythres)
        except:
            x_startind=0
        try:
            y_startind=next(i for i,v in enumerate(y_times) if v>historythres)
        except:
            y_startind=0
            
        [ATUMspec,LEICAspec,freq]=self.FFT(x_times[x_startind:],x[x_startind:],y_times[y_startind:],y[y_startind:])
        if ATUMspec is None:
            return
        
        x_fmax=ATUMspec.argmax()
        y_fmax=LEICAspec.argmax()
                
        self.ptATUMfft.setData(freq,ATUMspec)
        self.ptLEICAfft.setData(freq,LEICAspec)
        print("freq ratio (ATUM:Leica)= {0}".format(freq[x_fmax]/freq[y_fmax]))
        return freq[x_fmax]/freq[y_fmax]
                
    def FFT(self,x_times,x,y_times,y): 
        N=next_power_of2(min([x_times.__len__(),y_times.__len__()]))
        if N<=2:
            return [None,None,None]
        T = (max(max(x_times), max(y_times)) - min(min(x_times), min(y_times))) / N # average period
        if T==0:
            return [None,None,None]
        Fs = 1 / T # average sample rate frequency
        frq = Fs * np.arange(0, N // 2 + 1) / N; # resampled frequency vector
        x_new, x_times_new = signal.resample(x, N, x_times)        
        y_new, y_times_new = signal.resample(y, N, y_times)        
        
        x_new = stats.zscore(x_new)
        y_new = stats.zscore(y_new)
        frq = frq[range(int(N/2))]  # one side frequency range
        fft_x = fftpack.fft(x_new) / N  # fft computing and normalization
        fft_y = fftpack.fft(y_new) / N  # fft computing and normalization
            
        fft_x = fft_x[range(int(N/2))] / max(fft_x[range(int(N/2))])
        fft_y = fft_y[range(int(N/2))] / max(fft_y[range(int(N/2))])
            
        fft_x = abs(fft_x)
        fft_y = abs(fft_y)
        return [fft_x,fft_y,frq]    
    #        # regularize datasets by subtracting mean and dividing by s.d.
    #        x = stats.zscore(x)
    #        y = stats.zscore(y)
    #        # Find cross-correlation
    #        xcorr = signal.correlate(x,y)/nsamples
    #        
    #        # delta time array to match xcorr
    #        dt = np.arange(1-nsamples, nsamples)        
    #        recovered_time_shift = dt[xcorr.argmax()]
    #        peak=xcorr.max()
    #        if np.isnan(peak):
    #            peak=0.0
    #        print("peak: {0}".format(peak))
            


    def setupATUMsync(self):
        self.ptsyncLEICA_chopper = self.pg_sync.plot(pen=(0, 255, 200, 200))
        self.ptsyncATUM_chopper = self.pg_sync.plot(pen=(255, 0, 20, 200)) 
        self.ptwaterlevel=self.pg_waterlevel.plot(pen=(0, 255, 200, 200))
        self.ptwaterthres=pg.InfiniteLine(pen=(255, 0, 0, 200),angle=0,movable=False)
        self.pg_waterlevel.addItem(self.ptwaterthres)
#        self.ptphasediff=self.pg_FFT.plot(pen=(0, 255, 200, 200))
        self.ptLEICAfft=self.pg_FFT.plot(pen=(0, 255, 200, 200))
        self.ptATUMfft=self.pg_FFT.plot(pen=(255, 0, 20, 200))
        
        self.waterlevellog=waterlevellog();
        self.waterlevellog.initiateTimer(1000,self._logpath,'waterlevel',parent=self)
        
        self.retractspeedlog=retractspeedlog();
        self.retractspeedlog.initiateTimer(1000,self._logpath,'retractspeed',parent=self)

        self.ATUMchopperlog=ATUMchopperlog();
        self.ATUMchopperlog.initiateTimer(50,self._logpath,'ATUMchopper',parent=self)

        self.LEICAchopperlog=LEICAchopperlog();
        self.LEICAchopperlog.initiateTimer(50,self._logpath,'LEICAchopper',parent=self)
        
        self.FreqShiftlog=FreqShiftlog();
        self.FreqShiftlog.initiateTimer(1000,self._logpath,'freqshift',parent=self)
         
    def SetupHardware(self):
        self.cbx_pumpOn.setChecked(0)
        
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
        
    def SetPhase(self):
        phase=self.LEICAchopperlog.UpStates[-1]-self.ATUMchopperlog.UpStates[-1]
        print("set phase to {0}".format(phase))
        self.sbx_targetphase.setValue(phase)
            
#    def PID(self):                   
#        output=self.logATUM_fft[-1]-self.logLEICA_fft[-1]
#        dt=1.0/self._CamFrameRate
#        integrationwindow=10*self._CamFrameRate;
#        if self.logATUM_fft.__len__()==0:
#            errorval=0.0
#            integralval=0.0
#        else:
#            errorval=self.logATUM_fft[-1]-self.logLEICA_fft[-1]
#            integralval=np.sum(self.logPIDerror[(-1*integrationwindow):])*dt+errorval*dt
#        if self.logPIDerror.__len__()==0:
#            derivativeval=errorval/dt
#        else:
#            derivativeval=(errorval-self.logPIDerror[-1])/dt
#        output=self.sbx_Kp.value()*errorval+self.sbx_Ki.value()*integralval+self.sbx_Kd.value()*derivativeval
#        self.logPIDerror.append(errorval)
#        return output
        
#    def PID(self):
#        phaseweight=0.0*90.0/360.0
#        corrweight=1.0;
#        dt=1.0/self._CamFrameRate
#        integrationwindow=30*self._CamFrameRate;
#        setpoint=self.sbx_targetphase.value()
#        if self.logATUM_fft.__len__()==0:
#            errorval=phaseweight*setpoint+0.0
#            integralval=0
#        else:
#            errorval=phaseweight*(setpoint-self.logATUM_fft[-1])+corrweight*(1-self.logLEICA_fft[-1])
#            integralval=np.sum(self.logPIDerror[(-1*integrationwindow):])*dt+errorval*dt
#        if self.logPIDerror.__len__()==0:
#            derivativeval=errorval/dt
#        else:
#            derivativeval=(errorval-self.logPIDerror[-1])/dt
#        output=self.sbx_Kp.value()*errorval+self.sbx_Ki.value()*integralval+self.sbx_Kd.value()*derivativeval
#        self.logPIDerror.append(errorval)
#        return output

    def StartCams(self):
        Atum.sTT(int(30))
        Atum.sTS(1.0)
        Atum.Start()

        print("start cameras")
        Atum.sTS(0.4)
        Leica.setReturnSpeed(self.sbx_startSpeed.value())
        
        self.waterlevellog.start()
        self.retractspeedlog.start()
        self.ATUMchopperlog.start()
        self.LEICAchopperlog.start()  
        self.FreqShiftlog.start()        

    def StopCams(self):

        print("stopped cameras")
        Atum.Stop()
        if self.retractspeedlog.valuelog.__len__()>0:
            self.sbx_startSpeed.setValue(self.retractspeedlog.valuelog[-1])
            
        self.waterlevellog.stopLog()
        self.retractspeedlog.stopLog()
        self.ATUMchopperlog.stopLog()
        self.LEICAchopperlog.stopLog()   
        self.FreqShiftlog.stopLog()
        
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
                childName=str(child.objectName(),"utf-8")
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
        self.btn_setPhase.clicked.connect(self.SetPhase)
        self.btn_StartCams.clicked.connect(self.StartCams)
        self.btn_StopCams.clicked.connect(self.StopCams)
        self.sldr_WaterThres.valueChanged.connect(self.WaterThresholdChanged)

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