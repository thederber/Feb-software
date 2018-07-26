from Hist_Plotter import Hist_Plotter
import numpy as np
from datetime import datetime

current_date = datetime.now().date().strftime("%Y-%m-%d_%H-%M")

class ScanTest():
	def __init__(self,matrix=0,feb_field="None",val_field="None",val_range=range(0x0,0x1F),shape=(1,8),topleft=(0,0),pulserStatus="ON"):
		self.pulserStatus = "ON"
		self.matrix = matrix
		self.feb_field = feb_field
		self.val_field = val_field
		self.val_range = val_range
		self.shape = shape
		self.topleft = topleft
		self.fixed_threshold = None
		self.thresholds = None
		self.baselines = None
		self.scan_type = None
		self.is_th_scan = False
		self.is_bl_scan = False
	def set_matrix(self,matrix):
		self.matrix = matrix
	def set_val_field(self,val_field):
		self.val_field = val_field
	def set_val_range(self,val_range):
		self.val_range = val_range
	def set_shape(self,shape):
		self.shape = shape
	def set_topleft(self,topleft):
		self.topleft = topleft
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
	def scan(self,system,eventReader):
		if self.val_field == "None": raise("FIELD NOT SET FOR SCAN TEST")
		if self.is_bl_scan:
			system.feb.dac.dacPIXTHRaw.set(self.fixed_threshold)
		for val in self.val_range:
			eval("system.feb."+self.feb_field+"."+self.val_field+".set("+str(val)+")")
			if self.is_th_scan: 
				x_list = self.thresholds
			elif self.is_bl_scan: 
				x_list = self.baselines
			else: 
				raise("neither is_th_scan nor is_bl_scan")

			if len(x_list) == 0: 
				raise("length of x_list is zero")
			hist_fig = Hist_Plotter(self.shape,x_list)
			hist_fig.show()
			for x in x_list:
				if self.is_th_scan:
					system.feb.dac.dacPIXTHRaw.set(x)
				else:
					system.feb.dac.dacBLRaw.set(x)
				#system.feb.dac.dacBLRRaw.set(bl+144)
				eventReader.hitmap_reset()
				system.feb.sysReg.timingMode.set(0x0) #start taking data (through _acceptFrame in eventReader)
				time.sleep(.05)
				print("taking data")
				system.feb.sysReg.timingMode.set(0x3) #stop
				eventReader.hitmap_plot()
				hist_fig.add_data(eventReader.plotter.data1[self.topleft[0]:self.topleft[0]+8,self.topleft[1]][np.newaxis])
				#eval("hist_fig.add_data(eventReader.plotter.data"+self.matrix+"[self.topleft[0]:self.topleft[0]+"+self.shape[1]+",self.topleft[1]][np.newaxis])")
				hist_fig.plot()
			hist_fig.fig.savefig("/home/herve/Desktop/Chess2Data/noise_plots_"+current_date+"/pulser_"+self.pulserStatus+"_"+self.val_field+"_scan_"+str(val)+".png")
			print("Just saved fig")
			hist_fig.close()
			del hist_fig

