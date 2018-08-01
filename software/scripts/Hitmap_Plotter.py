import matplotlib.pyplot as plt
import matplotlib
import numpy as np

class Hitmap_Plotter:
	def __init__(self):
		self.data0 = np.zeros((128,32))
		self.data1 = np.zeros((128,32))
		self.data2 = np.zeros((128,32))
		self.fig, (self.ax0,self.ax1,self.ax2) = plt.subplots(3,1)
		self.im0 = self.ax0.imshow(self.data0,cmap='jet', aspect='auto',vmin=0,vmax=1)
		self.im1 = self.ax1.imshow(self.data1,cmap='jet', aspect='auto',vmin=0,vmax=1)
		self.im2 = self.ax2.imshow(self.data2,cmap='jet', aspect='auto',vmin=0,vmax=1)
		self.background0 = self.fig.canvas.copy_from_bbox(self.ax0.bbox)
		self.background1 = self.fig.canvas.copy_from_bbox(self.ax1.bbox)
		self.background2 = self.fig.canvas.copy_from_bbox(self.ax2.bbox)

	def add_data(self,data0,data1,data2):
		self.data0 = data0
		self.data1 = data1
		self.data2 = data2

	def show(self):
		plt.pause(0.2)
		
	def plot(self):
		self.fig.canvas.restore_region(self.background0)
		self.fig.canvas.restore_region(self.background1)
		self.fig.canvas.restore_region(self.background2)
		self.im0.set_data(self.data0/max(1,np.max(self.data0)))
		self.im1.set_data(self.data1/max(1,np.max(self.data1)))
		self.im2.set_data(self.data2/max(1,np.max(self.data2)))
		self.ax0.draw_artist(self.im0)
		self.ax1.draw_artist(self.im1)
		self.ax2.draw_artist(self.im2)
		self.fig.canvas.blit(self.ax0.bbox)
		self.fig.canvas.blit(self.ax1.bbox)
		self.fig.canvas.blit(self.ax2.bbox)

