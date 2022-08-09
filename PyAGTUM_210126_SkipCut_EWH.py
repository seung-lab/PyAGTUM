# -*- coding: utf-8 -*-

# based on PyAGTUM_210116
# remove un-used functions, remove cbx_synRetractSpeed
# 210223 remove 3rd camera, remove pump
# remove retract phase diff logs
# 210312 spring change on 210310

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic
from PIL import ImageQt

import sys
import os
from AGTUMconfigparser import config
#from ximea import xiapi
from datetime import datetime
import time
import nidaqmx
import serial
# import paintableqlabel
import cv2
#import copy

import numpy as np
from scipy import stats, signal, fftpack
import leicaCmds as Leica
import atumCmds_2 as Atum
# import syringepump as Pump
import valuelogger as log
#import barcode_reader as barcode
#from threading import timer #EWH

application_path = os.path.dirname(__file__)

#EWH: gloabl variable for counting in the virtual mode
virtual_counter_Leica = int(0)
virtual_counter_ATUM = int(0)

# videologpath = 'C:\dev\videologs'
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# datestr=datetime.today().strftime('%Y%m%d%H%M%S')
# out = cv2.VideoWriter(os.path.join(videologpath,self.name + '_' + datestr + '.avi'),fourcc, 20.0, (616,514))

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

        
class ATUMcyledurationlog(log.valuelogger):
    historylength=5000
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 2")

class ATUMslotdurationlog(log.valuelogger):
    historylength=5000
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 3")

class ATUMinterslotdurationlog(log.valuelogger):
    historylength=5000
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 4")

class LEICAretractdurationlog(log.valuelogger):
    historylength=5000
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 5")

class LEICAcutdurationlog(log.valuelogger):
    historylength=5000
    def updateVis(self):
        1
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 6")

class TapeSpeedDifflog(log.valuelogger):
    historylength=5000
  #  def updateVis(self): self.parent.ptTapeSpeedDiff.setData(self.timelog,self.valuelog)

    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 7")


class Offsetlog(log.valuelogger): #EWH - this one might be problematic for virtual
    historylength=5000
    def updateVis(self):
        try: 
            self.parent.ptOffset.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update graph of offset - line 408")
    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 8")


############################## UNDER CONSTRUCTION ##############################

class LEICAchopperlog(log.valuelogger):
    historylength=3000
    upStateStart=[]
    downStateStart=[]
    prev_offset=0
    state=0 # 0 - cutting, 1 - retract

    adjustment_counter = 0
    wait_cycle_num = 0 #EWH
    skip_checked= [0, 0, 0]
    StopCutTime = 0
    skip_checked_num = 0 #EWH
    first_time_stop_cut = 0
    NumSet_target = 0
    
    skip_checked_num_future = 0
    wait_cycle_num_future = 0
    stop_mode = 0
    LEICAcycle = 0
    first_time_wait_time = 0 #EWH
    start_cutting_delay = 0 #EWH
    stop_cutting_delay = 0 #EWH 
    second_time_wait_time = 0 #EWH
    Eric_cutDuration = 0 #EWH
    
    #EWH: virtual mode variables
    chopperSignal = 0
    switch_ = False
    num_switches = 0
    

    def updateVis(self):
        try:
            self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update Leica chopper log graph - line 448")
            
    def datacollector(self):
        
        #EWH: for virtual mode, the gloabl variable virtual_counter is updated here!
        global virtual_counter_Leica
        
        if self.parent.unit_test == False:
            self.chopperSignal=int(self.parent.syncLEICA_chopper.read())
        else:
            if virtual_counter_Leica < 1: #this is the "time" of retraction, hardwired
                self.chopperSignal = 0
                
            else:
                zero_signal = virtual_counter_Leica / self.parent._unit_test_pyAGTUM_SPEED
                if zero_signal.is_integer():
                    self.switch_ = True
                    self.num_switches += 1
                if self.switch_ == True: 
                    
                    current_num_switches = self.num_switches / 2
                    
                    if current_num_switches.is_integer():
                        self.parent.Display_cycle_num_LEICA.setHtml(str(current_num_switches))
                    
                    if self.chopperSignal == 0:
                        self.chopperSignal = 1
                        self.switch_ = False
                    else:
                        self.chopperSignal = 0
                        self.switch_ = False
                        

        virtual_counter_Leica += 1
                    
        self.updateLog(self.chopperSignal)
        #print("update log 9")
        BaseSpeed = self.parent.sbx_targetCycleSpeed.value()
        
            # turn off cutting for 5 cycles, only happen during retraction phase
        self.skip_checked.append(self.parent.cbx_skip.isChecked())
        self.skip_checked.pop(0)
        
        if self.parent.cbx_skip.isChecked():
            
            
            #EWH: checking if it is in cut or retraction, if not, keep the skip box checked
            #EWH: this is a very blunt approach to this. May need better methods in future
            chopperSignal_position = self.parent.LEICAchopperlog.valuelog.__len__() - 1
            chopperSignal_val = self.parent.LEICAchopperlog.valuelog[chopperSignal_position]
