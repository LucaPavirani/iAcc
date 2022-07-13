/* ========================================
 *
 * EEPROM header file.
 *
 * ========================================
*/

#ifndef __EEPROM_Custom_H
    #define __EEPROM_Custom_H
    
    #include "ErrorCodes.h"
    #include "cytypes.h"
    
    /**
    *   \brief Base address of the EEPROM memory in absolute address space - pointer
    */
    #define EEPROM_BASE_ADDRESS CYDEV_EE_BASE 
    
    /**
    *   \brief Base address remapped - is base address, not a pointer - 
    *   This has to be used with EEPROM API: EEPROM_Read/WriteByte.
    */
    #define EEPROM_BASE_ADDRESS_0 0x00
    
    /*********************************************
    *   RMK: each row of the EEPROM is 16 Bytes. 
    *   We can start writing at first row (0x00) and keep increasing the row as we need to write new data.
    **********************************************/
    
    /** \brief Start the EEPROM.
    *   
    *   This function starts the EEPROM so that it is ready to work.
    */
    ErrorCode EEPROM_Custom_Start(void);

    /** \brief Stop the EEPROM.
    *   
    *   This function stops the EEPROM so that it is ready to work.
    */
    ErrorCode EEPROM_Custom_Stop(void);
    
    /** \brief Save status.
    *   
    *   This function saves the FS and sensitivity values in the EEPROM.
    */
    void EEPROM_save_status(uint8_t FullScale,uint8_t Sensitivity[]);
    
    /** \brief Retrieve FS.
    *   
    *   This function uploads the FS (2 bits) value from the EEPROM (values were saved in a previous session).
    */
    uint8 EEPROM_retrieve_FS(void);
    
     /** \brief Retrieve So.
    *   
    *   This function uploads sensitivity (2 bits) value from the EEPROM (values were saved in a previous session).
    */
    uint8 EEPROM_retrieve_So_lsb(void); // data goes in CTRL_REG_4[3] 
    uint8 EEPROM_retrieve_So_msb(void); // data goes in CTRL_REG_1[3]
   
#endif

/* [] END OF FILE */
