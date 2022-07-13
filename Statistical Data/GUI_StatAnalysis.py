from setuptools import find_packages
import variables as var
from re import L
import struct
import sys
from telnetlib import STATUS
import time
import logging
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks, argrelmin
import scipy.signal as signal
from scipy.signal import butter

from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

# We import library dedicated to data plot
import pyqtgraph as pg
from pyqtgraph import PlotWidget

import serial 
import serial.tools.list_ports

import pandas as pd

start = 0
stop = 0 
timediff = 0
flagstart = 0

start_HR = 0
stop_HR = 0 
timediff_HR = 0
flagstart_HR = 0
contare= 0
start_bit = 0
stop_bit = 0
flag_bit = 0
count = 0
#Logging config
logging.basicConfig(format="%(message)s", level=logging.INFO)

#########################
# SERIAL_WORKER_SIGNALS #
#########################
class SerialWorkerSignals(QObject):
    """!
    @brief Class that defines the signals available to a serialworker.

    Available signals (with respective inputs) are:
        - device_port:
            str --> port name to which a device is connected
        - status:
            str --> port name
            int --> macro representing the state (0 - error during opening, 1 - success)
    """
    device_port = pyqtSignal(str)
    status = pyqtSignal(str, int)

#################
# SERIAL_WORKER #
#################
class SerialWorker(QRunnable):
    """!
    @brief Main class for serial communication: handles connection with device.
    """
    def __init__(self, serial_port_name):
        """!
        @brief Init worker.
        """
        self.is_killed = False
        super().__init__()
        #init port, params and signals
        self.port = serial.Serial()
        self.port_name = serial_port_name
        self.baudrate = var.baudRate #hard coded but can be a global variable, or an input param
        self.signals = SerialWorkerSignals()

    @pyqtSlot()
    def run(self):
        """!
        @brief Estabilish connection with desired serial port.
        """

        if not var.CONN_STATUS:
            try:
                self.port = serial.Serial(port=self.port_name, baudrate=self.baudrate,
                                        write_timeout=0, timeout=2)                
                if self.port.is_open:
                    self.send('t')
                    time.sleep(1)

                    if(self.read()=="HR/RR sensor"):
                        var.CONN_STATUS = True
                        self.signals.status.emit(self.port_name, 1)
                        time.sleep(1) #just for compatibility reasons 
                    var.connectionWait = False   
                           
            except serial.SerialException:
                logging.info("Error with port {}.".format(self.port_name))
                self.signals.status.emit(self.port_name, 0)
                time.sleep(0.01)
                var.connectionWait=False

    @pyqtSlot()
    def send(self, char):
        """!
        @brief Basic function to send a single char on serial port.
        """
        try:
            self.port.write(char.encode('utf-8'))
            logging.info("Written {} on port {}.".format(char, self.port_name))
        except:
            logging.info("Could not write {} on port {}.".format(char, self.port_name))

    @pyqtSlot()
    def read(self):
        """!
        @brief Basic function to read a single char on serial port.
        """
        testString=''
        try:
            while(self.port.in_waiting>0):
                testString+=self.port.read().decode('utf-8', errors='replace')
                #logging.info(self.port.in_waiting)
            logging.info("Received: {}".format(testString))
            return testString
        except:
            logging.info("Could not receive {} on port {}.".format(testString, self.port_name))
   
    @pyqtSlot()
    def readAcc(self):
        """!
        @brief Basic function to read a single char on serial port.
        """
        testString=''
        try:
            while(self.port.in_waiting>0):
                testString+=self.port.read().decode('utf-8', errors='replace')
                #logging.info(self.port.in_waiting)
            #logging.info("Received: {}".format(testString))
            return testString
        except:
            logging.info("Could not receive {} on port {}.".format(testString, self.port_name))

    @pyqtSlot()
    def killed(self):
        """!
        @brief Close the serial port before closing the app.
        """

        if self.is_killed and var.CONN_STATUS:
            self.send('s')
            self.port.close()
            time.sleep(0.01)
            var.CONN_STATUS = False
            self.signals.device_port.emit(self.port_name)
            
        logging.info("Killing the process")

    @pyqtSlot()
    def readData(self):
        """!
        @brief Function used to read the data and to implement the HR and RR algorithms. 
               Moreover we implemented a warning signal for the user in case of losing the connection. 
        """
        global start_bit,stop_bit,flag_bit, count
        try:
            dataArray = self.port.read(194)
            dataArray = struct.unpack('194B',dataArray)
            dataArray = np.asarray(dataArray,dtype=np.uint8)
            lastIndex = len(dataArray)-1
            if(dataArray[0]==10 and dataArray[lastIndex]==11):
                accData = dataArray[1:193]
                for i in range(var.axisSize):
                
                    var.xData[i] =  (((accData[i*6+1] & 0xFF)<<8) | (accData[i*6] & 0xFF))>>6
                    var.yData[i] =  (((accData[i*6+3] & 0xFF)<<8) | (accData[i*6+2] & 0xFF))>>6
                    var.zData[i] =  (((accData[i*6+5] & 0xFF)<<8) | (accData[i*6+4] & 0xFF))>>6

                    if(var.xData[i]>511 & var.xData[i]<1024):
                        var.xData_g[i] = var.xData[i]*(var.mDigitNeg)+var.qDigitNeg
                    else:
                        var.xData_g[i] = var.xData[i]*(var.mdigitPos) - var.qDigitPos
                    if(var.yData[i]>511 & var.yData[i]<1024):
                        var.yData_g[i] = var.yData[i]*(var.mDigitNeg)+var.qDigitNeg
                    else:
                        var.yData_g[i] = var.yData[i]*(var.mdigitPos) - var.qDigitPos
                    if(var.zData[i]>511 & var.zData[i]<1024):
                        var.zData_g[i] = var.zData[i]*(var.mDigitNeg)+var.qDigitNeg
                    else:
                        var.zData_g[i] = var.zData[i]*(var.mdigitPos) - var.qDigitPos
                  
                    # Sum_data is used to calculate the HR rate in order to be more robust against movements
                    var.sum_data[i]=var.zData_g[i]+var.yData_g[i]      
            
            # In order to plot a real time graph which is filtered
            var.zData_lowpass = self.butter_lowpass_filter(var.zData_g, var.cutoff_RR, var.SAMPLE_RATE, var.order)   

            # Algorithms for HR and RR computation
            var.HR_value = self.HR_computation(var.sum_data, var.calibration_flag)
            var.RR_value = self.RR_computation(var.zData_g, var.calibration_flag)

        except struct.error:
            
            # Warning message in case of connection problems
            self.dlg3 = QMessageBox()
            self.dlg3.setWindowTitle("WARNING")
            self.dlg3.setText("Connection lost, click OK and restart the application")
            self.dlg3.setStandardButtons(QMessageBox.Ok)
            self.dlg3.setIcon(QMessageBox.Critical)
            button=self.dlg3.exec_()
            if(button==QMessageBox.Ok):
                MainWindow.save_data(self)  # save data even if there are connection problems
                sys.exit(app.exec_())

    def HR_computation(self, data, calibration_flag):
        """!
        @brief Algorithm for Heart Rate computation after the calibration. 

        The pre-processing steps applied to the data are the following: 
            1) Data are Band-Pass filtered in a range between 1 Hz to 5 Hz;
            2) Then we apply a Savitzky-Golay filter;
            3) Finally a Moving Average.

        Then we proceed calculating the Heart Rate based on a threshold and on a time window in order to be
        more robust against noise and more precise in the computation. 
        """
        global start_HR, stop_HR, timediff_HR, flagstart_HR
        # We proceed with the computation of the Heart Rate only after the calibration is finished
        if (calibration_flag):
            var.count_sec_HR+=1   

            if (flagstart_HR ==0):
                start_HR = time.time()
                flagstart_HR=1
            var.zData_array_HR = np.append(var.zData_array_HR, data)
           
            if (var.count_sec_HR==32):     # The HR is updated after about 30 s
            
                zData_bandpass_HR = np.full(var.axisSize,0,dtype=np.float16)
                #zData_bandpass_HR = self.butter_bandpass_design(np.abs(var.zData_array_HR), var.LOW_CUT_HR, var.HIGH_CUT_HR,
                #                                                  var.SAMPLE_RATE)
                zData_bandpass_HR = self.butter_bandpass_design(var.zData_array_HR, var.LOW_CUT_HR, var.HIGH_CUT_HR,
                                                                  var.SAMPLE_RATE)
                self.HR_detrend = []
                self.HR_detrend= signal.detrend(zData_bandpass_HR)                                               
                var.zData_array_HR=[]    
                var.zData_windowed_HR = signal.savgol_filter(self.HR_detrend, window_length=15, polyorder=4)
                self.window_length_MA = 15
                var.zData_windowed_HR = self.moving_average(self.window_length_MA, var.zData_windowed_HR)  
                
                # Threshold computation
                self.threshold_wi=self.calibration_threshold_HR(var.zData_windowed_HR)
                self.delta_HR = 17

                # Number of peaks detected in the defined time window
                self.n_peaks_HR, var.i_peaks_HR  = self.find_peaks(var.zData_windowed_HR, self.threshold_wi, 
                                                                                            self.delta_HR)
                print('numero massimi HR', self.n_peaks_HR)
                stop_HR = time.time()
                timediff_HR = stop_HR - start_HR
                print('tempo HR', timediff_HR)
                stop_HR = 0
                start_HR = 0
                flagstart_HR = 0
                # HR calculation
                var.HR_old=var.HR_value
                var.HR_value= (self.n_peaks_HR * 60)/ timediff_HR
                var.HR_save = np.append(var.HR_save, var.HR_value)  # array in which we save the data to be exported
                var.count_sec_HR = 0

                plt.figure(2)
                plt.plot(var.zData_windowed_HR, label = 'zData_windowed')
                plt.plot(var.i_peaks_HR,var.zData_windowed_HR[var.i_peaks_HR], "x")
                plt.axhline(y = self.threshold_wi, color = 'r', linestyle = '-')
                plt.title('Filtered Signal for Heart Rate')
                plt.show()
                
                var.count_HR+=var.SECOND
                var.flag_graph_HR = True
                var.flag_HR = True

        return var.HR_value

    def RR_computation(self, data, calibration_flag):
        """!
        @brief Algorithm for Respiratory Rate computation after the calibration. 

        The pre-processing steps applied to the data are the following: 
            1) Firstly, data are Low-Pass filtered with a cut-off frequency of 3 Hz;
            2) Then we apply a Savitzky-Golay filter;

        Then we proceed calculating the Respiratory Rate based on a threshold and on a time window in order to be
        more robust against noise and more precise in the computation. 
        """
        global start, stop, timediff, flagstart
        # We proceed with the computation of the Heart Rate only after the calibration is finished
        if (calibration_flag):
            var.count_sec_RR+=1    
            if (flagstart ==0):
                start = time.time()
                flagstart=1

            var.zData_array_RR = np.append(var.zData_array_RR, data)
            
            if (var.count_sec_RR==32):     # The HR is updated after about 30 s
                
                
                var.zData_lowpass_RR = self.butter_lowpass_filter(var.zData_array_RR, var.cutoff_RR, var.SAMPLE_RATE, var.order)
                var.zData_array_RR=[]    
                #var.zData_smoothed_RR = signal.savgol_filter(var.zData_lowpass_RR, window_length=31, polyorder=3)
                self.detrend = self.butter_bandpass_design(var.zData_lowpass_RR, 0.01, 0.9,
                                                                  var.SAMPLE_RATE)

                var.zData_smoothed_RR=signal.detrend(self.detrend)
        
                # Threshold computation
                self.threshold_RR=self.calibration_threshold(var.zData_smoothed_RR)
                self.delta_RR =46

                # Number of peaks detected in the defined time window
                self.n_peaks_bp_RR, var.i_peaks_RR = self.find_peaks(var.zData_smoothed_RR, self.threshold_RR, self.delta_RR)
                print('numero massimi RR', self.n_peaks_bp_RR)

                stop = time.time()
                timediff = stop - start
                print('tempo', timediff)
                stop = 0
                start = 0
                flagstart=0

                '''
                self.diffsec= []
                for i in range(len(var.i_peaks_RR)-1):
                    self.diff = var.i_peaks_RR[i+1]-var.i_peaks_RR[i]
                    self.diffsec= np.append(self.diffsec, self.diff *0.02)

                self.avg = sum(self.diffsec)/len(var.i_peaks_RR)
                var.RR_value = 60 / self.avg
                print('Distanza media', self.avg)
                var.RR_save = np.append(var.RR_save, var.RR_value)  # array in which we save the data to be exported
                var.count_sec_RR = 0
                '''

                
                # RR calculation
                var.RR_old = var.RR_value
                #var.RR_value= (self.n_peaks_bp_RR* 60)/ (var.count_sec_RR*var.axisSize*(1/var.SAMPLE_RATE))
                var.RR_value= (self.n_peaks_bp_RR* 60)/ timediff
                print('count sec', var.count_sec_RR)
                print('il denominatore', (var.count_sec_RR*var.axisSize*(1/var.SAMPLE_RATE)))
                print('axis size',var.axisSize)
                var.RR_save = np.append(var.RR_save, var.RR_value)  # array in which we save the data to be exported
                var.count_sec_RR = 0
                

                plt.figure(1)
                plt.plot(var.zData_smoothed_RR, label = 'zData Bandpass detrended')
                plt.plot(var.i_peaks_RR,var.zData_smoothed_RR[var.i_peaks_RR], "x")
                #plt.plot(np.transpose(self.i_minima_ipo_bp),zData_bandpass[self.i_minima_ipo_bp], "x")
                plt.axhline(y = self.threshold_RR, color = 'r', linestyle = '-')
                plt.title('Filtered Signal for Respiratory rate')   
                plt.show()

                var.count_RR+=var.SECOND
                var.flag_graph_RR = True
                var.flag_RR = True

        return var.RR_value

    def moving_average(self, window_length, data):
        """!
        @brief Moving average function.   
        """
        
        smoothed = np.convolve(data, np.ones(window_length)) / window_length
    
        return smoothed
    
    def find_peaks(self, data, threshold, delta):
        """!
        @brief Function used to calculate the peaks.   
        """
        
        i_peaks, _ = find_peaks(data, height = threshold, distance = delta)
        peaks = len(i_peaks)

        return peaks , i_peaks

    def butter_bandpass_design(self, signal_array, low_cut, high_cut, sample_rate, order=4):
        """
        @brief Defines the Butterworth bandpass filter-design.
        :param low_cut: Lower cut off frequency in Hz
        :param high_cut: Higher cut off frequency in Hz
        :param sample_rate: Sample rate of the signal in Hz
        :param order: Order of the filter-design
        :return: b, a : ndarray, ndarray - Numerator (b) and denominator (a) polynomials of the IIR filter. Only returned if output='ba'.
        """
        sos = signal.butter(order, [low_cut, high_cut], btype='band', output ='sos',fs=sample_rate)
        y = signal.sosfiltfilt(sos, signal_array)

        return y

    def butter_lowpass(self, cutoff, fs, order):
        
        return butter(order, cutoff, fs=fs, btype='low', analog=False)

    def butter_lowpass_filter(self, data, cutoff, fs, order):
        """!
        @brief Defines the Butterworth lowpass filter.
        """
        b, a = self.butter_lowpass(cutoff, fs, order=order)
        y = signal.filtfilt(b, a, data) 

        return y

    def butter_highpass(self, cutoff, fs, order):

        return butter(order, cutoff, fs=fs, btype='high', analog=False)

    def butter_highpass_filter(self, data, cutoff, fs, order):
        """!
        @brief Defines the Butterworth highpass filter.
        """
        b, a = self.butter_highpass(cutoff, fs, order=order)
        y = signal.filtfilt(b, a, data) 

        return y

    def calibration_threshold(self, val):
        """!
        -------- CALIBRATION ---------
        The patient has to breath normally for 10 seconds 
        and the mean value calculated during this calibration window is used for the
        definition of a threshold.
        """
        threshold=0.0
        
        threshold= np.mean(val[len(val)//6:len(val)*5//6])
        return threshold
    
    def calibration_threshold_HR(self, val):
        """!
        -------- CALIBRATION ---------
        The patient has to breath normally for 10 seconds 
        and the mean value calculated during this calibration window is used for the
        definition of a threshold.
        """
        threshold=0.0
        
        threshold= np.mean(val) -(0.4 * max(val))
        return threshold

###############
# MAIN WINDOW #
###############
class MainWindow(QMainWindow):

    def __init__(self):
        """!
        @brief Init MainWindow.
        """
        # Define worker
        self.serial_worker = SerialWorker(None)

        super(MainWindow, self).__init__()

        # Title and geometry
        self.setFixedSize(1480,930)
        self.setWindowTitle("iAcc")
        self.center()
        self.show()

        # Create thread handler
        self.threadpool = QThreadPool()
        
        self.connected = var.CONN_STATUS
  
        self.initUI()
    
    #####################
    # GRAPHIC INTERFACE #
    #####################
    def initUI(self):
        """!
        @brief Set up the graphical interface structure.
        """

        # Create the plot widget
        self.graphWidget = PlotWidget()
        
        # Plot settings
            # Add grid
        self.graphWidget.showGrid(x=True, y=True)
            # Set background color
        self.graphWidget.setBackground('bbccdd')   #color in exa
            # Add title
        self.graphWidget.setTitle("Accelerometer data",color="b", size="12pt",italic=True)
            # Add axis labels
        styles = {'color':'k', 'font-size':'15px'}
        self.graphWidget.setLabel('left', 'Acc data [m/s2]', **styles)
        self.graphWidget.setLabel('bottom', 'Time [ms]', **styles)
            # Add legend
        self.graphWidget.addLegend()
        self.graphWidget.setMouseEnabled(x=False, y=False)
        self.graphWidget.setFixedHeight(320)

        # Create the Heart rate plot widget
        self.HR_plot = PlotWidget() 
        self.HR_plot.showGrid(x=True, y=True)
        self.HR_plot.setBackground('bbccdd')   #color in exa
        self.HR_plot.setTitle("Heart rate",color="b", size="12pt",italic=True)
        styles = {'color':'k', 'font-size':'15px'}
        self.HR_plot.setLabel('left', 'Heart Rate [bpm]', **styles)
        self.HR_plot.setLabel('bottom', 'Time [ms]', **styles)
        self.HR_plot.addLegend()
        self.HR_plot.setMouseEnabled(x=False, y=False)

        # Create the Respiratory rate plot widget
        self.RR_plot = PlotWidget() 
        self.RR_plot.showGrid(x=True, y=True)
        self.RR_plot.setBackground('bbccdd')   #color in exa
        self.RR_plot.setTitle("Respiratory rate",color="b", size="12pt",italic=True)
        styles = {'color':'k', 'font-size':'15px'}
        self.RR_plot.setLabel('left', 'Respiratory rate [bpm]', **styles)
        self.RR_plot.setLabel('bottom', 'Time [ms]', **styles)
        self.RR_plot.addLegend()
        self.RR_plot.setMouseEnabled(x=False, y=False)
        
        # Display 100 time points
        self.horAxis = list(range(320))  #100 time points
        self.xGraph = [0]*320
        self.yGraph = [0]*320
        self.zGraph = [0]*320
        self.zGraph_lowpass = [0]*320

        self.count = 0

        self.draw()
    
        # Plot data
        self.drawGeneralGraph()

        # Update the value of HR and RR in the GUI
        self.updateValue()
        
        # Toolbar
        toolbar = QToolBar("My main toolbar")   
        toolbar.setIconSize(QSize(16, 16))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Exporting files as .csv
        save_action = QAction(QIcon("disk_return_black.png"), "Export to .csv", self)
        save_action.setStatusTip("Export to .csv")
        save_action.triggered.connect(self.save_data)
        toolbar.addAction(save_action)
        self.setStatusBar(QStatusBar(self))
        toolbar.addSeparator()

        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        file_menu.addAction(save_action)

        # Label used to display HR values
        self.HR_label = QLabel()
        text = 'Instant heart rate value: {} bpm'
        a = text.format(var.HR_value)
        self.HR_label.setText(a)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        font = QFont("Lucida", 12, QFont.Bold)
        self.HR_label.setFont(font)
        self.HR_label.setStyleSheet("border: 1px solid black")
        self.HR_label.setAlignment(QtCore.Qt.AlignCenter)
        self.HR_label.setMinimumWidth(720)

        # Label used to display RR values
        self.RR_label = QLabel()
        text = 'Instant respiratory rate value: {} bpm'
        a = text.format(var.RR_value)
        self.RR_label.setText(a)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        font = QFont("Lucida", 12, QFont.Bold)
        self.RR_label.setFont(font)
        self.RR_label.setStyleSheet("border: 1px solid black")
        self.RR_label.setAlignment(QtCore.Qt.AlignCenter)
        self.RR_label.setMinimumWidth(720)

        verticalLayout = QVBoxLayout()
        heart_resp = QHBoxLayout()
        heart_plot = QVBoxLayout()
        resp_plot = QVBoxLayout()
        device_search = QHBoxLayout()
    
        self.conn_btn = QPushButton(
            text=("Device search"), 
            checkable=True,
            toggled=self.on_toggle)

        self.conn_label = QLabel(
            text = ("No device connected")
        )
        font = QFont()
        font.setBold(True)
        font.setWeight(75)
        self.conn_label.setFont(font)
        self.conn_label.setStyleSheet("background-color: rgb(255, 0, 0);\n" "border: 1px solid black")
        self.conn_label.setAlignment(QtCore.Qt.AlignCenter)

        device_search.addWidget(self.conn_btn)
        device_search.addWidget(self.conn_label)

        verticalLayout.addLayout(device_search)

        modeSelection = QHBoxLayout()

        # ComboBox for the HR and RR selection
        self.modeSelect = QComboBox()
        self.modeSelect.addItem("HR & RR")
        self.modeSelect.addItem("HR Only")
        self.modeSelect.addItem("RR Only")
        self.modeSelect.currentIndexChanged.connect(self.selectionchange)

        self.calibrate = QPushButton(
            text = ("Calibration")
        )
        self.calibrate.clicked.connect(self.startCalibration)

        self.updateBtn = QPushButton(
            text = "Start", 
            checkable= True, 
            toggled = self.dataUpdate
        )

        self.updateBtn.setDisabled(True)
        self.modeSelect.setDisabled(True)
        self.calibrate.setDisabled(True)

        self.updateBtn.setIcon(QtGui.QIcon('application-monitor.png'))
        self.updateBtn.setIconSize(QtCore.QSize(25,25))

        modeSelection.addWidget(self.modeSelect)
        modeSelection.addWidget(self.calibrate)
        modeSelection.addWidget(self.updateBtn)
        verticalLayout.addLayout(modeSelection)

        heart_plot.addWidget(self.HR_label)
        heart_plot.addWidget(self.HR_plot)
        resp_plot.addWidget(self.RR_label)
        resp_plot.addWidget(self.RR_plot)

        heart_resp.addLayout(heart_plot)
        heart_resp.addLayout(resp_plot)

        verticalLayout.addWidget(self.graphWidget)
        verticalLayout.addLayout(heart_resp)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)

        self.statusTimer = QtCore.QTimer()
        self.statusTimer.setInterval(2000)

        self.graphTimer= QtCore.QTimer()
        self.graphTimer.setInterval(1000)

        widget = QWidget()
        widget.setLayout(verticalLayout)
        self.setCentralWidget(widget)

        modeSelection.setContentsMargins(5,5,5,5)
        modeSelection.setSpacing(5)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def save_data(self):
        """!
        @brief Function used to save and export data in a .csv file. 
        """
        print("exporting to csv...")

        df = pd.DataFrame({
            'RR': var.RR_save,
            'HR': var.HR_save 
        })
        df.to_csv('HR_Rate.csv', float_format = '%.0f', index = False)

        
    def selectionchange(self,i):
        """!
        @brief Allows the selection of different graphs in the bottom panels of the GUI's window.
        # 0 --> HR
        # 1 --> RR
        # 2 --> both
        """
        var.flag_graph = i

        if (var.flag_graph == 0): # Both RR and HR
            self.RR_plot.setBackground('bbccdd')
            self.HR_plot.setBackground('bbccdd')
            self.HR_plot.show()
            self.HR_label.show()
            self.RR_plot.show()
            self.RR_label.show()
        
        elif (var.flag_graph == 1): #only HR
            self.RR_plot.hide()
            self.RR_label.hide()
            self.HR_plot.show()
            self.HR_label.show()

    
        elif (var.flag_graph == 2): #only RR
            self.HR_plot.hide()
            self.HR_label.hide()
            self.RR_plot.show()
            self.RR_label.show()

        
    def drawGeneralGraph(self):
        """!
        @brief Draw the plots.
        """
        for i in range(len(var.xData)):

            # Remove the first y element.
            if(self.count<321):
                self.count += 1
            else:
                self.horAxis = self.horAxis[1:]
                self.horAxis.append(self.horAxis[-1] + 1)  # Add a new value 1 higher than the last.
        
            # Z-axis
            self.zGraph = self.zGraph[1:]  # Remove the first 
            self.zGraph.append(var.zData_g[i])
            self.dataLinez.setData(self.horAxis, self.zGraph)  # Update the data.

            # Z-axis low pass FILTERED
            self.zGraph_lowpass = self.zGraph_lowpass[1:]  # Remove the first 
            self.zGraph_lowpass.append(var.zData_lowpass[i])
            self.dataLinez_lowpass.setData(self.horAxis, self.zGraph_lowpass)  # Update the data.

            if ((var.flag_graph == 0 or var.flag_graph == 1) and var.flag_graph_HR):
                # Heart Rate
                var.flag_graph_HR = False

                HR = np.linspace(var.HR_old, var.HR_value, var.SECOND*var.axisSize)
                var.HR_array = np.append(var.HR_array, HR)
                count_HR_array = np.linspace(1, var.count_HR*var.axisSize, var.count_HR*var.axisSize)
                self.dataLinez_HR.setData(count_HR_array, var.HR_array)  # Update the data.

            if ((var.flag_graph ==0 or var.flag_graph == 2) and var.flag_graph_RR):
                # Respiratory Rate
                var.flag_graph_RR = False

                RR = np.linspace(var.RR_old, var.RR_value, var.SECOND*var.axisSize)
                var.RR_array = np.append(var.RR_array, RR)
                count_RR_array = np.linspace(1, var.count_RR*var.axisSize, var.count_RR*var.axisSize)
                self.dataLinez_RR.setData(count_RR_array, var.RR_array)  # Update the data.
            
    def updateValue(self):
        """!
        @brief Update the values of HR and RR on the GUI.
        """

        text = 'Instant {} value: {}'

        if (var.flag_RR == True):

            RR_text = text.format('RR', int(round(var.RR_value)))
            print(RR_text + 'bpm')
            self.RR_label.setText(RR_text+' bpm')

            var.flag_RR = False

        if (var.flag_HR == True):
                
            HR_text = text.format('HR', int(round(var.HR_value)))
            print(HR_text + 'bpm')
            self.HR_label.setText(HR_text+' bpm')

            var.flag_HR = False
            
    def draw(self):
        """!
             @brief Draw the plots.
        """
        self.dataLinez = self.plot(self.graphWidget,var.clock,var.zData_g,'Z-axis','b')
        self.dataLinez_lowpass = self.plot(self.graphWidget,var.clock,var.zData_lowpass,'Z-axis Low-Pass Filtered','r')
        count_RR_array = np.linspace(1, var.count_RR*var.axisSize, var.count_RR*var.axisSize)
        RR = np.linspace(var.RR_old, var.RR_value, var.count_RR*var.axisSize)
        self.dataLinez_RR = self.plot(self.RR_plot,count_RR_array, RR,'Respiratory wave','b')
        count_HR_array = np.linspace(1, var.count_HR*var.axisSize, var.count_HR*var.axisSize)
        HR = np.linspace(var.HR_old, var.HR_value, var.count_HR*var.axisSize)
        self.dataLinez_HR = self.plot(self.HR_plot,count_HR_array, HR,'Heart beat','b')
    
    def plot(self, graph, x, y, curve_name, color):
        """!
        @brief Draw graph.
        """
        pen = pg.mkPen(color=color,width=2)
        line = graph.plot(x, y, name=curve_name, pen=pen)
        return line

    @pyqtSlot(bool)
    def on_toggle(self, checked):
        """!
        @brief Allow connection and disconnection from selected serial port.
        """
        if checked:
            self.conn_btn.setText("Searching device...") 
            self.conn_btn.repaint()
            time.sleep(0.1)
            # Acquire list of serial ports
            serial_ports = [
                p.name
                for p in serial.tools.list_ports.comports()
            ]

            for i in range(len(serial_ports)):
                self.port_text=serial_ports[i]

                # Setup reading worker
                self.serial_worker = SerialWorker(self.port_text) 
                var.connectionWait = True
                print("Active port ", self.port_text)
                # Connect worker signals to functions
                self.serial_worker.signals.device_port.connect(self.connected_device)
                # Execute the worker
                self.threadpool.start(self.serial_worker)
                while(var.connectionWait==True):
                    time.sleep(0.5)

                if(var.CONN_STATUS==True):
                    self.conn_btn.setText(
                    "Disconnect from port {}".format(self.port_text))
                    self.statusTimer.timeout.connect(self.checkStatus)
                    self.statusTimer.start()
                    self.conn_label.setText("Device connected")
                    self.conn_label.setStyleSheet("background-color: rgb(0, 255, 0);\n" "border: 1px solid black")
                    break

            if(var.CONN_STATUS==False):
                self.conn_btn.setText("Device not found")
                self.conn_btn.repaint()
                time.sleep(0.5)
                self.conn_btn.setChecked(False)
            self.updateBtn.setDisabled(False)
            
        else:
           
            self.updateBtn.setChecked(False)
            # Kill thread
            self.serial_worker.is_killed = True
            self.serial_worker.killed()
            self.conn_label.setText("No device connected")
            self.conn_label.setStyleSheet("background-color: rgb(255, 0, 0);\n" "border: 1px solid black")
            #self.com_list_widget.setDisabled(False) # enable the possibility to change port
            self.conn_btn.setText("Device search")
            self.updateBtn.setDisabled(True)
            self.modeSelect.setDisabled(True)
            self.calibrate.setDisabled(True)
            self.statusTimer.stop()
            
    def connected_device(self, port_name):
        """!
        @brief Checks on the termination of the serial worker.
        """
        logging.info("Port {} closed.".format(port_name))


    def checkStatus(self):
        """!
        @brief Handle the status of the serial port connection.
        Available status:
            - 0  --> Error during opening of serial port
            - 1  --> Serial port opened correctly
        """
        if self.serial_worker.port.is_open == False:
            self.conn_btn.setChecked(False)
            self.dlg3 = QMessageBox(self)
            self.dlg3.setWindowTitle("WARNING")
            self.dlg3.setText("Connection lost, reconnect the device before proceeding")
            self.dlg3.setStandardButtons(QMessageBox.Ok)
            self.dlg3.setIcon(QMessageBox.Critical)
            button=self.dlg3.exec_()
            if(button==QMessageBox.Ok):
                self.dlg3.accept()
        
    def ExitHandler(self):
        """!
        @brief Kill every possible running thread upon exiting application.
        """
        self.serial_worker.is_killed = True
        self.serial_worker.killed()

    def dataUpdate(self,checked):
        """!
        @brief Update the data.
        """

        if checked:
            self.serial_worker.send('a')
            self.updateBtn.setText("Stop")
            self.timer.timeout.connect(lambda: self.serial_worker.readData())
            self.timer.timeout.connect(lambda: self.updateValue())
            self.timer.start()
            self.graphTimer.timeout.connect(lambda: self.drawGeneralGraph())
            self.graphTimer.start() 
            self.calibrate.setDisabled(False)
            self.modeSelect.setDisabled(False)

        else:
            self.serial_worker.send('s')
            self.updateBtn.setText("Start")
            self.timer.stop()
            self.graphTimer.stop()
            self.modeSelect.setDisabled(False)
            self.calibrate.setDisabled(True)

    def startCalibration(self): 
        """!
        @brief After the button "Calibration" is pressed. 
        """

        var.calibration_flag = True
        self.calibrate.setDisabled(True) # Deactivate the button after first calibration (the next ones will be authomatic)

#############
#  RUN APP  #
#############
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MainWindow()
    app.aboutToQuit.connect(w.ExitHandler)
    w.show()
    sys.exit(app.exec_())