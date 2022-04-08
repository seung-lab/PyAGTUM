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

#class PreCamTimer(log.valuelogger):
#    # sefl.name = "PreCam"
#    def __init__(self):
#        super().__init__()
#        self.cam=xiapi.Camera()
#        self.camSN = None
#        self.camFrame = None
#        
#    def setupCams(self, camSN=None, CamFrame=None):
#        try:
#            self.cam.stop_acquisition()
#            print("Stop Acquisition Pre")
#        except xiapi.Xi_error:
#            pass
#        
#        try:
#            self.cam.close_device()
#            print("Close Pre")
#        except xiapi.Xi_error:
#            pass
#        
#        if self.camSN is None:
#            self.camSN = camSN
#        if self.camFrame is None:
#            self.camFrame = CamFrame
#
#        self.cam.open_device_by_SN(self.camSN)
#        print("Pre opening device", self.camSN)
#            # settings
#        self.cam.set_imgdataformat('XI_RGB24')
#            #1028*1232*3*20*24
#        self.cam.set_limit_bandwidth(1000)
#        self.cam.set_exposure(10000)
#        self.cam.set_decimation_horizontal(2)
#        self.cam.set_decimation_vertical(2)
#        self.cam.set_framerate(3)
#        #self.cam.frame=CamFrame
# #           cam.name=self.CamFrames[icam].text()
#        self.image=xiapi.Image()
#        self.cam.start_acquisition()
#        print("Pre start acquisition")
#
#
#
#    def updateVis(self):
#        #get data and pass them from camera to img
#        try:
#            self.cam.get_image(self.image, timeout=5000) #EWH
#    #                print('Image read from ' + cam.name)
#            
#            
#            npimg=self.image.get_image_data_numpy()
#            # cv2.imshow("XIMEA cams", npimg)
#            
#            barcode_img = npimg[800:1200, 125:1125] #EWH
#            
#            
#            
#            npimg=np.copy(npimg[::2,::2,::-1])
#    #            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))
#            
#            Qimg = QtGui.QImage(npimg,npimg.shape[1],npimg.shape[0], QtGui.QImage.Format_RGB888)
#            pix = QtGui.QPixmap.fromImage(Qimg)
#            self.camFrame.setPixmap(pix)        
#            
#            ###EWH: the below code takes the image and processes it so that is 
#            #is only a barcode that can then be read by the Barcode_Reader_Final_EWH.py
#            #Credit: Nico Kemnitz
#            
#            # Convert to HSV (Hue-Saturation-Value), pick hue
#            img_hsv = cv2.cvtColor(barcode_img, cv2.COLOR_RGB2HSV)
#            hue = img_hsv[..., 0]
#            
#            # https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
#            # Otsu's Binarization to pick threshold for bimodal distribution - not sure if that always works?
#            #_, mask = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#            
#            # Count white pixels for each column
#            #vcount = (mask > 0).astype(np.uint8).sum(axis=0).astype(np.uint8)
#            
#            # Another Otsu to get a good threshold value for white pixels per column - note that max height of image must be less than 256
#            #threshold, mask = cv2.threshold(vcount, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#            #mask = ~mask
#            
#            # Generate image with same shape as input and repeat mask vertically
#            #barcode_img = np.repeat(mask.reshape(1,-1), barcode_img.shape[0], axis=0)
#            #cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img)
#            
#            ###EWH This is hard coded and will need to be fixed at some point - EWH
#            #Turning off barcode since it does not seem to help and is usually not an issue. 
#            #cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img)
#        
#        except (OSError, xiapi.Xi_error) as e: #EWH
#            time_now = datetime.now()
#            try:
#                with open('C:/Users/jprice/PyAGTUM_ERROR_File.txt', 'a') as f:
#                    f.write(f'Pre Camera: Error: {e} \n Time: {time_now} \n')
#            except FileNotFoundError:
#                print("The 'Error Test - line 160' directory does not exist")    
#            #print('get_image ran into timeout.', e) #EWH
#            #print(datetime.now()) #EWH
#            
#            print('Image skipped Post')
#            print(f'Error: {e})')
#            #print("Cam Handle: ", self.cam.handle)
#            #print("Img address: ", self.image)
#            try:
#                self.setupCams()
#            except xiapi.Xi_error as e:
#                print(f"Tried to reset PostCam, but failed. Error: {e}")
#        
#
#
#
#
#    def datacollector(self):
#        self.updateVis()
#
#
#class PostCamTimer(log.valuelogger):
#    historylength = 4000
#    
#    def __init__(self):
#        super().__init__()
#        self.cam=xiapi.Camera()
#        self.camSN = None
#        self.camFrame = None
#        
#    def setupCams(self, camSN=None, CamFrame=None):
#        try:
#            self.cam.stop_acquisition()
#            print("Stop Acquisition Post")
#        except xiapi.Xi_error:
#            pass
#        
#        try:
#            self.cam.close_device()
#            print("Close Post")
#        except xiapi.Xi_error:
#            pass
#        
#        if self.camSN is None:
#            self.camSN = camSN
#        if self.camFrame is None:
#            self.camFrame = CamFrame
#
#        self.cam.open_device_by_SN(self.camSN)
#        print("Post opening device", self.camSN)
#            # settingsXI_RGB24
#        self.cam.set_imgdataformat('XI_RGB24') #EWH
#            #1028*1232*3*20*24
#        self.cam.set_limit_bandwidth(1000)
#        self.cam.set_wb_kg(5)
#        self.cam.set_wb_kb(10)
#        self.cam.set_wb_kr(10)
#        self.cam.set_exposure(30000)
# #       self.cam.set_decimation_horizontal(2) #EWH
# #       self.cam.set_decimation_vertical(2) #EWH
#        self.cam.set_framerate(3) #EWH
#        #self.cam.frame=CamFrame
# #           cam.name=self.CamFrames[icam].text()
#        self.image=xiapi.Image()
#        self.cam.start_acquisition()
#        print("Post start acquisition")
#    
#        self.track_len = 20 # max number of locations of point to remember
#        self.detect_interval = 10
#        self.tracks = []
#        self.frame_idx = 0
#        self.speed = 0
#        self.time = []
#        self.speed_list = []
#        self.counter = 0
#
#    def datacollector(self):
#        
#        #get data and pass them from camera to img
#        try:
#            self.cam.get_image(self.image, timeout=5000) #EWH
#            t1 = time.time()
#    #                print('Image read from ' + cam.name)
#            #cv2.imshow("XIMEA cams", img.get_image_data_numpy())
#    
#            npimg=self.image.get_image_data_numpy()
#
#            
#            vis=np.copy(npimg[::2,::2,::-1]) #EWH: 2,2,-1
#    #            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))
#            if self.parent.cbx_TrackSpeed.isChecked():
#                
#                frame_gray = cv2.cvtColor(vis, cv2.COLOR_BGR2GRAY)
#                if len(self.tracks) > 0:
#                    img0, img1 = self.prev_gray, frame_gray
#                    p0 = np.float32([tr[-1] for tr in self.tracks]).reshape(-1, 1, 2)
#                    p1, _st, _err = cv2.calcOpticalFlowPyrLK(img0, img1, p0, None, **lk_params)
#                    p0r, _st, _err = cv2.calcOpticalFlowPyrLK(img1, img0, p1, None, **lk_params)
#                    d = abs(p0-p0r).reshape(-1, 2).max(-1)
#                    good = d < 1
#                    new_tracks = []
#                    t20 = []
#                    for tr, (x, y), good_flag in zip(self.tracks, p1.reshape(-1, 2), good):
#                        if not good_flag:
#                            continue
#                        tr.append((x, y))
#                        if len(tr) > self.track_len:
#                            del tr[0]
#                            t20.append(tr[-1][0] - tr[0][0])
#                        new_tracks.append(tr)
#                        cv2.circle(vis, (x, y), 2, (0, 255, 0), -1)
#                    self.tracks = new_tracks
#                    cv2.polylines(vis, [np.int32(tr) for tr in self.tracks], False, (0, 255, 0))
#                    draw_str(vis, (20, 20), 'track count: %d' % len(self.tracks))
#                    if self.frame_idx % 20 == 0:
#                        self.time.append(t1)
#                        if len(self.time) > 2:
#                            self.speed = (sum(t20) / len(t20)) * 0.0136 / (self.time[-1] - self.time[-2])
#                            del self.time[0]
#                            self.updateLog(self.speed)
#                            #print("update log 1")
#                            print('Cam Tape speed: %3f' % self.speed)
#                            '''
#                            self.speed_list.append(self.speed)
#                            if len(self.speed_list) > 3:
#                                s1 = sum(self.speed_list[-3:])/3
#                                if s1 > 0.35:
#                                    self.parent.setTapeSpeed(0.39)
#                                    self.speed_list = []
#                                elif s1 < 0.325:
#                                    self.parent.setTapeSpeed(0.43)
#                                    self.speed_list = [] 
#                                else:
#                                    self.parent.setTapeSpeed(0.41)
#                                    del self.speed_list[0]
#                             '''   
#                                
#                    # 0.0136mm per pixel
#                    draw_str(vis, (20, 40), 'speed: %3f' % self.speed)
#    
#                if self.frame_idx % self.detect_interval == 0:
#                    mask = np.zeros_like(frame_gray)
#                    mask[:] = 255
#                    for x, y in [np.int32(tr[-1]) for tr in self.tracks]:
#                        cv2.circle(mask, (x, y), 5, 0, -1)
#                    p = cv2.goodFeaturesToTrack(frame_gray, mask = mask, **feature_params)
#                    if p is not None:
#                        for x, y in np.float32(p).reshape(-1, 2):
#                            self.tracks.append([(x, y)])
#    
#                self.frame_idx += 1
#                self.prev_gray = frame_gray
#               # cv.imshow('lk_track', vis)
#    
#            Qimg = QtGui.QImage(vis, vis.shape[1], vis.shape[0], QtGui.QImage.Format_RGB888)
#            pix = QtGui.QPixmap.fromImage(Qimg)
#            self.camFrame.setPixmap(pix)
#            
#   
#        except (OSError, xiapi.Xi_error) as e: #EWH
#            time_now = datetime.now()
#            try:
#                with open('C:/Users/jprice/PyAGTUM_ERROR_File.txt', 'a') as f:
#                    f.write(f'Post Camera: Error: {e} \n Time: {time_now} \n')
#            except FileNotFoundError:
#                print("The 'Error Test - line 324' directory does not exist")    
#            #print('get_image ran into timeout.', e) #EWH
#            #print(datetime.now()) #EWH
#            
#            print('Image skipped Post')
#            print(f'Error: {e})')
#            #print("Cam Handle: ", self.cam.handle)
#            #print("Img address: ", self.image)
#            try:
#                self.setupCams()
#            except xiapi.Xi_error as e:
#                print(f"Tried to reset PostCam, but failed. Error: {e}")
            
            

        
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


