# -*- coding: utf-8 -*-

"""

PyAGTUM - Main program for controlling ATUM and Leica for Serial Section Acquisition

This program is designed to control a Leica UC7 microtome and RMC ATUM. It stores various 
important data like the position of the Leica cutting arm (whether it is in the cutting 
window or not) and the duration of an ATUM cycle in classes of labeles as various logs. 
Most of these logs just add a 1 or a 0 to denote position but two of the logs contain the 
functions that perform sychronization, aperture skipping, protecting from tension issues, 
and more. 

The two key classes are: 

1. LEICAchopperlog
2. ATUMchopperlog

After that the class "mainGUI" connects the UI file to this script and relays the button 
and switch actions by the user to run the AGTUM. This class also contains most of the 
functions for getting or sending information to the hardware with button presses or value
changes in the GUI. 

"""

# Package Imports
import xyzStageCmds
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic
from PIL import ImageQt
import sys
import os
from AGTUMconfigparser import config
from datetime import datetime
import time
import nidaqmx
import serial
import cv2
import numpy as np
from scipy import stats, signal, fftpack
import leicaCmds as Leica
import atumCmds_2 as Atum
import valuelogger as log


application_path = os.path.dirname(__file__)

#EWH: gloabl variable for counting in the virtual mode
#EWH: this is not important for most users. I would not
# recommend messing with this. 

virtual_counter_Leica = int(0)
virtual_counter_ATUM = int(0)

if sys.platform.startswith('win'):
    win=1
else:
    win=0

#EWH: adding in the stages for the ATUM to move with cutting.
Stages = xyzStageCmds.stages(3) # need to specify the number of axes to create

# # # # # # # # # Logging Classes # # # # # # # # # # 
        
#EWH: important for maintain sychronization
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

# EWH: currently not in use. 
class TapeSpeedDifflog(log.valuelogger):
    historylength=5000
  #  def updateVis(self): self.parent.ptTapeSpeedDiff.setData(self.timelog,self.valuelog)

    def datacollector(self,value=None):
        if value is None:
           return
        self.updateLog(value)
        #print("update log 7")

#EWH: offset data is displayed on the lower graph in the PyAGTUM main window. 
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


