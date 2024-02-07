# -*- coding: utf-8 -*-
"""
Created on Sat Jul 30 18:57:45 2022

@author: jprice
"""



#import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets, uic
#from PIL import ImageQt

import sys
import os
from AGTUMconfigparser import config
from ximea import xiapi
from datetime import datetime
#import time
import nidaqmx
#import serial
# import paintableqlabel
import cv2
#import copy

import numpy as np
#from scipy import stats, signal, fftpack
#import leicaCmds as Leica
#import atumCmds_2 as Atum
## import syringepump as Pump
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

class PreCamTimer(log.valuelogger):
    # sefl.name = "PreCam"
    def __init__(self):
        super().__init__()
        self.cam=xiapi.Camera()
        self.camSN = None
        self.camFrame = None
        
    def setupCams(self, camSN=None, CamFrame=None):
        try:
            self.cam.stop_acquisition()
            print("Stop Acquisition Pre")
        except xiapi.Xi_error:
            pass
        
        try:
            self.cam.close_device()
            print("Close Pre")
        except xiapi.Xi_error:
            pass
        
        if self.camSN is None:
            self.camSN = camSN
        if self.camFrame is None:
            self.camFrame = CamFrame

        self.cam.open_device_by_SN(self.camSN)
        print("Pre opening device", self.camSN)
            # settings
        self.cam.set_imgdataformat('XI_RGB24')
            #1028*1232*3*20*24
        self.cam.set_limit_bandwidth(1000)
        self.cam.set_exposure(10000)
        self.cam.set_decimation_horizontal(2)
        self.cam.set_decimation_vertical(2)
        self.cam.set_framerate(3)
        #self.cam.frame=CamFrame
 #           cam.name=self.CamFrames[icam].text()
        self.image=xiapi.Image()
        self.cam.start_acquisition()
        print("Pre start acquisition")



    def updateVis(self):
        #get data and pass them from camera to img
        try:
            self.cam.get_image(self.image, timeout=5000) #EWH
    #                print('Image read from ' + cam.name)
            
            
            npimg=self.image.get_image_data_numpy()
            # cv2.imshow("XIMEA cams", npimg)
            
