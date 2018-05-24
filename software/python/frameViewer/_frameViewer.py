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
import threading
from SCurveNP import *
#from SCurveNP_8hits_addDecode import *
class Window(QtGui.QMainWindow, QObject):
    processMonitoringFrameTrigger = pyqtSignal()
    monitoringDataTrigger = pyqtSignal()

    def __init__(self,system):
        super(Window, self).__init__()    
        self.mainWdGeom = [50, 50, 2000,840 ] # x, y, width, height
        self.setGeometry(self.mainWdGeom[0], self.mainWdGeom[1], self.mainWdGeom[2],self.mainWdGeom[3])
        self.setWindowTitle("CHESS2 viewer")
       # self.numProcessFrames  = 0
        self.eventReaderMonitoring= EventReader(self)
        self.raw_Data_frame=frame_data()
        #print("init self.raw_Data_frame") 
        #self.processMonitoringFrameTrigger.connect(self.eventReader)
        self.processMonitoringFrameTrigger.connect(self.eventReaderMonitoring._processFrame)
        self.skipFrames=10
        self.monitoringDataTrigger.connect(self.displayMonitoringDataFromReader) 
        self.timestamp=0
        self.eventReaderMonitoring.ProcessFramePeriod = 1
        self.prepairWindow()
        self.show()
        self.togetInterval_t=[0,0]
        self.interval_time=0
        self.system=system
        #global t 
        self.statusBar().showMessage("the speed of the data received")
    def add_timestamp_interval(self,time_stamp):
        self.togetInterval_t.append(time_stamp)
        self.togetInterval_t.remove(self.togetInterval_t[0])
    def get_interval_time(self):
        self.interval_time=self.togetInterval_t[1]-self.togetInterval_t[0]
        return self.interval_time

    def displayMonitoringDataFromReader(self):
       # print("slave frame1: ",self.getFrameCount())
        rawData=self.eventReaderMonitoring.frameDataMonitoring
        #print("rawData:",rawData)
        #print("rawData_size",len(rawData))
        size_rawData=len(rawData)
        header=rawData[0:40] 
        raw_Data=rawData[40:] 
        if (len(raw_Data)==0):
            print("no raw data")
            return False
        else:
            data=np.frombuffer(raw_Data,dtype='uint16')
            header=np.frombuffer(header,dtype='uint16') 
            self.timestamp,frame_size=decode_header(header)
            self.add_timestamp_interval(self.timestamp)
            #if self.togetInterval_t[0]!=0 and self.togetInterval_t[1]!=0:
            #    interval_time=self.get_interval_time()
           # self.timedifferent            
            for i in range(0,len(data)):
               # print(bin(pay_load_16_temp))
                self.raw_Data_frame.add_data("buffer",data[i],i)
            if self.eventReaderMonitoring.numAcceptedFrames%self.skipFrames==0:
                self.togetInterval_t=[0,0]
                print("updating frame",self.eventReaderMonitoring.numAcceptedFrames)
                self.mainImageDisp.update_hitmap(self.raw_Data_frame.hitmap_t2,self.raw_Data_frame.hitmap_t1,self.raw_Data_frame.hitmap_t0)
                self.side_1.update_effi_plot(self.raw_Data_frame.dvflag_M0,self.raw_Data_frame.mhflag_M0,self.raw_Data_frame.dvflag_M1,self.raw_Data_frame.mhflag_M1,self.raw_Data_frame.dvflag_M2,self.raw_Data_frame.mhflag_M2)
                #time_t=self.timestamp
                time_t=self.timestamp*(1.0/320000000)
                self.side_2.update_time_plot(time_t)
                self.raw_Data_frame=frame_data()
                 
