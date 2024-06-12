# pyAGTUM 

## Warning: 
---

This library and the code are subject to change as this project is ongoing.  

## About: 
--- 

**pyAGTUM** is a program for controlling a Leica UC7 ultramicrotome and a modified version of the RMC automated tape collecting machine (ATUM) and a New Era Pump Systems syringe pump. The modifications to the RMC will be listed below in the construction section of this document and CAD files can be found in the folder CAD files. The modifications were made to enhance the RMC for collecting serial thin tissue sections on Luxel's Gridtape for TEM imaging. The ultimate purpose of this program is to control all machines and synchronize the cutting of the UC7 with the placement of the aperture in the Gridtape at the nose of the ATUM while also monitoring the water level in the boat of the diamond knife. Additionally a Zaber 3 axis stage is used to position the ATUM, and remember positions for storing the sysem away from the cutting area and resuming at the cutting area. All GUI use PyQT5 (except hardware.ui).  

---

There are four key .py files for running pyAGTUM, each one controlling a different aspect of the system:

- **PyAGTUM.py** is the script for the main UI for controlling the cutting and speed of the tape movement through the ATUM. This program will attempt to synchronize the cutting and the placement of the apertures on Gridtape. 

- **LeicaCamWater.py** is the script for getting the feed from the Leica IC90E microscope camera and monitoring the water level in the boat using a user defined subarea of the camera feed and a user defined threshold for a "good water level".  

- **GridtapeCameras.py** is the script for the UI connecting to the cameras that observe the Gridtape before and after section collection. 

- **hardwareUI.py** is the script for controlling the Zaber 3 axis stage for moving between storage, pickup, and any desired location inbetween. 

### PyAGTUM.py

Note: there are many features that are not in use, for example, the valuelogger that may latter be reimplemented but as of now are no longer used. The main features of the UI will be covered in this section, but not all classes and functions will be covered in this README. 

`PyAGTUM.py` requires the scripts 
1. AGTUMconfigparser.py
2. atumCmds_2.py
3. leicaCmds.py
4. valuelogger.py

Running `PyAGTUM.py` in any terminal should result in several starting messages. After ingesting the configuration filem, the script first loads the UI from `PyAGTUM_mainwindow.ui`. Default settings for the UI can be found in the configuration file: `DefaultConfig_win-3rdCam_-Water.cfg`. 

The class `mainGUI()` contains the widgets and main functions for opening and processing UI requests in the interface. The first important function call is `self.setupATUMsync()` which sets up the plot for plotting the light choppers of the ATUM and Leica. 1 indicates the presence of light (upstate) and 0 indicated the absence of light (downstate). For the ATUM upstate corresponds to the presence of an aperture in light chopper and for the Leica upstate represents the cutting *window*. Important, this is the cutting window, **not** exactly where the cutting is happening as each sample for cutting is a different length. This is where the offset becomes important for actually lining up the cutting and placement of the thin section with the Gridtape window. `setupATUMsync` also sets up the logs for many of the important variables like tapespeed, slot duration, and offset, not all of which are used in the current version of pyAGTUM. Next, `self.SetupHardware()` is called which connects to the Nidaq connected to the light choppers to recieve signals from them about the state of the cutting and Gridtape movement. `mainGUI` then connects all of the button, spinboxes, etc to the their respective actions through `self.ConnectGUISlots()`. All actions for buttons can be found here. The main UI is then setup and displayed on screen. 

When pressing **START** in the UI this will trigger both the `StartCams` and `StartCut` functions. `StartCams` starts the ATUM movement through a command directly to the ATUM `ATUM.Start()` while also also reading the current speed set in the UI `setTapeSpeed`. It also starts several "logs", but it should be noted that these logs do not actually output to .xml files anymore, but only use the current state in determining the position of the ATUM light chopper. The two most important classes called are the `ATUMchopperlog()` and the `LEICAchopperlog()`. 

* `ATUMchopperlog()`
      * In the function `datacollector` function reads the signal from the light chopper on the ATUM and stores that information in the form of a 1 or 0. This function will also print the current "ATUM cycle" which is the time is took from one tape aperture to the next. It is also in `datacollector` that the tension is displayed in UI.  

