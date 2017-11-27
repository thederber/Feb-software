#from __future__ import pickle
import pickle
import csv
import json
from ROOT import *
from ROOT import gROOT, TCanvas, TF1, TFile, TTree, gRandom, TH1F, TLorentzVector, TGraphErrors, TGraph
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
from SCurveNP_8hits_BL_json3 import *
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
    def __init__(self,pixel1,matrix1,index1,threshold1,time1):
        self.pixel=pixel1
        self.matrix=matrix1
        self.index=index1
        self.threshold=threshold1
        self.time=time1

def dic2timep(dic):
    return timep(dic['pixel'],dic['matrix'],dic['index'],dic['threshold'],dic['time'])
    #return timep(dic['pixel'],dic['matrix'],dic['threshold'],dic['index'],dic['time'])
#class timep2:
#    pixel=[(20,20)]
#    matrix=0
#    threshold=8
#    time=[]
#picklestring=pickle.load(timep2)
#class timep3:
#    def __init__(self,pixel,matrix,threshold,time):
#        self.info={'pixel':(1,1),'matrix':1,'threshold':10000,'time':[]}
#with open('f_pickle.pkl','rb') as f_pread:
#    hists=pickle.load(f_pread)
#with open('f_j.json') as f:
##with open('f_j.json',encoding='utf-8') as f:
#    hist=json.load(f,object_hook=dic2timep)
#    print(len(hist))
#    for a in hist:
#        print(a.pixel)
#        print(a.matrix)
#        print(a.threshold)
#        print(a.time)
#def plot(name_f_json,pixels,projection=1):    
def plot(name_f_json,projection=1):    
    pulse_start=35000
    pulse_width=15000
    sweep_type='threshold'
    time_scale=140000
    # one for each ASIC
    #pixels=[(0,1)]
    pixels=get_pixels(name_f_json+'.json')
    matrix=[0,1,2]
    hits=(0,1,2,3,4,5,6,7)
    th_l=0x0
    th_h=0x800
    th_delta=0x8
    thresholdCuts = range(th_l, th_h, th_delta)
    data_dic={}
    pulse_end=pulse_start+pulse_width
    fast_range=1500
    with open(name_f_json+'.json') as f:
    #with open('f_j.json') as f:
        hist=json.load(f,object_hook=dic2timep)
        data_dic=get_allHists(pixels,matrix,hits,thresholdCuts)
        #data_dic=get_allHists(pixels,matrix,thresholdCuts,hits)
        for a in hist:
            p1=a.pixel[0]
            p2=a.pixel[1]
            data_dic[(p1,p2)][a.matrix][a.index][a.threshold]=a.time
    for key in data_dic: #pixel
        print(key)
        rootf = TFile(name_f_json+'.root',"RECREATE") 
        for key1 in data_dic[key]: #matri2x
            h="hitnumber_pixel_"+str(key)+"_asic"+str(key1)+"_THsweep"
            h=TH1D(h,";Hit;Hits number",8,0,8)  
            h_name_all="cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_THsweep"
            #h_name_g="cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_THsweep_g"
            a=[]
            for key3 in data_dic[key][key1][1]: #threshold
                a.append(key3)
            a1=[float(b)/1241. for b in a]
            hist_name_all=TH2D(h_name_all,";Threshold [V];Time [ns]", (th_h-th_l)/th_delta, min(a1), max(a1), 2000, 0, time_scale)
            for key2 in data_dic[key][key1]:  #index
                h_name="cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_hit_"+str(key2)+"_THsweep"
                hist_name=TH2D(h_name,";Threshold [V];Time [ns]", (th_h-th_l)/th_delta, min(a1), max(a1), 800, 0, time_scale)
                g_x=[]
                g_y=[]
                g_ex=[]
                g_ey=[]
                a=data_dic[key][key1][key2].keys()
                a.sort()
                for key3 in a: #threhsold
                #for key3 in data_dic[key][key1][key2]: #threhsold
                    t_aftercut=[]
                    for val_i in range(len(data_dic[key][key1][key2][key3])):
                        timev=data_dic[key][key1][key2][key3][val_i]
                        #if timev>0:
                        #if (timev<35000):
                        if timev>0:
                            t_aftercut.append(timev)
                            hist_name.Fill(float(key3)/1241,timev)
                            hist_name_all.Fill(float(key3)/1241,timev)
                            h.Fill(key2)
                    if len(t_aftercut)!=0:
                        t_aftercut_a=np.array(t_aftercut)
                        g_x.append(float(key3)/1241)
                        #print(float(key3)/1241)
                        g_y.append(np.mean(t_aftercut_a))
                        g_ey.append(np.std(t_aftercut_a))
                        g_ex.append(0)
                hist_name.Write()
                g_ax=np.array(g_x)
                g_ay=np.array(g_y)
                g_aex=np.array(g_ex)
                g_aey=np.array(g_ey)
                #hist_name_g=TGraph(len(g_ax),g_ax,g_ay)
