#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: % P. M. Harrington
"""
import numpy as np
import matplotlib.pyplot as plt
import scipy.signal
import os
import sys
sys.path.append("/Applications/Labber/Script")
import Labber

def get_psd(file_name_label, VERBOSE=False):
    ''' calculates power spectral density '''

    file_name = file_name_label[0]
    # file_label = file_name_label[1]
    
    # set the directory to read
    file_str = path_data + file_name
    
    # get hdf5 logfile
    logfile = Labber.LogFile(file_str)
    
    # get data of first entry to calculate sample frequency
    num_entries = logfile.getNumberOfEntries()
    (time, signal) = logfile.getTraceXY(y_channel='Alazar DAQ1 - Ch1 - Data', 
                                        entry=int(0))
    
    # determine the sample frequency
    dt = time[1] - time[0]
    f_samp = 1/dt

    if VERBOSE:
        print('\n')
        print('Finding PSD: {}'.format(file_name_label[0]))
        
    #calculate PSDs for each file in the directory
    psd_list = []        
    for entry_num in range(num_entries):        
        if VERBOSE:
            print('Progress: {:4d}/{:4d}'.format(entry_num+1, num_entries))
        
        #import data
        (time, voltages) = logfile.getTraceXY(y_channel='Alazar DAQ1 - Ch1 - Data', 
                                              entry=int(entry_num))
        
        #calculate the periodogram with a hanning window
        freq, psd = scipy.signal.periodogram(voltages, 
                                             fs = f_samp,
                                             window = 'hann', 
                                             detrend = False, 
                                             scaling = 'density', 
                                             return_onesided = True)
        #add this PSD to the list
        psd_list.append(psd)
    
    #take the average of the PSDs
    average_psd = []
    for i in range(0,len(psd_list[0])):
        pre_average = []
        for j in range(0,len(psd_list)):
            pre_average.append(psd_list[j][i])
        average_psd.append(np.average(pre_average))
    return freq, average_psd

if __name__=='__main__':
    path_results_folder = os.getcwd()
    path_data = os.getcwd() + '/data/'
    directory_list = [['20200910_psd_00.hdf5', 'example_file_1'],
                      ['20200910_psd_01.hdf5', 'example_file_2'],
                      ]
    
    psd_list = []
    freq_list = []
    log_info = []
    for data_file_num, file_name_label in enumerate(directory_list):    
        freq, average_psd = get_psd(file_name_label, VERBOSE=True)
        freq_list.append(freq)
        psd_list.append(average_psd)
        log_info.append(file_name_label)

    # plotting
    legend_list = []
    for data_file_num, file_name_label in enumerate(log_info):    
        file_name = file_name_label[0]
        file_label = file_name_label[1]
        legend_list.append(file_label)
    
        freq = freq_list[data_file_num]
        _psd = np.sqrt(psd_list[data_file_num])
        plt.loglog(freq, _psd, '-', linewidth=0.5)
    
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Amplitude [V/$\sqrt{Hz}$]')
    plt.grid()
    plt.legend(legend_list, loc="upper right")
    #
    f_save = path_results_folder + '/psd_all'
    plt.savefig(f_save + '.png')
    plt.savefig(f_save + '.pdf')
    plt.show()