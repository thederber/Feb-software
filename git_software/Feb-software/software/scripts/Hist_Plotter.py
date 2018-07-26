import matplotlib.pyplot as plt
import matplotlib
from matplotlib.lines import Line2D
import numpy as np

class Hist_Plotter:
	def __init__(self,shape,x_list):
		#shape is (rows,cols) of 
		self.x_data = [0]
		self.x_data.extend(x_list)
		self.data = np.zeros(shape) 
		self.fig, self.ax = plt.subplots(1,1)
		self.lines = self.ax.plot(self.data)
		self.ax.set_autoscale_on(True)
		self.ax.set_xlim(x_list[0],x_list[-1])
		self.background = self.fig.canvas.copy_from_bbox(self.ax.bbox)

	def add_data(self,data):
		self.data = np.concatenate((self.data,data))

	def show(self):
		plt.pause(0.2)

	def close(self):
		plt.close(self.fig)
		
	def plot(self):
		self.fig.canvas.restore_region(self.background)
		#self.ax.relim()
		#self.ax.autoscale_view(True,True,True)
		for i in range(len(self.lines)):
			line_y = self.data[:,i].tolist()
			self.lines[i].set_data(self.x_data[1:len(line_y)], line_y[1:])
			self.ax.relim()
			self.ax.autoscale_view(True,True,True)
			self.ax.draw_artist(self.lines[i])
		#self.ax.relim()
		#self.ax.autoscale_view(True,True,True)
		self.fig.canvas.blit(self.ax.bbox)

