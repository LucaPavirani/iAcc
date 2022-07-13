import matplotlib.pyplot as plt
import numpy as np
import pdb
from numpy.random import random
import pandas as pd

STD_LIM = 1.96

def bland_altman_plot(data1, data2, *args, **kwargs):
    data1     = np.asarray(data1)
    data2     = np.asarray(data2)
    mean      = np.mean([data1, data2], axis=0)
    diff      = data1 - data2                   # Difference between data1 and data2
    md        = np.mean(diff)                   # Mean of the difference
    sd        = np.std(diff, axis=0)            # Standard deviation of the difference
    CI_low    = md - STD_LIM*sd
    CI_high   = md + STD_LIM*sd

    print(len(mean))
    print(mean)
    print(len(diff))
    print(diff)

    plt.scatter(mean, diff, *args, **kwargs)
    plt.axhline(md,           color='black', linestyle='-')
    plt.axhline(md + STD_LIM*sd, color='gray', linestyle='--')
    plt.axhline(md - STD_LIM*sd, color='gray', linestyle='--')
    return md, sd, mean, CI_low, CI_high


# compare zData with yData - try
new_meas = []
gold = []
new_meas_fin = []
gold_fin = []
df1 = pd.read_csv('HR_Rate.csv')
df2 = pd.read_csv('HR_Rate_True.csv')

new_meas = df1['RR']
gold = df2['RR']

md, sd, mean, CI_low, CI_high = bland_altman_plot(new_meas, gold)
plt.title(r"$\mathbf{Bland-Altman}$" + " " + r"$\mathbf{Plot}$")
plt.xlabel("Means")
plt.ylabel("Difference")
plt.ylim(md - 3.5*sd, md + 3.5*sd)

xOutPlot = np.min(mean) + (np.max(mean)-np.min(mean))*1.14

plt.text(xOutPlot, md - STD_LIM*sd, 
    r'-1.96SD:' + "\n" + "%.2f" % CI_low, 
    ha = "center",
    va = "center",
    )
plt.text(xOutPlot, md + STD_LIM*sd, 
    r'+1.96SD:' + "\n" + "%.2f" % CI_high, 
    ha = "center",
    va = "center",
    )
plt.text(xOutPlot, md, 
    r'Mean:' + "\n" + "%.2f" % md, 
    ha = "center",
    va = "center",
    )
plt.subplots_adjust(right=0.85)
plt.show()