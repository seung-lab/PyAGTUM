#!/usr/bin/env python
"""
Copyright (C) 2017 Allen Institute for Brain Science
This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License Version 3
as published by the Free Software Foundation on 29 June 2007.
This program is distributed WITHOUT WARRANTY OF MERCHANTABILITY OR FITNESS
FOR A PARTICULAR PURPOSE OR ANY OTHER WARRANTY, EXPRESSED OR IMPLIED.
See the GNU General Public License Version 3 for more details.
You should have received a copy of the GNU General Public License along
with this program. If not, see http://www.gnu.org/licenses/

Get/Set ptpc and atum commands for ATUM 2.0

"""
import os
import sys
import time
import logging
import leicaCmds as leica
#import serial
#from serial import Serial
from ctypes import *
try:
    import configGlobal as cfg
except Exception as e:
    class Foo(dict):  # built-ins can't have attributes!
        pass
    cfg = Foo()
    cfg.log_dir = ''
    cfg.specimen_and_media = 'test_0000'

# use the default logger for system messages and events
rmc_log_format = '%(levelname)s -- %(asctime)s -- %(message)s'
rmc_log_file = os.path.join(cfg.log_dir, cfg.specimen_and_media + '_RMC.txt')
logging.basicConfig(filename=rmc_log_file, format=rmc_log_format, level=logging.INFO)
logging.info('Startup atumcmds_2.py ------------------------------------------------------')


RMC_path = r"C:\dev\pyATUMpni\RMCDlls\x64"
if sys.flags.debug:
    rmc_dll = r"RMCFuncsDll.dll"
else:
    rmc_dll = r"RMCFuncsDll.dll"

sys.path.append(RMC_path)
dll_path = os.path.join(RMC_path, rmc_dll)

