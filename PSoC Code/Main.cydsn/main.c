
#include <stdio.h>
#include "project.h"
#include "I2C_Interface.h"
#include "LIS3DH.h"
#include "InterruptRoutines.h"
#include "InterruptRoutinesBT.h"
#include "EEPROM_Custom.h"
#include "Defines.h"

// Set this to 1 to send byte data for the Bridge Control Panel
// Otherwise set it to 0 to send temperature data as int16_t
#define USE_BRIDGECONTROLPANEL  0
uint8_t ovrnReady;
uint8_t emptyBit;
uint8_t reg;
ErrorCode error;

char message[50] = {'\0'};

int main(void)
{
    CyGlobalIntEnable; /* Enable global interrupts. */

    /* Place your initialization/startup code here (e.g. MyInst_Start()) */
    I2C_Peripheral_Start();
    //The user can comment the UART that doesn't use, depending on which is the used one, USB/BT
    UART_BT_Start();
    isr_RX_BT_StartEx(Custom_ISR_RX_BT);
    //UART_Start();
    //isr_RX_StartEx(Custom_ISR_RX);
  
    //EEPROM_Custom_Start();
    
    CyDelay(5); //"The boot procedure is complete about 5 ms after device power-up."
    
    printHeader();
    
    /******************************************/
    /*            I2C Reading                 */
    /******************************************/
          
    /*      I2C Master Read - WHOAMI Register       */
    uint8_t whoami_reg=0x00;
    readReg(whoami_reg,LIS3DH_WHO_AM_I_REG_ADDR);
    
    
    /*      I2C Master Read - STATUS Register       */
    //The PutString commands can be decommented to use them for debugging
    //UART_PutString("\r\nStatus reg \r\n");
    //UART_BT_PutString("\r\nStatus reg \r\n");
    uint8_t status_reg=0x00;
    readReg(status_reg,LIS3DH_STATUS_REG);

    
    /*      I2C Master Read - CTRL Register 1       */
    //UART_PutString("\r\nCTRL reg1 \r\n");
    //UART_BT_PutString("\r\nCTRL reg1 \r\n");
    uint8_t control_reg=0x00;
    readReg(control_reg, LIS3DH_CTRL_REG1);

    /*      I2C Master Read - CTRL Register 3      */
    //UART_PutString("\r\nCTRL reg3 \r\n");
    //UART_BT_PutString("\r\nCTRL reg3 \r\n");
    uint8_t control_reg_3=0x00;
    readReg(control_reg_3, LIS3DH_CTRL_REG3);
    
    /*      I2C Master Read - CTRL Register 4      */
    //UART_PutString("\r\nCTRL reg4 \r\n");
    //UART_BT_PutString("\r\nCTRL reg4 \r\n");
    uint8_t control_reg_4=0x00;
    readReg(control_reg_4, LIS3DH_CTRL_REG4);
    
    /*      I2C Master Read - CTRL Register 5       */
    //UART_PutString("\r\nCTRL reg5 \r\n");
    //UART_BT_PutString("\r\nCTRL reg5 \r\n");
    uint8_t control_reg_5=0x00;
    readReg(control_reg_5, LIS3DH_CTRL_REG5);

    /*      I2C Master Read - FIFO CTRL Register     */
    //UART_PutString("\r\nFIFO REG \r\n");
    //UART_BT_PutString("\r\nFIFO REG \r\n");
    uint8_t FIFO_control_reg=0x00;
    readReg(FIFO_control_reg, LIS3DH_FIFO_CTRL_REG);
   
    
    /******************************************/
    /*       I2C Writing CTRL REG1            */
    /******************************************/
    
    //UART_PutString("\r\nSetting ctrl reg1 \r\n");
    //UART_BT_PutString("\r\nSetting ctrl reg1 \r\n");
    
    if (control_reg != LIS3DH_NORMAL_MODE_CTRL_REG1)
    {
        control_reg = LIS3DH_NORMAL_MODE_CTRL_REG1;
        
        setReg(control_reg,LIS3DH_CTRL_REG1);
    }
    
    /******************************************/
    /*     I2C Reading CTRL REG1 again        */
    /******************************************/
    
    //readReg(control_reg, LIS3DH_CTRL_REG1);
    
    /******************************************/
    /*       I2C Writing CTRL REG5            */
    /******************************************/
    

    if (control_reg_5 != LIS3DH_CTRL_REG5_FIFO_ON)
    {
        control_reg_5 = LIS3DH_CTRL_REG5_FIFO_ON;
        
        setReg(control_reg_5,LIS3DH_CTRL_REG5);

    }
    
    /******************************************/
    /*       I2C Writing CTRL REG3            */
    /******************************************/
 
    
    if (control_reg_3 != LIS3DH_CTRL_REG3_INT)
    {
        control_reg_3 = LIS3DH_CTRL_REG3_INT;
        
        setReg(control_reg_3,LIS3DH_CTRL_REG3);

    }
    
    /******************************************/
    /*     I2C Reading CTRL REG3 again        */
    /******************************************/
    
    readReg(control_reg_3, LIS3DH_CTRL_REG3);
    
    /******************************************/
    /*       I2C Writing FIFO CTRL REG        */
    /******************************************/
    if (FIFO_control_reg != LIS3DH_FIFO_ON)
    {
        FIFO_control_reg = LIS3DH_FIFO_ON;
        
        setReg(FIFO_control_reg,LIS3DH_FIFO_CTRL_REG);
    }
    
    /*      I2C Master Read - CTRL Register 5       */
    
    readReg(control_reg_5, LIS3DH_CTRL_REG5);
    
    /*      I2C Master Read - FIFO CTRL Register     */

    readReg(FIFO_control_reg, LIS3DH_FIFO_CTRL_REG);
   
    
    int16 regCount = 192;
    uint8_t data[192];
    uint8_t fifoFull;
    int16 xData[32];
    int16 yData[32];
    int16 zData[32];
    uint8_t dataSend[194];

    uint8_t regSetting;
    int16 arrayToSend[98];

    status=0;
    
    //UART_PutString("\r\nConfiguration complete\r\n");
    //UART_BT_PutString("\r\nConfiguration complete\r\n");
    
    regSetting=0x00;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO_CTRL_REG,regSetting);
    regSetting=0x40;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO_CTRL_REG,regSetting);
    
    for(;;)
    {
        switch (status)
        {
            case INITIALIZATION:
            
                // retrieve from EEPROM memory
                FS = EEPROM_retrieve_FS();
                So[0] = EEPROM_retrieve_So_lsb();
                So[1] = EEPROM_retrieve_So_msb();
                
                // read registers 
                readReg(control_reg_4, LIS3DH_CTRL_REG4);   //for both So[1] and FS[1:0]
                readReg(control_reg, LIS3DH_CTRL_REG1);     //for So[0]
     
                //writes FS in register CTRL_REG_4[5:4]
                setReg(((FS<<4)|control_reg_4), LIS3DH_CTRL_REG4);   //CTRL_REG4[5:4] contain FS
                
                // writes So[1:0] bits in reg1[3] and reg4[3]
                setReg(((So[0]<<3)|control_reg_4), LIS3DH_CTRL_REG4);   //lsb in CTRL_REG_4[3]
                setReg(((So[1]<<3)|control_reg), LIS3DH_CTRL_REG1);     //msb in CTRL_REG_1[3]
                
                //UART_PutString("\r\nFull Scale and Sensitivity settings retrieved and set\r\n");
                //UART_BT_PutString("\r\nFull Scale and Sensitivity settings retrieved and set\r\n");
                
                status = 0;
   
                break;
            
            case READING:
            
                CyDelay(500); //to get stable data
                //Read the FIFO status register and save the value in fifoFull
                error=I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS, LIS3DH_FIFO_SRC_REG, &fifoFull); 
                //sprintf(message,"\r\novrn value: %d \r\n",(fifoFull & 0x40)>>6);
                //UART_PutString(message);
               
                if(error == NO_ERROR && (fifoFull & 0x40)>>6)   //if the FIFO register is full, the data is saved in the array to send
                {
                    I2C_Peripheral_ReadRegisterMulti(LIS3DH_DEVICE_ADDRESS,LIS3DH_OUT_X_L,regCount,data);
                    //UART_PutString("Data ready\n");
                    for(int i = 0; i<32;i++)
                    {
                        xData[i] = (int16) (data[i*6] | (data[i*6+1]<<8))>>6;
                        yData[i] = (int16) (data[i*6+2] | (data[i*6+3]<<8))>>6;
                        zData[i] = (int16) (data[i*6+4] | (data[i*6+5]<<8))>>6;
                    }
                    dataSend[0]=0x0A;
                    dataSend[193]=0x0B;
                    
                    for(int i=1;i<193;i++)
                    {
                        dataSend[i]=data[i-1];
                    }
                    
                    
                    //UART_PutArray(dataSend,194);
                    UART_BT_PutArray(dataSend, 194); //send data via BT
                    
                    //reset the FIFO register, so that it can acquire the new data
                    regSetting=0x00;
                    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO_CTRL_REG,regSetting);
                    regSetting=0x40;
                    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH_FIFO_CTRL_REG,regSetting);
                }
                
                break;
                
            case TURNOFF: //save status
                
                EEPROM_save_status(FS, So);
