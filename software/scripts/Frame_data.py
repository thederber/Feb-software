import numpy as np
import sys
np.set_printoptions(threshold=np.inf)

nrows = 128
ncols = 32

class Frame_data():
	def __init__(self,frame=None):
		self.frame = frame

		self.dvflag_M0=[]
		self.mhflag_M0=[]
		self.col_M0=[]
		self.row_M0=[]

		self.dvflag_M1=[]
		self.mhflag_M1=[]
		self.col_M1=[]
		self.row_M1=[]

		self.dvflag_M2=[]
		self.mhflag_M2=[]
		self.col_M2=[]
		self.row_M2=[]
		
		self.hitmap_t0 = np.zeros((nrows,ncols))
		self.hitmap_t1 = np.zeros((nrows,ncols))
		self.hitmap_t2 = np.zeros((nrows,ncols))

	def __str__(self):
		msg = str("Hitmap 0 (self.hitmap_t0):"+str(self.hitmap_t0)+"\n")
		msg += str("Hitmap 1 (self.hitmap_t1):"+str(self.hitmap_t1)+"\n")
		msg += str("Hitmap 2 (self.hitmap_t2):"+str(self.hitmap_t2)+"\n")
		return msg

	@classmethod
	def decode_data_16b(cls,dat):
		row = dat[0] & 0x7F
		col = ((dat[1] & 0x0F) << 1) | (dat[0] >> 7)
		multi_hit  = (dat[1] & 0x10) >> 4
		data_valid = (dat[1] & 0x20) >> 5
		#dec_ok     = (dat[1] & 0xC0) >> 6
		return data_valid, multi_hit, col, row

	def decode_data(self,dat):
		if not all(d == 0 for d in dat): #To speed things up - most frames have empty data
			for i in range(0,len(dat),8):
				[li.append(el) for el,li in zip(list(self.decode_data_16b(dat[i+0:i+2])),[self.dvflag_M0, self.mhflag_M0, self.col_M0, self.row_M0])]
				[li.append(el) for el,li in zip(list(self.decode_data_16b(dat[i+2:i+4])),[self.dvflag_M1, self.mhflag_M1, self.col_M1, self.row_M1])]
				[li.append(el) for el,li in zip(list(self.decode_data_16b(dat[i+4:i+6])),[self.dvflag_M2, self.mhflag_M2, self.col_M2, self.row_M2])]

				self.hitmap_t0[self.row_M0[-1]][self.col_M0[-1]] += self.dvflag_M0[-1]
				self.hitmap_t1[self.row_M1[-1]][self.col_M1[-1]] += self.dvflag_M1[-1]
				self.hitmap_t2[self.row_M2[-1]][self.col_M2[-1]] += self.dvflag_M2[-1]

	def decode_header(self, header):
		self.virt_chan_id = header[0] & 0x01
		self.dest_id      = header[0] & 0xFC
		self.transact_id  = (header[3] <<16) & (header[2] << 8) & header[1]
		self.acq_cnt      = (header[5] << 8) & header[4]
		self.op_code      = header[6]
		self.elem_id      = header[7] & 0x0F
		self.dest_z_id    = header[7] >> 4
		self.frame_nb     = (header[11] << 8*3) & (header[10] << 8*2) & (header[9] << 8) & header[8]
		self.ticks        = (header[15] << 8*3) & (header[14] << 8*2) & (header[13] << 8) & header[12]
		self.fiducials    = (header[19] << 8*3) & (header[18] << 8*2) & (header[17] << 8) & header[16]
		self.sbtemp       = [	(header[27] <<8  & header[26]),
					(header[25] <<8  & header[24]),
					(header[23] <<8  & header[22]),
					(header[21] <<8  & header[20])]
		self.frame_typ    = (header[31] << 8*3) & (header[30] << 8*2) & (header[29] << 8) & header[28]

	def decode_frame(self):
		header, data = self.frame[:32],self.frame[32:]
		self.decode_data(data)
		self.decode_header(header)
	def get_data(self):
		#return chunk of data about most recent frame
		datalines = []
		for m in range(3):
			this_hitmap = eval("self.hitmap_t"+str(m))
			for r in range(nrows):
				for c in range(ncols):	
					nhits = int(this_hitmap[r][c])
					if nhits > 0:
						datalines.append([m,r,c,nhits])
		return datalines	
	def get_att_vals(self,system,feb_field,val_fields):
		#values of interest: VNLogicatt,VNSFatt,VNatt,VPFBatt,VPLoadatt,VPTrimatt	
		vfs = []
		for vf in val_fields:
			vfs.append(chess_control.get_val(system,feb_field,vf))
		return vfs
	def print_valid_data(self):
		#We check if we have non-empty lists
		if self.dvflag_M0 or self.dvflag_M1 or self.dvflag_M2:
			print("Matrix 0 - Row: {0}, Col: {1}".format(self.row_M0,self.col_M0))
			print("Matrix 1 - Row: {0}, Col: {1}".format(self.row_M1,self.col_M1))
			print("Matrix 2 - Row: {0}, Col: {1}".format(self.row_M2,self.col_M2))
