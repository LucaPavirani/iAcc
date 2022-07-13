
#ifndef __INTERRUPT_ROUTINES_H
    #define __INTERRUPT_ROUTINES_H
    
    #include "cytypes.h"
    #include "stdio.h"
    
    uint8_t status;
    uint8_t flag_FS;
    uint8_t flag_So;
    
    uint8_t status;
    
    CY_ISR_PROTO (Custom_ISR_RX);
    
    volatile uint8 PacketReadyFlag;
#endif

/* [] END OF FILE */
