import sys
import os
import rogue.utilities
import rogue.utilities.fileio
import rogue.interfaces.stream
import pyrogue    
import time
from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import *
from PyQt4.QtCore import QObject, pyqtSignal
import numpy as np
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

class Window(QtGui.QMainWindow, QObject):
    processMonitoringFrameTrigger = pyqtSignal()
    monitoringDataTrigger = pyqtSignal()

    def __init__(self):
        super(Window, self).__init__()    
        self.mainWdGeom = [50, 50, 720, 600] # x, y, width, height
        self.setGeometry(self.mainWdGeom[0], self.mainWdGeom[1], self.mainWdGeom[2],self.mainWdGeom[3])
        self.setWindowTitle("CHESS2 viewer")
        self.numProcessFrames  = 0
        self.eventReaderMonitoring= EventReader(self)
  
        #self.processMonitoringFrameTrigger.connect(self.eventReader)
        self.processMonitoringFrameTrigger.connect(self.eventReaderMonitoring._processFrame)
        self.monitoringDataTrigger.connect(self.displayMonitoringDataFromReader) 

        self.eventReaderMonitoring.ProcessFramePeriod = 1
        self.prepairWindow()
        self.show()

    def displayMonitoringDataFromReader(self):
       # print("slave frame1: ",self.getFrameCount())
        rawData=self.eventReaderMonitoring.frameDataMonitoring
        if (len(rawData)==0):
            print("no raw data")
            return False
        else:
            print("Header: ",rawData)
    def prepairWindow(self):
        self.imageScaleMax = int(10000)
        self.imageScaleMin = int(-10000)
        screen = QtGui.QDesktopWidget().screenGeometry(self)
        size = self.geometry()
        self.buildUi()
       # self.fig = Figure(figsize=(width, height), dpi=dpi)
        #self.mainWdGeom = [50, 50, 1100, 920] # x, y, width, height
    def buildUi(self):
        self.mainImageDisp = MplCanvas(MyTitle = "CHESS2 Hitmap")
        self.mainWidget = QtGui.QWidget(self)
        vbox1 = QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignTop)
        #vbox1.addWidget(self.label,  QtCore.Qt.AlignTop)
        vbox1.addWidget(self.mainImageDisp,  QtCore.Qt.AlignTop)
        hbox = QHBoxLayout(self.mainWidget)
        hbox.addLayout(vbox1)
        self.mainWidget.setFocus()        
        self.setCentralWidget(self.mainWidget)
        
        plt.show()
    def center(self):
        screen=QtGui.QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2)
class EventReader(rogue.interfaces.stream.Slave):
    """retrieves data from a file using rogue utilities services"""

    def __init__(self, parent) :
        rogue.interfaces.stream.Slave.__init__(self)
        super(EventReader, self).__init__()
        self.enable = True
        self.numAcceptedFrames = 0
        self.numProcessFrames  = 0
        self.lastFrame = rogue.interfaces.stream.Frame
        self.frameDataMonitoring = bytearray()
        self.frameDataArray = [bytearray(),bytearray(),bytearray(),bytearray()] # bytearray()
        self.parent = parent


    def _acceptFrame(self,frame):
        print("Frame count: ",self.getFrameCount())
        self.lastFrame = frame
        p = bytearray(self.lastFrame.getPayload())
        print("payload:",p)
        #self.mainImageDisp.update_plot(p)
        print("payload size:",len(p))
        buffer_size=self.lastFrame.getSize()
        print("buffer size: ", buffer_size)     
       # p = self.lastFrame.getPayload()
        self.frameDataArray[self.numAcceptedFrames%4][:] = p#bytearray(self.lastFrame.getPayload())
        self.numAcceptedFrames += 1
    #    for i in range(len(p)):
    #        print("payload :", bin(p[i]) )
    #    self.parent.processMonitoringFrameTrigger.emit()
        print("slave frame: ",self.getFrameCount())
    def _processFrame(self):
        index = self.numProcessFrames%4
        self.numProcessFrames += 1
        #print("in the process...")
        p = self.frameDataArray[index] 
        self.frameDataMonitoring[:] = p
        self.parent.monitoringDataTrigger.emit()

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=11, height=9, MyTitle=""):
        #self.fig,self.axes=plt.subplots(figsize=(11,9))
        fig = Figure(figsize=(width, height))
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.MyTitle = MyTitle
        self.axes.set_title(self.MyTitle)
        fig.cbar = None
        self.axes.set_axis_off()
        self.chess2_point=[(87.9,108),(20228,108),(24300,108),(24300,18517),(24300,18517),(20227,18517),(87.9,18517),(87.9,13413),(87.9,13138),(87.9,8034),(87.9,5212),(20227,5212),(20227,8034),(20227,13138),(20227,13413)]
        self.compute_initial_figure()

    def compute_initial_figure(self):
        #if one wants to plot something at the begining of the application fill this function.
        for i in range(9):
            self.axes.plot([self.chess2_point[i][0],self.chess2_point[i+1][0]],[self.chess2_point[i][1],self.chess2_point[i+1][1]],'k')
        self.axes.plot([self.chess2_point[0][0],self.chess2_point[9][0]],[self.chess2_point[0][1],self.chess2_point[9][1]],'k')
        self.axes.plot([self.chess2_point[1][0],self.chess2_point[5][0]],[self.chess2_point[1][1],self.chess2_point[5][1]],'k')
        for i in range(7,12,1):
            self.axes.plot([self.chess2_point[i][0],self.chess2_point[21-i][0]],[self.chess2_point[i][1],self.chess2_point[21-i][1]],'k')

        self.draw()
    def update_plot(self, *args):
        




































