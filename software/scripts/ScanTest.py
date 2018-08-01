from Hist_Plotter import Hist_Plotter
import numpy as np
from datetime import datetime
import os
import time

NOW = datetime.now().strftime("%Y-%m-%d_%H-%M")

class ScanTest():
	def __init__(self,matrix=0,feb_field="None",val_field="None",val_range=range(0x0,0x1F),shape=(8,1),topleft=(0,0),ntrigs=5,sleeptime=10,pulserStatus="ON"):
		self.matrix = matrix
		self.feb_field = feb_field
		self.val_field = val_field
		self.val_range = val_range
		self.shape = shape
		self.topleft = topleft
		self.ntrigs = ntrigs #default, seems good for now--explore later
		self.sleeptime = sleeptime #ms, between each readout trig in ntrigs
		self.pulserStatus = pulserStatus

		self.thresholds = None #see set_scan_type
		self.baselines = None
		self.fixed_threshold = None
		self.scan_type = None 
		self.is_th_scan = False
		self.is_bl_scan = False

		self.data_savedir = "/home/herve/Desktop/Chess2Data/noise_"+NOW+"/data"
		self.fig_savedir = "/home/herve/Desktop/Chess2Data/noise_"+NOW+"/plots"

		if not os.path.isdir(self.data_savedir): os.makedirs(self.data_savedir)
		if not os.path.isdir(self.fig_savedir): os.makedirs(self.fig_savedir)
	def set_matrix(self,matrix):
		self.matrix = matrix
	def set_feb_field(self,feb_field):
		self.feb_field = feb_field
	def set_val_field(self,val_field):
		self.val_field = val_field
	def set_val_range(self,val_range):
		self.val_range = val_range
	def set_shape(self,shape):
		self.shape = shape
	def set_topleft(self,topleft):
		self.topleft = topleft
	def set_ntrigs(self,ntrigs):
		self.ntrigs = ntrigs
	def set_sleeptime(self,sleeptime):
		self.sleeptime = sleeptime
	def set_pulserStatus(self,pulserStatus):
		self.pulserStatus = pulserStatus
	def enable_block(self,system,chess_control):
		chess_control.enable_block(system,topleft=self.topleft,shape=self.shape,which_matrix=self.matrix,all_matrices=False)
	def set_scan_type(self,scan_type):
		#scan_type is "threshold_scan" or "baseline_scan"
		if scan_type == "threshold_scan":
			self.is_th_scan = True
		elif scan_type == "baseline_scan":
			self.is_bl_scan = True
		else:
			raise("set_scan_type(scan_type) takes 'threshold_scan' or 'baseline_scan'")
	def set_fixed_threshold(self,th):
		if self.scan_type == "threshold_scan": raise("Error: setting fixed threshold for threshold scan")
		self.fixed_threshold = th
	def set_thresholds(self,thresholds):
		self.thresholds = thresholds
	def set_baselines(self,baselines):
		self.baselines = baselines
	def save_fig(self,hist_fig,val):
		#save figure to Desktop
		fig_filename = "ntrigs_"+str(self.ntrigs)+"_sleeptime_"+str(self.sleeptime)+"ms_pulser_"+self.pulserStatus+"_"+self.val_field+"_"+str(val)+".png"
		hist_fig.fig.savefig(self.fig_savedir+"/"+fig_filename)
		print("Just saved fig")

	def scan(self,system,eventReader):
		if self.val_field == "None": raise("FIELD NOT SET FOR SCAN TEST")
		if self.is_bl_scan:
			system.feb.dac.dacPIXTHRaw.set(self.fixed_threshold)
		for val in self.val_range:
			eval("system.feb."+self.feb_field+"."+self.val_field+".set("+str(val)+")")
			if self.is_th_scan: 
				x_list = self.thresholds
				x_label = "Threshold Voltage (~3.3V at channel 4096)"
			elif self.is_bl_scan: 
				x_list = self.baselines
				x_label = "Baseline Voltage (units unknown)"
			else: 
				raise("neither is_th_scan nor is_bl_scan")
			if len(x_list) == 0: 
				raise("length of x_list is zero")

			fig_title = "ntrigs="+str(self.ntrigs)+",sleeptime="+str(self.sleeptime)+"ms,pulser="+self.pulserStatus+","+self.val_field+"="+str(val)	
			hist_fig = Hist_Plotter(self.shape,x_list,x_label,fig_title)
			hist_fig.show()

			for x in x_list:
				if self.is_th_scan:
					system.feb.dac.dacPIXTHRaw.set(x)
				else:
					system.feb.dac.dacBLRaw.set(x)
					system.feb.dac.dacBLRRaw.set(x+144) 
				eventReader.hitmap_reset()
				system.feb.sysReg.timingMode.set(0x0) #enable data stream
				print("taking data")
				trig_count = 0
				while trig_count < self.ntrigs:
					time.sleep(self.sleeptime/1000.0)
					system.feb.sysReg.softTrig()
					trig_count += 1
				#time.sleep(2.0)
				#system.ReadAll()
				system.feb.sysReg.timingMode.set(0x3) #stop taking data
				eventReader.hitmap_plot()
				#hist_fig.add_data(eventReader.plotter.data1[self.topleft[0]:self.topleft[0]+8,self.topleft[1]][np.newaxis])
				eval("hist_fig.add_data(eventReader.plotter.data"+str(self.matrix)+"[self.topleft[0]:self.topleft[0]+self.shape[0],self.topleft[1]:self.topleft[1]+self.shape[1]])")
				hist_fig.plot()
			self.save_fig(hist_fig,val)
			hist_fig.close()
			del hist_fig