#    def update_all_plot(self):
#        self.togetInterval_t=[0,0]
#        print("updating hitmap")
#        self.mainImageDisp.update_hitmap(self.raw_Data_frame.hitmap_t2,self.raw_Data_frame.hitmap_t1,self.raw_Data_frame.hitmap_t0)
#        self.side_1.update_effi_plot(self.raw_Data_frame.dvflag_M0,self.raw_Data_frame.mhflag_M0,self.raw_Data_frame.dvflag_M1,self.raw_Data_frame.mhflag_M1,self.raw_Data_frame.dvflag_M2,self.raw_Data_frame.mhflag_M2)
#        time_t=self.timestamp*(1.0/320000000)
#        self.side_2.update_time_plot(time_t)
#        self.t=threading.Timer(3.0,self.update_all_plot)
#        self.raw_Data_frame=frame_data()
#        
#        self.t.start() 
       # self.mainImageDisp.update_plot(p)
    def prepairWindow(self):
        self.imageScaleMax = int(10000)
        self.imageScaleMin = int(-10000)
        screen = QtGui.QDesktopWidget().screenGeometry(self)
        size = self.geometry()
        self.buildUi()

    def buildUi(self):

        self.mainImageDisp = MplCanvas_hitmap(MyTitle = "CHESS2 Hitmap")
        self.mainWidget = QtGui.QWidget(self)
    
        self.hitmap_accum= QtGui.QRadioButton("Accumulate the hitmap")  
        self.hitmap_accum.toggled.connect(self.hitmapAccumu)
        Acc_hitmap=QHBoxLayout()
        Acc_hitmap.addWidget(self.hitmap_accum)

        self.reset_image=QtGui.QPushButton("clear image")
        self.take_ref=QtGui.QPushButton("take ref hitmap")
        self.init_ref=QtGui.QPushButton("clear ref hitmap")
        self.reset_image.clicked.connect(self.reset_allimages) 
        self.take_ref.clicked.connect(self.take_refhitmap)
        self.init_ref.clicked.connect(self.init_refhitmap)
 
        vbox1 = QVBoxLayout()
        vbox1.setAlignment(QtCore.Qt.AlignTop)
        vbox1.addWidget(self.mainImageDisp,QtCore.Qt.AlignTop)
        hSubbox_l1=QHBoxLayout()
        hSubbox_l1.addWidget(self.init_ref)
        hSubbox_l1.addWidget(self.take_ref)

        hSubbox_l2=QHBoxLayout()
        hSubbox_l2.addWidget(self.reset_image)
        vbox1.addLayout(Acc_hitmap)
        vbox1.addLayout(hSubbox_l1)
        vbox1.addLayout(hSubbox_l2)
        self.mainImageDisp.initial_hitmap()



        self.side_1 = MplCanvas_effi_plot(MyTitle = "Efficiency")        
        self.side_2 = MplCanvas_effi_plot(MyTitle = "time distribution")        
        hSubbox1 = QHBoxLayout()
        hSubbox1.addWidget(self.side_1)
        hSubbox2 = QHBoxLayout()
        hSubbox2.addWidget(self.side_2)

        self.side_1.initial_effi_plot()
        self.side_2.initial_time_plot()
        vbox2 = QVBoxLayout()
        vbox2.addLayout(hSubbox2)
        vbox2.addLayout(hSubbox1)

        hbox = QHBoxLayout(self.mainWidget)
        hbox.addLayout(vbox1)
        hbox.addLayout(vbox2)
        self.mainWidget.setFocus()        
        self.setCentralWidget(self.mainWidget)
        
        plt.show()
        
    def center(self):
        screen=QtGui.QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2)
    def reset_allimages(self):
        self.mainImageDisp.initial_hitmap()
   
    def init_refhitmap(self):
        self.mainImageDisp.hitmap_ref0=np.zeros((self.mainImageDisp.nRows,self.mainImageDisp.nColumns))
        self.mainImageDisp.hitmap_ref1=np.zeros((self.mainImageDisp.nRows,self.mainImageDisp.nColumns))
        self.mainImageDisp.hitmap_ref2=np.zeros((self.mainImageDisp.nRows,self.mainImageDisp.nColumns))
 
    def take_refhitmap(self):
        self.mainImageDisp.ref=1
       
    def hitmapAccumu(self):
        if self.hitmap_accum.isChecked():
            self.mainImageDisp.hitmapAc=1
        else:
            self.mainImageDisp.hitmapAc=0
        
class EventReader(rogue.interfaces.stream.Slave):

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
        self.lastFrame = frame
        p = bytearray(self.lastFrame.getPayload())
        self.lastFrame.read(p,0)
        self.numAcceptedFrames += 1
        self.frameDataMonitoring[:]=p
        self.parent.monitoringDataTrigger.emit()

    def _processFrame(self):
   #     index = self.numProcessFrames%4
        self.numProcessFrames += 1
       # p = self.frameDataArray[index] 
        #self.frameDataMonitoring[:] = p
        self.parent.monitoringDataTrigger.emit()

