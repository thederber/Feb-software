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
#define CI_DAC_INIT_VALUE_MEM_OFFSET (BUS_OFFSET+0x0004000C)
#define CI_DAC_END_VALUE_MEM_OFFSET (BUS_OFFSET+0x00040010)
#define CI_DELAY_VALUE_MEM_OFFSET (BUS_OFFSET+0x00040014)
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


void swCallibInterruptHandler(void * ciTestRequestFlag) {
	//local variables
	uint32_t request = (uint32_t)Xil_In32(CIEVENTSCOUNTER_MEM_OFFSET);
    uint32_t * flag    = (uint32_t *)ciTestRequestFlag;
	
	//sanity check to see it works from the software
	xil_printf("CallibInterruptHandler REQ %d\n", request);
	request = request + 1;
	Xil_Out32(CIEVENTSCOUNTER_MEM_OFFSET, request);   //
    *flag = 1;
}


void swChargeInjectTest() {
	//local variables
	uint32_t dacDefaultValue = Xil_In32(DAC_TH_MEM_OFFSET);
	uint32_t seq_num = 0, num_counts;
    uint32_t dacInitValue = Xil_In32(CI_DAC_INIT_VALUE_MEM_OFFSET);
    uint32_t dacEndValue = Xil_In32(CI_DAC_END_VALUE_MEM_OFFSET);
    uint32_t dacDelayValue = Xil_In32(CI_DELAY_VALUE_MEM_OFFSET);
	
	//sanity check to see it works from the software
	xil_printf("Seq. # %d\n", seq_num); seq_num = seq_num + 1;
	//--------------------------
	// start testing procedure
	//--------------------------
	// set DAC to 0
	 
	Xil_Out32(DAC_TH_MEM_OFFSET, dacInitValue);
	xil_printf("Seq. # %d\n", seq_num); seq_num = seq_num + 1;
	// wait to settle	
	MB_Sleep(dacDelayValue);
	xil_printf("Seq. # %d, delay_counts %d\n", seq_num, num_counts); seq_num = seq_num + 1;
	// set to full scale
	Xil_Out32(DAC_TH_MEM_OFFSET, dacEndValue);
	// calibration injection cmd
	Xil_Out32(CI_CMD_MEM_OFFSET, 0x00000001);
	Xil_Out32(CI_CMD_MEM_OFFSET, 0x00000000);
	xil_printf("Seq. # %d\n", seq_num); seq_num = seq_num + 1;
	// wait to finish test
	MB_Sleep(dacDelayValue);
	xil_printf("Seq. # %d, delay_counts %d\n", seq_num, num_counts); seq_num = seq_num + 1;
	// restore DAC value
	Xil_Out32(DAC_TH_MEM_OFFSET, dacDefaultValue);
	xil_printf("Seq. # %d\n", seq_num); seq_num = seq_num + 1;
	
}




//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// Helper functions
//-----------------------------------------------------------------------



//-----------------------------------------------------------------------
//-----------------------------------------------------------------------
// Main function 
//-----------------------------------------------------------------------
int main(){      

	volatile uint32_t adcReq = 0;
	volatile uint32_t cfgReqNo = 0;
	volatile uint32_t heartBeatCounter = 0;
	volatile uint32_t numOfChargeInjEvents = 0;
    volatile uint32_t ciTestRequestFlag = 0;

    //setup variables and IRQ functions
    XIntc_Initialize(&intc,XPAR_AXI_INTC_0_DEVICE_ID);
    microblaze_enable_interrupts();
    XIntc_Connect(&intc,0,(XInterruptHandler)heartBeatInterruptHandler,(void*)&heartBeatCounter);
    XIntc_Connect(&intc,1,(XInterruptHandler)swCallibInterruptHandler,(void*)&ciTestRequestFlag);
    XIntc_Start(&intc,XIN_REAL_MODE);
    XIntc_Enable(&intc,0);
    XIntc_Enable(&intc,1);

    //ssi_printf_init(LOG_MEM_OFFSET, 1024*4);
    //ssi_printf("Program started\n");
    xil_printf("Program started\n");
    
    // testes write and read from an axi register
    Xil_Out32(BUS_OFFSET+0x4, 0x12340002);   //write in a known scratch pad register a value that shows it is alive
    xil_printf("Program started %x\n", Xil_In32(BUS_OFFSET+0x4));
    
    // init counter reg value
    Xil_Out32(CIEVENTSCOUNTER_MEM_OFFSET, 0);
    
    //update registers as uc is initialized
    Xil_Out32(HEARTBEAT_MEM_OFFSET, numOfChargeInjEvents);  
    
    //infinite loop that waits for IRQ requests
    int delayReturn;
    while(1){
    	
    	//write in a known scratch pad register a value that shows it is alive
    	Xil_Out32(BUS_OFFSET+0x4, adcReq);   
        if (ciTestRequestFlag == 1){
            ciTestRequestFlag = 0;
            swChargeInjectTest();
        }
    	MB_Sleep(1);
    	adcReq = adcReq + 1;
    	//asm("nop");
    }
}
