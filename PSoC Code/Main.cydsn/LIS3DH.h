
#ifndef __LIS3DH_H
    #define __LIS3DH_H
    
    #include "cytypes.h"
    #include "stdio.h"

    /**
    *   \brief 7-bit I2C address of the slave device.
    */
    #define LIS3DH_DEVICE_ADDRESS 0x18

    /**
    *   \brief Address of the WHO AM I register
    */
    #define LIS3DH_WHO_AM_I_REG_ADDR 0x0F
    
    /**
    *   \brief WHOAMI return value
    */
    #define LIS3DH_WHOAMI_RETVAL     0x33

    /**
    *   \brief Address of the Status register
    */
    #define LIS3DH_STATUS_REG 0x27

    /**
    *   \brief Address of the Control register 1
    */
    #define LIS3DH_CTRL_REG1 0x20

    /**
    *   \brief Hex value to set normal mode to the accelerator
    */
    #define LIS3DH_NORMAL_MODE_CTRL_REG1 0x47
    
    /**
    *   \brief Hex value to set normal mode (powered off)
    **/
    #define LIS3DH_NORMAL_MODE_OFF_CTRL_REG1 0x07

    /**
    *   \brief  Address of the Temperature Sensor Configuration register
    */
    #define LIS3DH_TEMP_CFG_REG 0x1F 

    #define LIS3DH_TEMP_CFG_REG_ACTIVE 0xC0
   
    /////////////////////////////////////////////////
    //EX.3
    
    // Brief Address of CTRL REG 4
    #define LIS3DH_CTRL_REG4 0x23
        
    // brief Block Data Update (BDU) Flag
    
    #define LIS3DH_CTRL_REG4_BDU_ACTIVE 0x80

    // Brief Address of the ADC output LSB register
    
    #define LIS3DH_OUT_ADC_3L 0x0C

    // Brief Address of the ADC output MSB register
    
    #define LIS3DH_OUT_ADC_3H 0x0D
    ////////////////////////////////////////////////
    
    //Registers addresses, along with their default values
    
    #define LIS3DH_OUT_X_L 0x28
    #define LIS3DH_OUT_X_H 0x29
    #define LIS3DH_OUT_Y_L 0x2A
    #define LIS3DH_OUT_Y_H 0x2B
    #define LIS3DH_OUT_Z_L 0x2C
    #define LIS3DH_OUT_Z_H 0x2D
    
    #define LIS3DH_FIFO_CTRL_REG 0x2E
    #define LIS3DH_FIFO_ON 0x40
    #define LIS3DH_FIFO_BYP 0x00
    
    #define LIS3DH_CTRL_REG3 0x22
    #define LIS3DH_CTRL_REG3_INT 0x02 
    
    #define LIS3DH_CTRL_REG5 0x24
    #define LIS3DH_CTRL_REG5_FIFO_ON 0x40
    
    #define LIS3DH_FIFO_SRC_REG 0x2F
    #define LIS3DH_FIFO_SRC_OVRN 0b01000000
    
    //FS = CTRL_REG4[5:4]
    #define FS2     0x00
    #define FS4     0x01
    #define FS8     0x02
    #define FS16    0x03
    
    //So = CTRL_REG1[3]+CTRL_REG4[3]
    #define Normal  0x00 //00
    #define HR      0x01 //01
    #define LP      0x02 //10
    #define NA      0x03 //11
    
    uint8 So[2];
    uint8 FS;
    
#endif


/* [] END OF FILE */
