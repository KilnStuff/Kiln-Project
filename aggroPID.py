#!/usr/bin/env python3

import numpy as np
import time
import board
import busio
import digitalio
import adafruit_max31855
import RPi.GPIO as gpio

zones = np.array([17,27,23])   #pin number of each zone  (1,2,3)

gpio.setmode(gpio.BCM)
for z in zones:
    gpio.setup(int(z), gpio.OUT)

 
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs1 = digitalio.DigitalInOut(board.D4)
cs2 = digitalio.DigitalInOut(board.D25)
cs3 = digitalio.DigitalInOut(board.D12)
 
thermo1 = adafruit_max31855.MAX31855(spi, cs1)
thermo2 = adafruit_max31855.MAX31855(spi, cs2)
thermo3 = adafruit_max31855.MAX31855(spi, cs3)

#################################################################################################
#imputs

setpoint = input("Enter setpoint(C)\n")
try:
    setpoint = float(setpoint)
except ValueError:
    print("Your input was not a number.")
    print("exiting")
    exit(1)


fileName = input("Enter file name to write to(type 'none' to not record data to textfile)\n")
if fileName == "none":
    textfile = False
else:
    textfile = True

if textfile == True:
    Out = open(fileName,'w')
    Out.write("time [sec], Temperature (1), Temperature (2), Temperature (3) ;\n")
    Out.close()

'''
sampleRate = input("Enter sample period(seconds between samples)\n")
try:
    sampleRate = float(sampleRate)
except ValueError:
    print("Your input was not a number.")
    print("exiting")
    exit(1)
'''


#################################################################################
#################################################################################
#setup for loop

sampleRate = 1
updateRate = 5
powerCycle = 2

allowedFailTime = 10
fail1 = False
fail2 = False
fail3 = False


P = np.array([260,260,137])
I = np.array([2.6,2.6,1.37])
D = np.array([26,26,13.7])

boxLen = 10
maxPower = np.array([2618,2618,1371]) 
kout = np.array([2.76,.6,1.05])
maxIntErr = maxPower/I
intErrBound = 25
roomTemp = 25

errs = np.array([[],[],[]])
intErr = np.array([0.,0.,0.])
derErr = np.array([0.,0.,0.]) 
ts = np.array([])
power  = np.array([0.,0.,0.])
powerRatio = np.array([0.,0.,0.])
boolOn = np.array([False,False,False])

tstart = time.perf_counter()
#begin PID loop

t = -sampleRate  #ensures first loop measures temp
updateTime = tstart-updateRate  #ensures first loop updates power

'''
tOff = tstart + np.array([0,0,0])
tOn = tstart + np.array([0,0,0])
'''
tOff =np.array([0,0,0])
tOn =np.array([0,0,0])

