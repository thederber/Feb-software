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
from SCurveNP import *

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

if(len(sys.argv) < 2):
	sys.exit("2 arguments required: input file, output file")
#thresholdHexList = [0xbc2,0xbc2,0xbc2,0xbc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x6b2,0x6a2,0x692,0x682,0x672,0x662,0x652,0x642,0x632,0x622,0x612,0x602,0x5f2,0x5e2,0x5c2,0x5b2,0x5a2,0x592,0x582,0x572,0x562,0x552,0x542,0x532,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
#thresholdList = [int(hexVal)/1241. for hexVal in thresholdHexList] # convert hex to float
#thresholdHexList = np.arange(0xbc2, 0, -2) # for the file'chess2_scan_NoQinjPulse_BLx_SCurveTest_trim70x%i_.csv
#thresholdHexList = [0xfc2,0xec2,0xdc2,0xcc2,0xbc2,0xac2,0x9c2,0x8c2,0x7c2,0x6c2,0x6b2,0x6a2,0x692,0x682,0x672,0x662,0x652,0x642,0x632,0x622,0x612,0x602,0x5f2,0x5e2,0x5c2,0x5b2,0x5a2,0x592,0x582,0x572,0x562,0x552,0x542,0x532,0x4c2,0x3c2,0x2c2,0x1c2,0x0c2]
#thresholdHexList = [0xfc2,0xec2,0xdc2,0xcc2]
#thresholdHexList = np.arange(0xd14, 0x400, -16)
#thresholdHexList = np.arange(0x800, 0x500, -2) # for the file 'chess2_scan_QinjPulse_BLx_SCurveTest_trim7' 
thresholdHexList = get_thresholds(sys.argv[1])
thresholdList = [int(hexVal)/1241. for hexVal in thresholdHexList]
minBL=min(thresholdList)
maxBL=max(thresholdList)
# one for each ASIC
timingList0 = []
timingList1 = []
timingList2 = []

nRows = 128
nCols = 32
# parse csv file, save first entry of delta t
#for root, dirs, filenames in os.walk(sys.argv[1]):
#	for f in filenames:
tf = TFile(sys.argv[2]+".root","RECREATE")

