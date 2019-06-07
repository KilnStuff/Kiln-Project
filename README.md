# Kiln-Project

  In this guide we will detail our process and design for an electronic temperature controlled kiln. The goal of this project was to convert a manual temperature controlled kiln, which originally set the temperature by means of a knob, to a much more sophisticated electronic control system that could drive the kiln to a specific temperature based on thermocouple feedback. This project required us to wire and build the system from scratch, with the only previously constructed components being the kiln itself and our means to electronically communicate with the kiln, a raspberry pi (as well as peripherals for the pi).
  
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_142748.jpg)
  
  ## Table of Contents
* [List of Components](https://github.com/KilnStuff/Kiln-Project#list-of-components)
* [Design](https://github.com/KilnStuff/Kiln-Project#design)
* [Building Process](https://github.com/KilnStuff/Kiln-Project#building-process)
* [Designing A PID](https://github.com/KilnStuff/Kiln-Project#designing-a-pid)
* [Finished Product and Data](https://github.com/KilnStuff/Kiln-Project#finished-product-and-data)
* [Contributors](https://github.com/KilnStuff/Kiln-Project#contributors)


# List of Components

  As previously stated the only components that were preassembled were a raspberry pi and the kiln with manual controls. The remaining parts that we used are listed below in two categories: those whose purpose was to house/contain/transmit AC current, and those used to communicate with the pi through DC current (or deal exclusively with the pi). The purpose and function of these parts are explained throughout the Design and Building Process sections.
  
  ## AC Components
  * Cutler Hammer CH220 Circuit Breaker x3 (~$14 each)
  * Cable SEOOW, Black Outer Insulation, 8 Gauge, 3 Wires, 10 ft. (~$27)
  * Cable SJTW, Orange Outer Insulation, 12 Gauge, 3 Wires, 25 ft. (~$32)
  * Eaton Type CH 16-Circuit 125-Amp Main Lug Load Center (~$44)
  * Red 8 Gauge Heat Shrink Butt Connectors (~$20)
  * MURRAY ECLX071M Siemens Eclx Ground Bar Kit x2 (~$8 each)
  * BUD Industries JBH-4956-KO Steel NEMA 1 Sheet Metal Box (~$17)
  
  
  ## DC/Pi Components
  * Adafruit Perma-Proto HAT for Pi Mini Kit (~$9)
  * High Temperature k-type Thermocouple Sensor (~30)
  * Solid State Relay SSR-25 DA 25A x3 (~$10 each)
  * Adafruit Thermocouple Amplifier MAX31855 x3 (~$16 each)
  * 2N2222 to-92 Transistor NPN 40V 600mA 300MHz 625mW x3 (~$7 total for 200)
  * ABS Junction Box Universal Project Enclosure (~$11)
  * MEANWELL Switching Power Supplies 50W 5V 10A (~$20)
  * Eaton CHF215 Plug-On Mount Type CHF Circuit Breaker 15A (~$20)

The total came out to roughly ~$400 with shipping costs. Overall, this investment is much cheaper than buying an electronic kiln commercially of this size, which can easily go for $2500. We spent $500 for the kiln and $75 for the pi and peripherals, so overall this project gave us a product half as cheap for the same (or debatebly better) functionality.

# Design

  Since the actual coils inside the kiln are powered by AC current from the wall, but the pi is powered/communicates through DC the way we chose to limit the power reaching the kiln was through solid state relays. These relays are connected to the wall at 240 V and on the other side to the pi at 5V. These relays are "always open", so AC will only pass through if the pi is applying a DC current. They are also "zero crossing", so they will only start/stop transmitting AC when its phase corresponds to when the wall voltage is at 0. This allows for a type of PWM (Pulse Width Modulation) for the kiln, where we can control the amount of power entering within a given time frame by limiting the amount of time the coils are on within a period. Below is the schematic for the AC current side:
  
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/AC%20Schematic.png)
  
  As long as the Hot Wires are properly matched it doesn't matter which is connected to each end of the plug/SSR (They both alternate between +120 and -120 with a 180 degree phase shift). Each black/white wire forms a loop with the coil inside the kiln, so we only needed to attach the SSR across one wire (we chose the black wire). Hence the circuit is open when the SSR is open (no current applied on DC side) and closed if the SSR is closed (DC current is applied by pi). There is a transformer which transforms the wall power to a 5V power supply connected to the SSR's. The other terminal of the DC side on the SSR is connected to a transistor which ensures the circuit is open until the Pi applies power. The exact circuit is described firther down in this section. Another point to note on the above diagram is that for simplicity sake only 1 SSR is wired (and only 1 wire plugged into the kiln). However in reality all 3 wires are connected to the SSR and kiln in the exact same fashion as shown in the diagram above. Pictures of the breaker box and box with the relays are below:
  
  ## Closed Breaker Box/Open Breaker Box
  ![alt text]
  
  ![alt text]

# Building Process



# Designing a PID



# Finished Product and Data



# Contributors
