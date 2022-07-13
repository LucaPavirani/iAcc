// Include header
#include "InterruptRoutinesBT.h"

// Include required header files
#include "project.h"
#include "LIS3DH.h"

uint8 ch_received;
uint16_t FS_received;
uint16_t So_received;

CY_ISR(Custom_ISR_RX_BT)
{
    // Non-blocking call to get the latest data recieved
    ch_received = UART_BT_GetChar();
    FS_received = UART_BT_GetByte();   // byte contains FS values
    So_received = UART_BT_GetByte();   // byte contains So values

        
    // Set flags based on UART command
    switch(ch_received)
    {
        //start recording
        case 'A':
        case 'a':
            status = 2;
            break;
        
        //stop recording
        case 'S':
        case 's':
            status = 0;
            break;
        
        //connection
        case 'T':
        case 't':
            UART_BT_PutString("HR/RR sensor");
            //UART_PutString("HR/RR sensor");
            break;
        
        /*
        //initialization
        case 'I':
        case 'i':
            status = 1;
            break;
            
            
        //turn off
        case 'X':
        case 'x':
            status = 4;
            break;
        Since UART is not used */     
            
        default:
            break;    
    }
    
    // Set flags and FS and So values on user modifications.
    switch (FS_received)
    {
        case FS2:
            FS = FS2;
            flag_FS = 1;
            break;
        
        case FS4:
            FS = FS2;
            flag_FS = 1;
            break;
        
        case FS8:
            FS = FS2;
            flag_FS = 1;
            break;
        
        case FS16:
            FS = FS2;
            flag_FS = 1;
            break;
        
        default:
        break;
    }
    
    switch (So_received)
    {
        case LP: //10
            So[0] = 0;
            So[1] = 1;
            flag_So = 1;
            break;
        
        case Normal: //00
            So[0] = 0;
            So[1] = 0;
            flag_So = 1;
            
        case HR: //01
            So[0] = 1;
            So[1] = 0;
            flag_So = 1;
            
        case NA:
            break;
            
        default:
        break;
    }
}
/* [] END OF FILE */