//                EEPROM_Stop();
//                I2C_Peripheral_Stop();
//                UART_BT_Stop();
//                UART_Stop();
                //UART_BT_PutString("turn off device");
                //UART_PutString("turn off device");
                status = 0;
                
                break;
                
            default:
                break;
                
        }       
        // at any cycle check if there were changes from GUI in the FS and So registers and save in EEPROM
        
        if ((flag_FS == 1)||(flag_So == 1)) // FS value stored in FS
        {
            // save in EEPROM
            EEPROM_save_status(FS, So);
            
            // read again registers values
            readReg(control_reg, LIS3DH_CTRL_REG1);
            readReg(control_reg_4, LIS3DH_CTRL_REG4);
            
            // set necessary bits to 0
            control_reg = control_reg & 0b11000111; 
            control_reg_4 = control_reg_4 & 0b11110111;
            
            // write necessary values in registers
            setReg(((FS<<4)|control_reg_4), LIS3DH_CTRL_REG4);  
            setReg(((So[0]<<3)|control_reg_4), LIS3DH_CTRL_REG4); 
            setReg(((So[1]<<3)|control_reg), LIS3DH_CTRL_REG1); 
            
            flag_FS = 0;
            flag_So = 0;
        }
    }
}

/* [] END OF FILE */