#            print(f"Chopper Signal CURRENT POSITION = {chopperSignal_position}")
#            print(f"Chopper Signal NOW = {chopperSignal_val}")

            #EWH: hoping this is a way to make sure it only stops at the start of cutting 
            # and no other time. 
            chopperSignal_prev_position = chopperSignal_position - 1
            chopperSignal_prev_value = self.parent.LEICAchopperlog.valuelog[chopperSignal_prev_position]
            
#            print(f"Chopper Signal PREVIOUS POSITION = {chopperSignal_prev_position}")
#            print(f"Chopper Signal PREVIOUS = {chopperSignal_prev_value}")
#            print("-----------------------------------------------------------------")
            if chopperSignal_val == 1 or self.stop_mode == 1:
                
                if chopperSignal_prev_value == 0 or self.stop_mode == 1:
#                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
#                    print("Entered Into Skip Cut")
#                    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
                    
                    self.skip_checked_num += 1
                    #EWH: Setting "the wait to nose" time (hardcoded for current luxel tape sizes)  
                    if self.skip_checked_num == 1:
                        #EWH: 13 cycles (15 to the nose) - but ensuring missing some before bad section
                        self.wait_cycle_num = 12 + self.parent.ATUMcyledurationlog.valuelog.__len__()
                        #print(f"Wait Cycle Time Set to: {self.wait_cycle_num}")
                    
                    current_cycle_num = self.parent.ATUMcyledurationlog.valuelog.__len__()
                    #print(f"Current Cycle Num: {current_cycle_num}")
                    #print(f"Target Cycle Num: {self.wait_cycle_num}")
      
                    #EWH: there is a small bug here, sometimes the current_cycle_num is 0 when it should not be. 
                    #EWH: no idea why, but this is an attempt to catch it. 
                    if current_cycle_num > 0: 
                        
                        #EWH: waiting to stop cutting until the aperture is at the nose
                        if current_cycle_num >= self.wait_cycle_num:
                            
                            #EWH: now we need to make sure that we are not actively cutting.
                            #EWH: we don't care where the wheel is at in 1 or 0 terms now. 
                            self.stop_mode = 1
                             
                            self.first_time_wait_time += 1
                            
                            #EWH: record the time that we entered the delay for cutting window
                            if self.first_time_wait_time == 1:
                                self.start_cutting_delay = self.timelog[-1]
                                #EWH: get the current duration for a cut.
                                self.Eric_cutDuration = self.downStateStart[-1]-self.upStateStart[-1]
                            
                            current_time = self.timelog[-1] 
                            
                            wait_for_cut = current_time - self.start_cutting_delay
                            #print(f"Cut Duration = {self.Eric_cutDuration}")
                            #print(f"wait for cut time = {wait_for_cut}")
                            
                            if wait_for_cut > self.Eric_cutDuration:
                                
                                #EWH: if it is the first aperture to stop at then send stop commands
                                self.first_time_stop_cut += 1
                            
                                if  self.first_time_stop_cut == 1:
                                    #print("STOPPING CUTTING")
                                    self.parent.StopCut()
                                    self.StopCutTime = self.timelog[-1]
                                    # turn off synchronization
                                    self.parent.cbx_synTS.setChecked(False)
                                    NumSet = self.parent.sbx_NumSections.value()
                                    self.NumSet_target = NumSet + self.parent.ATUMcyledurationlog.valuelog.__len__()
                                    #EWH: this is special to allow stopping when the chopper is stuck
                                    
                                else: 
                                    self.parent.cbx_skip.setChecked(True)
                            else: 
                                self.parent.cbx_skip.setChecked(True)
        #                if self.parent.ATUMcyledurationlog.valuelog.__len__()>0:
        
                        
                        #print("-----------------------------------------------------")    
                        #print(f"NumSet is set to: {self.NumSet_target}")
                        #print(f"Current Cycle is: {current_cycle_num}")
                        #EWH: wait until the target num of apertures have passed (in GUI) 
                        if self.NumSet_target > 0:
                        
                            if current_cycle_num >= self.NumSet_target: 
                                
                                self.second_time_wait_time += 1
                                
                                #EWH: record the time that we entered the delay for cutting window
                                if self.second_time_wait_time == 1:
                                    self.stop_cutting_delay = self.timelog[-1]
                                    self.Eric_cutDuration = self.downStateStart[-1]-self.upStateStart[-1]
                                    
                                current_time = self.timelog[-1] 
                                
                                wait_for_cut = current_time - self.stop_cutting_delay
                                
                                #EWH: to have the cutting restart with the correct offset from pure synchronization
                                offset_target = self.parent.sbx_targetphase.value()
                                
                                if wait_for_cut > self.Eric_cutDuration + offset_target:
                                    
                                    print("Entered into Start Cut")
                                    #EWH: restart cutting and reset synch and skip cut boxes
                                    self.parent.StartCut()
                                    self.StopCutTime = self.timelog[-1]
                                    if self.parent.cbx_reskip.isChecked():
                                        self.parent.cbx_skip.setChecked(True)
                                        self.parent.cbx_synTS.setChecked(False)
                                        self.skip_checked_num = 2
                                        self.first_time_stop_cut = 0
                                        self.wait_cycle_num = self.wait_cycle_num_future
                                        self.NumSet_target = 0
                                        self.parent.cbx_reskip.setChecked(False)
                                        self.stop_mode = 0
                                        self.start_cutting_delay = 0
                                        self.first_time_wait_time = 0
                                        self.stop_cutting_delay = 0
                                        self.second_time_wait_time = 0
                                        
                                    else:
                                        self.parent.cbx_skip.setChecked(False)
                                        self.parent.cbx_synTS.setChecked(True)
                                    #EWH: reset all the params to 0 for next run. 
                                        self.skip_checked_num = 0
                                        self.first_time_stop_cut = 0
                                        self.wait_cycle_num = 0
                                        self.NumSet_target = 0
                                        self.stop_mode = 0
                                        self.start_cutting_delay = 0
                                        self.first_time_wait_time = 0
                                        self.stop_cutting_delay = 0
                                        self.second_time_wait_time = 0
                                else:
                                    self.parent.cbx_skip.setChecked(True)
                            else: 
                                self.parent.cbx_skip.setChecked(True)
                        else: 
                            self.parent.cbx_skip.setChecked(True)
                    else: 
                        self.parent.cbx_skip.setChecked(True)
                else: 
                    self.parent.cbx_skip.setChecked(True)
            
            if self.parent.cbx_reskip.isChecked():
                if self.chopperSignal == 0: 
                    self.skip_checked_num_future += 1
                    #EWH: Setting "the wait to nose" time (hardcoded for current luxel tape sizes)  
                    if self.skip_checked_num_future == 1:
                        #EWH: 13 cycles (15 to the nose)
                        self.wait_cycle_num_future = 13 + self.parent.ATUMcyledurationlog.valuelog.__len__()
                        #print(f"Wait Cycle Time Set to: {self.wait_cycle_num}")
            else: 
                self.skip_checked_num_future = 0
                 
        
        
        if self.valuelog.__len__()<2:
            return

        if self.valuelog[-1]==1 and self.valuelog[-2]==0: #cutting phase starts
            self.state = 0
            self.upStateStart.append(self.timelog[-1])
            if self.parent.unit_test == False:
                rs,_ = Leica.getReturnSpeed()
            else:
                rs = 1200 #EWH: virtual test, hardwired

            self.parent.DisplayRetractSpeed.setHtml(str(rs))

            if self.downStateStart.__len__()>0 and self.upStateStart.__len__()>0:
                retractDuration=self.upStateStart[-1]-self.downStateStart[-1]
                self.parent.LEICAretractdurationlog.datacollector(retractDuration)

        if self.valuelog[-2]==1 and self.valuelog[-1]==0: #retraction phase starts
            self.state = 1            
            self.downStateStart.append(self.timelog[-1])
                    
                
            
            if self.upStateStart.__len__()>0 and self.downStateStart.__len__()>0:
                cutDuration=self.downStateStart[-1]-self.upStateStart[-1]
                self.parent.LEICAcutdurationlog.datacollector(cutDuration)
                if self.parent.LEICAretractdurationlog.valuelog.__len__()>0:
                    self.LEICAcycle = cutDuration + self.parent.LEICAretractdurationlog.valuelog[-1]
                    self.parent.DisplayCycleDuration_(self.LEICAcycle)
                    print("LEICA cycle: {}s".format(round(self.LEICAcycle,2)))


            if self.parent.ATUMcyledurationlog.valuelog.__len__()>0:
                CycleTime=self.parent.ATUMcyledurationlog.valuelog[-1]
                TargetCycleTime=(self.parent._DistanceBetweenSlots/self.parent.sbx_targetCycleSpeed.value())
                TapeSpeedDiff=CycleTime-TargetCycleTime
                self.parent.TapeSpeedDifflog.datacollector(TapeSpeedDiff)

                if self.parent.tapespeedlog.valuelog.__len__()>0:
                    if self.upStateStart.__len__()>1 and self.parent.ATUMchopperlog.upStateStart.__len__()>0:
                        offset=self.upStateStart[-1]-self.parent.ATUMchopperlog.upStateStart[-1]

                        # 210130 ZZ adjust tape speed for each cycle based on ATUM cycle time
                        if self.parent.cbx_synTS.isChecked():
                            cdelta = offset - self.parent.sbx_targetphase.value()
                            try: 
                                OffsetDiff = abs(self.parent.Offsetlog.valuelog[-1]) - abs(offset)

                                # offset Leica - ATUM
                                # offset < 0 -> Leica happened then ATUM
                                # more minus -> ATUM later than leica too much
    
                                # ATUMcycle = np.mean(self.parent.ATUMcyledurationlog.valuelog[-2:])
                                # cdelta = ATUMcycle - LEICAcycle
                                if abs(cdelta) > 0.4:
                                   self.adjustment_counter += 1
                                   if OffsetDiff < 0:
                                       # not getting better
                                       af = 2
                                   else:
                                       af = 1
                                   if self.parent.cbx_adjFactor.isChecked():
                                       af = self.parent.sbx_adjFactor.value()
                                   if cdelta < 0:
                                       self.parent.setTapeSpeed(BaseSpeed + 0.03*af)
                                       print("tape speed up")
                                   else:
                                       self.parent.setTapeSpeed(BaseSpeed - 0.03*af)
                                       print("tape slow down")
                                else:
                                    print("in sync")
                            except: 
                                print("No prior offset, Will calculate offset next time")
                            print("offset:{}".format(round(offset, 2)))
                            print("--------------------------------------------------------")
                            self.parent.Offsetlog.datacollector(offset)
        if self.adjustment_counter > 100:
            self.parent.setTapeSpeed(BaseSpeed)
            self.adjustment_counter = 0
        elif self.adjustment_counter > 0:
            self.adjustment_counter += 1
        del self.upStateStart[:-3]
        del self.downStateStart[:-3]

