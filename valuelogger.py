"""

EWH - used to start a thread for a specific valuelogger. 

"""

from datetime import datetime
import os
import time
from PyQt5 import QtCore
        
def isnan(num):
    return num != num

class valuelogger(QtCore.QThread):
    timelog=None
    valuelog=None
    historylength=None
    logfile=None
    filebasepath=None
    filebasename=None
    fid=None
    parent=None
    def __init__(self, *args, **kwargs) :
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.Timer = QtCore.QTimer()
        self.Timer.moveToThread(self)

    def initiateTimer(self,timeout,filebasepath,filebasename,parent=None):
        self.timeout=timeout
        self.filebasepath=filebasepath
        self.filebasename=filebasename
        self.timelog=[]
        self.valuelog=[]
        self.parent=parent
        
    def run(self):#,timeout=1000):
# =============================================================================
#         if not (self.filebasename is None or self.filebasepath is None):
#              datestr=datetime.today().strftime('%Y%m%d%H%M%S')
#              self.logfile=os.path.join(self.filebasepath,self.filebasename + '_' + datestr + '.csv')
#              self.fid=open(self.logfile,'w')
# =============================================================================
        self.Timer.timeout.connect(self.datacollector)
        self.Timer.start(self.timeout)
        loop = QtCore.QEventLoop()
        loop.exec_()
                
    def updateLog(self,value,valtime=None):
        if valtime==None:
            valtime=time.time()
        self.timelog.append(valtime)
        self.valuelog.append(value)
        
        if self.parent.unit_test == True:
            self.historylength = 30
        
# =============================================================================
#         if not self.fid is None:
#              if not isnan(self.valuelog[-1]):
#                  if self.fid.closed:
#                      datestr=datetime.today().strftime('%Y%m%d%H%M%S')
#                      if not (self.filebasename is None or self.filebasepath is None):
#                          self.logfile=os.path.join(self.filebasepath,self.filebasename + '_' + datestr + '.csv')
#                          self.fid=open(self.logfile,'w')
#                  self.fid.write("{0},{1}\n".format(self.timelog[-1],self.valuelog[-1]))
# =============================================================================
        if len(self.timelog)>self.historylength:
# =============================================================================
#               if not self.fid is None:
#                    self.fid.close()
#                    if not (self.filebasename is None or self.filebasepath is None):
#                        datestr=datetime.today().strftime('%Y%m%d%H%M%S')
#                        self.logfile=os.path.join(self.filebasepath,self.filebasename + '_' + datestr + '.csv')
#                        self.fid=open(self.logfile,'w')
# =============================================================================

               # whenever it reaches historylength, save .csv, keep last 5, continue to log
              self.timelog.clear()
              self.valuelog.clear()
#              del self.timelog[:-10]
#              del self.valuelog[:-10]

        self.updateVis()

    def stopLog(self):
        self.Timer.stop()
        self.terminate()
        for istep in range(10):
            if not self.Timer.isActive():
                break;
            else:
                self.Timer.stop()
        
        if not self.fid is None:
            self.fid.close()
            
        self.timelog=[]
        self.valuelog=[]
        
    def updateVis(self):
        1;
        
    def datacollector(self):
        print("collecting data")
        1
        