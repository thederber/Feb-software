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
		self.fixed_baseline = None
		self.scan_type = None 
		self.is_th_scan = False
		self.is_bl_scan = False

		self.scan_dir = "../../Chess2Data/noise_"+NOW
		self.data_savedir = self.scan_dir+"/data"
		self.fig_savedir = self.scan_dir+"/plots"
		self.config_file_dir = self.scan_dir+"/config"

		if not os.path.isdir(self.data_savedir): os.makedirs(self.data_savedir)
		if not os.path.isdir(self.fig_savedir): os.makedirs(self.fig_savedir)
		if not os.path.isdir(self.config_file_dir): os.makedirs(self.config_file_dir)
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
	def set_fixed_baseline(self,bl):
		if self.scan_type == "baseline_scan": raise("Error: setting fixed bl for thresh scan")
		self.fixed_baseline = bl
	def set_thresholds(self,thresholds):
		self.thresholds = thresholds
	def set_baselines(self,baselines):
		self.baselines = baselines
	def save_fig(self,hist_fig,val):
		#save figure to Desktop
		fig_filename = "ntrigs_"+str(self.ntrigs)+"_sleeptime_"+str(self.sleeptime)+"ms_pulser_"+self.pulserStatus+"_"+self.val_field+"_"+str(val)+".png"
		hist_fig.fig.savefig(self.fig_savedir+"/"+fig_filename)
		print("Just saved fig")
	def save_fig_config(self,val,field_vals_msg):
		fig_config_filename = "ntrigs_"+str(self.ntrigs)+"_sleeptime_"+str(self.sleeptime)+"ms_pulser_"+self.pulserStatus+"_"+self.val_field+"_"+str(val)+"_config.txt"
		with open(self.config_file_dir+"/"+fig_config_filename,"w") as f:
			f.write(field_vals_msg)
		f.close()

	def get_plot_config_msg(self,system,val,val_fields,start_time,stop_time):
		msg = "Start: "+start_time.strftime("%c")+"\t Stop: "+stop_time.strftime("%c")+"\n"
		deltatime = stop_time-start_time
		msg += "Delta: "+str(deltatime.seconds)+" seconds\n"
		msg += "ntrigs: "+str(self.ntrigs)+"\n"
		msg += "sleeptime: "+str(self.sleeptime)+"ms between trigs\n"
		msg += "pulser: "+self.pulserStatus+"\n"
		if self.is_th_scan: msg += "Baseline channel: "+str(self.fixed_baseline)+"\n"
		else: msg += "Threshold channel: "+str(self.fixed_threshold)+"\n"
		msg += "scan_param: "+self.val_field+"\n"
		#now add lines specifying parameter config
		get_param_val_assign_msg = lambda f,v: "param_val = system.feb."+f+"."+v+".get()"
		for i in range(len(val_fields)):
			vf = val_fields[i]
			exec_scope = {'system':system}
			exec(get_param_val_assign_msg(self.feb_field,vf),exec_scope)
			param_val = exec_scope['param_val']
			msg += vf+'='+str(param_val)+'\n'
		return msg
	def save_data_to_csv(self,hist_data,val):
		csv_filename = "ntrigs_"+str(self.ntrigs)+"_sleeptime_"+str(self.sleeptime)+"ms_pulser_"+self.pulserStatus+"_"+self.val_field+"_"+str(val)+".csv"
		f = open(self.data_savedir+"/"+csv_filename,"w")
		for xind in range(len(hist_data)):
			xval = hist_data[xind][0][0][0]
			if self.is_th_scan: f.write("Threshold "+str(xval)+":\n")
			else: f.write("Baseline "+str(xval)+":\n")
			for frameind in range(len(hist_data[xind])):
				f.write("\tFrame "+str(frameind)+":\n")
				for pix in hist_data[xind][frameind]:
					#write line of pix, (th,m,r,c,nhits) w/o th
					msg = "\t\t"+str(pix[1])
					for v in pix[2:]: 
						msg += ","+str(v)
					msg += "\n"
					f.write(msg)	
		f.close()
	def scan(self,system,eventReader,val_fields):
		if self.val_field == "None": raise("FIELD NOT SET FOR SCAN TEST")
		if self.is_th_scan: 
			system.feb.dac.dacBLRaw.set(self.fixed_baseline)
		else:
			system.feb.dac.dacPIXTHRaw.set(self.fixed_threshold)
		for val in self.val_range:
			start_time = datetime.now()
			eval("system.feb."+self.feb_field+"."+self.val_field+".set("+str(val)+")")
			if self.is_th_scan: 
				x_list = self.thresholds
				x_label = "Threshold Voltage Channel (~3.3V at channel 4096)"
			else: 
				x_list = self.baselines
				x_label = "Baseline Voltage Channel (~3.3V at channel 4096)"
			if len(x_list) == 0: 
				raise("length of x_list is zero")

			fig_title = "ntrigs="+str(self.ntrigs)+",sleeptime="+str(self.sleeptime)+"ms,pulser="+self.pulserStatus+","+self.val_field+"="+str(val)+" (see config file)"
			if self.is_th_scan: vline_x = system.feb.dac.dacBLRaw.get()
			else: vline_x = system.feb.dac.dacPIXTHRaw.get()
			hist_fig = Hist_Plotter(self.shape,x_list,x_label,fig_title,vline_x)
			hist_fig.show()
			#x is threshold or baseline
			hist_data = []
			for x in x_list:
				if self.is_th_scan:
					system.feb.dac.dacPIXTHRaw.set(x)
				else:
					#BL and BLR should be 144 from each other
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
				system.feb.sysReg.timingMode.set(0x3) #stop taking data
				eventReader.hitmap_plot()
				eval("hist_fig.add_data(eventReader.plotter.data"+str(self.matrix)+"[self.topleft[0]:self.topleft[0]+self.shape[0],self.topleft[1]:self.topleft[1]+self.shape[1]])")
				hist_fig.plot()
				#before appending to hist data, insert threshold into each pix hit
				dfs = eventReader.data_frames
				print("Data frames:",dfs)
				for i in range(len(dfs)):
					for j in range(len(dfs[i])):
						dfs[i][j].insert(0,x)
				if len(dfs) > 0: 
					hist_data.append(dfs)
				eventReader.reset_data_frames()
			#save plots,configs,and csvs
			stop_time = datetime.now()
			self.save_fig(hist_fig,val)
			plot_config_msg = self.get_plot_config_msg(system,val,val_fields,start_time,stop_time)
			self.save_fig_config(val,plot_config_msg)
			hist_fig.close()
			del hist_fig
			#save csv files with data from hist_data
			print(hist_data[0])
			self.save_data_to_csv(hist_data,val)
