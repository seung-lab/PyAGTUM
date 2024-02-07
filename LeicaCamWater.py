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
import serial

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
#    w = np.ones(w)
#    out = np.convolve(x, w, mode=shape)
#    return out
    out=np.convolve(x, w, shape) / w
    if x.__len__()<w and shape=='same':
        out=out[0:x.__len__()]
    #print(out)
    return out


class Thread(log.valuelogger):
#    changePixmap = pyqtSignal(QImage)
    
    first_time = 0
    pixmap_image = 0
    painterInstance = 0
    penRectangle = 0
    
    def Setup(self, label, parent=None):
        #EWH: I don't know who made this but plabel is now cam knife (in init)
        self.plabel = label
        self.parent=parent

    def run(self):
        if self.parent.unit_test == False:
            #print(self.parent.camera_index)
            cap = cv2.VideoCapture(self.parent.camera_index, cv2.CAP_DSHOW)
            #print(self.parent.camera_index)
        else: 
            video_name = "LeicaCamWater_Movie.mp4"
            video_path = os.path.join(application_path, video_name)
            cap = cv2.VideoCapture(video_path)
            starttime = time.time()
            
        while self.parent.is_running:
            ret, frame = cap.read()
            #print(cap.isOpened())
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
                if self.parent.cbx_ScreenLock.isChecked():
                    if self.first_time < 1:
                        print("Pump: Screen Locked")
                        self.first_time += 1
                    
                else:
                    if self.parent.cbx_UseLastBox.isChecked():
                        ROIXbegin=int(self.parent.DisplayBoxLoc_1.toPlainText())
                        ROIXend=int(self.parent.DisplayBoxLoc_2.toPlainText())
                        ROIYbegin=int(self.parent.DisplayBoxLoc_3.toPlainText())
                        ROIYend=int(self.parent.DisplayBoxLoc_4.toPlainText())
                        
                        self.parent.ROIXbegin = ROIXbegin
                        self.parent.ROIXend = ROIXend
                        self.parent.ROIYbegin = ROIYbegin
                        self.parent.ROIYend = ROIYend
                        
                    else:
                        ROIXbegin=min([self.plabel.begin.x(),self.plabel.end.x()])
                        ROIXend=max([self.plabel.begin.x(),self.plabel.end.x()])
                        ROIYbegin=min([self.plabel.begin.y(),self.plabel.end.y()])
                        ROIYend=max([self.plabel.begin.y(),self.plabel.end.y()])
                        
                        self.parent.ROIXbegin = ROIXbegin
                        self.parent.ROIXend = ROIXend
                        self.parent.ROIYbegin = ROIYbegin
                        self.parent.ROIYend = ROIYend
                    
                    if self.first_time > 0:
                        self.first_time = 0
                try:
                    self.parent.waterlevellog.waterlevel=np.mean(frame[ROIYbegin:ROIYend,ROIXbegin:ROIXend])
                except:
                    pass
    
                p = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
                #print(p)
                
                
                if self.parent.cbx_UseLastBox.isChecked():
                    # convert image file into pixmap
                    self.pixmap_image = QtGui.QPixmap.fromImage(p)
                    
                    # create painter instance with pixmap
                    self.painterInstance = QtGui.QPainter(self.pixmap_image)
                    
                    # set rectangle color and thickness
                    self.penRectangle = QtGui.QPen(QtCore.Qt.red)
                    self.penRectangle.setWidth(3)
                    
                    # draw rectangle on painter
                    self.painterInstance.setPen(self.penRectangle)
                    #self.painterInstance.drawRect(800,265,100,165)
                    self.painterInstance.drawRect(ROIXbegin, ROIYbegin, ROIXend-ROIXbegin, ROIYend-ROIYbegin)
                    self.painterInstance.end()
                    
                    # set pixmap onto the label widget
                    self.plabel.setPixmap(self.pixmap_image)
                    #self.ui.label_imageDisplay.show()
                        # self.changePixmap.emit(p)
                else: 
                    self.plabel.setPixmap(QtGui.QPixmap.fromImage(p))


