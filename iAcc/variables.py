import numpy as np

# Global variables
CONN_STATUS = False
dataSize = 98
baudRate = 115200 #9600 for USB, 115200 for BT
axisSize = dataSize//3
SECOND = 32 #sample acquisition time window, to obtain HR/RR
xData = np.full(axisSize,0,dtype=np.int16)
yData = np.full(axisSize,0,dtype=np.int16)
zData = np.full(axisSize,0,dtype=np.int16)

#array for the accelerations converted from digits
xData_g = np.full(axisSize,0,dtype=np.float16)
yData_g = np.full(axisSize,0,dtype=np.float16)
zData_g = np.full(axisSize,0,dtype=np.float16)
sum_data = np.full(axisSize,0,dtype=np.float16)

clock = np.zeros(axisSize) #clock used to draw x axis

#arrays to save the data to be exported
RR_save = [] 
HR_save = []

#arrays to save the data, after the filtering procedure
zData_windowed_HR = np.full(axisSize,0,dtype=np.float16)
zData_lowpass_RR = np.full(axisSize,0,dtype=np.float16)
zData_bandpass_RR = np.full(axisSize,0,dtype=np.float16)
zData_lowpass = np.full(axisSize,0,dtype=np.float16)

zData_array_HR = []
zData_array_RR = []
HR_array = []
RR_array= []

flag_graph = 0 #used to select which axis to show
flag_graph_RR = 0
flag_graph_HR = 0
count_sec_HR = 0
count_sec_RR = 0
connectionWait = False #flag used for the while during the connection: it prevents the serial scanner to read the following port before the current sends the signals
calibration_flag=False #flag to start the calibration
#variables to show the data in the interface
RR_value=0.0
HR_value=0.0
RR_old=0.0
HR_old=0.0
count_RR = 0
count_HR = 0
i_peaks_HR = 0
i_peaks_RR = 0
flag_RR = False
flag_HR = False

start_RR = 0
stop_RR = 0 
timediff_RR = 0
flagstart_RR = 0

start_HR = 0
stop_HR = 0 
timediff_HR = 0
flagstart_HR = 0

SAMPLE_RATE = 50

# the heart rate varies between 1 Hz and 1.66 Hz, during physical activity it can reach up to 3 Hz
LOW_CUT_HR = 1    
HIGH_CUT_HR = 3

# the respiratory rate instead varies between 0.1 Hz and 0.9 Hz
LOW_CUT_RR = 0.1
HIGH_CUT_RR = 0.9

order = 5
cutoff_RR = 3

#conversion parameter, to obtain the accelerations from the digits: negative accelerations go from 512 to 1023, while the positive ones go from to 0 to 511. 511 is 2G, 512 -2G
mDigitNeg = -0.0039060665362
qDigitNeg = 3.99990606654
mdigitPos = -0.0039137254902
qDigitPos= 0.0000862745098039