for j in [6]:
        hists=load_chess2_data(sys.argv[1]) #load the data and get the shape of the matrix
        a=hists.shape
        print(a)
        g0 = TGraph()
        g1 = TGraph()
        g2 = TGraph()
        g0_fast = TGraph()
	g1_fast = TGraph()
	g2_fast = TGraph()
	hist1D0 = TH1D('timeHist_asic0_trim70x%i'%(j),'timeHist_asic0_trim70x%i;time;'%(j),100,0,10000)
	hist1D1 = TH1D('timeHist_asic1_trim70x%i'%(j),'timeHist_asic1_trim70x%i;time;'%(j),100,0,10000)
	hist1D2 = TH1D('timeHist_asic2_trim70x%i'%(j),'timeHist_asic2_trim70x%i;time;'%(j),100,0,10000)
	hist1D0_fast = TH1D('fast_timeHist_asic0_trim70x%i'%(j),'fast_timeHist_asic0_trim70x%i;time;'%(j),50,0,500)
	hist1D1_fast = TH1D('fast_timeHist_asic1_trim70x%i'%(j),'fast_timeHist_asic1_trim70x%i;time;'%(j),50,0,500)
	hist1D2_fast = TH1D('fast_timeHist_asic2_trim70x%i'%(j),'fast_timeHist_asic2_trim70x%i;time;'%(j),50,0,500)
	#histCumul0_fast= TH2D('fast_cumulTimeHist_asic0_trim70x%i'%(j),'fast_cumTimeHist_asic0_trim70x%i;BL;time;numbHits'%(j), 50, 0.9, 1.6, 100, 0, 10000)
	#histCumul1_fast= TH2D('fast_cumulTimeHist_asic1_trim70x%i'%(j),'fast_cumTimeHist_asic1_trim70x%i;BL;time;numbHits'%(j), 50, 0.9, 1.6, 100, 0, 10000)
	#histCumul2_fast= TH2D('fast_cumulTimeHist_asic2_trim70x%i'%(j),'fast_cumTimeHist_asic2_trim70x%i;BL;time;numbHits'%(j), 50, 0.9, 1.6, 100, 0, 10000)
	histCumul0_fast= TH2D('fast_cumulTimeHist_asic0_trim70x%i'%(j),'fast_cumTimeHist_asic0_trim70x%i;BL;time;numbHits'%(j), 100, minBL, maxBL, 100, 0, 10000)
	histCumul1_fast= TH2D('fast_cumulTimeHist_asic1_trim70x%i'%(j),'fast_cumTimeHist_asic1_trim70x%i;BL;time;numbHits'%(j), 100, minBL, maxBL, 100, 0, 10000)
	histCumul2_fast= TH2D('fast_cumulTimeHist_asic2_trim70x%i'%(j),'fast_cumTimeHist_asic2_trim70x%i;BL;time;numbHits'%(j), 100, minBL, maxBL, 100, 0, 10000)
	histCumul0_fast_hit= TH2D('fast_cumulTimeHist_asic0_fast_hit_trim70x%i'%(j),'fast_cumTimeHist_asic0_fast_hit_trim70x%i;BL;time;numbHits'%(j), 50, minBL, maxBL, 100, 0, 10000)
	histCumul1_fast_hit= TH2D('fast_cumulTimeHist_asic1_fast_hit_trim70x%i'%(j),'fast_cumTimeHist_asic1_fast_hit_trim70x%i;BL;time;numbHits'%(j), 50, minBL, maxBL, 100, 0, 10000)
	histCumul2_fast_hit= TH2D('fast_cumulTimeHist_asic2_fast_hit_trim70x%i'%(j),'fast_cumTimeHist_asic2_fast_hit_trim70x%i;BL;time;numbHits'%(j), 50, minBL, maxBL, 100, 0, 10000)
	X = []
	Y = []
	Z = []
        for i0 in range(a[0]): # the pixel number
            BLcounter = 0
            for i1 in range(a[1]): # threshold number
                BLcounter +=1
		print(BLcounter)
                for i2 in range(a[2]): # asic number
                    asic=i2
		    numHits = 0
		    numHits_fast = 0
                    if(a[3] >1):
                        for i3 in range(a[3]): # number of counts 
                            timev=hists[i0,i1,i2,i3]
                            if (timev)>-1:
                                numHits += 1
                                if timev<500:
			            numHits_fast += 1
	                    if(asic==0): 
	                        if timev > -1 :
		                    hist1D0.Fill(timev)
			            histCumul0_fast.Fill(thresholdList[BLcounter-1], timev)
		                if timev < 500: 
		                    hist1D0_fast.Fill(timev)
			            histCumul0_fast_hit.Fill(thresholdList[BLcounter-1], timev)
	                    #X.append(thresholdList[BLcounter-1])
			    #Z.append(timev)
			    #if timev < 0:
			     #   Y.append(-1)
			    #if timev >= 0:
			     #   Y.append(1) 
		            if(asic==1): 
	                        if timev > -1 :
	                            hist1D1.Fill(timev)
		                    histCumul1_fast.Fill(thresholdList[BLcounter-1], timev)
			        if timev < 500: 
			            hist1D1_fast.Fill(timev)
			            histCumul1_fast_hit.Fill(thresholdList[BLcounter-1], timev)
									
		            if(asic==2): 
		                if timev > -1 :
		                    hist1D2.Fill(timev)
			            histCumul2_fast.Fill(thresholdList[BLcounter-1], timev)
			        if timev < 500: 
			            hist1D2_fast.Fill(timev)
			            histCumul2_fast_hit.Fill(thresholdList[BLcounter-1], timev)
	            if(asic==0): 
	                g0.SetPoint(g0.GetN(), thresholdList[BLcounter-1], numHits)
		        g0_fast.SetPoint(g0_fast.GetN(), thresholdList[BLcounter-1], numHits_fast)
	            if(asic==1): 
	                g1.SetPoint(g1.GetN(), thresholdList[BLcounter-1], numHits)
		        g1_fast.SetPoint(g1_fast.GetN(), thresholdList[BLcounter-1], numHits_fast)
	            if(asic==2): 
	                g2.SetPoint(g2.GetN(), thresholdList[BLcounter-1], numHits)
		        g2_fast.SetPoint(g2_fast.GetN(), thresholdList[BLcounter-1], numHits_fast)
	g0.SetTitle('numberOfHits_asic0_trim70x%i;BL;hits'%(j))
	g1.SetTitle('numberOfHits_asic1_trim70x%i;BL;hits'%(j))
	g2.SetTitle('numberOfHits_asic2_trim70x%i;BL;hits'%(j))
	g0.Write('numberOfHits_asic0_trim70x%i'%(j))
	g1.Write('numberOfHits_asic1_trim70x%i'%(j))
	g2.Write('numberOfHits_asic2_trim70x%i'%(j))
	hist1D0.Write()
	hist1D1.Write()
	hist1D2.Write()
	g1.SetLineColor(4)
	g2.SetLineColor(2)
	g0.SetLineWidth(4)
	g1.SetLineWidth(4)
	g2.SetLineWidth(4)
	hist1D1.SetLineColor(4)
	hist1D2.SetLineColor(2)
	g0.SetDrawOption("AL*")
	g1.SetDrawOption("AL*")
	g2.SetDrawOption("AL*")

	g0_fast.SetTitle('fast_numberOfHits_asic0_trim70x%i;BL;hits'%(j))
	g1_fast.SetTitle('fast_numberOfHits_asic1_trim70x%i;BL;hits'%(j))
	g2_fast.SetTitle('fast_numberOfHits_asic2_trim70x%i;BL;hits'%(j))
	g0_fast.Write('fast_numberOfHits_asic0_trim70x%i'%(j))
	g1_fast.Write('fast_numberOfHits_asic1_trim70x%i'%(j))
	g2_fast.Write('fast_numberOfHits_asic2_trim70x%i'%(j))
	hist1D0_fast.Write()
	hist1D1_fast.Write()
	hist1D2_fast.Write()
	g1_fast.SetLineColor(4)
	g2_fast.SetLineColor(2)
	g0_fast.SetLineWidth(4)
	g1_fast.SetLineWidth(4)
	g2_fast.SetLineWidth(4)
	hist1D1_fast.SetLineColor(4)
	hist1D2_fast.SetLineColor(2)
	g0_fast.SetDrawOption("AL*")
	g1_fast.SetDrawOption("AL*")
	g2_fast.SetDrawOption("AL*")

	histCumul0_fast.SetDrawOption("SURF7")
	histCumul1_fast.SetDrawOption("SURF7")
	histCumul2_fast.SetDrawOption("SURF7")
	histCumul0_fast.Write()
	histCumul1_fast.Write()
	histCumul2_fast.Write()

	histCumul0_fast_hit.SetDrawOption("COL")
	histCumul1_fast_hit.SetDrawOption("COL")
	histCumul2_fast_hit.SetDrawOption("COL")
	histCumul0_fast_hit.Write()
	histCumul1_fast_hit.Write()
	histCumul2_fast_hit.Write()
        c1 = TCanvas('c1','Time Histograms',1400,1400)
        #c1.SetLogy()
        c1.SetGrid()
        hist1D0.Draw('hist')
        hist1D1.Draw('SameHist')
        hist1D2.Draw('SameHist')
        c1.BuildLegend()
        c1.SaveAs(sys.argv[2]+'timeHist_all_asics_0x%i.jpg'%(j))
        c2 = TCanvas('c2','Number of Hits VS BL',1400,1400)
        c2.SetGrid()
        mg = TMultiGraph()
        mg.SetTitle('numberOfHits_all_asics_trim70x%i;BL;hits'%(j))
        mg.Add(g0)
        mg.Add(g1)
        mg.Add(g2)
        mg.Draw("AL*")
        gPad.Modified()
        #mg.GetXaxis().SetLimits(0,40)
        #mg.SetMinimum(0.)
        #mg.SetMaximum(11.)
        leg = TLegend(.5,.1,.9,.2)
        leg.SetFillColor(0)
        leg.AddEntry(g0)
        leg.AddEntry(g1)
        leg.AddEntry(g2)
        leg.Draw("Same")
        c2.SaveAs(sys.argv[2]+'numberOfHits_asic0_0x%i.jpg'%(j))

        c3 = TCanvas('c3','Fast Time Histograms',1400,1400)
        c3.SetGrid()
        hist1D0_fast.Draw('hist')
        hist1D1_fast.Draw('SameHist')
        hist1D2_fast.Draw('SameHist')
        c3.BuildLegend()
        c3.SaveAs(sys.argv[2]+'fast_timeHist_all_asics_0x%i.jpg'%(j))
        c4 = TCanvas('c4','Number of Fast Hits VS BL',1400,1400)
        c4.SetGrid()
        mg2 = TMultiGraph()
        mg2.SetTitle('fast_numberOfHits_all_asics_trim70x%i;BL;hits'%(j))
        mg2.Add(g0_fast)
        mg2.Add(g1_fast)
        mg2.Add(g2_fast)
        mg2.Draw("AL*")
        gPad.Modified()
        #mg.GetXaxis().SetLimits(0,40)
        #mg.SetMinimum(0.)
        #mg.SetMaximum(11.)
        leg2 = TLegend(.5,.1,.9,.2)
        leg2.SetFillColor(0)
        leg2.AddEntry(g0_fast)
        leg2.AddEntry(g1_fast)
        leg2.AddEntry(g2_fast)
        leg2.Draw("Same")
        c4.SaveAs(sys.argv[2]+'fast_numberOfHits_asic0_0x%i.jpg'%(j))

        c5 = TCanvas('c5','2-D Cumulative Time histogram',1400,1400)
        c5.SetGrid()
        histCumul0_fast.Draw("CONTZ")
        c5.BuildLegend()
        c5.SaveAs(sys.argv[2]+'cumulTimeHist_asics0_0x%i.jpg'%(j))
        c6 = TCanvas('c6','2-D Cumulative Time histogram',1400,1400)
        c6.SetGrid()
        histCumul1_fast.Draw("CONTZ")
        c6.BuildLegend()
        c6.SaveAs(sys.argv[2]+'cumulTimeHist_asics1_0x%i.jpg'%(j))
        c7 = TCanvas('c7','2-D Cumulative Time histogram',1400,1400)
        c7.SetGrid()
        histCumul2_fast.Draw("CONTZ")
        c7.BuildLegend()
        c7.SaveAs(sys.argv[2]+'cumulTimeHist_asics2_0x%i.jpg'%(j))

        c8 = TCanvas('c8','3-D Time histogram',1400,1400)
        c8.SetGrid()
        histCumul0_fast.Draw("LEGO2Z")
        c8.BuildLegend()
        c8.SaveAs(sys.argv[2]+'3DcumulTimeHist_asics0_0x%i.jpg'%(j))
        c9 = TCanvas('c9','3-D Time histogram',1400,1400)
        c9.SetGrid()
        histCumul1_fast.Draw("LEGO2Z")
        c9.BuildLegend()
        c9.SaveAs(sys.argv[2]+'3DcumulTimeHist_asics1_0x%i.jpg'%(j))
        c10 = TCanvas('c10','3-D Time histogram',1400,1400)
        c10.SetGrid()
        histCumul2_fast.Draw("LEGO2Z")
        c10.BuildLegend()
        c10.SaveAs(sys.argv[2]+'3DcumulTime_fastHits_asics2_0x%i.jpg'%(j))
        c11 = TCanvas('c11','3-D Time histogram_fasthits',1400,1400)
        c11.SetGrid()
        histCumul0_fast_hit.Draw("LEGO2Z")
        c11.BuildLegend()
        c11.SaveAs(sys.argv[2]+'3DcumulTime_fastHits_asics0_0x%i.jpg'%(j))
        c12 = TCanvas('c12','3-D Time histogram_fasthits',1400,1400)
        c12.SetGrid()
        histCumul1_fast_hit.Draw("LEGO2Z")
        c12.BuildLegend()
        c12.SaveAs(sys.argv[2]+'3DcumulTime_fastHits_asics1_0x%i.jpg'%(j))
        c13 = TCanvas('c13','3-D Time histogram_fasthits',1400,1400)
        c13.SetGrid()
        histCumul2_fast_hit.Draw("LEGO2Z")
        c13.BuildLegend()
        c13.SaveAs(sys.argv[2]+'3DcumulTimeHist_asics2_0x%i.jpg'%(j))
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
