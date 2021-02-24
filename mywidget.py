# -*- coding: utf-8 -*-
from pyqtgraph.Qt import QtCore, QtGui, QtWidgets

class mywidget(QtWidgets.QLabel):
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
        br = QtGui.QBrush(QtGui.QColor(100, 10, 10, 40))  
        qp.setBrush(br)   
        qp.drawRect(QtCore.QRect(self.begin, self.end))  
#        print("paintEvent")
        if (not event):
            self.update()
#            print("updated")

    def mousePressEvent(self, event):
        self.begin = event.pos()
#        self.end = event.pos()
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
#        self.begin = event.pos()
        self.end = event.pos()
        self.update()