class waterlevellog(log.valuelogger):
    waterlevel=None
    waterwindow=20
    historylength=3000
    num_iters = 0
    first_hit= True
    slope = -1
    starttime_pump = 0
    under_thres = 0
    over_thres = 0
    over_error = 0
    thres_reached = False
    startpumpingtime = 0
    counter_iters_pump = 0
    finished = False
    counter_start_time = 0
    threshold_dif = 0
    entered_under = 0
    time_threshold = 0
    over = False
    label_under = 0
    leica_cycle_check = 0
    warning_timer = 0
    warning_active = False
    first_pass = True
    warning_low_message = True
    warning_high_message = True
    last_max = 0
    second_to_last_max = 0
    first_pass_after_warning = False
    time_for_green = 0
    bad_pump_tracking = [0,0,0,0]
    bad_pump_tracking_gate_1 = 1
    bad_pump_1 = True
    bad_pump_2 = True
    bad_pump_3 = True
    bad_pump_4 = True
    bad_pump_tracking_pass = 0
    bad_pump_warning = False
    bad_pump_warning_timer = 0
    warning_message_1 = 1
    warning_message_2 = 1


    def updateVis(self):
        if len(self.valuelog) < self.waterwindow: 
            pass
        else:
            self.parent.ptwaterlevel.setData(self.timelog,np.around((moving_average(self.valuelog,self.waterwindow,'same')),1))
        
        if self.parent.unit_test == True:
            self.parent.DisplayCurrentCount.setHtml(str(self.num_iters))
            
        if np.isnan(np.average(self.valuelog[(-1*self.waterwindow):-1])):
            pass
        else:
            self.parent.DisplayCurrentLevel.setHtml(str(round(self.valuelog[-1],2)))
        #self.parent.sldr_WaterThres.setMinimum(min(self.parent.pg_waterlevel.getAxis('left').range))
        #self.parent.sldr_WaterThres.setMaximum(max(self.parent.pg_waterlevel.getAxis('left').range))
        
        #print(moving_average(self.valuelog,self.waterwindow,'same'))

    def datacollector(self):
        self.updateLog(self.waterlevel)
        

            #print(moving_average(self.valuelog,self.waterwindow,'same'))
            
        if self.parent.unit_test == True: 
        
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
                        self.first_hit = False
                    else:
                        pass
                if self.slope < 0:
                    self.first_hit = True
                else:
                    pass
        
# =============================================================================
#         #EWH: Water Level Oscillating Controller with PID-style Control
#
# This is somewhat nutty way of doing this, but the goal of this is to oscillate 
# between the two Upper and Lower Thresholds. There are multiple uses of time. 

# First: setting the period for taking the maxmium. I want the maximum of the 
# running average but only over a single period of the Leica cycle. The Leica 
# must be input manually to the GUI, but this is displayed on the PyAGTUM. This
# allows for only maxmima of a single period to determine if a threshold has 
# been reached. 

# Next: Once the pump is checked
# I see if the current max is below the lower thres or above the upper thres. 
# If it is below the lower thres, it is allowed to pump until it hit the upper 
# threshold as thres_reached = True, until it is changed to false by the upper 
# threshold. 
# I am making sure it can only pump once every 30 seconds, and that it pumps for
# for only 1 second. 
#        
# Error: 
# There is a slight error that when valuelogger starts or resets, the array is 
# smaller than the counter_iters_pump, so it generates an error when indexing by
# counter_iters_pump. I just have it not do anything than a print statement, until
# counter_iters_pump becomes larger than valuelog. 
#
# PID Style Controller:
# The idea is that the distance the (in pixels) the line of the average pixel
# intensity is from the Water Level Center line, the more water is pumped to get
# back to the Water Level Center Line. Using 3.5 mL / sec and 1/4 of the time if
# pixels = seconds seems to produce a good leveling mechanism. It also won't let 
# it pump 2X without a 20 second pause. If it goes below the lower threshold it 
# will pump for a minimum of 2 seconds every 30 seconds until it hits the middle
# to ensure that something drive it back to the middle, this is if for example
# the condistions in the room changed dramatically such that the current settings
# were not good enough. 
#

