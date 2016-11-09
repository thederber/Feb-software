#include <stdio.h>
#include <string.h>

#include "xil_types.h"
#include "xil_io.h"

#define BUS_OFFSET  0x80000000
#define AXI_VERSION (BUS_OFFSET+0x00000000)
#define AXI_MEMORY  (BUS_OFFSET+0x00020000)

int main(){      
   while(1){
      asm("nop");
   }
}
