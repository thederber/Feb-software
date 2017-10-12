#from __future__ import pickle
import csv
import json
from ROOT import *
from ROOT import gROOT, TCanvas, TF1, TFile, TTree, gRandom, TH1F, TLorentzVector
from ROOT import TPad, TPaveText, TLegend, THStack
from ROOT import gBenchmark, gStyle, gROOT, gPad
import sys
import re
from array import array
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from array import array
import math
#from SCurveNP_new3 import *
from SCurveNP_json import *
#gROOT.SetStyle("Plain")   # set plain TStyle
#gStyle.SetOptStat(0);
#gROOT.SetBatch(1)         #This was to suppress the canvas outputs
#gStyle.SetOptStat(111111) # draw statistics on plots,
                            # (0) for no output
#gStyle.SetPadTickY(1)
#gStyle.SetOptFit(1111)    # draw fit results on plot,
                            # (0) for no ouput
#gStyle.SetPalette(57)     # set color map
#gStyle.SetOptTitle(0)     # suppress title box
#def plot(csv_file,projection=1): 
class timep:
    def __init__(self,pixel,matrix,threshold,time):
        self.pixel=pixel
        self.matrix=matrix
        self.threshold=threshold
        self.time=time

def dic2timep(dic):
    return timep(dic['pixel'],dic['matrix'],dic['threshold'],dic['time'])

def plot(name_f_json,projection=1):    
    pulse_start=35000
    pulse_width=15000
    sweep_type='threshold'
    time_scale=140000
    # one for each ASIC
    pixels=[(20,20)]
    matrix=[0,1,2]
    thresholdCuts = range(0x0, 0x800, 0x8)
    data_dic={}
    pulse_end=pulse_start+pulse_width
    fast_range=1500
    with open(name_f_json+'.json') as f:
    #with open('f_j.json') as f:
        hist=json.load(f,object_hook=dic2timep)
        data_dic=get_allHists(pixels,matrix,thresholdCuts)
        for a in hist:
            p1=a.pixel[0]
            p2=a.pixel[1]
            data_dic[(p1,p2)][a.matrix][a.threshold]=a.time
            #print(type(a.time))
   
#        rootf=TFile('f_pickle_'+str(key)+'.root',"RECREATE")   
    for key in data_dic:
        print key
        rootf = TFile(name_f_json+'.root',"RECREATE")   
        for key1 in data_dic[key]:
            a=[]
            for key2 in data_dic[key][key1]:
               a.append(key2)
               a1=[float(b)/1241. for b in a]
            h_name="cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_THsweep"
            hist_name=TH2D(h_name,";Threshold [V];Time [ns]", 200, min(a1), max(a1), 800, 0, time_scale)
            for key2 in data_dic[key][key1]:
                for val_i in range(len(data_dic[key][key1][key2])):
                    timev=data_dic[key][key1][key2][val_i]
                    if timev>30000:
                        hist_name.Fill(float(key2)/1241,timev)
            hist_name.Write()
            if projection:
                cut1=[min(a1),0]
                cut2=[max(a1),140000]
                proj_x=get_proj_X(hist_name,h_name,cut1,cut2,min(a1),max(a1))
                proj_y=get_proj_Y(hist_name,h_name,cut1,cut2,0,time_scale)
                proj_x.Write()
                proj_y.Write()
            
        rootf.Close()     
            
def cut_area(cut_point1,cut_point2,x_name='threshold',y_name='time'):
    cut=TCutG("cut",4)
    cut.SetVarX(x_name)
    cut.SetVarY(y_name)
    cut.SetPoint(0,cut_point1[0],cut_point1[1])
    cut.SetPoint(1,cut_point1[0],cut_point2[1])
    cut.SetPoint(2,cut_point2[0],cut_point2[1])
    cut.SetPoint(3,cut_point2[0],cut_point1[1])
    return cut

def get_proj_X(hist_name,file_name,cut1,cut2,minx,maxx):
    p_name=str(file_name)+"projection_on_threshold"
    proj_x=TH1D("proj_x","projection on threshold",1000,minx,maxx)
    cut=cut_area(cut1,cut2)
    proj_x=hist_name.ProjectionX("_px",0,-1,"[cut]")
    #proj_x=hist_name.ProjectionX(hist_name,Ycut1,Ycut2)
    return proj_x 

def get_proj_Y(hist_name,file_name,cut1,cut2,miny,maxy):
    p_name=str(file_name)+"projection_on_time"
    proj_y=TH1D("proj_y","projection on time",1000,miny,maxy)
    cut=cut_area(cut1,cut2)
    proj_y=hist_name.ProjectionY("_py",0,-1,"[cut]") 
    #proj_y=hist_name.ProjectionY(hist_name,Xcut1,Xcut2) 
    return proj_y
#for bl in [1280,1365,1489]:
for bl in [8,310,434,576,744,868,930,993,1117,1280,1365,1489]:
    plot("chess2_scan_SCurveTest_10092017_board_192.168.3.28_run_53_BL_"+str(bl)+"_chargeInjectionEnbled_0_thN_0x6_PulseDelay_11199_PXTHsweep",1)  
    plot("chess2_scan_SCurveTest_10092017_board_192.168.3.28_run_53_BL_"+str(bl)+"_chargeInjectionEnbled_1_thN_0x6_PulseDelay_11199_PXTHsweep",1)  
     