* `LEICAchopperlog()`
    * This class contains the same named function, `datacollector`, but unlike in `ATUMchopperlog()` it contains the vast majority for features and functions for the proper running of the collection system. First it reads the user input tension limit from the UI and compares it to the value from the ATUM and if the tension is too great `self.parent.StopCams()` and `self.parent.StopCut()` is issued stopping the cutting completely and requiring user invovlment with the ATUM hardware. This is very important to avoid damaging the ATUM during collecting or when testing the device. The function checks the status of the light chopper using `self.chopperSignal` and updates the log `self.updateLog(self.chopperSignal)`. The next portion of code deals with the situation where the user has checked the checkbox in the UI for "SkipCut". This feature allows the user to avoid a bad nanofilm in the Gridtape when it is seen by the user in the pre-sectioning collection camera in `GridtapeCameras_EWH_220730.py`'s UI. This block of code waits 12 cycles (hard coded number of slots to the nose) and detects the position of the cutting cycle to stop cutting. It also reads the user input from the UI for "number of slots to skip". This helps ensure that the aperture is skipped. There is also the checkbox on the UI for "double skip" which is for the rare instance where there are two apertures that are bad. If this is checked, the program will avoid the first section and now this second section 12 apertures away. This should also result in print statments to the terminal that the current section is being skipped once cutting has stopped. Important, this code keeps the current synchronization and does not stop cutting mid-cut. The code then records how many sections have been cut (this is really how many cycles have gone through so it needs to be reset by the user once cutting starts using the reset checkbox in the UI) and displays that on the UI using `self.parent.textEdit_SectionNum.setHtml(str(self.parent.section_number))`. There is also a very the ability for the user to se the limit for cutting which is read and checked at `self.parent.section_number >= int(self.parent.textEdit_SectionLimit.toPlainText())`. If this is triggered the machine will stop using the same commands as before. Next the cutting duration and total cycle time are calculated using `self.LEICAcycle = cutDuration + self.parent.LEICAretractdurationlog.valuelog[-1]`. This cycle time will be printed in the terminal as well. Next the user offset is taken into consideration with the current cycle speeds of both the Leica and the ATUM to determine if the ATUM motors need to speed up or slow down (during the non-cutting phase of the Leica). `offset=self.upStateStart[-1]-self.parent.ATUMchopperlog.upStateStart[-1]` measures the current offset by substrating the start of light being on in the Leica chopper and the light being on in the ATUM chopper. If the user has the checkbox for "synchronize" checked then the program will compare the aformentioned offset number with the user UI input offset. Depending on if the tape needs to speed up or slow down the necessary action will be printed in the terminal as "tape speed up" or "tape slow down". Or if the actual offset and the user defined offset and within 0.4 it will print "in sync". There is also the variable "af" which is the adjustment factor. This is another user definable parameter from the UI. If the corresponding spinbox is check then the user can change the how fast the tape will move when needed `self.parent.setTapeSpeed(BaseSpeed + 0.03*af)`. Note: this is a multiplicative adjustment so changed do not need to be very high to have a large impact. But the higher the number the harder it will be actually acheieve synchronization, but it can be useful if the offset is very far off for example when first starting the machine or during a tape change. The overall offset will also be printed in the terminal.         
    
Users may also notice a lot of comments referring to a "virtual mode" which is a testing setting to ensure the system is working over thousands of iterations (as a single real sections takes 16 seconds it would take hours to robustly test this otherwise). It is not recommended to work with virtual mode unless the user is very well versed with the code. There is a high probability of breaking the script when working in virtual mode, and several files are missing the Github repository to run virtual mode out of the box. 

### LeicaCamWater.py

`LeicaCamWater.py` requires the scripts 
1. AGTUMconfigparser.py
2. paintableqlabel.py
3. syringepump.py
4. valuelogger.py

When running the `LeicaCamWater.py` script in a terminal it will first load the configration `DefaultConfig_win-3rdCam_-Water.cfg` and UI file `LeicaCam_Window.ui`. It will also load in the last "saved" ROI for measuring the water level. There is no actual save button or feature, but if the program is exited out off normally it will also save the location of the box in the current video feed from the Leica. The thread for running the video feed form the Lecia is made and started `self.CamTH = Thread(self)` and `self.CamTH.start()`. The function `self.paintableCam` is also created by feeding `self.cam_knife` into `paintableqlabel`. The main UI for LeicaCamWater is then displayed on the screen. 

In the class `Thread()` the function `run` starts the paintableqlabel and video feed from the Leica using CV2. As the user clicks and drags a box along the paintableqlabel in the UI it record the position in ROIXbeg, ROIXend, ROIYbeg, and ROIYend. The "waterlevel" which is will be used throughout the `waterlevellog` is determined here `self.parent.waterlevellog.waterlevel=np.mean(frame[ROIYbegin:ROIYend,ROIXbegin:ROIXend])` where the mean of the pixels is calculated. The change in the mean of the pixels reflects the change in the amount of light reflecting off the water as it evaporates. There is also a feature in this class where if the user has selected the spinbox for "Screen Lock" the ROI will not be changed even if a new box is drawn (this is to prevent an accident where someone clicks in the UI and ruins the sectioning run). The numbers for the ROI positions are then written into variables in `mainGUI`, ROIXbegin, ROIXend, ROIYbegin, ROIYend where they will also be saved to the config file at the end.   