# =============================================================================
        
        if self.counter_iters_pump == 0:
            self.counter_start_time = time.time()
            #print(self.counter_start_time)
        
        current_time = time.time()
        
        if round((current_time - self.counter_start_time),1) != self.parent.dsbx_LeicaCycle.value() and self.finished == False:
            self.counter_iters_pump += 1
            #print(self.counter_iters_pump)
        
        if round((current_time - self.counter_start_time),1) == self.parent.dsbx_LeicaCycle.value():
            self.finished = True
            self.leica_cycle_check = self.parent.dsbx_LeicaCycle.value()
            print(f"Number of iterations for cycle is: {self.counter_iters_pump}")
            
                #EWH: checking to make sure the Leica Cycle time has not changed - change in iterations
        
        if self.leica_cycle_check != self.parent.dsbx_LeicaCycle.value() and self.finished == True:
            self.counter_iters_pump = 0
            self.finished = False
        
        if len(self.valuelog) > self.counter_iters_pump:
            if self.finished == True:
                self.parent.DisplayCurrentMax.setHtml(str(round(np.max(self.valuelog[(-1*self.counter_iters_pump):-1]),2)))
        
#        length_log = len(self.valuelog)
#        print(f"Log length: {length_log}")
#        print(f"Iterations: {self.counter_iters_pump}")
        if self.bad_pump_warning == True:
            self.parent.DisplayCurrentWarningTime.setHtml(str(round((120-(time.time()-self.bad_pump_warning_timer)),0)))
            if time.time() - self.bad_pump_warning_timer > 120:
                self.parent.cbx_pumpOn.setChecked(True)
                print("NOTICE: Warning over, turning pump back on.")
                self.parent.pb_WarningLight.setStyleSheet("background-color: yellow")
                self.parent.pb_PumpLight.setStyleSheet("background-color: yellow")
                self.warning_message_1 = 1
                self.warning_message_2 = 1
                self.bad_pump_warning = False
                self.parent.DisplayCurrentWarningTime.setHtml(str(0))

        
        if self.parent.cbx_pumpOn.isChecked():
