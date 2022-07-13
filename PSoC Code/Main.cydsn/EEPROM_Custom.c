/* ========================================
 *
 * This file includes all the required source code to interface
 * the EEPROM
 *
 * ========================================
*/

#include "EEPROM_Custom.h" 
#include "project.h"
#include "ErrorCodes.h"
#include "stdio.h"

ErrorCode EEPROM_Custom_Start(void) 
{
    // Start I2C peripheral
    EEPROM_Start();  
    
    // Return no error since start function does not return any error
    return NO_ERROR;
}

// --------------------------------------------------------------------------------- //

ErrorCode EEPROM_Custom_Stop(void)
{
    // Stop I2C peripheral
    EEPROM_Stop();
    // Return no error since stop function does not return any error
    return NO_ERROR;
}

// --------------------------------------------------------------------------------- //

// error message via UART (better via GUI)

void UART_message(cystatus return_value)
{
    switch(return_value) {
    // messaggi che sarebbero da mandare via GUI?
        case CYRET_SUCCESS:
            UART_PutString("Saving successful \r\n");
            break;
        case CYRET_BAD_PARAM:
            UART_PutString("Bad parameter error\r\n");
            break;
        case CYRET_LOCKED:
            UART_PutString("SPC locked\r\n");
            break;
        case CYRET_UNKNOWN:
            UART_PutString("Unknown error\r\n");
            break;
    }
}

// --------------------------------------------------------------------------------- //

void EEPROM_save_status(uint8_t FullScale, uint8_t Sensitivity[])
{
    // saves Full Scale value
    cystatus return_value = EEPROM_WriteByte(FullScale, EEPROM_BASE_ADDRESS_0);
    UART_PutString("Saving FULL SCALE ... \r\n");
    UART_BT_PutString("Saving FULL SCALE ... \r\n");
    UART_message(return_value);
    
    // Saves Sensitivity value
    return_value = EEPROM_WriteByte(Sensitivity[0], EEPROM_BASE_ADDRESS_0+1);
    return_value = EEPROM_WriteByte(Sensitivity[1], EEPROM_BASE_ADDRESS_0+2);
    UART_PutString("Saving SENSITIVTY ... \r\n");
    UART_BT_PutString("Saving SENSITIVTY ... \r\n");
    UART_message(return_value);
    
}

// --------------------------------------------------------------------------------- //

uint8 EEPROM_retrieve_FS(void)
{
    // read EEPROM and retrieves FS value
    uint8_t FS_read = EEPROM_ReadByte(EEPROM_BASE_ADDRESS_0);
    
    return FS_read;
} 

uint8 EEPROM_retrieve_So_lsb(void)
{
    // read EEPROM and retrieves So value
    uint8_t So_read = EEPROM_ReadByte(EEPROM_BASE_ADDRESS_0+1);
    
    return So_read;
} 

uint8 EEPROM_retrieve_So_msb(void)
{
    // read EEPROM and retrieves So value
    uint8_t So_read = EEPROM_ReadByte(EEPROM_BASE_ADDRESS_0+2);
    
    return So_read;
} 

/* [] END OF FILE */
