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
  
  def toggle_pixel(self,system,row,col,enable=1,which_matrix=0,all_matrices=True):
    chargeInj = 1 if enable else 0

    if all_matrices:
        for i in range(0,3):
            eval("system.feb.Chess2Ctrl"+str(i)+".writePixel(enable="+str(enable)+",chargeInj="+str(chargeInj)+",col=col,row=row)")
    else:
        eval("system.feb.Chess2Ctrl"+str(which_matrix)+".writePixel(enable="+str(enable)+",chargeInj="+str(chargeInj)+",col=col,row=row)")

  def toggle_block(self,system,topleft,shape=(8,1),enable=1,which_matrix=0,all_matrices=True):
    for r in range(shape[0]):
      for c in range(shape[1]):
        self.toggle_pixel(system,topleft[0]+r,topleft[1]+c,enable=enable,which_matrix=which_matrix,all_matrices=all_matrices)

  def enable_block(self,system,topleft,shape=(8,1),which_matrix=0,all_matrices=True):
    self.toggle_block(system,topleft,shape=shape,enable=1,which_matrix=which_matrix,all_matrices=all_matrices)
  def disable_block(self,system,topleft,shape=(8,1),which_matrix=0,all_matrices=True):
    self.toggle_block(system,topleft,shape=shape,enable=0,which_matrix=which_matrix,all_matrices=all_matrices)
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

  def get_val(self,system,feb_field,val_field):
    return eval("system.feb."+feb_field+"."+val_field+".get()")