class ATUMchopperlog(log.valuelogger):
    
    historylength=3000
    upStateStart=[]
    downStateStart=[]
    
    #EWH: virtual mode variables
    chopperSignal = 0
    switch_ = False
    num_switches = 0
    
    def updateVis(self):
        try: 
            self.parent.ptsyncATUM_chopper.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update ATUMchopper log graph - line 765")
    def datacollector(self):
                #EWH: for virtual mode, the gloabl variable virtual_counter is updated here!
                
                #EWH: for virtual mode, the gloabl variable virtual_counter is updated here!
        global virtual_counter_ATUM
            
        if self.parent.unit_test == False:
            try: 
                self.chopperSignal=int(self.parent.syncATUM_chopper.read())
            #invert chopper signal
                if self.chopperSignal==1:
                    self.chopperSignal=0
                elif self.chopperSignal==0:
                    self.chopperSignal=1
            except nidaqmx.DaqError as e:
                print(f"Nidaq error detected: {e}")
        else:
            if virtual_counter_ATUM < 1: #this is the "time" of no slot, hardwired
                self.chopperSignal = 0
                
            else:
                zero_signal = virtual_counter_ATUM / self.parent._unit_test_pyAGTUM_SPEED
                if zero_signal.is_integer():
                    self.switch_ = True
                    self.num_switches += 1
                    
                if self.switch_ == True: 
                    
                    current_num_switches = self.num_switches / 2
                    
                    if current_num_switches.is_integer():
                        self.parent.Display_cycle_num_ATUM.setHtml(str(current_num_switches))    
                        
                    if self.chopperSignal == 0:
                        self.chopperSignal = 1
                        self.switch_ = False
                    else:
                        self.chopperSignal = 0
                        self.switch_ = False 
                    
        virtual_counter_ATUM += 1
       #print(f"Chopper Signal for ATUM: {self.chopperSignal}")
            

        self.updateLog(self.chopperSignal)
        #print("update log 10")
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
                print("ATUM cycle: {}".format(round(ATUMcycle[-1],2)))
                # print("actual tape speed: {}".format(round(6/ATUMcycle[-1],3)))
                
                if self.parent.unit_test == False:
                    self.parent.DisplayTension.setHtml( str( round(Atum.gTT(),2) ) )
                else:
                    self.parent.DisplayTension.setHtml(str(round(60.353,2)))
                    
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
            if self.parent.unit_test == False:
                value=Atum.gTS()
            else:
                value=0.4 #EWH: virtual mode, hardwired
        self.updateLog(value)
        #print("update log 11")
        #print("Tension: {0}".format(Atum.gTT()))