#            barcode_img = npimg[800:1200, 125:1125] #EWH
            
            
            
            npimg=np.copy(npimg[::2,::2,::-1])
    #            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))
            
            Qimg = QtGui.QImage(npimg,npimg.shape[1],npimg.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(Qimg)
            self.camFrame.setPixmap(pix)        
            
            ###EWH: the below code takes the image and processes it so that is 
            #is only a barcode that can then be read by the Barcode_Reader_Final_EWH.py
            #Credit: Nico Kemnitz
            
            # Convert to HSV (Hue-Saturation-Value), pick hue
#            img_hsv = cv2.cvtColor(barcode_img, cv2.COLOR_RGB2HSV)
#            hue = img_hsv[..., 0]
            
            # https://docs.opencv.org/4.x/d7/d4d/tutorial_py_thresholding.html
            # Otsu's Binarization to pick threshold for bimodal distribution - not sure if that always works?
            #_, mask = cv2.threshold(hue, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Count white pixels for each column
            #vcount = (mask > 0).astype(np.uint8).sum(axis=0).astype(np.uint8)
            
            # Another Otsu to get a good threshold value for white pixels per column - note that max height of image must be less than 256
            #threshold, mask = cv2.threshold(vcount, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            #mask = ~mask
            
            # Generate image with same shape as input and repeat mask vertically
            #barcode_img = np.repeat(mask.reshape(1,-1), barcode_img.shape[0], axis=0)
            #cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img)
            
            ###EWH This is hard coded and will need to be fixed at some point - EWH
            #Turning off barcode since it does not seem to help and is usually not an issue. 
            #cv2.imwrite("C:/dev/data/barcode_out.png", barcode_img)
        
        except (OSError, xiapi.Xi_error) as e: #EWH
            time_now = datetime.now()
            try:
                with open('C:/Users/jprice/PyAGTUM_ERROR_File.txt', 'a') as f:
                    f.write(f'Pre Camera: Error: {e} \n Time: {time_now} \n')
            except FileNotFoundError:
                print("The 'Error Test - line 160' directory does not exist")    
            #print('get_image ran into timeout.', e) #EWH
            #print(datetime.now()) #EWH
            
            print('Image skipped Post')
            print(f'Error: {e})')
            #print("Cam Handle: ", self.cam.handle)
            #print("Img address: ", self.image)
            try:
                self.setupCams()
            except xiapi.Xi_error as e:
                print(f"Tried to reset PostCam, but failed. Error: {e}")
        




    def datacollector(self):
        self.updateVis()


class PostCamTimer(log.valuelogger):
    historylength = 4000
    
    def __init__(self):
        super().__init__()
        self.cam=xiapi.Camera()
        self.camSN = None
        self.camFrame = None
        
    def setupCams(self, camSN=None, CamFrame=None):
        try:
            self.cam.stop_acquisition()
            print("Stop Acquisition Post")
        except xiapi.Xi_error:
            pass
        
        try:
            self.cam.close_device()
            print("Close Post")
        except xiapi.Xi_error:
            pass
        
        if self.camSN is None:
            self.camSN = camSN
        if self.camFrame is None:
            self.camFrame = CamFrame

        self.cam.open_device_by_SN(self.camSN)
        print("Post opening device", self.camSN)
            # settingsXI_RGB24
        self.cam.set_imgdataformat('XI_RGB24') #EWH
            #1028*1232*3*20*24
        self.cam.set_limit_bandwidth(1000)
        self.cam.set_wb_kg(5)
        self.cam.set_wb_kb(10)
        self.cam.set_wb_kr(10)
        self.cam.set_exposure(1000)
 #       self.cam.set_decimation_horizontal(2) #EWH
 #       self.cam.set_decimation_vertical(2) #EWH
        self.cam.set_framerate(3) #EWH
        #self.cam.frame=CamFrame
 #           cam.name=self.CamFrames[icam].text()
        self.image=xiapi.Image()
        self.cam.start_acquisition()
        print("Post start acquisition")
    
        self.track_len = 20 # max number of locations of point to remember
        self.detect_interval = 10
        self.tracks = []
        self.frame_idx = 0
        self.speed = 0
        self.time = []
        self.speed_list = []
        self.counter = 0

    def datacollector(self):
        
        #get data and pass them from camera to img
        try:
            self.cam.get_image(self.image, timeout=5000) #EWH
#            t1 = time.time()
    #                print('Image read from ' + cam.name)
            #cv2.imshow("XIMEA cams", img.get_image_data_numpy())
    
            npimg=self.image.get_image_data_numpy()
            #npimg=npimg[200:1656, 1000:2064, 0:3] #vertical, horizontal 
            #print(np.shape(npimg))

            
            vis=np.copy(npimg[::2,::2,::-1]) #EWH: 2,2,-1
    #            print('{0} {1}'.format(npimg.shape[0],npimg.shape[1]))
#            if self.parent.cbx_TrackSpeed.isChecked():
#                print("This feature is no longer available. Please uncheck the box. - EWH 220730")
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
    
#                self.frame_idx += 1
#                self.prev_gray = frame_gray
               # cv.imshow('lk_track', vis)
    
            Qimg = QtGui.QImage(vis, vis.shape[1], vis.shape[0], QtGui.QImage.Format_RGB888)
            pix = QtGui.QPixmap.fromImage(Qimg)
            self.camFrame.setPixmap(pix)
            
   
        except (OSError, xiapi.Xi_error) as e: #EWH
            time_now = datetime.now()
            try:
                with open('C:/Users/jprice/PyAGTUM_ERROR_File.txt', 'a') as f:
                    f.write(f'Post Camera: Error: {e} \n Time: {time_now} \n')
            except FileNotFoundError:
                print("The 'Error Test - line 324' directory does not exist")    
            #print('get_image ran into timeout.', e) #EWH
            #print(datetime.now()) #EWH
            
            print('Image skipped Post')
            print(f'Error: {e})')
            #print("Cam Handle: ", self.cam.handle)
            #print("Img address: ", self.image)
            try:
                self.setupCams()
            except xiapi.Xi_error as e:
                print(f"Tried to reset PostCam, but failed. Error: {e}")
            
        

class mainGUI(QtWidgets.QMainWindow):
    #gui elements whose value/state is saved in the configuration file.
    #gui elements whose name starts with '_' are excluded.
    GUIElements=[QtWidgets.QSlider,QtWidgets.QRadioButton,QtWidgets.QCheckBox,QtWidgets.QDoubleSpinBox,QtWidgets.QSpinBox,QtWidgets.QComboBox,QtWidgets.QLineEdit]
    _StartPosition=[]
    _CameraSNs=['CICAU1641091','CICAU1914024']
    # _CameraSNs=['CICAU1641091','CICAU1914024','CICAU1914041']
#    _syncATUM_chopperPort="Dev1/pfi0"
#    _syncLEICA_chopperPort="Dev1/pfi1"
    _logpath='C:\dev\PyAGTUM\logs'
    _DistanceBetweenSlots=6.0#mm

    def __init__(self,uifile):
        QtWidgets.QMainWindow.__init__(self)
        uic.loadUi(uifile, self)
        self.setWindowState(QtCore.Qt.WindowMaximized)
        print("Loading GUI config...")
        myconfig.LoadConfig(self,"pyAGTUM")

#        print("Setup ATUM sync...")
#        self.setupATUMsync()
#        print("Connect GUI slots...")
#        self.ConnectGUISlots()


        print("Setup hardware...")
        self.SetupHardware()

        if hasattr(self,'_StartPosition'):
            if self._StartPosition.__len__()>3:
                self.setWindowState(QtCore.Qt.WindowNoState)
                self.setGeometry(self._StartPosition[0],self._StartPosition[1],self._StartPosition[2],self._StartPosition[3])

        print("Setup GUI state...")
        self.UpdateWindowTitle()
#        self.SetupGUIState(self)

        print("Show GUI...")
        self.show()


    def SetupHardware(self):
        self.PreCamTimer = PreCamTimer()
        self.PreCamTimer.setupCams(self._CameraSNs[0], self._cam_presection)
        self.PreCamTimer.initiateTimer(100, None, None, parent=self)
        self.PreCamTimer.start()

        self.PostCamTimer = PostCamTimer()
        self.PostCamTimer.setupCams(self._CameraSNs[1], self._cam_postsection)
        self.PostCamTimer.initiateTimer(100, self._logpath,'CamTapeSpeed', parent=self)
        self.PostCamTimer.start()

#        
    def StopHardware(self):
        self.PreCamTimer.stopLog()
        self.PostCamTimer.stopLog()
        self.PreCamTimer.cam.stop_acquisition()
        self.PostCamTimer.cam.stop_acquisition()
        self.PreCamTimer.cam.close_device()
        self.PostCamTimer.cam.close_device()

        
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


    def UpdateWindowTitle(self):
        Title="Tape Cameras"
        self.setWindowTitle(Title)
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    #Loading default configuration
    if win:
        config_name = 'DefaultConfig_win-cameras.cfg'
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
        print("Loading configuration...")
        myconfig = config(configfile)
    except:
        QtWidgets.QMessageBox.warning(None, "Error",
            "Configuration file corrupted:\n {0}".format(configfile),
            QtWidgets.QMessageBox.Cancel, QtWidgets.QMessageBox.NoButton)
        sys.exit()

    print("Loading main GUI...")
    ui_path = os.path.join(application_path, 'ui')
    window = mainGUI(os.path.join(ui_path,"PyAGTUM_cams_window_220730_EWH.ui")) #EWH

    sys.exit(app.exec_())