class Offsetlog(log.valuelogger):
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
    

    def updateVis(self):
        try:
            self.parent.ptsyncLEICA_chopper.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update Leica chopper log graph - line 448")
            
    def datacollector(self):
        chopperSignal=int(self.parent.syncLEICA_chopper.read())
        self.updateLog(chopperSignal)
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
                if chopperSignal == 0: 
                    self.skip_checked_num_future += 1
                    #EWH: Setting "the wait to nose" time (hardcoded for current luxel tape sizes)  
                    if self.skip_checked_num_future == 1:
                        #EWH: 13 cycles (15 to the nose)
                        self.wait_cycle_num_future = 13 + self.parent.ATUMcyledurationlog.valuelog.__len__()
                        #print(f"Wait Cycle Time Set to: {self.wait_cycle_num}")
            else: 
                self.skip_checked_num_future = 0



#    def datacollector(self):
#        chopperSignal=int(self.parent.syncLEICA_chopper.read())
#        self.updateLog(chopperSignal)
#        BaseSpeed = self.parent.sbx_targetCycleSpeed.value()
#        
#        
#            # turn off cutting for 5 cycles, only happen during retraction phase
#        self.skip_checked.append(self.parent.cbx_skip.isChecked())
#        self.skip_checked.pop(0)
#        if self.skip_checked[-2]:
#            wait_cycles = 14 + self.parent.ATUMcyledurationlog.valuelog.__len__

