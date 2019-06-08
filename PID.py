#!/usr/bin/env python3

import numpy as np
import time
import board
import busio
import digitalio
import adafruit_max31855
import RPi.GPIO as gpio

zones = np.array([17,27,23])   #pin number on pi that controls each zone  (1,2,3)

#setup to turn on off the gpio to control relays
gpio.setmode(gpio.BCM)
for z in zones:
    gpio.setup(int(z), gpio.OUT)

 #setup for themocoulple boards
spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
cs1 = digitalio.DigitalInOut(board.D4)
cs2 = digitalio.DigitalInOut(board.D25)
cs3 = digitalio.DigitalInOut(board.D12)
 
thermo1 = adafruit_max31855.MAX31855(spi, cs1)
thermo2 = adafruit_max31855.MAX31855(spi, cs2)
thermo3 = adafruit_max31855.MAX31855(spi, cs3)

#################################################################################################
#inputs
#gets the file name of the firing shcedule to use
#if nothin is typed it allow you to enter a fixed setpoint value
setFileName = input("Enter file name of the firing schedule(press enter to use fixed value)\n")
if setFileName == "":
    setFile = False
    setPoint = input("Enter setPoint(C)\n")
    try:
        setPoint = float(setPoint)
    except ValueError:
        print("Your input was not a number.")
        print("exiting")
        exit(1)
else:
    setFile = True

 #reads setpint file   
if setFile == True:
    setData = np.transpose(np.loadtxt(setFileName, delimiter = ',', skiprows = 1))
# get file name to record data to
fileName = input("Enter file name to write to(press enter to not record data to textfile)\n")
if fileName == "":
    textfile = False
else:
    textfile = True

# sets up text file for data 
# first line is the file name of the firing shceluel
#if no shceduel setpont is recorded on the secound line
if textfile == True:
    Out = open(fileName,'w')
    if setFile == False:
        Out.write("\ntime [sec], Temperature (1), Temperature (2), Temperature (3) ;set point = %.f\n" % setPoint)
    else:
        Out.write("%s\ntime [sec], Temperature (1), Temperature (2), Temperature (3)\n" % setFileName)
    Out.close()



#################################################################################
#################################################################################
#setup for loop

sampleRate = 1 #seconds between temperature measurements
updateRate = 5 #seconds between power updates
powerCycle = 2 #length in seconds of on on off cycle of coils

allowedFailTime = 5*60   #allowed time for a themocouple to be broken befor the kiln shuts off
fail1 = False  # set to true when a thermocouple has a faulty reading
fail2 = False
fail3 = False

#the slowzone array is the ordering of how fast each zone can heat with respect to the others
#the fist element is the number of the slowest zone and the last is the fastest'
#this is used to decide which zone is followed
slowZone = np.array([3,1,2])   #  index will be slowZone-1
minRamp = 1/60   # minimum ramp rate where the zones become uncoupled

P = np.array([260,260,137])    #porportion constant
I = np.array([2.6,2.6,1.37])   #integral constant
D = np.array([26,26,13.7])/2   #derivitive constant

boxLen = 20   #number of perivious pionts to use in caluculation of the derivitive term
rampBoxLen = 40    #number of perivious pionts to use in caluculation of the current ramp rate
maxPower = np.array([2618,2618,1371])   # max power each zone can deliver
kout = np.array([2.76,.6,1.05])    #disiapative coeffefitents
maxIntErr = maxPower/I  # max value of the integral  helps avoid integral windup
intErrBound = 25            # the integral is only summed when the error is less than this value
roomTemp = 25           

temps = np.array([[],[],[]])
err = np.array([0.,0.,0.])
errs = np.array([[],[],[]])
intErr = np.array([0.,0.,0.])
derErr = np.array([0.,0.,0.])
ramp = np.array([0.,0.,0.])
ts = np.array([])
power  = np.array([0.,0.,0.])
powerRatio = np.array([0.,0.,0.])         # ratio of the powerneeded vs max power
boolOn = np.array([False,False,False])         #keeps track of wether or not a coil is on
setPoints = np.array([0.,0.,0.])           #setpints for each zone

tstart = time.perf_counter()
#begin PID loop

t = -sampleRate  #ensures first loop measures temp
updateTime = tstart-updateRate  #ensures first loop updates power


tOff = np.array([0,0,0]) + tstart   #time the coil was turned off at
tOn = np.array([0,0,0]) + tstart    #time the coil was turned on at
timeOff = np.array([0,0,0]) + tstart    #time the coil is supposed to be off for
timeOn = np.array([0,0,0]) + tstart      #time the coil is supposed to be on for

