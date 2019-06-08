# Kiln-Project

  In this guide we will detail our process and design for an electronic temperature controlled kiln. The goal of this project was to convert a manual temperature controlled kiln, which originally set the temperature by means of knobs, to a much more sophisticated electronic control system that could drive the kiln to a specific temperature based on thermocouple feedback. This project required us to wire and build the system from scratch, with the only previously constructed components being the kiln itself and our means to electronically communicate with the kiln, a raspberry pi (as well as peripherals for the pi).
  
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_142748.jpg)
  
  ## Table of Contents
* [List of Components](https://github.com/KilnStuff/Kiln-Project#list-of-components)
* [Design](https://github.com/KilnStuff/Kiln-Project#design)
* [Building Process](https://github.com/KilnStuff/Kiln-Project#building-process)
* [Code](https://github.com/KilnStuff/Kiln-Project#Code)
* [Designing A PID](https://github.com/KilnStuff/Kiln-Project#designing-a-pid)
* [Finished Product](https://github.com/KilnStuff/Kiln-Project#finished-product)
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

The total came out to roughly ~$400 with shipping costs. Overall, this investment is much cheaper than buying an electronic kiln commercially of this size, which can easily go for $2500. We spent $500 for the kiln and $75 for the pi and peripherals, so overall this project gave us a product over half as cheap for the same (or debatebly better) functionality.

# Design

  Since the actual coils inside the kiln are powered by AC current from the wall, but the pi is powered/communicates through DC the way we chose to limit the power reaching the kiln was through solid state relays. These relays are connected to the wall at 240 V and on the other side to the pi at 5V. These relays are "always open", so AC will only pass through if the pi is applying a DC current. They are also "zero crossing", so they will only start/stop transmitting AC when its phase corresponds to when the wall voltage is at 0. This allows for a type of PWM (Pulse Width Modulation) for the kiln, where we can control the amount of power entering within a given time frame by limiting the amount of time the coils are on within a period. The zero crossing function also means there is far less noise in the system, as dropping suddenly from a high frequency to zero corresponds to a broad range of frequency spectrum. Below is the schematic for the AC current side:
  
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/AC%20Schematic.png)
  
  As long as the Hot Wires are properly matched it doesn't matter which is connected to each end of the plug/SSR (They both alternate between +120 and -120 with a 180 degree phase shift). Each black/white wire forms a loop with the coil inside the kiln, so we only needed to attach the SSR across one wire (we chose the black wire). Hence the circuit is open when the SSR is open (no current applied on DC side) and closed if the SSR is closed (DC current is applied by pi). There is a transformer which transforms the wall power to a 5V power supply connected to the SSR's. The other terminal of the DC side on the SSR is connected to a transistor which ensures the circuit is open until the Pi applies power. The exact circuit is described further down in this section. Another point to note on the above diagram is that for simplicity sake only 1 SSR is wired (and only 1 wire plugged into the kiln). However in reality all 3 wires are connected to the SSR and kiln in the exact same fashion as shown in the diagram above. Pictures of the breaker box and box with the relays are below:
  
  ## Closed Breaker Box/Open Breaker Box
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_142810.jpg)
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_142917.jpg)
  
  ## Wiring of Breaker Box
  
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_143202.jpg)
  
  ## Wiring of SSR's
  
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_142939.jpg)
  
  ## Pi Wiring
  
The wiring of the Raspberry Pi’s hat is separated into two separate circuits. One circuit is what controls the SSRs through the GPIO pins, and the other circuit communicates with the thermocouple amplifier boards to read off the temperature.
  
**SSR Circuit**

To run SSRs of the type we are using, the 3.3V supplied directly from the pi’s GPIO pins is insufficient to fully close the SSRs and have them allow current through. Instead, a 5V supply must be used, but because the Pi does not support 5V directly from the GPIO, transistors must be used instead.

In this circuit (below), the relevant GPIO pin on the pi is attached through an LED and then 100 ohm resistor, in series, to the base wire of one of the three transistors. The emitter is connected directly to ground, while the collector connects to the V- leg of the DC side of the SSR. Meanwhile, the V+ leg is wired directly to the + terminal on the power supply. 

In this system, when the GPIO is supplying voltage to the base of the transistor, the transistor closes the circuit and allows 5V current to flow from the power supply to ground (the – terminal on the power supply).

Meanwhile, on the AC side of the SSRs, one leg of the AC side is connected directly to the coil, while the other leg connects to one of the lines coming from the breaker. The other line goes directly from the breaker to the coil. This circuit allows current to pass through the SSR only when the GPIO is supplying voltage to the transistor, and therefore the power supply is in turn supplying voltage to the SSR.

**Thermocouple Circuit**

The thermocouples have two sides, a thermocouple side which connects the board to the thermocouple, and a Pi side which connects the board to the Pi. The thermocouple side is straightforward, the positive wire of the thermocouple connects to the positive screw terminal, and the negative side to the negative screw terminal. These should of course be marked on the board and the thermocouple, but when in doubt check the data sheets to make sure which is which. If connected backwards, the thermocouple will read a reduction in temperature rather than an increase.

If your MAX31855 does not already have a capacitor soldered to the leads of the screw terminals under the board, it is highly recommended to solder a capacitor between them, we used 10 picoFarads but anything less than 0.1 microFarad should work.
For the Pi side of things, between the boards the Vin, Gnd, Do, and CLK pins were all tied to the same pins on the other boards (not to each other of course). To clarify, the Vin on one board was connected to the Vin on the other two, then the same was done between the Gnds, and so on.

For connections to the Pi, the 3.3V pin from the Pi was connected to the Vin of one board (and therefore all the boards since they’re connected together). The same was done for the GND pin on the Pi to the GND on the board, the MOSI pin on the pi to the DO pin on the board, and the CLK pin on the Pi to the CLK pin on the board. To find the relevant pins on your raspberry pi, refer to a pinout diagram of your Raspberry Pi and see directions for setting up the circuit with Python https://learn.adafruit.com/thermocouple/python-circuitpython#python-computer-wiring-4-3 .

For the CS pin, the boards should not be connected together. Instead, one CS pin should be connected to GPIO 4 on the Pi, one to GPIO 25, and one to GPIO 12. Once again, refer to a pinout diagram to find where the relevant GPIO pins are, as they are scattered seemingly randomly across the pins.

Finally, place a capacitor, 100nf works, across the 3.3V and GND connections to the first board. This will help reduce the effect noise has on your system, much like the capacitors across the screw terminal leads.

Here's the wiring diagram:
  
  ## SSR Circuit Diagram
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/relayCircut.PNG)
  
  ## Thermocouple Circuit Diagram
  ![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/themoCircut.PNG)