while True:
    ###################################################################
    #temp aquisition
    if (time.perf_counter() - tstart)-t >= sampleRate-.0069:
        
        try:
            temp1 = thermo1.temperature
            fail1 = False
        except RuntimeError:
            if fail1 == False:
                failTime = t
                fail1 = True
                print("thermocouple 1 has been having a rough day\n")
            else:
                #print("fail time: %.2f\n" % (t-failTime))
                if (time.perf_counter() - tstart)-failTime > allowedFailTime:
                    print("themocouple 1 execeded allowed fail time")
                    print("Exiting PID loop")
                    break
            continue
        
       
        try:
            temp2 = thermo2.temperature
            fail2 = False
        except RuntimeError:
            if fail2 == False:
                failTime = t
                fail2 = True
                print("thermocouple 2 has been having a rough day\n")
            else:
                #print("fail time: %.2f\n" % (t-failTime))
                if (time.perf_counter() - tstart)-failTime > allowedFailTime:
                    print("themocouple 2 execeded allowed fail time")
                    print("Exiting PID loop")
                    break
            continue
                      
        try:
            temp3 = thermo3.temperature
            fail3 = False
        except RuntimeError:
            if fail3 == False:
                failTime = t
                fail1 = True
                print("thermocouple 3 has been having a rough day\n")
            else:
                #print("fail time: %.2f\n" % (t-failTime))
                if (time.perf_counter() - tstart)-failTime > allowedFailTime:
                    print("themocouple 3 execeded allowed fail time")
                    print("Exiting PID loop")
                    break
            continue

        #time of measuremernt
        t = time.perf_counter() - tstart

        #print stuffs
        h = t//3600
        m = (t-h*3600)//60
        s = t - h*3600 - m*60
        tstr = "%.f hrs, %.f min, %.2f sec" % (h,m,s)
       
        print("Time(s): %s Temperatures(C): %.2f, %.2f, %.2f Rate(C/min): %.2f, %.2f, %.2f\n" % (tstr , temp1, temp2, temp3, -derErr[0]*60, -derErr[1]*60, -derErr[2]*60))
       
        if textfile == True:
            Out = open(fileName,'a')
            Out.write("%.2f, %.2f, %.2f, %.2f\n" % (t , temp1, temp2, temp3))
            Out.close()

        # updates error array
        temp = np.array([temp1,temp2,temp3])
        err = setpoint - temp
        
        if len(errs[0])>=boxLen:
            for i in range(len(errs)):
                errs[i] = np.delete(np.append(np.transpose(np.array([err])),errs, axis = 1)[i],len(errs[i]))
        else:
            errs = np.append(np.transpose(np.array([err])),errs, axis = 1)

        if len(ts)>=boxLen:
                ts = np.delete(np.append(np.array([t]),ts),len(ts))
        else:
            ts = np.append(np.array([t]),ts)

    ###############################################################################
    #updates power and time on for coils
    if time.perf_counter()-updateTime >= updateRate:
        updateTime = time.perf_counter()
        # CAlculate P,I,D
        
        #intgral term
        if len(ts)>1:
            for i in range(len(intErr)):
                if abs(intErr[i] + err[i]*(ts[0]-ts[1])) < maxIntErr[i] and abs(err[i])< intErrBound:
                    intErr[i] += err[i]*(ts[0]-ts[1])
        
        #dermintive term
        if len(ts)>1:
            for i in range(len(derErr)):
                dsum = 0
                for j in range(len(errs[i])-1):
                    dsum += (errs[i][j+1]-errs[i][j])/(ts[j+1]-ts[j])
                derErr[i] = dsum/(len(errs[i]))

        #calculate powers
        for i in range(len(power)):

            power[i] = P[i]*err[i] + I[i]*intErr[i] + D[i]*derErr[i] + kout[i]*(temp[i]-roomTemp)

            if power[i] > maxPower[i]:
                power[i] = maxPower[i]
            if power[i] < 0:
                power[i] = 0

        for i in range(len(powerRatio)):
            powerRatio[i] = power[i]/maxPower[i]    #give the fraction of power to deliver

        #powerRatio = np.array([.5,.5,.5])
        
        timeOn = powerCycle*powerRatio  #time spent with power on
        timeOff = powerCycle - timeOn    #time spent with power off

        #print stuffs

        tu = updateTime - tstart
        h = tu//3600
        m = (tu-h*3600)//60
        s = tu - h*3600 - m*60
        tstr = "%.f hrs, %.f min, %.2f sec" % (h,m,s)
        #print(power)
        print("Time: %s Powers: %.2f, %.2f, %.2f\n" % (tstr , powerRatio[0], powerRatio[1], powerRatio[2]))

    ##########################################################################################
    #turns on and off coils
    #print("preloop")
    for i in range(len(zones)):
        if time.perf_counter() - tOff[i] >= timeOff[i] and boolOn[i] == False:
            gpio.output(int(zones[i]),gpio.HIGH)
            tOn[i] = time.perf_counter()
            boolOn[i] = True
            #print("coil %.f ON" % (i+1))
            

    for i in range(len(zones)):
        if time.perf_counter() - tOn[i] >= timeOn[i] and boolOn[i] == True:
            gpio.output(int(zones[i]),gpio.LOW)
            tOff[i] = time.perf_counter()
            boolOn[i] = False
            #print("coil %.f OFF" % (i+1))
###############################################################################################
###############################################################################################
#bad stuffs
for i in range(len(zones)):
        gpio.output(zones[i],gpio.LOW)
print("Power Off")