#            cycleduration = self.parent.sbx_CycleDurationSet.value()
#            period_start = time.time()
#            period_end = period_start + cycleduration
#            with open('C:\dev\logs\waterlevel.csv', 'a', newline='') as f: #EWH
#                writer = csv.writer(f) #EWH
#                writer.writerow(str(round(self.waterlevel,4))) #EWH 
            
            if self.first_pass == True:
                self.parent.pb_PumpLight.setStyleSheet("background-color: yellow")
                self.first_pass = False
            
            #print(np.max(self.valuelog[(-1*self.counter_iters_pump):-1]))
            if len(self.valuelog) > self.counter_iters_pump:
                
                if self.bad_pump_tracking_gate_1 == 1: 
                    self.bad_pump_tracking_pass = time.time()
                    self.bad_pump_tracking_gate_1 += 1

                if time.time() - self.bad_pump_tracking_pass > self.parent.dsbx_LeicaCycle.value():
                    if self.bad_pump_1 == True:
                        self.bad_pump_tracking[0] = np.max(self.valuelog[(-1*self.counter_iters_pump):-1])
                        self.bad_pump_1 = False
                    
                if time.time() - self.bad_pump_tracking_pass > self.parent.dsbx_LeicaCycle.value()*2:
                    if self.bad_pump_2 == True:
                        self.bad_pump_tracking[1] = np.max(self.valuelog[(-1*self.counter_iters_pump):-1])
                        self.bad_pump_2 = False
                    
                if time.time() - self.bad_pump_tracking_pass > self.parent.dsbx_LeicaCycle.value()*3:
                    if self.bad_pump_3 == True:
                        self.bad_pump_tracking[2] = np.max(self.valuelog[(-1*self.counter_iters_pump):-1])
                  
                if time.time() - self.bad_pump_tracking_pass > self.parent.dsbx_LeicaCycle.value()*4:
                    if self.bad_pump_4 == True:
                        self.bad_pump_tracking[3] = np.max(self.valuelog[(-1*self.counter_iters_pump):-1])                        
                        self.bad_pump_tracking_gate_1 = 1
                        self.bad_pump_1 = True
                        self.bad_pump_2 = True
                        self.bad_pump_3 - True
                        
                
                if self.bad_pump_tracking[0] < self.parent.sbx_WaterLevelCenter.value() and self.bad_pump_tracking[0] != 0:
                    if self.bad_pump_tracking[1] < self.parent.sbx_WaterLevelCenter.value() and self.bad_pump_tracking[1] != 0:
                        if self.bad_pump_tracking[2] < self.parent.sbx_WaterLevelCenter.value() and self.bad_pump_tracking[2] != 0:
                            if self.bad_pump_tracking[3] < self.parent.sbx_WaterLevelCenter.value() and self.bad_pump_tracking[3] != 0:
                                if self.warning_message_2 == 1:
                                    self.warning_message_2 = 0
                                    print("WARNING: Four Iterations of Leica Cycle with Failure to Achieve Water Level! --- STOPPING PUMP")
                                self.parent.pb_WarningLight.setStyleSheet("background-color: red")
                                self.parent.pb_PumpLight.setStyleSheet("background-color: red")
                                self.bad_pump_tracking[0] = 0
                                self.bad_pump_tracking[1] = 0
                                self.bad_pump_tracking[2] = 0 
                                self.bad_pump_tracking[3] = 0
                                self.parent.cbx_pumpOn.setChecked(False)
                                self.bad_pump_warning = True
                                self.bad_pump_warning_timer = time.time()
                            
                            
                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) < self.parent.sbx_WaterLevelCenter.value() + 30:
                    
                    if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelCenter.value() - 30:
                            
                        if round((current_time - self.warning_timer),1) > 60 or self.warning_active == False:
                            
                            self.warning_active = False
                            self.warning_timer = 0 
                            self.warning_low_message = True
                            self.warning_high_message = True
                            self.parent.DisplayCurrentWarningTime.setHtml(str(0))
                            
                            if self.first_pass_after_warning == True:
                                self.parent.pb_PumpLight.setStyleSheet("background-color: yellow")
                                self.first_pass_after_warning = False
                        
                            if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelCenter.value():
                                if self.label_under < 1:
                                    print("Pump: Reached Center Threshold: will stop pumping...")
                                    self.parent.pb_PumpLight.setStyleSheet("background-color: yellow")
                                    self.label_under += 1
                                    
                            if (np.max(self.valuelog[(-1*self.counter_iters_pump):-1])) < self.parent.sbx_WaterLevelCenter.value() - \
                                                                                            self.parent.sbx_WaterThresRange.value():
                                
                                if self.entered_under == 0: 
                                    self.time_threshold = time.time()
                                    self.entered_under += 1
                                
                                self.threshold_dif = self.parent.sbx_WaterLevelCenter.value() - np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) 
                                #print(threshold_dif)
                                #EWH: this is currently assuming a 1:1/4 relationship between the amount of time 
                                # for pumping and the pixel value below threshold. 
                                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelCenter.value():
                                    #print("Pump: Reached Center Threshold: will stop pumping...")
                                    self.entered_under = 0
                                        
                                if self.time_threshold + self.parent.dsbx_LeicaCycle.value() < current_time:
                                    self.entered_under = 0
                                
                                if self.time_threshold + (self.threshold_dif/4) > current_time:
                                    
                                    Pump.trigger_pump()
                                    self.label_under = 0
                                    print("Pump: Pumping...")
                                    self.parent.pb_PumpLight.setStyleSheet("background-color: green")
                                    
                                    self.time_for_green = time.time()
                                          
                                else:
                                    if current_time - self.time_for_green > 1:
                                        self.parent.pb_PumpLight.setStyleSheet("background-color: yellow")
                                        self.time_for_green = 0 
                                    else: 
                                        pass
                                    