class LEICAchopperlog(log.valuelogger):
    historylength=3000
    upStateStart=[]
    downStateStart=[]
    prev_offset=0
    #EWH: in log; 0 = cutting, 1 = retract 
    state=0 

    #EWH: these are used to keep track of various conditions. 
    adjustment_counter = 0
    wait_cycle_num = 0 
    skip_checked= [0, 0, 0]
    StopCutTime = 0
    skip_checked_num = 0 
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

    #EWH: Variables for measuring distances of cut
    cut_dist_mm = 0
    cut_mm = 0
    cut_nm = 0
    previous_section_total = 0
    stage_flag_timer = 5
    stage_flag_time = 0
    stage_flag_first = 0
    adjustment_counter_2 = 0
    
    #EWH: virtual mode variables
    chopperSignal = 0
    switch_ = False
    num_switches = 0
    
    #EWH: update the value for the graph of synchronization 
    def updateVis(self):
        try:
            self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update Leica chopper log graph - line 173")
            
    def datacollector(self):
        
        #EWH: for virtual mode, the gloabl variable virtual_counter is updated here!
        global virtual_counter_Leica
        
        #EWH: checking tension and making sure nothing crazy has happened with the tape. If so, stop moving and cutting.
        tension = self.parent.getTension()
        
        #EWH: checking tension and stopping the cutting and tape movement if too high to prevent ATUM damage. 
        #EWH: see development for latest version of tension control, it all has checks in place to prevent
        #EWH: stopping during the cutting process. 
        if tension > self.parent.sbx_tapeTensionControl.value():
            self.parent.StopCams()
            self.parent.StopCut()
            print("ERROR: Tension Too High! Check Tape!")

        # # # Virtual Mode - Ignore # # #
        
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
        
        BaseSpeed = self.parent.sbx_targetCycleSpeed.value()
        
        # # # SkipCut Area # # #
        #EWH: if skipping is signaled by the user from the GUI this code is run
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
            
            if chopperSignal_val == 1 or self.stop_mode == 1:
                
                if chopperSignal_prev_value == 0 or self.stop_mode == 1:
                    
                    self.skip_checked_num += 1
                    #EWH: Setting "the wait to nose" time (hardcoded for current luxel tape sizes) 
                    #EWH: future users may need to change this if luxel ever changes the spacing or 
                    # size of apertures.  
                    if self.skip_checked_num == 1:
                        #EWH: 13 cycles (15 to the nose) - but ensuring missing some before bad section
                        self.wait_cycle_num = 12 + self.parent.ATUMcyledurationlog.valuelog.__len__()
                    
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
                            
                            if wait_for_cut > self.Eric_cutDuration:
                                
                                #EWH: if it is the first aperture to stop at then send stop commands
                                self.first_time_stop_cut += 1
                            
                                if  self.first_time_stop_cut == 1:
                                    #print("STOPPING CUTTING")
                                    self.parent.StopCut()
                                    self.StopCutTime = self.timelog[-1]
                                    #EWH: turn off synchronization
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
            
            #EWH: I believe this code allows one to do a "double skip" if there are two bad 
            # apertues.  
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

        #EWH: counting the number of sections. 
        if self.valuelog[-1]==1 and self.valuelog[-2]==0: #cutting phase starts
            self.state = 0
            
            self.parent.section_number += 1
            self.parent.textEdit_SectionNum.setHtml(str(self.parent.section_number))                
            
            if self.parent.cbx_ResetSectionNum.isChecked():
                self.parent.section_number = 0
                self.parent.textEdit_SectionNum.setHtml(str(self.parent.section_number))
                self.parent.cbx_ResetSectionNum.setChecked(False)
            
            self.upStateStart.append(self.timelog[-1])
            if self.parent.unit_test == False:
                rs,_ = Leica.getReturnSpeed()
            else:
                rs = 1200 #EWH: virtual test, hardwired

            self.parent.DisplayRetractSpeed.setHtml(str(rs))

            if self.downStateStart.__len__()>0 and self.upStateStart.__len__()>0:
                retractDuration=self.upStateStart[-1]-self.downStateStart[-1]
                self.parent.LEICAretractdurationlog.datacollector(retractDuration)


        #EWH: this is where we make sure to only speed up or slow down during retraction and not during cut.
        if self.valuelog[-2]==1 and self.valuelog[-1]==0: #retraction phase starts

            self.state = 1            
            self.downStateStart.append(self.timelog[-1])
            
            #EWH: this limitor will stop the cutting if a given amount is reached. Probably not
            # needed, but could be a way to prevent a sleepy opperator from cutting into the 
            # following strand of Gridtape.
            if self.parent.section_number >= int(self.parent.textEdit_SectionLimit.toPlainText()):
                self.parent.StopCams()
                self.parent.StopCut()
                exit()
                print("NOTICE: Section Limit Reached, Collection Stopping.")
            
            if self.upStateStart.__len__()>0 and self.downStateStart.__len__()>0:
                cutDuration=self.downStateStart[-1]-self.upStateStart[-1]
                self.parent.LEICAcutdurationlog.datacollector(cutDuration)
                if self.parent.LEICAretractdurationlog.valuelog.__len__()>0:
                    self.LEICAcycle = cutDuration + self.parent.LEICAretractdurationlog.valuelog[-1]
                    self.parent.DisplayCycleDuration_(self.LEICAcycle)
                    print("LEICA cycle: {}s".format(round(self.LEICAcycle,2)))

            #EWH if the log has been populated, check the retraction state.
            #if self.upStateStart.__len__()>0 and self.downStateStart.__len__()>0:
            # # # Synchronization # # #
            #EWH: this code changes the adjustment factor proportionally to the amount of distance the offset is from
            # the target offset. Works really well, will push soon.

            if self.parent.ATUMcyledurationlog.valuelog.__len__()>0:
                CycleTime=self.parent.ATUMcyledurationlog.valuelog[-1]
                TargetCycleTime=(self.parent._DistanceBetweenSlots/self.parent.sbx_targetCycleSpeed.value())
                TapeSpeedDiff=CycleTime-TargetCycleTime
                self.parent.TapeSpeedDifflog.datacollector(TapeSpeedDiff)

                if self.parent.tapespeedlog.valuelog.__len__()>0:
                    #EWH: I believe this is the line that makes sure we only move the tape faster or slower when not
                    # actively cutting.
                    if self.upStateStart.__len__()>1 and self.parent.ATUMchopperlog.upStateStart.__len__()>0:
                        offset=self.upStateStart[-1]-self.parent.ATUMchopperlog.upStateStart[-1]
                        self.adjustment_counter_2 += 1

                        # 210130 ZZ adjust tape speed for each cycle based on ATUM cycle time
                        if self.parent.cbx_synTS.isChecked():
                            cdelta = abs(offset - self.parent.sbx_targetphase.value())
                            #print(cdelta)

                            if self.parent.cbx_adjFactor_2.isChecked(): #automatic adjustment
                               self.adjustment_counter += 1
                               if offset < self.parent.sbx_targetphase.value():
                                   if cdelta < 0.3:
                                       if cdelta  < 0.2:
                                           if cdelta > 0.1:
                                               print('+ + + + IN SYNC + + + +')
                                               print("Offset: {}".format(round(offset,3)))
                                               speed_change = abs(BaseSpeed + (0.0125*cdelta))
                                               self.parent.setTapeSpeed(speed_change)
                                               print("ATUM: tape speed up - - - - speed {}".format(round(speed_change,4)))
                                           else:
                                               print('+ + + + IN SYNC + + + +')
                                               print("Offset: {}".format(round(offset, 3)))
                                               speed_change = abs(BaseSpeed + (0.005*cdelta))
                                               self.parent.setTapeSpeed(speed_change)
                                               print("ATUM: tape speed up - - - - speed {}".format(round(speed_change,4)))
                                       else:
                                           print('+ + + + IN SYNC + + + +')
                                           print("Offset: {}".format(round(offset, 3)))
                                           speed_change = abs(BaseSpeed + (0.02 * cdelta))
                                           self.parent.setTapeSpeed(speed_change)
                                           print("ATUM: tape speed up - - - - speed {}".format(round(speed_change, 4)))

                                   else:
                                       speed_change = abs(BaseSpeed + (0.1*cdelta))
                                       if speed_change > 0.6:
                                            self.parent.setTapeSpeed(0.6)
                                            print("Offset: {}".format(round(offset, 3)))
                                            print("ATUM: tape speed up - - - - speed {}".format(round(0.6, 4)))
                                       else:
                                            self.parent.setTapeSpeed(speed_change)
                                            print("Offset: {}".format(round(offset, 3)))
                                            print("ATUM: tape speed up - - - - speed {}".format(round(speed_change,4)))
                               else:
                                   if cdelta < 0.3:
                                       if cdelta < 0.2:
                                           if cdelta > 0.1:
                                               print('+ + + + IN SYNC + + + +')
                                               print("Offset: {}".format(round(offset,3)))
                                               speed_change = abs(BaseSpeed - (0.0125*cdelta))
                                               self.parent.setTapeSpeed(speed_change)
                                               print("ATUM: tape slow down - - - - speed {}".format(round(speed_change,4)))
                                           else:
                                               print('+ + + + IN SYNC + + + +')
                                               print("Offset: {}".format(round(offset, 3)))
                                               speed_change = abs(BaseSpeed - (0.005*cdelta))
                                               self.parent.setTapeSpeed(speed_change)
                                               print("ATUM: tape speed up - - - - speed {}".format(round(speed_change,4)))
                                       else:
                                           print('+ + + + IN SYNC + + + +')
                                           print("Offset: {}".format(round(offset,3)))
                                           speed_change = abs(BaseSpeed - (0.02*cdelta))
                                           self.parent.setTapeSpeed(speed_change)
                                           print("ATUM: tape slow down - - - - speed {}".format(round(speed_change,4)))
                                   else:
                                       speed_change = abs(BaseSpeed - (0.1*cdelta))
                                       if speed_change < 0.2:
                                           self.parent.setTapeSpeed(0.2)
                                           print("Offset: {}".format(round(offset, 3)))
                                           print("ATUM: tape slow down - - - - speed {}".format(round(0.2, 4)))
                                       else:
                                            self.parent.setTapeSpeed(speed_change)
                                            print("Offset: {}".format(round(offset, 3)))
                                            print("ATUM: tape slow down - - - - speed {}".format(round(speed_change,4)))


                            else:
                                if self.parent.cbx_adjFactor.isChecked():
                                    af = self.parent.sbx_adjFactor.value()
                                else:
                                    af = 2
                                if offset < 0:
                                    self.parent.setTapeSpeed(BaseSpeed + 0.03 * af)
                                    print("ATUM: tape speed up")
                                    print("Offset: {}".format(round(offset, 3)))
                                    if cdelta < 0.3:
                                        print('IN SYNC')
                                else:
                                    self.parent.setTapeSpeed(BaseSpeed - 0.03 * af)
                                    print("ATUM: tape slow down")
                                    print("Offset: {}".format(round(offset, 3)))
                                    if cdelta < 0.3:
                                        print('IN SYNC')
                            self.parent.Offsetlog.datacollector(offset)
                        print("----------------------------------------------------------------------------")

        #EWH: this is an important little area, this counter is used to make sure the adjustment in tape
        # speed is only for a short time period and gets set back.
        if self.adjustment_counter > 100:
            self.parent.setTapeSpeed(BaseSpeed)
            self.adjustment_counter = 0

        #EWH: setting up moving the stage forward at each ~200th cut for 45 nm sections.
        #EWH: this seems to be a good number (25) to get it to move in middle of the retraction phase.
        if self.adjustment_counter_2 > 25:
            self.adjustment_counter_2 = 0
            if self.parent.cbx_AutoStageMove.isChecked():

                self.stage_flag_first += 1
                if self.stage_flag_first == 1:
                    self.parent.pushButton_StageLight.setStyleSheet("background-color: yellow")
                    self.parent.cbx_ResetSectionNum.setChecked(True)

                #EWH: make sure to allow one pass to reset the section number count
                if self.stage_flag_first >= 2:

                    current_time_stage = time.time()

                    if current_time_stage >= self.stage_flag_timer + self.stage_flag_time:
                        self.parent.pushButton_StageLight.setStyleSheet("background-color: yellow")

                    self.cut_nm = int(self.parent.textEdit_Section_Thickness.toPlainText()) #Add scaler (100 to run faster for testing) #REMOVE SCALER !!!!!
                    self.cut_mm = self.cut_nm/1000000
                    running_section_tot = int(self.parent.textEdit_SectionNum.toPlainText()) - self.previous_section_total
                    self.cut_dist_mm =  running_section_tot * self.cut_mm
                    #print(self.cut_dist_mm)

                    if self.cut_dist_mm >= 0.01:
                        if self.cut_dist_mm > 0.02:
                            pass
                            # self.parent.pushButton_StageLight.setStyleSheet("background-color: red")
                            # print("ATUM: WARNING - stage requested to move greater than 0.02 mm! - Denied")
                            # self.parent.cbx_AutoStageMove.setChecked(False)

                        else:
                            self.parent.pushButton_StageLight.setStyleSheet("background-color: green")
                            self.stage_flag_timer = 2
                            self.stage_flag_time = time.time()
                            #lblStagesJogX.delete(0, END)
                            #lblStagesJogX.insert(0, str(cut_dist_mm))
                            Stages.moveYrel(self.cut_dist_mm) #Add scaler to run faster (10) #REMOVE SCALER!!!!!!!
                            print("ATUM: Auto Move --------- moved {} mm distance".format(round(self.cut_dist_mm,4)))
                            self.previous_section_total = int(self.parent.textEdit_SectionNum.toPlainText())
                            self.cut_dist_mm = 0
                            self.cut_mm = 0
                            self.cut_nm = 0
            else:
                self.parent.pushButton_StageLight.setStyleSheet("background-color: gray")




        elif self.adjustment_counter > 0:
            self.adjustment_counter += 1
        if self.adjustment_counter_2 > 0:
            self.adjustment_counter_2 += 1
        del self.upStateStart[:-3]
        del self.downStateStart[:-3]



