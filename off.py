#!/usr/bin/env python3

import RPi.GPIO as gpio
gpio.setmode(gpio.BCM)
gpio.setup(17, gpio.OUT) #1
gpio.setup(27, gpio.OUT) #2
gpio.setup(23, gpio.OUT) #3

gpio.output(17,gpio.LOW)
gpio.output(27,gpio.LOW)
gpio.output(23,gpio.LOW)#turns off

print("off")
