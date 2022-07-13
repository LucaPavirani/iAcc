/*******************************************************************************
* File Name: Timer_LED_PM.c
* Version 2.80
*
*  Description:
*     This file provides the power management source code to API for the
*     Timer.
*
*   Note:
*     None
*
*******************************************************************************
* Copyright 2008-2017, Cypress Semiconductor Corporation.  All rights reserved.
* You may use this file only in accordance with the license, terms, conditions,
* disclaimers, and limitations in the end user license agreement accompanying
* the software package with which this file was provided.
********************************************************************************/

#include "Timer_LED.h"

static Timer_LED_backupStruct Timer_LED_backup;


/*******************************************************************************
* Function Name: Timer_LED_SaveConfig
********************************************************************************
*
* Summary:
*     Save the current user configuration
*
* Parameters:
*  void
*
* Return:
*  void
*
* Global variables:
*  Timer_LED_backup:  Variables of this global structure are modified to
*  store the values of non retention configuration registers when Sleep() API is
*  called.
*
*******************************************************************************/
void Timer_LED_SaveConfig(void) 
{
    #if (!Timer_LED_UsingFixedFunction)
        Timer_LED_backup.TimerUdb = Timer_LED_ReadCounter();
        Timer_LED_backup.InterruptMaskValue = Timer_LED_STATUS_MASK;
        #if (Timer_LED_UsingHWCaptureCounter)
            Timer_LED_backup.TimerCaptureCounter = Timer_LED_ReadCaptureCount();
        #endif /* Back Up capture counter register  */

        #if(!Timer_LED_UDB_CONTROL_REG_REMOVED)
            Timer_LED_backup.TimerControlRegister = Timer_LED_ReadControlRegister();
        #endif /* Backup the enable state of the Timer component */
    #endif /* Backup non retention registers in UDB implementation. All fixed function registers are retention */
}


/*******************************************************************************
* Function Name: Timer_LED_RestoreConfig
********************************************************************************
*
* Summary:
*  Restores the current user configuration.
*
* Parameters:
*  void
*
* Return:
*  void
*
* Global variables:
*  Timer_LED_backup:  Variables of this global structure are used to
*  restore the values of non retention registers on wakeup from sleep mode.
*
*******************************************************************************/
void Timer_LED_RestoreConfig(void) 
{   
    #if (!Timer_LED_UsingFixedFunction)

        Timer_LED_WriteCounter(Timer_LED_backup.TimerUdb);
        Timer_LED_STATUS_MASK =Timer_LED_backup.InterruptMaskValue;
        #if (Timer_LED_UsingHWCaptureCounter)
            Timer_LED_SetCaptureCount(Timer_LED_backup.TimerCaptureCounter);
        #endif /* Restore Capture counter register*/

        #if(!Timer_LED_UDB_CONTROL_REG_REMOVED)
            Timer_LED_WriteControlRegister(Timer_LED_backup.TimerControlRegister);
        #endif /* Restore the enable state of the Timer component */
    #endif /* Restore non retention registers in the UDB implementation only */
}


/*******************************************************************************
* Function Name: Timer_LED_Sleep
********************************************************************************
*
* Summary:
*     Stop and Save the user configuration
*
* Parameters:
*  void
*
* Return:
*  void
*
* Global variables:
*  Timer_LED_backup.TimerEnableState:  Is modified depending on the
*  enable state of the block before entering sleep mode.
*
*******************************************************************************/
void Timer_LED_Sleep(void) 
{
    #if(!Timer_LED_UDB_CONTROL_REG_REMOVED)
        /* Save Counter's enable state */
        if(Timer_LED_CTRL_ENABLE == (Timer_LED_CONTROL & Timer_LED_CTRL_ENABLE))
        {
            /* Timer is enabled */
            Timer_LED_backup.TimerEnableState = 1u;
        }
        else
        {
            /* Timer is disabled */
            Timer_LED_backup.TimerEnableState = 0u;
        }
    #endif /* Back up enable state from the Timer control register */
    Timer_LED_Stop();
    Timer_LED_SaveConfig();
}


/*******************************************************************************
* Function Name: Timer_LED_Wakeup
********************************************************************************
*
* Summary:
*  Restores and enables the user configuration
*
* Parameters:
*  void
*
* Return:
*  void
*
* Global variables:
*  Timer_LED_backup.enableState:  Is used to restore the enable state of
*  block on wakeup from sleep mode.
*
*******************************************************************************/
void Timer_LED_Wakeup(void) 
{
    Timer_LED_RestoreConfig();
    #if(!Timer_LED_UDB_CONTROL_REG_REMOVED)
        if(Timer_LED_backup.TimerEnableState == 1u)
        {     /* Enable Timer's operation */
                Timer_LED_Enable();
        } /* Do nothing if Timer was disabled before */
    #endif /* Remove this code section if Control register is removed */
}


/* [] END OF FILE */