# Building Process

There were several considerations that needed to be taken into account when constructing this project. The first main chalenge was how to instal the thermocouples. Previously they were placed inside of the portholes that already existed on the kiln, and were removed temporaraly whenever we needed to look inside of the kiln. However, with the PID controling the kiln removing the thermocouples was no longer an option as this sudden change in measured temperature would throw off the controler driving the power way up inside the kiln (when in fact is does not need to). To allow for port holes to still be accessible so that we could look inside the kiln, we needed to drill additional holes for the thermocouples. However while drilling these new holes we had to take into account that we were drilling fire brick, so we needed to take special consideration. Fire brick is especially soft and brittle, and we needed to be very gental while drilling the holes in order to avoid breaking the bricks. To make things more difficult the kiln is also wraped in a steel sheet metal, which is not easy to drill through gently. We decided that the best way to go about driling these holes would be to first drill the sheet metal by starting with a small bit and slowly incrementing up in bit size to the final hole size. By slowly going up in bit size we minimized the shock we put into the firebrick each time we punched throught the fire brick. Then we drilled from the inside of the kiln out throught the fire brick. We decided to drill out this way because the sheet metal will support the backside of the brick and help prevent any blowout while drilling. When drilling the firebrick it would probably be best to use a masonary bit, but we had no issues using a standard drill bit due to how stof the material is. Also be sure to **not** use a hammer drill or you will destroy the firebrick. 


Here are the 1/2 inch holes we drilled for the thermocouples:

![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG_20190606_143416.jpg)

# Code

Before using the raspberry pi with the thermocouple boards, the MAX31855 library must be installed. The following site has all the necessary information for doing so: https://learn.adafruit.com/thermocouple/python-circuitpython#python-installation-of-max31855-library-4-6 This even gives sample code for reading from the thermocouple boards if you are interested in writing your own program.

# Designing a PID



## Getting Coefficients

The first constants we aquired were the coeficents for power loss out of each of the zones. We mesuered these by going through each zone and seting one of the zones to full power then measureing the temperatures at equilibrium. By assumung the power loss scales linealy with the diffence to external temperature this gave us a system of three equations with three unknowns allowing us to solve for dissipation coeficents which had a value of about 2 to 0.5. The next chalenge was to find the coeficents of the PID itself. We decided to set the value of P for each zone by deciding what the minimum value for the error we wanted the coils to be on at full power. We decide this value to be 10 degrees, mean that if the kiln was more than 10 degrees below the set point it would apply full power to the coils. P = (maxPower)/(minError) ~ 100 to 200. We decided that we wanted the values of I to be on the same order of magnitude as the disipative constants because the have a similar effect while still being proporional to the power that the coils can deliver. So we just scaled down our value of P down by 100 to get I. For the D coefitient we wanted it to still be porpotional to the max power of the coils and because sticking to a specific ramp rate is crutial to us we decided keep it relitivly large compared to I. This lead us to decide D = P/10. However during later tests we noticed some oscilations that we thought were form the derivitve term so we decresed this to P/20.


