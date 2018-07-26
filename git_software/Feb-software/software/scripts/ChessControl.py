import sys
#makes system.feb.Chess2Ctrl commands easier to use
class ChessControl(): 
  def __init__(self):
    self.threshold = 0
    self.nrows = 128
    self.ncols = 32
    #self.starting_coords = [(r,c) for r in range(0,self.nrows-1,8) for c in range(0,self.ncols)]
    #self.starting_coords = [(r,c) for r in range(0,64,8) for c in range(0,32)]
  def set_threshold(self,system,threshold):
    system.feb.dac.dacPIXTHRaw.set(threshold)
  
  def toggle_pixel(self,system,row,col,enable,which_matrix,all_matrices=True):
    chargeInj = 1 if enable else 0

    if all_matrices:
        for i in range(0,3):
            eval("system.feb.Chess2Ctrl"+str(i)+".writePixel(enable="+str(enable)+",chargeInj="+str(chargeInj)+",col=col,row=row)")
    else:
        eval("system.feb.Chess2Ctrl"+str(which_matrix)+".writePixel(enable="+str(enable)+",chargeInj="+str(chargeInj)+",col=col,row=row)")

  def toggle_block_1x8(self,system,topleft,enable,which_matrix=0,all_matrices=True):
    for r in range(topleft[0],topleft[0]+8):
      self.toggle_pixel(system,r,topleft[1],enable,which_matrix,all_matrices)

  def disable_all_pixels(self,system,which_matrix=0,all_matrices=True):
    if all_matrices:
        for i in range(0,3):
            eval("system.feb.Chess2Ctrl"+str(i)+".writeAllPixels(enable=0,chargeInj=0)")
    else:
        eval("system.feb.Chess2Ctrl"+str(which_matrix)+".writeAllPixels(enable=0,chargeInj=0)")
  
  def enable_all_pixels(self,system,which_matrix=0,all_matrices=True):
    if all_matrices:
        for i in range(0,3):
            eval("system.feb.Chess2Ctrl"+str(i)+".writeAllPixels(enable=1,chargeInj=1)")
    else:
        eval("system.feb.Chess2Ctrl"+str(which_matrix)+".writeAllPixels(enable=1,chargeInj=1)")