#            
#                            if (np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) < self.parent.sbx_WaterLevelLowerThres.value() - \
#                                                                                            self.parent.sbx_WaterThresRange.value() \
#                                                                                            or self.thres_reached):
#                                self.thres_reached = True 
#                                
#                                if self.under_thres < 1:
#                                    self.starttime_pump = time.time()
#                                    self.under_thres += 1
#                                    self.label_under = 0
#                                    print("Pump: Reached Lower Threshold: will begin pumping...")
#                                    
#                                cur_pump_time = time.time()
#                                if cur_pump_time - self.starttime_pump > 30:
#                                    
#                                    if cur_pump_time - self.starttime_pump < 31:
#                                    
#                                        if self.parent.unit_test == False:
#                                            Pump.trigger_pump() 
#                                            self.over_thres = 0
#                                            self.over_error = 0
#                                            print("Pump: Pumping...")
#                                            self.parent.pb_PumpLight.setStyleSheet("background-color: green")
#                                            self.time_for_green = time.time()
#                                            #print(f"Water Pump: pumped {cur_pump_time}")
#                #                        row = [1] #EWH
#                #                        with open('C:\dev\logs\waterpumps.csv', 'a', newline='') as f: #EWH
#                #                            writer = csv.writer(f) #EWH
#                #                            writer.writerow(row) #EWH
#                                        else:
#                                            if current_time - self.time_for_green > 1:
#                                                self.parent.pb_PumpLight.setStyleSheet("background-color: yellow")
#                                                self.time_for_green = 0 
#                                            else: 
#                                                pass
#                                    else:
#                                        self.starttime_pump = time.time()
                #            else:
                #                row = [0] #EWH
                #                with open('C:\dev\logs\waterpumps.csv', 'a', newline='') as f: #EWH
                #                    writer = csv.writer(f) #EWH
                #                    writer.writerow(row) #EWH
                                        
                            if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelCenter.value() - \
                                                                                            self.parent.sbx_WaterThresRange.value():
                                
                                if self.over_thres < 1:
                                    print("Pump: Reached Center Threshold: will stop pumping...")
                                    self.over_thres += 1
                                    
                                self.thres_reached = False
                                self.under_thres = 0
                                self.over_error = 0
    
                        else:
                            
                            time_remaining_warning = 60 - round((current_time - self.warning_timer),0)
                            
                            self.parent.DisplayCurrentWarningTime.setHtml(str(time_remaining_warning))          
                            #print(f"In warning state. Time Remaining: {time_remaining_warning}")
                            self.parent.pb_PumpLight.setStyleSheet("background-color: red")
                    else:
                        self.warning_active = True
                        self.first_pass_after_warning = True
                        if self.warning_low_message == True:
                            print("Warning: Water Level too LOW")
                            self.warning_low_message = False
                            self.warning_timer = time.time()
                else:
                    self.warning_active = True
                    self.first_pass_after_warning = True
                    if self.warning_high_message == True:
                        print("Warning: Water Level too HIGH")
                        self.warning_high_message = False
                        self.warning_timer = time.time()
            else:
                if self.over_error < 1:
                    print("Pump: zero-sized array caught")
                    self.over_error += 1
                pass
        else:
            if self.bad_pump_warning == True:
                self.parent.pb_PumpLight.setStyleSheet("background-color: red")
            else:
                self.parent.pb_PumpLight.setStyleSheet("background-color: grey")
            self.first_pass = True
                    
