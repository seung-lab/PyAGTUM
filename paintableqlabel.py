# -*- coding: utf-8 -*-

"""

EWH - I did not make this, but this is what is used for the LeicaWaterCam script
so that a user can draw the area they want to get the light reflection off the 
water from. 

"""
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

class paintableqlabel(QtWidgets.QLabel):
    modifierstate='drawnew'
    refpos=[]
    def __init__(self,parent,*args):
        super().__init__(parent,*args)
#        self.setGeometry(30,30,600,400)
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
#        self.show()

    def paintEvent(self, event):
        if not (not event):
            super().paintEvent(event)
        qp = QtGui.QPainter(self)
        br = QtGui.QBrush(QtGui.QColor(200,200, 10, 50))  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.begin, self.end))  
#        print("paintEvent")
        if (not event):
            self.update()
#            print("updated")

    def mousePressEvent(self, event):
        if event.button()==QtCore.Qt.MiddleButton:
            self.modifierstate='onthemove'
            self.refpos=event.pos()
        else:
            self.modifierstate='drawnew'
            self.begin = event.pos()
            self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        if self.modifierstate=='onthemove':
            newpos=event.pos()-self.refpos
            self.end = self.end+newpos
            self.begin = self.begin+newpos
            self.refpos=event.pos()
        else:
            self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.modifierstate=='onthemove':
            newpos=event.pos()-self.refpos
            self.end = self.end+newpos
            self.begin = self.begin+newpos
            self.refpos=event.pos()
        else:
            self.end = event.pos()
        self.update()