#        if wait_cycles == self.parent.ATUMcyledurationlog.valuelog.__len__:
#            if self.parent.cbx_skip.isChecked():
#                
#                if self.state == 0: #EWH
#                    if not self.skip_checked[-2]: #EWH
#                        print("entered into stop cut area")
#                        print(self.skip_checked)
#                        if self.skip_checked[-14]:
#                            self.parent.StopCut()
#                            self.StopCutTime = self.timelog[-1]
#                            # turn off synchronization
#                            self.parent.cbx_synTS.setChecked(False)
#                        
#                        if self.parent.ATUMcyledurationlog.valuelog.__len__()>0:
#                            
#                            NumSet = self.parent.sbx_NumSections.value()
#                                                
#                            if self.timelog[-1] - self.StopCutTime > self.parent.ATUMcyledurationlog.valuelog[-1]*NumSet:
#                                print("entered into start cut")
#                                self.parent.StartCut()
#                                self.StopCutTime = self.timelog[-1]
#                                self.parent.cbx_skip.setChecked(False)
#                                self.parent.cbx_synTS.setChecked(True)

#                    print("entered into if not self.skip_checked[-2]")
#                    print(self.skip_checked)
#                    self.StartPauseTime = self.timelog[-1] #EWH
#                    
#                    #This is where the delay needs for the wait
#                    
#                    dist_nose = 15*6 #EWH: This is hard coded by current gridtape 
#                                 # specs (15 apertues, 6 mm apart) 
#                    svalue=Atum.gTS() 
#                    print(f"Speed of Tape for Eric: {svalue}")
#                    #svalue=int(svalue)
#                    time_nose=dist_nose / svalue #EWH: time to get to the nose from cams
#                    ATUMcycle=np.diff(self.upStateStart[-2:])
#                    print(f"ATUM cycle time for Eric: {ATUMcycle}")
#                    self.time_nose_cycle = time_nose - ATUMcycle
#                    self.time_nose_cycle = int(self.time_nose_cycle[0])
#                    print(f"Waiting: {self.time_nose_cycle} seconds")
#                    print(self.timelog[-1] - self.StartPauseTime)
    #EWH: this is not working as intendend... always 0