while True:
    ###################################################################
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


    #temp aquisition
    if (time.perf_counter() - tstart)-t >= sampleRate-.0069:
        
        # measures temp of each zone. returns back to the top of the loop if an error is thrownwhile reading a themocouple
        #themo1
        try:
            temp1 = thermo1.temperature
            fail1 = False
        except RuntimeError as e:
            if fail1 == False:
                failTime = t
                fail1 = True
                print("thermocouple 1 has been having a rough day. He has been feeling like a %s.\n" %e)
            else:
                #print("fail time: %.2f\n" % (t-failTime))
                if (time.perf_counter() - tstart)-failTime > allowedFailTime:
                    print("themocouple 1 execeded allowed fail time")
                    print("Exiting PID loop")
                    break
            continue
        
       #themo2
        try:
            temp2 = thermo2.temperature
            fail2 = False
        except RuntimeError as e:
            if fail2 == False:
                failTime = t
                fail2 = True
                print("thermocouple 2 has been having a rough day. He has been feeling like a %s.\n" %e)
            else:
                #print("fail time: %.2f\n" % (t-failTime))
                if (time.perf_counter() - tstart)-failTime > allowedFailTime:
                    print("themocouple 2 execeded allowed fail time")
                    print("Exiting PID loop")
                    break
            continue
            
        #themo3              
        try:
            temp3 = thermo3.temperature
            fail3 = False
        except RuntimeError as e:
            if fail3 == False:
                failTime = t
                fail3 = True
                print("thermocouple 3 has been having a rough day. He has been feeling like a %s.\n" %e)
            else:
                #print("fail time: %.2f\n" % (t-failTime))
                if (time.perf_counter() - tstart)-failTime > allowedFailTime:
                    print("themocouple 3 execeded allowed fail time")
                    print("Exiting PID loop")
                    break
            continue

        #time of the temperature measuremernt
        t = time.perf_counter() - tstart

        #print stuffs
        h = t//3600
        m = (t-h*3600)//60
        s = t - h*3600 - m*60
        tstr = "%.f hrs, %.f min, %.2f sec" % (h,m,s)
       
        print("Time(s): %s Temperatures(C): %.2f, %.2f, %.2f Rate(C/min): %.2f, %.2f, %.2f\n" % (tstr , temp1, temp2, temp3, ramp[0]*60, ramp[1]*60, ramp[2]*60))       
        if textfile == True:
            Out = open(fileName,'a')
            Out.write("%.2f, %.2f, %.2f, %.2f\n" % (t , temp1, temp2, temp3))
            Out.close()

        # updates temps array
        temp = np.array([temp1,temp2,temp3])
        
        if len(temps[0])>=rampBoxLen:
            for i in range(len(temps)):
                temps[i] = np.delete(np.append(np.transpose(np.array([temp])),temps, axis = 1)[i],len(temps[i]))
        else:
            temps = np.append(np.transpose(np.array([temp])),temps, axis = 1)

        #updates the times aray
        if len(ts)>=rampBoxLen:
                ts = np.delete(np.append(np.array([t]),ts),len(ts))
        else:
            ts = np.append(np.array([t]),ts)
        
        
        #calculates the current ramprate
        if len(ts)>1:
            for i in range(len(ramp)):
                dsum = 0
                for j in range(len(temps[i])-1):
                    dsum += (temps[i][j+1]-temps[i][j])/(ts[j+1]-ts[j])
                ramp[i] = dsum/(len(temps[i]))


        #find the set value
        if setFile == True:
            endFile = True
            for i in range(len(setData[0])):
                if setData[0][i]>t:
                    setPoint = setData[1][i-1]
                    endFile = False
                    break
            #exits the firing if the text file is finished
            if endFile == True:
                print('end of firing Schedule')
                break
            
                
        #uncouples the zones when the slowzone is less than the minimum Ramp
        setPoints[slowZone[0]-1] = setPoint
        if ramp[slowZone[0]-1] < minRamp:
            setPoints[slowZone[1]-1] = setPoint
            if ramp[slowZone[1]-1] < minRamp:
                setPoints[slowZone[2]-1] = setPoint
                #print("follow setPoint")
            else:
                setPoints[slowZone[2]-1] = temp[slowZone[1]-1]
                #print("follow zone 1")
        else:
            setPoints[slowZone[1]-1] = temp[slowZone[0]-1]
            setPoints[slowZone[2]-1] = temp[slowZone[0]-1]
            #print("follow zone 3")

        #calculates the error 
        for i in range(len(zones)):
            err[i] = setPoints[i] - temp[i]
        
        #creates an array of te previous errors
        if len(errs[0])>=boxLen:
            for i in range(len(errs)):
                errs[i] = np.delete(np.append(np.transpose(np.array([err])),errs, axis = 1)[i],len(errs[i]))
        else:
            errs = np.append(np.transpose(np.array([err])),errs, axis = 1)


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
        print("Time(s): %s Set Points(C): %.2f, %.2f, %.2f Powers: %.2f, %.2f, %.2f\n" % (tstr , setPoints[0],setPoints[1],setPoints[2], powerRatio[0], powerRatio[1], powerRatio[2]))

    ##########################################################################################
    ###############################################################################################
#bad stuffs  get here by some error or if the firing is finished
for i in range(len(zones)):
        gpio.output(int(zones[i]),gpio.LOW)
print("Power Off")

