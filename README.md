# Kerbal Space Program Mission Control Panel
This repository contains the code necessary to drive a mission control panel
for the space simulation game Kerbal Space Program. The panel consists of a
Raspberry Pi and a Teensy.

## Raspberry Pi
The Raspberry Pi handles the outputs of the panel. The outputs consist of an
LCD display for displaying orbital information, a 10 segment bargraph LED for
displaying fuel level, an I2C LED seven segment for displaying altitude, and
several LED indicator lights for displaying flight system status. The output
is based on two libraries. The I2C seven segment display is driven by a [library
written by Adafruit](https://github.com/adafruit/Adafruit_Python_LED_Backpack). All other outputs are driven by display_tools, a library
I wrote that provides classes for several types of peripherals. The LCD class
in display_tools was modified from a [script](https://www.raspberrypi-spy.co.uk/2012/07/16x2-lcd-module-control-using-python/) by Matt at raspberrypi-spy.co.uk.
The data to send to the peripherals is retrieved by using the Telemachus mod
for KSP, which creates a webserver from the machine running the game that
accepts API calls and returns flight data.

## Teensy
The Teensy controls the inputs. The inputs of the panel are lighted pushbuttons,
a sliding potentiometer, and toggle switches. The Teensy plugs into the machine
running the game and acts as a USB controller to send commands to the game.
