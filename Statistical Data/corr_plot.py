#fig, ax = plt.subplots(nrows=2, ncols=4, figsize=(15, 8))
#
#for noise, i in zip([0.05,0.2,0.8,2],[0,1,2,3]):
#    # Add noise
#    x_with_noise = x+rand.normal(0,noise,x.shape)
#    
#    # Compute correlation
#    rho_noise = np.corrcoef(x_with_noise)
#    
#    # Plot column wise. Positive correlation in row 0 and negative in row 1
#    ax[0,i].scatter(x_with_noise[0,],x_with_noise[1,],color='magenta')
#    ax[1,i].scatter(x_with_noise[0,],x_with_noise[2,],color='green')
#    ax[0,i].title.set_text('Correlation = ' + "{:.2f}".format(rho_noise[0,1])
#                        + '\n Noise = ' + "{:.2f}".format(noise) )
#    ax[1,i].title.set_text('Correlation = ' + "{:.2f}".format(rho_noise[0,2])
#                        + '\n Noise = ' + "{:.2f}".format(noise))
#    ax[0,i].set(xlabel='x',ylabel='y')    
#    ax[1,i].set(xlabel='x',ylabel='y')
#    
#fig.subplots_adjust(wspace=0.3,hspace=0.4)    
#plt.show()

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pdb
from numpy.random import random
import pandas as pd
import scipy
from scipy import stats

df1 = pd.read_csv('HR_Rate.csv')
df2 = pd.read_csv('HR_Rate_True.csv')
df3 = pd.read_csv('Heart_Rate_True.csv')
df4 = pd.read_csv('Heart_Rate.csv')

new_meas = df1['RR']
gold = df2['RR']
new_meas_HR = df3['HR']
gold_HR = df4['HR']

#plt.scatter(gold, new_meas)
plt.scatter(gold_HR, new_meas_HR, color = 'red')
plt.title('Heart Rate')
#plt.title('Respiratory Rate')
plt.xlabel('gold standard [bpm]')
plt.ylabel('custom device [bpm]')
plt.show()

pHR = stats.pearsonr(gold_HR, new_meas_HR)
print(pHR)

pRR = stats.pearsonr(gold, new_meas)
print(pRR)

### PEARSON COEFFICIENT ###

#sns.scatterplot(x=gold, y=new_meas)