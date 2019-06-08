#!/usr/bin/env python3

import time
import numpy as np
import matplotlib.pyplot as plt


size = 2
buffersize = 1/50

fileName = input("Enter file name data to plot\n")
refreshTime = input("Enter how often to refresh the plot(enter 0 to plot once)\n")
try:
    refreshTime = float(refreshTime)
except ValueError:
    print("Your input was not a number.")
    print("exiting")
    exit(1)
    
In = open(fileName)
setFileName = In.readline()[:-1]
In.close()

if setFileName == '' or setFileName == "time [sec], Temperature (1), Temperature (2), Temperature (3)" or setFileName == "time [sec], Temperature (1), Temperature (2), Temperature (3) ;":
    setFile = False
else:
    setFile = True

if setFile == True:
    setData = np.transpose(np.loadtxt(setFileName, delimiter = ',', skiprows = 1))

if setFile == True:
    show = input("Show whole set point plot?(Press enter for no and type anything for yes)\n")
    if show == "":
        showSet = False
    else:
        showSet = True
else:
    showSet =False
         
fig, ax = plt.subplots()
ax.set_title(fileName)
ax.set_xlabel('Time [sec]')
ax.set_ylabel('Temp [c]')
fig.show()

while True:
    to = time.perf_counter()
    data = np.transpose(np.loadtxt(fileName, delimiter = ',', skiprows = 2))

    
    l1, = ax.plot(data[0],data[1],'r.', label = 'zone 1', markersize = size)
    l2, = ax.plot(data[0],data[2],'g.', label = 'zone 2', markersize = size)
    l3, = ax.plot(data[0],data[3],'b.', label = 'zone 3', markersize = size)
    if setFile == True:
        l4, = ax.plot(setData[0],setData[1],'k--', label = 'Set Point', markersize = size)
    
    ax.legend()
    if showSet == False:
        ax.set_xlim([data[0][0]-(data[0][-1]-data[0][0])*buffersize, data[0][-1]+(data[0][-1]-data[0][0])*buffersize])
    

    fig.canvas.draw()

    if refreshTime <= 0:
        break

    l1.remove()
    l2.remove()
    l3.remove()
    if setFile == True:
        l4.remove()
    
    
    time.sleep(refreshTime)

input("Press Enter to Exit")