While trying to create the best PID for our system, we tried 3 different methods, each with different results. A slight inconvenience to our system was that the 3rd zone on the kiln (the one lowest to the ground) was significantly slower at ramping its power than the above 2 zones. The last 2 PID's take this into account in different ways.

## Aggressive PID

The first PID we tried was to have each zone independently attempt to reach the desired temperature as fast as possible. Essentially each zone used its own thermocouple to measure how fast it should try and reach the target temperature. However, as stated above, the 3rd zone was significantly slower to ramp than the other two, leading to a fairly large temperature gradient across the kiln. When making ceramics, this can lead to issues them not being properly fired, leading to possible cracks or not being fully heated. We called this method the "Aggressive PID" since it just ramps as fast as it can in each zone to the desired temperature. Below is a graph of one such firing:

![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/test2_5_31.png)

Oscillations in the PID are very small, since the time scale is very large (it take many hours to heat a kiln to desired temperature) but also when a zone's coil turns off, it dissipates a lot of heat to the environment (temperature difference between the kiln and outside is very large). So there is very little overshoot after reaching the desired temperature, and hence the amplitude of oscillations are very small (as seen in the graph above). However, to try and address the large temperature gradient, we needed to attempt a new PID system.

## Couple to Slowest

Our next iteration of the PID had each zone "couple" to the slowest zone (zone 3), while zone 3 ramped as fast as possible to the desired temperature. This meant that zones 1 and 2 set their desired temperature to the current temperature of zone 3. The main issue we observed with this version however was that at high temperatures, the actual temperature seemed to "droop" below the desired temperature, as seen below:

![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/figure_1.png)

Our theory for this was that the bottom zone on its own could not ramp up to our desired temperatures (above 1000 C). It requires the top two zones to provide enough power/heat to drive the bottom zone to our desired temp. Since the upper 2 zones are always coupled to the bottom zone, then they can only move as fast as the bottom zone ramps. This lead to us designing a hybrid between the "Aggressive PID" and "Couple to Slowest PID".

## Decoupling at Low Rate of Change

Our last iteration (and solution to the "drooping" issue) was to have the upper 2 zones initially couple to the slowest zone. However, once the last zone's rate of change dropped below one degree per minute, we had the upper two zones "decouple", meaning they would essentially just ramp their power to acheive the desired temperature as fast as possible. This is seen in the graph below:

![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/figure_2.png)

The main issue with this version of the PID was that the upper 2 zones were roughly 20 degrees ahead of the bottom zone. However, compared to the over 100 degree difference between zones 1 and 3 of the "aggressive PID", and the ability to ramp past 1000 C unlike the "Couple to Slowest PID", our last iteration did remarkably well, and it is the version we currently implement. 

In addition to the PID we also implemented "firing schedules", which give an array of desired temperatures the PID should set as its goal for a given time. These live in the form of a text file that the PID calls upon to reference. These firing schedules allow us to tailor our PID to the specific type of firing we desire, such as a bisque or glaze firing (which have different desired final temperatures). The code for the bisque and glaze firing schedules, as well as each PID are within the repository. 

Another issue we encountered at high temperatures was the thermocouples shorting to ground the vast majority of measurements, although any measurements that did go through were perfectly fine. We believe this is because at high temperatures the voltage detected by the thermo board is small and therefore heavily affected by noise. In the future, we would use either shorter or shielded/twisted thermocouple wires and keep the wires away from the rest of the electronics to try to minimize this noise.

# Finished Product

Overall this project was extremely successful. Not only does it fire ceramics on its own with minimal user interaction (after itializing it) but also it is significantly cheaper than most electric temperature controlling kilns. Below are examples of many ceramics that have all been fired in the modified kiln:

![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/20190607_231628.jpg)

## Cookies!

As a last test, we decided to bake cookies in our kiln, just to see if it was feasible. It worked! We set the temperature to 190 C and placed them in for 7 minutes or so (the primary measurement was looking inside and seeing if the cookies looked ready). Here are some pictures of the cookies we baked inside (and for the record, they were delicious).

![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG955889.jpg)
![alt text](https://github.com/KilnStuff/Kiln-Project/blob/master/IMG955899.jpg)


# Contributors

This project was made for Phys CS 15C lab class at UCSB with the aid of Trevor Anderberg, Ohr Benshlomo, and Brian Kent.