class retractspeedlog(log.valuelogger):
    historylength=500
    def datacollector(self):
        if self.parent.unit_test == False:
            [RetractionSpeed,resstr]=Leica.getReturnSpeed()
        else: 
            RetractionSpeed = 1200
        if RetractionSpeed>=0:
            self.updateLog(RetractionSpeed)
            #print("update log 12")
        return


class mainGUI(QtWidgets.QMainWindow):
    #gui elements whose value/state is saved in the configuration file.
    #gui elements whose name starts with '_' are excluded.
    GUIElements=[QtWidgets.QSlider,QtWidgets.QRadioButton,QtWidgets.QCheckBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox,QtWidgets.QComboBox,QtWidgets.QLineEdit]
    _StartPosition=[]
#    _CameraSNs=['CICAU1641091','CICAU1914024']
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
        
        self.unit_test = bool(myconfig["pyAGTUM"]["_unit_test"])
        print(self.unit_test)
        self._unit_test_pyAGTUM_SPEED = int(myconfig["pyAGTUM"]["_unit_test_pyAGTUM_SPEED"])
        
        print("Setup ATUM sync...")
        self.setupATUMsync()

   
        if self.unit_test == False:
            print("Setup hardware...")
            self.SetupHardware()
        else: 
            print("Virtual Mode enabled...")

        print("Connect GUI slots...")
        self.ConnectGUISlots()

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
        if self.unit_test == False: 
            Atum.sTS(value)

    def setReturnSpeed(self,value=None):
        if value is None:
            value=self.sbx_retractionSpeed.value()
        else:
            self.sbx_retractionSpeed.blockSignals(True)
            self.sbx_retractionSpeed.setValue(value)
            self.sbx_retractionSpeed.blockSignals(False)
        if self.unit_test == False:
            Leica.setReturnSpeed(value)
            print("return speed: {}".format(value))
        else: 
            print("unit test mode")

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
        
    def DisplayCycleDuration_(self, LEICAcycle):
        value = str(round(LEICAcycle,2))
        self.DisplayCycleDuration.setHtml(value)


    def SetupHardware(self):