#                #hist_name_g="cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_hit_"+str(key2)+"_THsweep_g"
                if len(g_ax)!=0:
                    graph_g=TGraph(len(g_ax),g_ax,g_ay)
                    graph_g.SetName("cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_hit_"+str(key2)+"_THsweep_graph")
                    graph_g.SetTitle(";Threshold [V];Time [ns]")
                    graph_g.SetMarkerStyle(20);
                    graph_g.SetMarkerSize(0.6);
                    graph_g.Write()
                    hist_name_g=TGraphErrors(len(g_ax),g_ax,g_ay,g_aex,g_aey)
                    hist_name_g.SetName("cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_hit_"+str(key2)+"_THsweep_g")
                    hist_name_g.SetTitle(";Threshold [V];Time [ns]")
                    hist_name_g.SetFillColor(1);
                    hist_name_g.SetMarkerStyle(20);
                    hist_name_g.SetMarkerSize(0.6);
                    hist_name_g.Write()
                if projection:
                    cut1=[min(a1),0]
                    cut2=[max(a1),140000]
                    proj_x=get_proj_X(hist_name,h_name,cut1,cut2,min(a1),max(a1))
                    proj_y=get_proj_Y(hist_name,h_name,cut1,cut2,0,time_scale)
                    proj_x.Write()
                    proj_y.Write()
                #hist_name_g="cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_THsweep_g"
                #hist_name_g=TGraphErrors(n,g_ax,g_aex,g_ay,g_aey)
                #hist_name_g=TGraphErrors(n,g_ax,g_aex,g_ay,g_aey)
                #hist_name_g.SetTitle("cumulTimeHist_pixel_"+str(key)+"_asic"+str(key1)+"_THsweep_g")
                #hist_name_g=TGraphErrors(h_name_g,";Threshold [V];Time [ns]",n,g_x,g_y,g_ex,g_ey)
            hist_name_all.Write()
            h.Write()
            if projection:
                cut1=[min(a1),0]
                cut2=[max(a1),140000]
                proj_x_all=get_proj_X(hist_name_all,h_name_all,cut1,cut2,min(a1),max(a1))
                proj_y_all=get_proj_Y(hist_name_all,h_name_all,cut1,cut2,0,time_scale)
                proj_x_all.Write()
                proj_y_all.Write()
            
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

#for bl in [8,310,434,576]:
#for bl in [930,1365]:
for bl in [930]:
    plot("/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-02/chess2_scan_SCurveTest_11152017_board_192.168.3.28_run_29_BL_"+str(bl)+"_chargeInjectionEnbled_1_thN_0x6_PulseDelay_11199_PXTHsweep_50ns_6p_v1",1)
    plot("/u1/atlas-chess2-Asic-tests/data/data_h/pre-ampdata-02/chess2_scan_SCurveTest_11152017_board_192.168.3.28_run_29_BL_"+str(bl)+"_chargeInjectionEnbled_0_thN_0x6_PulseDelay_11199_PXTHsweep_50ns_6p_v1",1)
     
