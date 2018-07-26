# load the configure file, (you could use defaultsR2_test.yml )
# disable and enable all the pixels
import time


def write_config(system,path,threshold,BL):
	filename = path+"/data_BL_"+str(BL)+"_Threshold_"+str(threshold)
	system.dataWriter.dataFile.set(filename) # set the data file name

def write_frames(system,nFrames = 20, timeout = 0.1):
	stoptime = time.time() + timeout
#	system.dataWriter._setOpen(system.dataWriter,system.dataWriter.open,True,1)  #open the .dat file
#	system.feb.sysReg.timingMode.set(0x0) # 0x0 stands for Lemo timing mode
	# add how many data you want to save, for example how many frames 
	while system.dataWriter._getFrameCount(system.dataWriter,system.dataWriter._getFrameCount) < nFrames and time.time() < stoptime:
		#get 'nframes' frames for this configuration 
		pass
#	system.dataWriter._setOpen(system.dataWriter,system.dataWriter.open,False,1) #close the file
	return system.dataWriter._getFrameCount(system.dataWriter,system.dataWriter._getFrameCount)