class RMCFuncsDll(object):
    """
    Hooks onto the C++ DLL.  These are all the foreign functions we are going to be using
        from the dll, along with their arguments types and return values.
    """
    print(dll_path)
    _RMCFuncsDll = cdll.LoadLibrary(dll_path)

    #InitATUMDevice = _RMCFuncsDll.InitATUMDevice
    InitATUMDevice = getattr(_RMCFuncsDll, "?InitATUMDevice@ATUMFuncs@RMCFuncs@@SA_NXZ")
    InitATUMDevice.argtypes = None
    InitATUMDevice.restype = c_uint32

    #CloseATUMDevice = _RMCFuncsDll.CloseATUMDevice
    CloseATUMDevice = getattr(_RMCFuncsDll, "?CloseATUMDevice@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    CloseATUMDevice.argtype = None
    CloseATUMDevice.restype = c_uint32

    #StartATUMDevice = _RMCFuncsDll.StartATUMDevice
    StartATUMDevice = getattr(_RMCFuncsDll, "?StartATUMDevice@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    StartATUMDevice.argtypes = None
    StartATUMDevice.restype = c_uint32

    #StopATUMDevice = _RMCFuncsDll.StopATUMDevice
    StopATUMDevice = getattr(_RMCFuncsDll, "?StopATUMDevice@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    StopATUMDevice.argtypes = None
    StopATUMDevice.restype = c_uint32

    #SetTapeSpeed = _RMCFuncsDll.SetTapeSpeed
    SetTapeSpeed = getattr(_RMCFuncsDll, "?SetTapeSpeed@ATUMFuncs@RMCFuncs@@SA_NN@Z")    
    SetTapeSpeed.argtypes = [c_double]
    SetTapeSpeed.restype = c_uint32

    #SetTapeTension = _RMCFuncsDll.SetTapeTension
    SetTapeTension = getattr(_RMCFuncsDll, "?SetTapeTension@ATUMFuncs@RMCFuncs@@SA_NI@Z")    
    SetTapeTension.argtypes = [c_uint32]
    SetTapeTension.restype = c_uint32

    #StartTapeTensionMotor = _RMCFuncsDll.StartTapeTensionMotor
    StartTapeTensionMotor = getattr(_RMCFuncsDll, "?StartTapeTensionMotor@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    StartTapeTensionMotor.argtypes = None
    StartTapeTensionMotor.restype = c_uint32

    #StopTapeTensionMotor = _RMCFuncsDll.StopTapeTensionMotor
    StopTapeTensionMotor = getattr(_RMCFuncsDll, "?StopTapeTensionMotor@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    StopTapeTensionMotor.argtypes = None
    StopTapeTensionMotor.restype = c_uint32

    #StartATUMTopMotor = _RMCFuncsDll.StartATUMTopMotor
    StartATUMTopMotor = getattr(_RMCFuncsDll, "?StartATUMTopMotor@ATUMFuncs@RMCFuncs@@SA_N_N@Z")    
    StartATUMTopMotor.argtypes = [c_uint32]  # bool forward
    StartATUMTopMotor.restype = c_uint32

    #StopATUMTopMotor = _RMCFuncsDll.StopATUMTopMotor
    StopATUMTopMotor = getattr(_RMCFuncsDll, "?StopATUMTopMotor@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    StopATUMTopMotor.argtypes = None
    StopATUMTopMotor.restype = c_uint32

    #StartATUMBottomMotor = _RMCFuncsDll.StartATUMBottomMotor
    StartATUMBottomMotor = getattr(_RMCFuncsDll, "?StartATUMBottomMotor@ATUMFuncs@RMCFuncs@@SA_N_N@Z")    
    StartATUMBottomMotor.argtypes = [c_uint32] # bool forward
    StartATUMBottomMotor.restype = c_uint32

    #StopATUMBottomMotor = _RMCFuncsDll.StopATUMBottomMotor
    StopATUMBottomMotor = getattr(_RMCFuncsDll, "?StopATUMBottomMotor@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    StopATUMBottomMotor.argtypes = None
    StopATUMBottomMotor.restype = c_uint32

    #GetTapeSpeed = _RMCFuncsDll.GetTapeSpeed
    GetTapeSpeed = getattr(_RMCFuncsDll, "?GetTapeSpeed@ATUMFuncs@RMCFuncs@@SANXZ")    
    GetTapeSpeed.argtypes = None
    GetTapeSpeed.restype = c_double

    #GetTapeTensionReading = _RMCFuncsDll.GetTapeTensionReading
    GetTapeTensionReading = getattr(_RMCFuncsDll, "?GetTapeTensionReading@ATUMFuncs@RMCFuncs@@SAIXZ")    
    GetTapeTensionReading.argtypes = None
    GetTapeTensionReading.restype = c_uint32

    #CheckIfRunning = _RMCFuncsDll.CheckIfRunning
    CheckIfRunning = getattr(_RMCFuncsDll, "?CheckIfRunning@ATUMFuncs@RMCFuncs@@SA_NXZ")    
    CheckIfRunning.argtypes = None
    CheckIfRunning.restype = c_uint32

    # retain the state of certain values
    cutting = False

# # init the DLL i/f to the ATUM

logging.info('Atum Initialized: ' + str(RMCFuncsDll.InitATUMDevice()))

#init the serial port/USB i/f to the microtome
# ser = serial.Serial(PORT, 115200, timeout=2)
# ser = Serial(PORT, 115200, timeout=2)

#ser.write("".encode()) # get the Bii> prompt


def ptStart():
    print('ptStart: No RMC microtome')
    return
    #start the machine cutting#
    if not RMCFuncsDll.cutting:
        _writeline(r'toglcut')
        val = _readline(just_newline=False)
        val = _readline(just_newline=False)
        RMCFuncsDll.cutting = True
    else:
        sout = 'ptStart when already cutting'
        print(sout)
        logging.error(sout)

def ptStop():
    print('ptStop: No RMC microtome')
    return
    #stop the machine cutting#
    if RMCFuncsDll.cutting:
        _writeline(r'toglcut')
        val = _readline(just_newline=False)
        val = _readline(just_newline=False)
        RMCFuncsDll.cutting = False
    else:
        sout = 'ptEnd when not cutting'
        print(sout)
        logging.error(sout)


def Start():
    ok1 = RMCFuncsDll.StartATUMDevice()
    return ok1

def Stop():
    ''' stop the ATUM motors '''
    ok1 = RMCFuncsDll.StopATUMDevice()
    return ok1

def Reverse():
    ''' start the ATUM motors '''
    ok1 = RMCFuncsDll.StartATUMTopMotor(False)
    ok2 = RMCFuncsDll.StartATUMBottomMotor(True)
    ok3 = RMCFuncsDll.StartTapeTensionMotor()
    return ok1 and ok2 and ok3


# get commands ---------------------------------------------


def gRS():
    #get retract speed#
    val=leica.getReturnSpeed()
    val=leica.getReturnSpeed()
    val = float(val)
    return val


def gTS():
    ''' get tape speed '''
    val = RMCFuncsDll.GetTapeSpeed()
    return val

def gTT():
    ''' get tape tension '''
    val = RMCFuncsDll.GetTapeTensionReading()
    # corrects for inverse relationship between tension and value of encoder. Sets positive tension from 0 to 100
    # as encoder max tension  = 2500 and min = 4000
    val = (4100 - val)/15
    return val


def gCS():
    #get cut speed#
    val=leica.getCuttingSpeed()
    val = float(val)
    return val

def gST():
    #get section thickness#
    val = leica.getFeedRate()  
    val = float(val)
    return val

def gEP():
    #get rotary encoder position#
    val = leica.getHandwheelPosition()
    val = float(val)
#    val = 0  # debugging line, be sure to delete and enable above line!
    return val

# set functions require an input var -----------------------------


def sADC(adc=False):
    print('sADC: no RMC microtome.')
    return;
    #set ActiveBlockDuringCut. True means motor on during cut window.#
    if adc:
        val = 1
    else:
        val = 0
    _writeline('ADC {}'.format(val))
    val = _readline(just_newline=False)
    val = _readline(just_newline=False)
    return val

def sRS(retractSpeed):
    #set retract speed in mm/s, example = 10.0#
    val=leica.setReturnSpeed(int(retractSpeed*1000.0))
    val = float(val)
    return val


def sTS(tapeSpeed):
    ''' set tape speed in mm/s, example = 0.2 '''
    ok = RMCFuncsDll.SetTapeSpeed(tapeSpeed)
    return ok

def sTT(tapeTension):
    tapeTension = int(4100-tapeTension*15) # corrects for hardware inverse relationship between tension and value of reading
    ok = RMCFuncsDll.SetTapeTension(tapeTension)
    return ok



def sCS(cutSpeed):
    #set cut speed in mm/s, example = 0.2#
    val=leica.setCuttingSpeed(int(cutSpeed*1000.0))
    return val

def sST(sectionThick):
    #set section thickness in nm#
    val=leica.setFeedRate(sectionThick)
    return val

def get_total_advance():
    print('get_total_advance: no RMC microtome.')
    return;
    #get total forward movement#
    _writeline('rtotadv')
    val = _readline()
    val = _readline()
    val = float(val)
    return val

def set_cut_window_top(cw):
    print('set_cut_window_top: no RMC microtome.')
    return;
    #set top of cut window#
    _writeline('sucwinf {}'.format(cw))
    val = _readline()
    val = _readline()
    return val

def get_cut_window_top():
    print('get_cut_window_top: no RMC microtome.')
    return;
    # get top of cut window #
    _writeline('rucwinf')
    val = _readline()
    val = _readline()
    val = float(val)
    return val

def get_cut_window_bottom():
    print('get_cut_window_bottom: no RMC microtome.')
    return;
    # get bottom of cut window #
    _writeline('rlcwinf')
    val = _readline()
    val = _readline()
    val = float(val)
    return val

def set_cut_window_bottom(cw):
    print('set_cut_window_bottom: no RMC microtome.')
    return;
    # set bottom of cut window #
    _writeline('slcwinf {}'.format(cw))
    val = _readline()
    val = _readline()
    return val

def step(forward=True):
    print('step: no RMC microtome.')
    return;
    # step microtome forward or back #
    if forward:
        _writeline('stepfwd')
    else:
        _writeline('stepbac')
    val = _readline(just_newline=False)
    val = _readline(just_newline=False)
    return val

def floor_light():
    print('floor_light: no RMC microtome.')
    return;
   # toggle the floor lamp on or off #
    _writeline(r'floorlt')
    val = _readline(just_newline=True)

def flood_light():
    print('flood_light: no RMC microtome.')
    return;
    # toggle the flood lamp on or off #
    _writeline(r'floodlt')
    val = _readline(just_newline=True)

def status():
    print('status: no RMC microtome.')
    return;
    # get the machine status #
    _writeline('rstatus')
    val = _readline()
    val = _readline()
    return val

def reset():
    print('reset: no RMC microtome.')
    return;
    # reset the microtome #
    _writeline('ssreset')
    val = _readline()
    return val

def get_linear_encoder_position():
    print('get_linear_encoder_position: no RMC microtome.')
    return;
    # the actual position (not the command)#
    _writeline('pos')
    val = _readline()
    val = _readline()
    val = float(val)
    return val

def set_linear_encoder_position(pos):
    print('set_linear_encoder_position: no RMC microtome.')
    return;
    # set the actual position of the linear encoder#
    _writeline('move {}'.format(pos))
    val = _readline(just_newline=True)
    return val


#def _writeline(val):
#    ''' write to the microtome '''
#    ser.write((val + '\r').encode())

#def _readline(just_newline=False):
#    ''' Crap.  Different commands have different formatting:
#    - sometimes just '\n',
#    - sometimes '\n'ReturnValue'\r'

'''
    return ser.readline()

    eol = b'\r'
    leneol = len(eol)
    line = bytearray()
    while True:
        c = ser.read(1)
        if c:
            if c == b'\n':
                if just_newline:
                    return ''
                continue # ignore it
            if c == eol:
                break
            line += c
        else:
            break
    return str(bytes(line))
'''

if __name__ == '__main__':
    import unittest


    class TestATUM2(unittest.TestCase):
        ''' ATUM2 tests'''

        def test_microtome_reset(self):
            ''' reset the microtome'''
            reset()

        def test_atum(self):
            ''' test basic atum functions '''
            val = RMCFuncsDll.CheckIfRunning()
            print('CheckIfRunning: {}'.format(val))
            atumStart()
            val = RMCFuncsDll.CheckIfRunning()
            print('CheckIfRunning: {}'.format(val))
            time.sleep(2.0)
            atumStop()

        def test_microtome(self):
            ''' test basic microtome functions'''

            # test status
            print('status: {}'.format(status()))
            print('status: {}'.format(status()))

            # test retract speed
            val = gRS()
            val = gRS()
            val = sRS(val)
            val = sRS(val)
            
            print('gRS: {}'.format(val))
            print('sRS: {}'.format(sRS(val+2)))
            val2 = gRS()
            print('gRS: {}'.format(val2))
            print('sRS: {}'.format(sRS(val)))
            val2 = gRS()
            self.assertEqual(val, gRS())

            # test section thickness
            val = gST()
            print('gST: {}'.format(val))
            print('sST: {}'.format(sST(40)))
            val2 = gST()
            print('gST: {}'.format(val2))
            self.assertEqual(val2, gST())

            # try setting section thickness to zero
            print('sST: {}'.format(sST(0)))
            val2 = gST()
            print('gST: {}'.format(val2))
            # bugbug, the following should be True
            # self.assertEqual(val2, 0)

            # test cut speed
            print('gCS: {}'.format(gCS()))

            # test rotary encoder position
            print('gEP: {}'.format(gEP()))

            print('get_linear_encoder_position: {}'.format(get_linear_encoder_position()))
            print('get_total_advance: {}'.format(get_total_advance()))

            step(True)
            step(False)

            # turn on the lights and cut
            floor_light()
            flood_light()
            ptStart()
            time.sleep(3)
            ptStop()
            flood_light()
            floor_light()

        def test_Backlash(self, nSteps=20):
            ''' step back then forward, measuring the start and end linear encoder position '''
            sST(40)
            for index in range(nSteps):
                start_pos = get_linear_encoder_position()
                for steps in range(index):
                    step(forward=True)
                    time.sleep(1)
                for steps in range(index):
                    step(forward=False)
                    time.sleep(1)
                end_pos = get_linear_encoder_position()
                logging.info('steps: , {}, start: , {}, end:, {}'.format(index, start_pos, end_pos))

        def test_LinearEncoder(self, steps=10000, forward=True):
            ''' test linear encoder advance '''

            sST(40)
            logging.info('starting test_LinearEncoder: steps: {}, forward: {}'.format(steps, forward))
            for index in range(steps):
                val = get_total_advance()
                pos = get_linear_encoder_position()
                logging.info('{}, {}, {}'.format(index, val, pos))
                step(forward)
                time.sleep(1.0)
                status()

        def test_LinearEncoderReverse(self, steps=25000):
            self.test_LinearEncoder(steps, False)

        def test_LinearEncoderLoop(self, steps=200, forward=True, nLoops=3):
            ''' test linear encoder advance, looping over the same point '''
            sST(40)
            for loop in nLoops:
                reset()
                logging.info('starting test_LinearEncoder: steps: {}, forward: {}, loop: {}'.format(steps, forward, loop))
                for index in range(steps):
                    val = get_total_advance()
                    pos = get_linear_encoder_position()
                    logging.info('{}, {}, {}'.format(index, val, pos))
                    step(forward)
                    time.sleep(1.0)
                    status()



        def test_LinearEncoderStepOnly(self, cuts=25000):
            ''' test linear encoder advance, while cutting '''
            sADC(adc=False)
            sST(40)
            sRS(40) # mm/sec
            sCS(10.0)
            set_cut_window_top(450)
            set_cut_window_bottom(550)
            #ptStart()
            cut_total = 0
            rot_last = gEP()
            cut_window_top = get_cut_window_top()
            cut_window_bottom = get_cut_window_bottom()
            enable_cut_window_top = True
            enable_cut_window_bottom = True
            linear_encoder_at_cut_window_top = 0
            linear_encoder_at_cut_window_bottom = 0

            while cut_total < cuts:
                rot = 0
                lin = get_linear_encoder_position()
                adv = get_total_advance()

                linear_encoder_at_cut_window_top = lin
                linear_encoder_at_cut_window_bottom = lin

                step(True)

                logging.info('loop, {}, adv, {}, rot, {}, lin, {}, lin_at_cwt, {},  lin_at_cwb, {},'.format(cut_total, adv, rot, lin, 
                                        linear_encoder_at_cut_window_top, linear_encoder_at_cut_window_bottom))
                time.sleep(1.0)
            #ptStop()

        def test_LinearEncoderLoopCutting(self, cuts=25000):
            ''' test linear encoder advance, while cutting '''
            sADC(adc=False)
            sST(40)
            sRS(40) # mm/sec
            sCS(10.0)
            set_cut_window_top(450)
            set_cut_window_bottom(550)
            ptStart()
            cut_total = 0
            rot_last = gEP()
            cut_window_top = get_cut_window_top()
            cut_window_bottom = get_cut_window_bottom()
            enable_cut_window_top = True
            enable_cut_window_bottom = True
            linear_encoder_at_cut_window_top = 0
            linear_encoder_at_cut_window_bottom = 0

            while cut_total < cuts:
                rot = gEP()
                lin = get_linear_encoder_position()
                adv = get_total_advance()

                if enable_cut_window_top and rot > cut_window_top:
                    enable_cut_window_top = False
                    linear_encoder_at_cut_window_top = lin
                if enable_cut_window_bottom and rot > cut_window_bottom:
                    enable_cut_window_bottom = False
                    linear_encoder_at_cut_window_bottom = lin

                if rot < rot_last: # zero crossing
                    cut_total += 1
                    enable_cut_window_top = True
                    enable_cut_window_bottom = True
                    #step(False)
                rot_last = rot

                logging.info('loop, {}, adv, {}, rot, {}, lin, {}, lin_at_cwt, {},  lin_at_cwb, {},'.format(cut_total, adv, rot, lin, 
                                        linear_encoder_at_cut_window_top, linear_encoder_at_cut_window_bottom))
                #time.sleep(0.1)
            ptStop()
            
    def get_suite():
        ''' return the list of tests to run '''
        suite = unittest.TestSuite()
        # suite.addTest(TestATUM2('test_atum'))
        #suite.addTest(TestATUM2('test_microtome_reset'))
        #suite.addTest(TestATUM2('test_microtome'))
        # suite.addTest(TestATUM2('test_LinearEncoder'))
        # suite.addTest(TestATUM2('test_LinearEncoderLoop'))
        # suite.addTest(TestATUM2('test_Backlash'))
        suite.addTest(TestATUM2('test_LinearEncoderStepOnly'))
        # suite.addTest(TestATUM2('test_LinearEncoderLoopCutting'))
        #suite.addTest(TestATUM2('test_LinearEncoderReverse'))
        return suite

    try:
        unittest.TextTestRunner().run(get_suite())
        print('done testing ATUM.')
    except Exception as e:
        pass

  
   