#        EWH: removing cameras 
#        self.PreCamTimer = PreCamTimer()
#        self.PreCamTimer.setupCams(self._CameraSNs[0], self._cam_presection)
#        self.PreCamTimer.initiateTimer(100, None, None, parent=self)
#        self.PreCamTimer.start()
#
#        self.PostCamTimer = PostCamTimer()
#        self.PostCamTimer.setupCams(self._CameraSNs[1], self._cam_postsection)
#        self.PostCamTimer.initiateTimer(100, self._logpath,'CamTapeSpeed', parent=self)
#        self.PostCamTimer.start()

        self.syncATUM_chopper=nidaqmx.Task()
        self.syncATUM_chopper.di_channels.add_di_chan(self._syncATUM_chopperPort)
        self.syncLEICA_chopper=nidaqmx.Task()
        self.syncLEICA_chopper.di_channels.add_di_chan(self._syncLEICA_chopperPort)


    def StartCams(self):

        if self.unit_test == False:
            Atum.Start()

        print("start cameras")

 #       v=self.sbx_tapeSpeed.value()        
 #       self.setTapeSpeed(1)
 #       self.sbx_tapeSpeed.setValue(v)
        self.setTapeSpeed()

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
        if self.unit_test == False: 
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
    
    def StartCut(self):
        if self.unit_test == False:
            Leica.startCuttingMotor()
        self.setReturnSpeed()
        
    def StopCut(self):
        if self.unit_test == False:
            Leica.stopCuttingMotor()
    
    def getRetractSpeed(self):
        if self.unit_test == False:
            value = Leica.getReturnSpeed()
        else:
            value = 1200 #hardwired
        self.DisplayRetractSpeed.setHtml(str(value[0]))
        
    def setRetractSpeed(self):
        value=self.sbx_retractionSpeed.value()
        if self.unit_test == False:
            Leica.setReturnSpeed(value)
        
    def getNS(self):
        if self.unit_test == False:
            value = Leica.getNS_Abs()
        else:
            value = 3.185 #hardwired
        self.DisplayNS.setHtml(str(value))
        
    def goNS(self):
        value = self.sbx_setNS.value()
        if self.unit_test == False:
            Leica.moveNS_Abs(value)
        self.DisplayNS.setHtml(str(value))
        
    def getEW(self):
        if self.unit_test == False:
            value = Leica.getEW_Abs()
        else: 
            value = 4.75 #hardwired
        self.DisplayEW.setHtml(str(round(value,3)))
        
    def goEW(self):
        value = self.sbx_setEW.value()
        if self.unit_test == False:
            Leica.moveEW_Abs(value)
        self.DisplayEW.setHtml(str(value))
        
    def getTension(self):
        if self.unit_test == False:
            self.DisplayTension.setHtml(str(round(Atum.gTT(),2)))
        else:
            self.DisplayTension.setHtml(str(round(60.3456,2))) #hardwired
            
    def StopHardware(self):
