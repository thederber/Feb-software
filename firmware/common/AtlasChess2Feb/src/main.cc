#include <stdio.h>
#include <string.h>
//
#include "xil_types.h"
#include "xil_io.h"
//
#include "xintc.h"
#include "xparameters.h"
#include "microblaze_sleep.h"
#include "xil_printf.h"
//#include "regs.h"
//#include "ssi_printf.h"
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// GLOBAL CONSTANTS
//-----------------------------------------------------------------------
#define BUS_OFFSET  0x80000000
#define AXI_VERSION (BUS_OFFSET+0x00000000)
#define AXI_MEMORY  (BUS_OFFSET+0x00020000)
#define LOG_MEM_OFFSET (BUS_OFFSET+0x00040000)
#define HEARTBEAT_MEM_OFFSET (BUS_OFFSET+0x00040004)
#define CIEVENTSCOUNTER_MEM_OFFSET (BUS_OFFSET+0x00040008)
#define DAC_TH_MEM_OFFSET (BUS_OFFSET+0x00100004)
#define CI_CMD_MEM_OFFSET (BUS_OFFSET+0x00330010)
//
#define TARGET_LINK_PGP 1
#define TARGET_LINK_ETHERNET 2
#define TARGET_LINK TARGET_LINK_PGP

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// GLOBAL VARIABLES
//-----------------------------------------------------------------------
static XIntc intc;


//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// Function declarations
//-----------------------------------------------------------------------
int delay(uint32_t);
//void swCallibInterruptHandler(void);
//void heartBeatInterruptHandler(void);

//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// IRQ called functions
//-----------------------------------------------------------------------
void heartBeatInterruptHandler(void * data) {

	uint32_t * request = (uint32_t *)data;
    //ssi_printf("heartBeatInterruptHandler REQ %d\n", *request);
	//xil_printf("heartBeatInterruptHandler REQ %d\n", *request);
	*request = *request + 1;
	Xil_Out32(HEARTBEAT_MEM_OFFSET, *request);   //
}




void swCallibInterruptHandler(void * data) {
	//local variables
	uint32_t * request = (uint32_t *)data;
	uint32_t dacInitialValue = Xil_In32(DAC_TH_MEM_OFFSET);
	
	//sanity check to see it works from the software
	xil_printf("CallibInterruptHandler REQ %d\n", *request);
	*request = *request + 1;
	Xil_Out32(CIEVENTSCOUNTER_MEM_OFFSET, *request);   //
	
	//--------------------------
	// start testing procedure
	//--------------------------
	// set DAC to 0
	Xil_Out32(DAC_TH_MEM_OFFSET, 0x00000FFF);
	// wait to settle
	delay(100);
	// set to full scale
	Xil_Out32(DAC_TH_MEM_OFFSET, 0x00000000);
	// calibration injection cmd
	Xil_Out32(CI_CMD_MEM_OFFSET, 0x00000001);
	Xil_Out32(CI_CMD_MEM_OFFSET, 0x00000000);
	// wait to finish test
	delay(100);
	// restore DAC value
	Xil_Out32(DAC_TH_MEM_OFFSET, dacInitialValue);
	
	

}




//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// Helper functions
//-----------------------------------------------------------------------
//Delay function in microseconds delayTime
int delay(uint32_t delayTime){
	uint32_t counter = 0;
	uint32_t delayTimeInClockCycles = 0;
	//xil_printf("Started custom delay\n");
    
    // converts microseconds into number of clock cycles based on the 
    // clock frequency available which depends on the comm. link.
    if (TARGET_LINK == TARGET_LINK_PGP){
        delayTimeInClockCycles = delayTime * 156;
    } else{
        delayTimeInClockCycles = delayTime * 125;
    }

    // wait for the requested time
    while (counter<delayTimeInClockCycles){
        counter = counter+1;
    }
    //return true when done
    return 0;
}
//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// Main function 
//-----------------------------------------------------------------------
int main(){      

	volatile uint32_t adcReq = 0;
	volatile uint32_t cfgReqNo = 0;
	volatile uint32_t heartBeatCounter = 0;
	volatile uint32_t numOfChargeInjEvents = 0;

    //setup variables and IRQ functions
    XIntc_Initialize(&intc,XPAR_AXI_INTC_0_DEVICE_ID);
    microblaze_enable_interrupts();
    XIntc_Connect(&intc,0,(XInterruptHandler)heartBeatInterruptHandler,(void*)&heartBeatCounter);
    XIntc_Connect(&intc,1,(XInterruptHandler)swCallibInterruptHandler,(void*)&numOfChargeInjEvents);
    XIntc_Start(&intc,XIN_REAL_MODE);
    XIntc_Enable(&intc,0);
    XIntc_Enable(&intc,1);

    //ssi_printf_init(LOG_MEM_OFFSET, 1024*4);
    //ssi_printf("Program started\n");
    xil_printf("Program started\n");
    
    // testes write and read from an axi register
    Xil_Out32(BUS_OFFSET+0x4, 0x12340002);   //write in a known scratch pad register a value that shows it is alive
    xil_printf("Program started %x\n", Xil_In32(BUS_OFFSET+0x4));
    
    
    //update registers as uc is initialized
    Xil_Out32(HEARTBEAT_MEM_OFFSET, numOfChargeInjEvents);  
    
    //infinite loop that waits for IRQ requests
    int delayReturn;
    while(1){
    	
    	//write in a known scratch pad register a value that shows it is alive
    	Xil_Out32(BUS_OFFSET+0x4, adcReq);   
    	delayReturn = delay(10000);
    	adcReq = adcReq + 1;
    	//asm("nop");
    }
}
