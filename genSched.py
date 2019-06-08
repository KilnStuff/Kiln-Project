#!/usr/bin/env python3

import numpy as np


#fileName = "sched1"

#linear Ramp

#tmax = 1.5*60*60

#ts = np.arange(tmax)

#roomTemp = 25  # C

#rampRate = .1 # C/sex

#temps = rampRate*ts+roomTemp

'''
fileName = "bisque2"

#candle at 125 for 60 min
tcandle = 1*60*60
tempcandle = 125

ts = np.array([0,tcandle])
temps = np.array([tempcandle,tempcandle])

#best ramp to 700 and ~3 hrs
tm = 700
bestTime = 3*60*60

ts = np.append(ts, np.array([tcandle]))
temps = np.append(temps , np.array([tm]))

#ramp at 1 c per min to 1060 (cone04)
ramp = 1/60

tempf = 1060

t = np.arange((tempf-tm)/ramp)

temp = tm+ramp*t

ts = np.append(ts, t+bestTime+tcandle)
temps = np.append(temps , temp)
'''


fileName = "glaze2"

#candle at 125 for 1 hr

tcandle = 60*60
tempcandle = 125

ts = np.array([0,tcandle])
temps = np.array([tempcandle,tempcandle])


#best ramp to 1000 and ~5 hrs
tHold = 1000
t = 22000-3600+1000

ts = np.append(ts, np.array([ts[-1],t+ts[-1]]))
temps = np.append(temps , np.array([tHold,tHold]))
'''
#ramp at 1.5 c per min to 900 (~cone03)
ramp = 1.5/60
tempf = 900

t = np.arange((tempf-temps[-1])/ramp)

temp = temps[-1]+ramp*t

ts = np.append(ts, t+ts[-1])
temps = np.append(temps , temp)
'''
#ramp at 1 c per min to 1100 (~cone3)
ramp = 1/60
tempf = 1100


t = np.arange((tempf-temps[-1])/ramp)

temp = temps[-1]+ramp*t

ts = np.append(ts, t+ts[-1])
temps = np.append(temps , temp)

#ramp at .25 c per min to 1250 (~cone6)
ramp = .25/60
tempf = 1250


t = np.arange((tempf-temps[-1])/ramp)

temp = temps[-1]+ramp*t

ts = np.append(ts, t+ts[-1])
temps = np.append(temps , temp)




Out = open(fileName,'w')
Out.write("time [sec], Temperature\n")
Out.close()

for t,temp in zip(ts,temps):
    Out = open(fileName,'a')
    Out.write("%.2f, %.2f\n" % (t , temp))
    Out.close()

import matplotlib.pyplot as plt

size = 2


setData = np.transpose(np.loadtxt(fileName, delimiter = ',', skiprows = 1))

fig, ax = plt.subplots()
ax.set_title(fileName)
ax.set_xlabel('Time [sec]')
ax.set_ylabel('Temp [c]')
ax.plot(setData[0],setData[1],'k--', label = 'Set Point', markersize = size)
ax.legend()
fig.show()

input("Press Enter to Exit")