class MplCanvas_hitmap(FigureCanvas):
    def __init__(self, parent=None, width=11, height=9, MyTitle=""):
        #self.fig,self.axes=plt.subplots(figsize=(11,9))
        self.fig = Figure(figsize=(width, height))
        self.axes = self.fig.add_subplot(111)
        self.ref=0
        plt.ion()
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        self.hitmapAc=0
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.MyTitle = MyTitle
        self.axes.set_title(self.MyTitle)
        #fig.cbar = None
        self.nRows=128
        self.nColumns=32
        self.axes.set_axis_off()
        self.chess2_point=[(87.9,108),(20228,108),(24300,108),(24300,18517),(24300,18517),(20227,18517),(87.9,18517),(87.9,13413),(87.9,13138),(87.9,8034),(87.9,5212),(20227,5212),(20227,8034),(20227,13138),(20227,13413)]
        self.ax0=self.fig.add_axes([0.16,0.144,0.586,0.1957])
        self.ax1=self.fig.add_axes([0.16,0.444,0.586,0.1962])
        self.ax2=self.fig.add_axes([0.16,0.6485,0.586,0.1960])
        self.hitmap_ref0=np.zeros((self.nRows,self.nColumns))
        self.hitmap_ref1=np.zeros((self.nRows,self.nColumns))
        self.hitmap_ref2=np.zeros((self.nRows,self.nColumns))

    def initial_hitmap(self):
        self.hitmap_t0=np.zeros((self.nRows,self.nColumns))
        self.hitmap_t1=np.zeros((self.nRows,self.nColumns))
        self.hitmap_t2=np.zeros((self.nRows,self.nColumns))

        #if one wants to plot something at the begining of the application fill this function.
        for i in range(9):
            self.axes.plot([self.chess2_point[i][0],self.chess2_point[i+1][0]],[self.chess2_point[i][1],self.chess2_point[i+1][1]],'k')
        self.axes.plot([self.chess2_point[0][0],self.chess2_point[9][0]],[self.chess2_point[0][1],self.chess2_point[9][1]],'k')
        self.axes.plot([self.chess2_point[1][0],self.chess2_point[5][0]],[self.chess2_point[1][1],self.chess2_point[5][1]],'k')
        for i in range(7,12,1):
            self.axes.plot([self.chess2_point[i][0],self.chess2_point[21-i][0]],[self.chess2_point[i][1],self.chess2_point[21-i][1]],'k')
        self.plot()
    def plot(self):
        self.ax0.clear()
        self.ax0.imshow(self.hitmap_t2,aspect="auto",cmap='gray',origin='upper',interpolation='nearest')
        self.ax1.clear()
        self.ax1.imshow(self.hitmap_t1,aspect="auto",cmap='gray',origin='upper',interpolation='nearest')
        self.ax2.clear()
        self.ax2.imshow(self.hitmap_t0,aspect="auto",cmap='gray',origin='lower',interpolation='nearest')
        self.draw()
        self.fig.canvas.draw()
    def update_hitmap(self,hitmap_2,hitmap_1,hitmap_0):

        if self.hitmapAc==1:
            self.hitmap_t2+=hitmap_2
            self.hitmap_t1+=hitmap_1
            self.hitmap_t0+=hitmap_0
        else:
            self.hitmap_t2=hitmap_2
            self.hitmap_t1=hitmap_1
            self.hitmap_t0=hitmap_0

        if self.ref==1:
            print("using as noise hitmap ....")
            self.hitmap_ref0=self.hitmap_t0 
            self.hitmap_ref1=self.hitmap_t1 
            self.hitmap_ref2=self.hitmap_t2
            self.ref=0 
        self.reducenoise()   
     
    def reducenoise(self):
     #   max_data0=np.linalg.norm(self.hitmap_t0)
     #   max_ref0=np.linalg.norm(self.hitmap_ref0)
     #   #max_data0=np.amax(self.hitmap_t0)
     #   #max_ref0=np.amax(self.hitmap_ref0)
     #   if max_data0>0 and max_ref0>0:
     #       print(max_data0/max_ref0)
     #       self.hitmap_ref0=self.hitmap_ref0*(max_data0/max_ref0)
     #   max_data1=np.amax(self.hitmap_t1)
     #   max_ref1=np.amax(self.hitmap_ref1)
     #   if max_data1>0 and max_ref1>0:
     #       print(max_data1/max_ref1)
     #       self.hitmap_ref1=self.hitmap_ref1*(max_data1/max_ref1)
     #   max_data2=np.amax(self.hitmap_t2)
     #   max_ref2=np.amax(self.hitmap_ref2)
     #   if max_data2>0 and max_ref2>0:
     #       self.hitmap_ref2=self.hitmap_ref2*(max_data2/max_ref2)
        r=15
        r1=15
        s=0.8
        if sum(sum(self.hitmap_t2))>0 and sum(sum(self.hitmap_ref2))>0:
             rate_2=sum(sum(self.hitmap_t2))/sum(sum(self.hitmap_ref2))
        else:
            rate_2=0.1
        if sum(sum(self.hitmap_t1))>0 and sum(sum(self.hitmap_ref1))>0:
             rate_1=sum(sum(self.hitmap_t1))/sum(sum(self.hitmap_ref1))
            # rate_1=self.hitmap_t1[r][r1]/self.hitmap_ref1[r][r1]
        else:
            rate_1=0.1
        if sum(sum(self.hitmap_t0))>0 and sum(sum(self.hitmap_ref0))>0:
             rate_0=sum(sum(self.hitmap_t0))/sum(sum(self.hitmap_ref0))
            # rate_0=self.hitmap_t0[r][r1]/self.hitmap_ref0[r][r1]
        else:
            rate_0=0.1
        self.hitmap_t2=self.hitmap_t2-self.hitmap_ref2*rate_2*s
        self.hitmap_t1=self.hitmap_t1-self.hitmap_ref1*rate_1*s
        self.hitmap_t0=self.hitmap_t0-self.hitmap_ref0*rate_0*s
        
        self.plot()


