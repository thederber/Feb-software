import csv
from ROOT import *
import sys
import re
from array import array
import os
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from ROOT import gROOT, TCanvas, TF1, TFile, TTree, gRandom, TH1F, TLorentzVector
from array import array
import math
from ROOT import TPad, TPaveText, TLegend, THStack
from ROOT import gBenchmark, gStyle, gROOT, gPad
from SCurveNP_new import *

gROOT.SetStyle("Plain")   # set plain TStyle
gStyle.SetOptStat(0);
gROOT.SetBatch(1)         #This was to suppress the canvas outputs
#gStyle.SetOptStat(111111) # draw statistics on plots,
                            # (0) for no output
gStyle.SetPadTickY(1)
#gStyle.SetOptFit(1111)    # draw fit results on plot,
                            # (0) for no ouput
#gStyle.SetPalette(57)     # set color map
gStyle.SetOptTitle(0)     # suppress title box

#if(len(sys.argv) < 3):
#	sys.exit("3 arguments required: input file, output file")
#thresholdHexList = [0xbc2,0xbc2,0xbc2,0xbc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x6b2,0x6a2,0x692,0x682,0x672,0x662,0x652,0x642,0x632,0x622,0x612,0x602,0x5f2,0x5e2,0x5c2,0x5b2,0x5a2,0x592,0x582,0x572,0x562,0x552,0x542,0x532,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
#thresholdList = [int(hexVal)/1241. for hexVal in thresholdHexList] # convert hex to float
#thresholdHexList = np.arange(0xbc2, 0, -2) # for the file'chess2_scan_NoQinjPulse_BLx_SCurveTest_trim70x%i_.csv
#thresholdHexList = [0xfc2,0xec2,0xdc2,0xcc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x6b2,0x6a2,0x692,0x682,0x672,0x662,0x652,0x642,0x632,0x622,0x612,0x602,0x5f2,0x5e2,0x5c2,0x5b2,0x5a2,0x592,0x582,0x572,0x562,0x552,0x542,0x532,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
#thresholdHexList = [0xfc2,0xec2,0xdc2,0xcc2]
#thresholdHexList = np.arange(0x800, 0x500, -2) # for the file 'chess2_scan_QinjPulse_BLx_SCurveTest_trim7' 
#thresholdHexList = [0x500] # for the file 'chess2_scan_QinjPulse_BLx_SCurveTest_trim7' 
#thresholdList = [int(hexVal)/1241. for hexVal in thresholdHexList]

# one for each ASIC
timingList0 = []
timingList1 = []
timingList2 = []

nRows = 128
nCols = 32
# parse csv file, save first entry of delta t
#for root, dirs, filenames in os.walk(sys.argv[1]):
#	for f in filenames:
tf = TFile(sys.argv[2]+"hitmap.root","RECREATE")

for j in [7]:
        hists0=load_chess2_data(sys.argv[1]) #load the data and get the shape of the matrix
        a=hists0.shape
        hist2D00 = TH2D("hitMap00","hitMap_of_matrix0_no_charge_injection",128,0,128,32,0,32)
        hist2D01 = TH2D("hitMap01","hitMap_of_matrix1_no_charge_injection",128,0,128,32,0,32)
        hist2D02 = TH2D("hitMap02","hitMap_of_matrix2_no_charge_injection",128,0,128,32,0,32)
        #hist2D00 = TH2D("hitMap00","hitMap_of_matrix0_no_charge_injection",32,0,32,129,0,129)
        #hist2D01 = TH2D("hitMap01","hitMap_of_matrix1_no_charge_injection",32,0,32,129,0,129)
        #hist2D02 = TH2D("hitMap02","hitMap_of_matrix2_no_charge_injection",32,0,32,129,0,129)
        for i0 in range(a[0]): # the threshold number
            #BLcounter = 0
            #pixels = (row,col) for row in range(nRows) for col in range(nCols) 
            #BLcounter +=1
            #print(BLcounter)
            #print(pixels)
            for row in range(nRows):
                for col in range(nCols):
                    pixels=(row,col)
            #for i1 in range(a[1]): # pixel number
                #pixels = (row,col) for row in range(nRows) for col in range(nCols) 
                #BLcounter +=1
                    i1=32*row+col
		   # print(pixels)
                    for i2 in range(a[2]): # asic number
                        asic=i2
                        #print(pixels)
		       # numHits0 = 0
		       # numHits1 = 0
		        #numHits_fast = 0
                        if(a[3] >1):
                            #active_of_pixel0=0
                            #active_of_pixel1=0 
                            for i3 in range(a[3]): # number of counts
                                timev0=hists0[i0,i1,i2,i3]
                                if((timev0)>-1 and asic==0): hist2D00.Fill(row,col)
                                if((timev0)>-1 and asic==1): hist2D01.Fill(row,col)
                                if((timev0)>-1 and asic==2): hist2D02.Fill(row,col)

        c0 = TCanvas("c0","",800,600) 
        hist2D00.SetStats(kFALSE)
        hist2D00.Draw("COLZ")
        hist2D00.GetXaxis().SetTitle("COL number");
        hist2D00.GetYaxis().SetTitle("ROW number");
        c0.Print(sys.argv[2] + "asic00_hitMap.png")

        c1 = TCanvas("c1","",800,600)
        hist2D01.SetStats(kFALSE)
        hist2D01.Draw("COLZ")
        hist2D01.GetXaxis().SetTitle("COL number");
        hist2D01.GetYaxis().SetTitle("ROW number");
        c1.Print(sys.argv[2] + "asic01_hitMap.png")

        c2 = TCanvas("c2","",800,600)
        hist2D02.SetStats(kFALSE)
        hist2D02.Draw("COLZ")
        hist2D02.GetXaxis().SetTitle("COL number");
        hist2D02.GetYaxis().SetTitle("ROW number");
        c2.Print( sys.argv[2] +"asic02_hitMap.png")

        hist2D00.Write()
        hist2D01.Write()
        hist2D02.Write()
tf.Close()

#timingArray = array('f',timingList0)
#thresholdArray = array('f',thresholdList)
#c1 = TCanvas("c1","",800,600)
#gr1 = TGraph(len(timingArray),thresholdArray,timingArray)
#gr1.SetMinimum(0)
#gr1.SetMarkerStyle(23)
#gr1.SetMarkerSize(2)
#gr1.Draw("ap")
#c1.Print(sys.argv[2])