# =============================================================================
#         #EWH: Warning Light Button
#
# Pretty simple, just change the background of the button to red to warn that the
# level of the water hasgone beyond the user set limit. Only works, once the pump
# is on as it would be annoying before then. 
# =============================================================================    
        if self.parent.cbx_pumpOn.isChecked():
            if len(self.valuelog) > self.counter_iters_pump:
                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelUpperLim.value():
                    self.parent.pb_WarningLight.setStyleSheet("background-color: red")
                
                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) < self.parent.sbx_WaterLevelLowerLim.value():
                    self.parent.pb_WarningLight.setStyleSheet("background-color: red")
                    
                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) < self.parent.sbx_WaterLevelUpperLim.value() \
                                            and np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelUpperThres.value():
                    self.parent.pb_WarningLight.setStyleSheet("background-color: yellow")
                    
                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelLowerLim.value() \
                                            and np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) < self.parent.sbx_WaterLevelLowerThres.value():
                    self.parent.pb_WarningLight.setStyleSheet("background-color: yellow")
                    
                if np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) < self.parent.sbx_WaterLevelUpperThres.value() \
                                            and np.max(self.valuelog[(-1*self.counter_iters_pump):-1]) > self.parent.sbx_WaterLevelLowerThres.value():
                    self.parent.pb_WarningLight.setStyleSheet("background-color: green")
        else:
            if self.bad_pump_warning == True:    
                self.parent.pb_WarningLight.setStyleSheet("background-color: red")
            else:  
                self.parent.pb_WarningLight.setStyleSheet("background-color: gray")
                

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
        
        
#        serial_port = serial.Serial("COM11", 9600)
#        print("Port is open")
#        
#        except serial.SerialException:
#          serial.Serial("COM11", 9600).close()
#          print("Port is closed")
#          serial_port = serial.Serial("COM11",9600)
#          print("Port is open again")
        
        self.unit_test = bool(myconfig["LeicaCam"]["_unit_test"])
        
        self.ROIXbegin = int(myconfig["LeicaCam"]["ROIXbegin"]) 
        self.ROIXend = int(myconfig["LeicaCam"]["ROIXend"])
        self.ROIYbegin = int(myconfig["LeicaCam"]["ROIYbegin"])
        self.ROIYend = int(myconfig["LeicaCam"]["ROIYend"])
             
        print("Setup water level log...")
        self.SetupWaterLog()
        print("Connect GUI slots...")
        self.ConnectGUISlots()
        
        print("Setup camera...")
        self.cbx_pumpOn.setChecked(0)
        
        self.camera_index = 0
        
        self.is_running = bool(myconfig["LeicaCam"]["_is_running"])
        
        self.CamTh = Thread(self)
        self.CamTh.Setup(self.cam_knife, parent=self)


        if hasattr(self,'_StartPosition'):
            if self._StartPosition.__len__()>3:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setGeometry(self._StartPosition[0],self._StartPosition[1],self._StartPosition[2],self._StartPosition[3])

#        cbx_pumpOn = False
#        _StartPosition = 222, 332, 2564, 1273

        self.paintableCam=paintableqlabel.paintableqlabel(self.cam_knife)