class MplCanvas_effi_plot(FigureCanvas):
    def __init__(self, parent=None, width=8, height=4.5, MyTitle=""):
        #self.fig,self.axes=plt.subplots(figsize=(11,9))
        self.fig = Figure(figsize=(width, height))
        self.axes = self.fig.add_subplot(111)
        plt.ion()
        self.maxContain=100
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(self, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.MyTitle = MyTitle
        self.axes.set_title(self.MyTitle)
        #fig.cbar = None


    def initial_effi_plot(self):
        self.datasize=[]
        self.eff_0=0
        self.eff_1=0
        self.eff_2=0
        self.efficiency_data_arrived=[[],[],[]]
        self.efficiency_signal_received=[]
        self.plot()  
    def plot(self):
        self.axes.clear()
        #if one wants to plot something at the begining of the application fill this function.
        self.axes.plot(self.efficiency_data_arrived[0],'b--',label='Matrix 0')
        self.axes.plot(self.efficiency_data_arrived[1],'y-.',label='Matrix 1')
        self.axes.plot(self.efficiency_data_arrived[2],'r-',label='Matrix 2')
        self.axes.legend()
        #self.fig.xlabel("Frame number",fontsize=10)
        #self.fig.ylabel("Efficiency",fontsize=10)
        #self.fig.canvas.draw()
       # plt.plot(self.datasize,self.efficiency_signal_received,'b-')
        self.draw()
    def update_effi_plot(self,dvflag_M0,mhflag_M0,dvflag_M1,mhflag_M1,dvflag_M2,mhflag_M2):
        if len(dvflag_M0)==0:
            print("nothing ")
        else:
            self.eff_0=0
            self.eff_1=0
            self.eff_2=0
            for i in range(len(dvflag_M0)):
                if dvflag_M0[i]==1:
                    self.eff_0+=1 
                if dvflag_M1[i]==1:
                    self.eff_1+=1 
                if dvflag_M2[i]==1:
                    self.eff_2+=1 
            self.efficiency_data_arrived[0].append(self.eff_0/(len(dvflag_M0)/4))     
            self.efficiency_data_arrived[1].append(self.eff_1/(len(dvflag_M0)/4))    
            self.efficiency_data_arrived[2].append(self.eff_2/(len(dvflag_M0)/4))
            if len(self.efficiency_data_arrived[0])>=self.maxContain:
                self.efficiency_data_arrived[0].remove(self.efficiency_data_arrived[0][0])
                self.efficiency_data_arrived[1].remove(self.efficiency_data_arrived[1][0])
                self.efficiency_data_arrived[2].remove(self.efficiency_data_arrived[2][0])
            self.plot()    
    def initial_time_plot(self):
        self.timeofFrames=[]
        self.plot_time()

    def update_time_plot(self,time_i):
        self.timeofFrames.append(time_i) 
        if len(self.timeofFrames)>=self.maxContain:
            self.timeofFrames.remove(self.timeofFrames[0])
        self.plot_time()

    def plot_time(self):
        self.axes.clear()
        self.axes.plot(self.timeofFrames,'r-',label='Time [1/320MHz]') 
        self.axes.legend()
        self.draw()


