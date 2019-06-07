# Kiln-Project

  In this guide we will detail our process and design for an electronic temperature controlled kiln. The goal of this project was to convert a manual temperature controlled kiln, which originally set the temperature by means of a knob, to a much more sophisticated electronic control system that could drive the kiln to a specific temperature based on thermocouple feedback. This project required us to wire and build the system from scratch, with the only previously constructed components being the kiln itself and our means to electronically communicate with the kiln, a raspberry pi (as well as peripherals for the pi).
  
  
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
  *
  *
  *
  
  ## DC/Pi Components
  * Adafruit Perma-Proto
  *
  *



# Design

  Since the actual coils inside the kiln are powered by AC current from the wall, but the pi is powered/communicates through DC the way we chose to limit the power reaching the kiln was through solid state relays. These relays are connected to the wall at 240 V and on the other side to the pi at 5V. These relays are "always open", so AC will only pass through if the pi is applying a DC current. They are also "zero crossing", so they will only start/stop transmitting AC when its phase corresponds to when the wall voltage is at 0. This allows for a type of PWM (Pulse Width Modulation) for the kiln, where we can control the amount of power entering within a given time frame by limiting the amount of time the coils are on within a period. Below is the schematic for the AC current side:

# Building Process



# Designing a PID



# Finished Product and Data



# Contributors