#        th.changePixmap.connect(self.setImage)
        
        self.CamTh.start()

        self.UpdateWindowTitle()

        print("Loading Configuration...")
        #myconfig.LoadConfig(self,"LeicaCam")
        self.SetupGUIState(self)

        print("Show GUI...")
        self.show()
        
    def setCycleDuration(self,value=None):
        if value is None:
            value=self.sbx_CycleDurationSet.value()
        else:
            self.sbx_CycleDurationSet.blockSignals(True)
            self.sbx_CycleDurationSet.setValue(value)
            self.sbx_CycleDurationSet.blockSignals(False)

    def WaterThresholdChangedLower(self):
        newValue=self.sbx_WaterLevelLowerThres.value()
        self.ptwaterthres_lower.setValue(newValue)
        #print("Threshold updated: {0}".format(newValue))
        
        
    def WaterThresholdChangedUpper(self):
        newValue=self.sbx_WaterLevelUpperThres.value()
        self.ptwaterthres_upper.setValue(newValue)
        #print("Threshold updated: {0}".format(newValue))
        
    def WaterUpperLimChanged(self):
        newValue = self.sbx_WaterLevelUpperLim.value()
        self.ptwaterupperlim.setValue(newValue)
        #print("Upper Limit updated: {0}".format(newValue))
        
    def WaterLowerLimChanged(self):
        newValue = self.sbx_WaterLevelLowerLim.value()
        self.ptwaterlowerlim.setValue(newValue)
        #print("Upper Limit updated: {0}".format(newValue))

    def WaterChanged(self):
        newValue = self.sbx_WaterLevelCenter.value()
        self.ptwater.setValue(newValue)
        #print("Upper Limit updated: {0}".format(newValue))
        
    def LeicaValueChanged(self):
        newValue = self.dsbx_LeicaCycle.value()
        #print(f"Updated Leica Cycle Value: {newValue}")
        
    def StopCam(self):
        self.CamTh.terminate()
        self.is_running = False
        print("clicked stop")
        
    def StartCam(self):
        self.is_running = True
        self.CamTh = Thread(self)
        self.CamTh.Setup(self.cam_knife, parent=self)
        self.CamTh.start()
        print("clicked start")

    def ConnectGUISlots(self):
        self.btn_StartCams.clicked.connect(self.StartCams)
        self.btn_StopCams.clicked.connect(self.StopCams)
        self.sbx_WaterLevelLowerThres.valueChanged.connect(self.WaterThresholdChangedLower)
        self.sbx_WaterLevelUpperThres.valueChanged.connect(self.WaterThresholdChangedUpper)
        self.sbx_WaterLevelCenter.valueChanged.connect(self.WaterChanged)

        self.sbx_WaterLevelUpperLim.valueChanged.connect(self.WaterUpperLimChanged)
        self.sbx_WaterLevelLowerLim.valueChanged.connect(self.WaterLowerLimChanged)
        
        self.dsbx_LeicaCycle.valueChanged.connect(self.LeicaValueChanged)
        
        self.pb_WarningLight.clicked.connect(self.StopCam)
        
        self.pb_StopCam.clicked.connect(self.StopCam)
        self.pb_StartCam.clicked.connect(self.StartCam)
        

    def SetupWaterLog(self):
        self.ptwaterlevel=self.pg_waterlevel.plot(pen=(0, 255, 200, 200))
        
        self.ptwaterthres_upper=pg.InfiniteLine(pen='y',angle=0,movable=False)
        self.ptwaterthres_lower=pg.InfiniteLine(pen='y',angle=0,movable=False)
        
        self.ptwaterupperlim=pg.InfiniteLine(pen='r', angle=0, movable=False)
        self.ptwaterlowerlim=pg.InfiniteLine(pen='r', angle=0, movable=False)
        
        self.pg_waterlevel.addItem(self.ptwaterupperlim)
        self.pg_waterlevel.addItem(self.ptwaterlowerlim)
        
        self.pg_waterlevel.addItem(self.ptwaterthres_upper)
        self.pg_waterlevel.addItem(self.ptwaterthres_lower)
        
        self.ptwater=pg.InfiniteLine(pen='g', angle=0, movable=False)
        self.pg_waterlevel.addItem(self.ptwater)

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
    
    def SetupGUIState(self,GUIobj):
        if not "LeicaCam" in myconfig:
            print("Error: could not find LeicaCam in Config File")
            
        #EWH: Eric here, this is a very hacky way of doing what is done in PyAGTUM, 
        # for some reason it caused issues here with widgets become strings without
        # attributes, but it appears to work in this function without issue. 
        # closeEvent's version of saving the config file is the same as PyAGTUM
        
        newValue = float(myconfig["LeicaCam"]["sbx_WaterLevelLowerThres"])
        self.sbx_WaterLevelLowerThres.setValue(newValue)
        
        newValue = float(myconfig["LeicaCam"]["sbx_WaterLevelUpperThres"])
        self.sbx_WaterLevelUpperThres.setValue(newValue)

        newValue = float(myconfig["LeicaCam"]["sbx_WaterLevelLowerLim"])
        self.sbx_WaterLevelLowerLim.setValue(newValue)

        newValue = float(myconfig["LeicaCam"]["sbx_WaterLevelUpperLim"])
        self.sbx_WaterLevelUpperLim.setValue(newValue)
        
        newValue = float(myconfig["LeicaCam"]["sbx_WaterLevelCenter"])
        self.sbx_WaterLevelCenter.setValue(newValue)
        
        newValue = float(myconfig["LeicaCam"]["dsbx_LeicaCycle"])
        self.dsbx_LeicaCycle.setValue(newValue)
        
        ROIXbegin = myconfig["LeicaCam"]["ROIXbegin"]
        self.DisplayBoxLoc_1.setHtml(ROIXbegin)
        ROIXend = myconfig["LeicaCam"]["ROIXend"]
        self.DisplayBoxLoc_2.setHtml(ROIXend)
        ROIYbegin = myconfig["LeicaCam"]["ROIYbegin"]
        self.DisplayBoxLoc_3.setHtml(ROIYbegin)
        ROIYend = myconfig["LeicaCam"]["ROIYend"]
        self.DisplayBoxLoc_4.setHtml(ROIYend)
        
        
    
    def closeEvent(self, event):
        #super(MainWindow, self).closeEvent(event)
        print("Closing Ports")

        if not "LeicaCam" in myconfig:
            myconfig["LeicaCam"]={}
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
                myconfig["LeicaCam"][childName]=value
        
        do_not_save_zeros = (self.ROIXbegin, self.ROIXend, self.ROIYbegin, self.ROIYend)
        
        if all([dnsz == 0 for dnsz in do_not_save_zeros]):
            print("Detected All Zero Box Location, not saving...")
            pass
        else:
            myconfig["LeicaCam"]["ROIXbegin"] = str(self.ROIXbegin)
            myconfig["LeicaCam"]["ROIXend"] = str(self.ROIXend)
            myconfig["LeicaCam"]["ROIYbegin"] = str(self.ROIYbegin)
            myconfig["LeicaCam"]["ROIYend"] = str(self.ROIYend)

        myconfig.SaveConfig(self,"LeicaCam")
        print("Saving Config File...")
        myconfig.write()
        
        Pump.pump_ser.close()
        if self.CamTh.isRunning():
            self.CamTh.terminate()
            serial.Serial("COM11", 9600).close()
            print("Eric closed the COM11 port.")
        event.accept()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    print("Loading main GUI...")

    #Loading default configuration
    if win:
        config_name = 'DefaultConfig_win-3rdCam_-Water.cfg'
    else:
        config_name = 'DefaultConfig.cfg'

    config_path = os.path.join(application_path, 'configs')
    configfile = os.path.join(config_path, config_name)
    
    if not os.path.isfile(configfile):
        QtWidgets.QMessageBox.warning(None,"Error",
            "Configuration file missing:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)
        sys.exit()

    try:
        print("Loading Config File...")
        myconfig = config(configfile)
                
    except:
        QtWidgets.QMessageBox.warning(None, "Error",
            "Configuration file corrupted:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)
        sys.exit()

    ui_path = os.path.join(application_path, 'ui')
    window = mainGUI(os.path.join(ui_path,"LeicaCam_Window_210215_EWH.ui"))

    sys.exit(app.exec_())