Upon the user presseing **START** in the UI, `self.startCams` is called which calls `self.waterlevellog.start()`. Don't be confused by the other fucntions called `self.startCam` which is supposed to restart the camera if it freezes by user pushbuttom input on the UI. The class `waterlevellog` is the main functionality of the script with the decisions to pump or not calculated in the function `datacollector()`. It first updates the log with the current water level `self.updateLog(self.waterlevel)`. It next determines what the maximum waterlevel was over the time it take to complete a Leica cycle (this is user input in the UI). This is important, because the pump way pump too much or too long if it tries to read multiple times during one cutting cycle, this maximum is then displayed in the UI:  `self.parent.DisplayCurrentMax.setHtml(str(round(np.max(self.valuelog[(-1*self.counter_iters_pump):-1]),2)))`. The rest of the code will only be run if the user has checked the spinbox for "Pump ON". This is checked using this line of code: `self.parent.cbx_pumpOn.isChecked()`. The next few lines of code are used to determine if the pump has attempted to pump 4 times in a row, this is a safety valve to prevent overflow if something is not right and alert the user to this issue. Next are a few lines where the pump is reset if there is a problem with over pumping or the water level is already too high about the high threshold (set by user in UI). This will set the background of the "Pump" button to yellow. The color code is as follows: 
* Yellow = Pump on but not pumping 
* Green = pump on and actively pumping
* Red = Error: user must see notification as to specific water level issue
The next lines of code are checking if the water level has reached the desired level over the past 4 Leica cutting cycles. If it failed to reach that level then it goes into the Error state and will prevent pumping for a hard coded amount of time (60 seconds) and until that time is reached it will not allow the pump to go into the code for checking if it needs to pump `if round((current_time - self.warning_timer),1) > 60 or self.warning_active == False:`. If it is not in the warning state, then the function measures the max of the water level from the current moment to all the iterations back for a single Leica cutting cycle `np.max(self.valuelog[(-1*self.counter_iters_pump):-1])` and compares that the user defined level and threshold range. If it is less than then the script will determine by how much it is under and pump more or less water accordingly. It will also keep track of how many time it has done this for the error catching `self.entered_under == 0`. Currently the amount of time for pumping is the difference between the threshold and the actual max of the water level, *self.threshold_dif*, divided by 4. This works for the Diatome Maxi boats, but may not be ideal for your setup. It is best however to change the amount pumped at the level of the syringe interface at the syringe hardware instead of in the code here. The pump is then triggered to pump using `Pump.trigger_pump()` and will print "Pump: pumping..." in the terminal during the pump.  

### GridtapeCameras.py
`GridtapeCameras.py` requires the scripts 
1. AGTUMconfigparser.py
2. valuelogger.p

Run the script GridtapeCameras.py in a terminal and that should load the config file `DefaultConfig_win-cameras.cfg` and the UI file `PyAGTUM_cams_window.ui` and open the GUI. The overall layout of this script is nearly identical to `PyAGTUM_210126_SkipCut_EWH.py`. The main difference is in `mainGUI()`, the function `self.SetupHardware()` now has the `PreCamTimer` and `PostCamTimer` for the two cameras where settings for the cameras can be changed. However, changing these settings may make seeing the section in the post sectioning camera difficult to see. In `PreCamTimer` there is commented out code for adding a barcode reader to get the exact section number, but this functionallity causes the computer to run slow and freeze. `PostCamTimer` has functionality for measuring the tape speed using computer vision that has been commented out. This could be brough back by users with presumably little issue. 

### hardwareUI.py 
`hardwareUI.py` requires the scripts: 
1. xyzStageCmds.py
2. atumCmds_2.py
3. leicaCmds.py

This GUI uses tkinter to form the main window and widgets. Most of the code is setting this up and many of the features in this script are not used (for example, moving the Leica stage or starting the ATUM). Those features have been moved to `PyAGTUM.py`. The important functions are those that call functions from xyzStageCmds which is `Stages` in this script. An important function is `updateReadouts()` which updates all stage positions in the XYZ stage. There are specific functions that get called when pressed by the user in the UI which will stow, `clkStagesStow()`, set the pickup (sectioning) location, `clkStagesSetPickup`, move to the pickup location, `clkStagesMoveToPickup`, and importantly park the stage which will not allow the user to move the stage until they "unpark" the stage by clicking the button again, `clkStagesParking()`. This can prevent accidental movements while sectioning. There are also "move" and "jog" features that are utalized in the UI as the user can move to a specific location or jog a specific distance.   


## Getting Started: 
---

A rough guide for setting up the hardware for this system can be found here: 

* Set up Guide: `Seung Lab - ATUM_Leica Hardware Setup Rough Guide`
* CAD Files can be found in the repo as well in the "AGTUM Hardware" folder. 

Once set up, see our walk through for setting up a collection run: 

* Tutorial and Running the ATUM: `Seung Lab - ATUM SS Manual Pictures.pdf`
