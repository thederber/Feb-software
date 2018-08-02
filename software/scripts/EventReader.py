import rogue.hardware.pgp
import rogue
import pyrogue.utilities.fileio
import pyrogue.gui
import pyrogue.protocols
import AtlasChess2Feb
from Hitmap_Plotter import Hitmap_Plotter
import numpy as np
from Frame_data import Frame_data

nrows = 128
ncols = 32

class EventReader(rogue.interfaces.stream.Slave):
    def __init__(self):
        rogue.interfaces.stream.Slave.__init__(self)
        self.plotter = Hitmap_Plotter()
        self.counter = 0
        self.reset_hitmaps()
        self.data_frames = []
    def reset_hitmaps(self):    
        self.ev_hitmap_t0 = np.zeros((nrows,ncols))
        self.ev_hitmap_t1 = np.zeros((nrows,ncols))
        self.ev_hitmap_t2 = np.zeros((nrows,ncols))
    def reset_data_frames(self):
        self.data_frames = []

    def _acceptFrame(self,frame):
        p = bytearray(frame.getPayload())
        frame.read(p,0)
        f = Frame_data(p)
        f.decode_frame()
        self.hitmap_update(f)
        csv_data = f.get_data()
        if len(csv_data) > 0:
            self.data_frames.append(csv_data)
        self.counter += 1
        print("Getting frames:"+str(self.counter))

    def hitmap_update(self,frame_data):
        self.ev_hitmap_t0 += frame_data.hitmap_t0
        self.ev_hitmap_t1 += frame_data.hitmap_t1
        self.ev_hitmap_t2 += frame_data.hitmap_t2

    def hitmap_show(self):
        self.plotter.show()

    def hitmap_plot(self):
        self.plotter.add_data(self.ev_hitmap_t0,
                              self.ev_hitmap_t1,
                              self.ev_hitmap_t2)
        self.plotter.plot()

    def hitmap_reset(self):
        self.counter = 0
        self.reset_hitmaps()

    def hitmap_print(self):
        msg = str("Hitmap 0 (self.hitmap_t0):"+str(self.ev_hitmap_t0)+"\n")
        msg += str("Hitmap 1 (self.hitmap_t1):"+str(self.ev_hitmap_t1)+"\n")
        msg += str("Hitmap 2 (self.hitmap_t2):"+str(self.ev_hitmap_t2)+"\n")
        print(msg)