############################# UNDER CONSTRUCTION ##############################                     
        
        
        if self.valuelog.__len__()<2:
            return

        if self.valuelog[-1]==1 and self.valuelog[-2]==0: #cutting phase starts
            self.state = 0
            self.upStateStart.append(self.timelog[-1])
            rs,_ = Leica.getReturnSpeed()

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
    def updateVis(self):
        try: 
            self.parent.ptsyncATUM_chopper.setData(self.timelog,self.valuelog)
        except: 
            print("Error: failed to update ATUMchopper log graph - line 765")
    def datacollector(self):
        try: 
            chopperSignal=int(self.parent.syncATUM_chopper.read())
        #invert chopper signal
            if chopperSignal==1:
                chopperSignal=0
            elif chopperSignal==0:
                chopperSignal=1
        except nidaqmx.DaqError as e:
            print(f"Nidaq error detected: {e}")
            

        self.updateLog(chopperSignal)
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
                self.parent.DisplayTension.setHtml( str( round(Atum.gTT(),2) ) )

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
        #print("update log 11")
        #print("Tension: {0}".format(Atum.gTT()))

class retractspeedlog(log.valuelogger):
    historylength=500
    def datacollector(self):
        [RetractionSpeed,resstr]=Leica.getReturnSpeed()
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
        print("return speed: {}".format(value))

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
        Leica.startCuttingMotor()
        self.setReturnSpeed()
        
    def StopCut(self):
        Leica.stopCuttingMotor()
    
    def getRetractSpeed(self):
        value = Leica.getReturnSpeed()
        self.DisplayRetractSpeed.setHtml(str(value[0]))
        
    def setRetractSpeed(self):
        value=self.sbx_retractionSpeed.value()
        Leica.setReturnSpeed(value)
        
    def getNS(self):
        value = Leica.getNS_Abs()
        self.DisplayNS.setHtml(str(value))
        
    def goNS(self):
        value = self.sbx_setNS.value()
        Leica.moveNS_Abs(value)
        self.DisplayNS.setHtml(str(value))
        
    def getEW(self):
        value = Leica.getEW_Abs()
        self.DisplayEW.setHtml(str(round(value,3)))
        
    def goEW(self):
        value = self.sbx_setEW.value()
        Leica.moveEW_Abs(value)
        self.DisplayEW.setHtml(str(value))
        
    def getTension(self):
        self.DisplayTension.setHtml(str(round(Atum.gTT(),2)))
        
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
#        self.StopHardware()

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
    window = mainGUI(os.path.join(application_path,"PyAGTUM_mainwindow_220730_no_cams_EWH.ui")) #EWH

    sys.exit(app.exec_())
