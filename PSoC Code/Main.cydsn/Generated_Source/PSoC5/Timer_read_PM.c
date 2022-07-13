/*******************************************************************************
* File Name: Timer_read_PM.c
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

#include "Timer_read.h"

static Timer_read_backupStruct Timer_read_backup;


/*******************************************************************************
* Function Name: Timer_read_SaveConfig
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
*  Timer_read_backup:  Variables of this global structure are modified to
*  store the values of non retention configuration registers when Sleep() API is
*  called.
*
*******************************************************************************/
void Timer_read_SaveConfig(void) 
{
    #if (!Timer_read_UsingFixedFunction)
        Timer_read_backup.TimerUdb = Timer_read_ReadCounter();
        Timer_read_backup.InterruptMaskValue = Timer_read_STATUS_MASK;
        #if (Timer_read_UsingHWCaptureCounter)
            Timer_read_backup.TimerCaptureCounter = Timer_read_ReadCaptureCount();
        #endif /* Back Up capture counter register  */

        #if(!Timer_read_UDB_CONTROL_REG_REMOVED)
            Timer_read_backup.TimerControlRegister = Timer_read_ReadControlRegister();
        #endif /* Backup the enable state of the Timer component */
    #endif /* Backup non retention registers in UDB implementation. All fixed function registers are retention */
}


/*******************************************************************************
* Function Name: Timer_read_RestoreConfig
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
*  Timer_read_backup:  Variables of this global structure are used to
*  restore the values of non retention registers on wakeup from sleep mode.
*
*******************************************************************************/
void Timer_read_RestoreConfig(void) 
{   
    #if (!Timer_read_UsingFixedFunction)

        Timer_read_WriteCounter(Timer_read_backup.TimerUdb);
        Timer_read_STATUS_MASK =Timer_read_backup.InterruptMaskValue;
        #if (Timer_read_UsingHWCaptureCounter)
            Timer_read_SetCaptureCount(Timer_read_backup.TimerCaptureCounter);
        #endif /* Restore Capture counter register*/

        #if(!Timer_read_UDB_CONTROL_REG_REMOVED)
            Timer_read_WriteControlRegister(Timer_read_backup.TimerControlRegister);
        #endif /* Restore the enable state of the Timer component */
    #endif /* Restore non retention registers in the UDB implementation only */
}


/*******************************************************************************
* Function Name: Timer_read_Sleep
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
*  Timer_read_backup.TimerEnableState:  Is modified depending on the
*  enable state of the block before entering sleep mode.
*
*******************************************************************************/
void Timer_read_Sleep(void) 
{
    #if(!Timer_read_UDB_CONTROL_REG_REMOVED)
        /* Save Counter's enable state */
        if(Timer_read_CTRL_ENABLE == (Timer_read_CONTROL & Timer_read_CTRL_ENABLE))
        {
            /* Timer is enabled */
            Timer_read_backup.TimerEnableState = 1u;
        }
        else
        {
            /* Timer is disabled */
            Timer_read_backup.TimerEnableState = 0u;
        }
    #endif /* Back up enable state from the Timer control register */
    Timer_read_Stop();
    Timer_read_SaveConfig();
}


/*******************************************************************************
* Function Name: Timer_read_Wakeup
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
*  Timer_read_backup.enableState:  Is used to restore the enable state of
*  block on wakeup from sleep mode.
*
*******************************************************************************/
void Timer_read_Wakeup(void) 
{
    Timer_read_RestoreConfig();
    #if(!Timer_read_UDB_CONTROL_REG_REMOVED)
        if(Timer_read_backup.TimerEnableState == 1u)
        {     /* Enable Timer's operation */
                Timer_read_Enable();
        } /* Do nothing if Timer was disabled before */
    #endif /* Remove this code section if Control register is removed */
}


/* [] END OF FILE */
