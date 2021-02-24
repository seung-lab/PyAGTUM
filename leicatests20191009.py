# -*- coding: utf-8 -*-
"""
Created on Wed Oct  9 11:02:15 2019

@author: jprice
"""
from leicaCmds import *
import matplotlib
import numpy as np
import mplcursors

x=[];
returnspeed=[];
response=[]


targetspeed=2500
setReturnSpeed(targetspeed)
[speed,resstr]=getReturnSpeed()
print(speed)
time.sleep(0.1)
#for iter in range(0,2000,1):
#    x.append(time.time());
#    [speed,resstr]=getReturnSpeed(); 
#    returnspeed.append(speed);
#    response.append(resstr)
#
#    if not np.abs(speed-iter)<1.0:
#        errors.append(resstr)
#    
#    pos=getHandwheelPosition();
#    handwheelpos.append(pos)

errors=[];
for iter in range(0,2000,20):
    x.append(time.time());
    setReturnSpeed(iter)
    [speed,resstr]=getReturnSpeed(); 
    returnspeed.append(speed);
    response.append(resstr)
    if not np.abs(speed-iter)<1.0:
        errors.append(resstr)
    time.sleep(0.1)
#
#
#
#errors=[];
#difference=[]
#for iter in range(0,2000):
#    difference.append(returnspeed[iter]-targetspeed)
#    if not np.abs(difference[iter])<1.0:
#        errors.append(response[iter])
#        print("{0}".format(returnspeed[iter]))
#    
#
#ind=next(x for x in range(difference.__len__()) if difference[x]==0);
#
#print("time: {0}".format(x[ind]-x[0]))
#
#set(errors)
#    
#
#
#matplotlib.pyplot.figure()
#matplotlib.pyplot.plot(difference)
#mplcursors.cursor()
#
#print(set(returnspeed))
#
##set([response[iter] for iter in range(response.__len__()) if 'FF' in response[iter]])
#
#set(handwheelpos)
#set(returnspeed)
#
#matplotlib.pyplot.figure()
#matplotlib.pyplot.plot(x,returnspeed)
#mplcursors.cursor()
#
#matplotlib.pyplot.figure()
#matplotlib.pyplot.plot(x,np.array(handwheelpos))
#mplcursors.cursor()



#returnspeed:
'!1420FF00CD6E92\r'
'!1420FF00CD8C74\r'
'!1420FF00CDC838\r'
'!1530FF00CDAA56\r'
'!1530FF03A9\r'
'!1531FF006457\r'
'!1540FF00AC\r'
'!1540FF01AB\r'
'!1540FF02AA\r'
'!1540FF03A9\r'    