class ATUMchopperlog(log.valuelogger):
    
    historylength=3000
    upStateStart=[]
    downStateStart=[]
    
    #EWH: virtual mode variables - ignore them
    chopperSignal = 0
    switch_ = False
    num_switches = 0
    
    #EWH: updating the value for the graph in the GUI. 
    def updateVis(self):
        try: 
            self.parent.ptsyncATUM_chopper.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update ATUMchopper log graph - line 765")

    def datacollector(self):
        #EWH: for virtual mode, the gloabl variable virtual_counter is updated here!        
        global virtual_counter_ATUM

        #Zaber = just display the current position
        #loc_X = Stages.getAllPos()[0]
        #loc_Y = Stages.getAllPos()[1]
        #loc_Z = Stages.getAllPos()[2]
        #self.parent.Display_Zaber_PosX.setHtml(str(loc_X))
        #self.parent.Display_Zaber_PosY.setHtml(str(loc_Y))
        #self.parent.Display_Zaber_PosZ.setHtml(str(loc_Z))
            
        if self.parent.unit_test == False:
            try: 
                self.chopperSignal=int(self.parent.syncATUM_chopper.read())
            #invert chopper signal
                if self.chopperSignal==1:
                    self.chopperSignal=0
                elif self.chopperSignal==0:
                    self.chopperSignal=1
            except nidaqmx.DaqError as e:
                print("Nidaq error detected: {}".format(e))
        
        # # # Virtual Stuff - ignore # # # 
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
            
        #EWH: Logging the important information from the ATUM regarding positions and cycles. 
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
    #EWH: cameras were moved into their own GUI. 
    #_CameraSNs=['CICAU1641091','CICAU1914024']
    #_CameraSNs=['CICAU1641091','CICAU1914024','CICAU1914041']
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
        
        #EWH: virtual mode config stuff - ignore
        self.unit_test = bool(myconfig["pyAGTUM"]["_unit_test"])
        self.section_number = int(myconfig['pyAGTUM']['section_number'])
        self._unit_test_pyAGTUM_SPEED = int(myconfig["pyAGTUM"]["_unit_test_pyAGTUM_SPEED"])
        
        print("Setup ATUM sync...")
        self.setupATUMsync()

        #EWH: if not in virtual mode, connect to the hardware. 
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

        loc_X = round(Stages.getAllPos()[0], 2)
        loc_Y = round(Stages.getAllPos()[1], 2)
        loc_Z = round(Stages.getAllPos()[2], 2)
        self.Display_Zaber_PosX.setHtml(str(loc_X))
        self.Display_Zaber_PosY.setHtml(str(loc_Y))
        self.Display_Zaber_PosZ.setHtml(str(loc_Z))

        print("Show GUI...")
        self.show()

        #EWH: for displaying the print statements
        sys.stdout = self


    # # # Functions for GUI Buttons # # #

    # EWH: for displaying print statments in GUI

    def write(self, text):
        self.textEdit_TextConsole.moveCursor(self.textEdit_TextConsole.textCursor().End)
        self.textEdit_TextConsole.insertPlainText(text)
        self.textEdit_TextConsole.moveCursor(self.textEdit_TextConsole.textCursor().End)
        #QApplication.processEvents()  # Update the GUI

    # EWH: Zaber Controls

    def clkStagesHome(self):
        Stages.homeAll()
        loc_X = round(Stages.getAllPos()[0], 2)
        loc_Y = round(Stages.getAllPos()[1], 2)
        loc_Z = round(Stages.getAllPos()[2], 2)
        self.Display_Zaber_PosX.setHtml(str(loc_X))
        self.Display_Zaber_PosY.setHtml(str(loc_Y))
        self.Display_Zaber_PosZ.setHtml(str(loc_Z))

    def clkStagesStow(self):
        Stages.moveToStow()
        loc_X = round(Stages.getAllPos()[0], 2)
        loc_Y = round(Stages.getAllPos()[1], 2)
        loc_Z = round(Stages.getAllPos()[2], 2)
        self.Display_Zaber_PosX.setHtml(str(loc_X))
        self.Display_Zaber_PosY.setHtml(str(loc_Y))
        self.Display_Zaber_PosZ.setHtml(str(loc_Z))

    def clkStagesSetPickup(self):
        Stages.setPickupPositionNoOffset()
        loc_X = round(Stages.getAllPos()[0], 2)
        loc_Y = round(Stages.getAllPos()[1], 2)
        loc_Z = round(Stages.getAllPos()[2], 2)
        self.Display_Zaber_PickupPosX.setHtml(str(loc_X))
        self.Display_Zaber_PickupPosY.setHtml(str(loc_Y))
        self.Display_Zaber_PickupPosZ.setHtml(str(loc_Z))

    def clkStagesMoveToPickup(self):
        Stages.moveToPickup()
        self.clkStagesParking()
        loc_X = round(Stages.getAllPos()[0], 2)
        loc_Y = round(Stages.getAllPos()[1], 2)
        loc_Z = round(Stages.getAllPos()[2], 2)
        self.Display_Zaber_PosX.setHtml(str(loc_X))
        self.Display_Zaber_PosY.setHtml(str(loc_Y))
        self.Display_Zaber_PosZ.setHtml(str(loc_Z))

    def clkStagesParking(self):
        action = Stages.getParkState()[0]
        print('ATUM Stage: Action = ' + action)
        if action == "Unpark":
            Stages.Unpark()
            self.pushButton_ZaberPark.setStyleSheet("background-color: green")
        else:
            Stages.Park()
            self.pushButton_ZaberPark.setStyleSheet("background-color: red")

    # move-to button clicks
    def clkStagesMove(self):
        move_X = self.sbx_ZaberMove_X.value()
        move_Y = self.sbx_ZaberMove_Y.value()
        move_Z = self.sbx_ZaberMove_Z.value()
        if move_X > 0:
            Stages.moveXabs(move_X)
            loc_X = round(Stages.getAllPos()[0],2)
            self.Display_Zaber_PosX.setHtml(str(loc_X))
        if move_Y > 0:
            Stages.moveYabs(move_Y)
            loc_Y = round(Stages.getAllPos()[1],2)
            self.Display_Zaber_PosY.setHtml(str(loc_Y))
        if move_Z > 0:
            Stages.moveZabs(move_Z)
            loc_Z = round(Stages.getAllPos()[0],2)
            self.Display_Zaber_PosZ.setHtml(str(loc_Z))

    # jog button clicks
    def clkStagesJog(self):
        jog_X = self.sbx_ZaberJog_X.value()
        jog_Y = self.sbx_ZaberJog_Y.value()
        jog_Z = self.sbx_ZaberJog_Z.value()
        Stages.moveXrel(jog_X)
        Stages.moveYrel(jog_Y)
        Stages.moveZrel(jog_Z)
        loc_X = round(Stages.getAllPos()[0], 2)
        loc_Y = round(Stages.getAllPos()[1], 2)
        loc_Z = round(Stages.getAllPos()[2], 2)
        self.Display_Zaber_PosX.setHtml(str(loc_X))
        self.Display_Zaber_PosY.setHtml(str(loc_Y))
        self.Display_Zaber_PosZ.setHtml(str(loc_Z))



    #

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
        #EWH: data for the graphs for the GUI
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

    #EWH: function called when starting the Leica and ATUM together
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

    #EWH: function for stopping the Leica and ATUM together.
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
    
    #EWH: start Leica
    def StartCut(self):
        if self.unit_test == False:
            Leica.startCuttingMotor()
        self.setReturnSpeed()
    
    #EWH: stop Leica
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
    
    #EWH: not really in use at the moment. 
    def goEW(self):
        value = self.sbx_setEW.value()
        if self.unit_test == False:
            Leica.moveEW_Abs(value)
        self.DisplayEW.setHtml(str(value))
        
    def getTension(self):
        if self.unit_test == False:
            self.DisplayTension.setHtml(str(round(Atum.gTT(),0)))
        else:
            self.DisplayTension.setHtml(str(round(60.3456,2))) #hardwired
        return round(Atum.gTT(),0)
            
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

        #EWH: saving the current GUI setup so it is the same when opened next time. 
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
                
        myconfig["pyAGTUM"]["section_number"] = str(self.section_number)

        myconfig.SaveConfig(self,"pyAGTUM")
        myconfig.write()
        Leica.ser.close()
        Atum.sys.exit
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
                    print(child)
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
        
        self.textEdit_SectionNum.setHtml(str(self.section_number))

    def ConnectGUISlots(self):
        if self.radioButton_LeicaLock.isChecked():
                self.btn_goEW.setEnabled(False)
        if self.radioButton_LeicaLock.isChecked():
                self.btn_goNS.setEnabled(False)
        if self.radioButton_LeicaLock.isChecked() == False:
                self.btn_goEW.setEnabled(True)
        if self.radioButton_LeicaLock.isChecked() == False:
                self.btn_goNS.setEnabled(True)
        self.btn_StartBOTH.clicked.connect(self.StartCams)
        self.btn_StartBOTH.clicked.connect(self.StartCut)
        self.btn_StopBOTH.clicked.connect(self.StopCams)
        self.btn_StopBOTH.clicked.connect(self.StopCut)
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

        self.pushButton_ZaberPark.clicked.connect(self.clkStagesParking)
        self.pushButton_ZaberMove.clicked.connect(self.clkStagesMove)
        self.pushButton_ZaberJog.clicked.connect(self.clkStagesJog)
        self.pushButton_ZaberHome.clicked.connect(self.clkStagesHome)
        self.pushButton_ZaberStow.clicked.connect(self.clkStagesStow)
        self.pushButton_ZaberSetPickup.clicked.connect(self.clkStagesSetPickup)
        self.pushButton_ZaberMovePickup.clicked.connect(self.clkStagesMoveToPickup)
        #self.btn_GetTension.clicked.connect(self.getTension)

    #EWH: start the ATUM
    def TapeStart(self):
        if self.unit_test == False:
            if self.radiobtn_forward.isChecked():
                Atum.Start()
            else:
                Atum.Reverse()

    #EWH: stop the ATUM
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

    config_path = os.path.join(application_path, 'configs')
    configfile = os.path.join(config_path, config_name)
    print(configfile)
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
    ui_path = os.path.join(application_path, 'ui')
    window = mainGUI(os.path.join(ui_path,"PyAGTUM_mainwindow.ui")) #EWH

    sys.exit(app.exec_())