#        EWH: removing cameras
#        self.PreCamTimer.stopLog()
#        self.PostCamTimer.stopLog()
#        self.PreCamTimer.cam.stop_acquisition()
#        self.PostCamTimer.cam.stop_acquisition()
#        self.PreCamTimer.cam.close_device()
#        self.PostCamTimer.cam.close_device()
#        self.StopCams()

        self.syncATUM_chopper.close()
        self.syncLEICA_chopper.close()
        
        print("done closing hardware")
        

    def closeEvent(self, event):
#         EWH: removing cameras 
        if self.unit_test == False:
            self.StopHardware()
        else:
            print("Virtual mode: no hardware to close.")
            
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
        self.btn_StartCut.clicked.connect(self.StartCut)
        self.btn_StopCut.clicked.connect(self.StopCut)
        self.sbx_tapeSpeed.valueChanged.connect(self.setTapeSpeed)
        self.btn_TapeStart.clicked.connect(self.TapeStart)
        self.btn_TapeStop.clicked.connect(self.TapeStop)
        self.btn_GetRetract.clicked.connect(self.getRetractSpeed)
        self.btn_SetRetract.clicked.connect(self.setRetractSpeed)
        self.btn_getEW.clicked.connect(self.getEW)
        self.btn_goEW.clicked.connect(self.goEW)
        self.btn_getNS.clicked.connect(self.getNS)
        self.btn_goNS.clicked.connect(self.goNS)
        self.btn_GetTension.clicked.connect(self.getTension)

    def TapeStart(self):
        if self.unit_test == False:
            if self.radiobtn_forward.isChecked():
                Atum.Start()
            else:
                Atum.Reverse()

    def TapeStop(self):
        if self.unit_test == False:
            Atum.Stop()

    def UpdateWindowTitle(self):
        if self.unit_test == False:
            Title="AGTUM"
            self.setWindowTitle(Title)
        else:
            Title="AGTUM - VIRTUAL MODE"
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
    window = mainGUI(os.path.join(application_path,"PyAGTUM_mainwindow_220730_no_cams_EWH.ui")) #EWH

    sys.exit(app.exec_())
