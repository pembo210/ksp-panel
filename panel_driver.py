""" This program drives the outputs for a mission control panel for the space simulation
game Kerbal Space Program (KSP). The outputs consist of indicator LEDs, a 10 segment bargraph
LED, a 16x2 LCD display, an I2C quad seven segment display, and an MCP23017 port
expander chip. The foundation of the program comes from display_tools, a library I wrote
(with the exception of the LCD class, which I modified from existing code by Matt at 
raspberrypi-spy.co.uk), and the Adafruit library for driving the I2C quad seven segment.
The program uses the Telemachus mod for KSP, which creates a webserver from the machine running
the game that can return information from the current flight. I also wrote a patch for the game
that enables telemachus datalinks from all control pods in the game. """

from __future__ import division
from urllib2 import urlopen
from Adafruit_LED_Backpack import SevenSegment
import time
import json
import os
import display_tools
import smbus
import RPi.GPIO as GPIO

bus = smbus.SMBus(1)  
device = 0x20 # I2C port expander address
GPA = 0x14 # GPA output register

GPIO.setmode(GPIO.BCM)

# Instantiate I2C seven segment from Adafruit library
altimeter = SevenSegment.SevenSegment()
altimeter.begin()

# Instantiate display classes from display_tools library
lcd_display = display_tools.LCD_16x2(18, 23, 24, 25, 12, 16)
fuelLevel = display_tools.bargraph_LED(4, 17, 27, 22, 5, 6, 13, 19, 26, 21)

# Setting GPA pins to outputs
bus.write_byte_data(device, 0x00, 0x00)

def getPercent(max, current):
	# Take current value and max value and calculate percentage
	if max != 0: # If max == 0, we divide by zero and end the universe
		percent = current/max
		percent *= 100
		percent = int(percent)
	else:
		percent = 0	

	return percent

def formatAlt(alt):
	# Take long number in meters and convert to km, Mm, Gm where appropriate
	alt = int(alt)

	if alt < 1000:
		output = '%d m' % alt

	if alt >= 1000 and alt < 1000000:
		alt *= (10 ** -3) # Move decimal place to give how many km
		round(alt, 1) # Remove digits after first decimal place
		output = '%.1f km' % alt # Format as string

	if alt >= 1000000 and alt < 1000000000:
		alt *= (10 ** -6) 
		round(alt, 1)
		output = '%.1f Mm' % alt

	if alt >= 1000000000:
		alt *= (10 ** -9)
		round(alt, 1)
		output = '%.1f Gm' % alt

	return output

# The API call string that returns flight info
query = (
	"http://192.168.1.185:8085/telemachus/datalink?Antenna=p.paused&RCS=v.rcsValue&"
	"SAS=v.sasValue&lights=v.lightValue&brakes=v.brakeValue&gear=v.gearValue&pe=o.PeA"
	"&ap=o.ApA&terrainHeight=v.heightFromTerrain&ASL=v.altitude&maxElec=r.resourceMax["
	"ElectricCharge]&currElec=r.resource[ElectricCharge]&stCurrLiq=r.resourceCurrent["
	"LiquidFuel]&stMaxLiq=r.resourceCurrentMax[LiquidFuel]"
	)

# Main program loop
while 1:
	try:
		response = urlopen(query).read().decode('utf-8') # Calling the API
		telemetry = json.loads(response) # Loading response data into dictionary
				
		# Convert variable types for readability and compatibility with output devices
		telemetry['ap'] = int(telemetry['ap']) # Apoapsis
		telemetry['pe'] = int(telemetry['pe']) # Periapsis
		telemetry['terrainHeight'] = str(int(telemetry['terrainHeight'])) # Height from terrain
		telemetry['ASL'] = int(telemetry['ASL']) # Altitude above sea level
		telemetry['currElec'] = int(telemetry['currElec']) # Amount of electric charge
		telemetry['maxElec'] = int(telemetry['maxElec']) # Maximum electric charge capacity
		telemetry['stCurrLiq'] = int(telemetry['stCurrLiq']) # Amount of liquid fuel on stage
		telemetry['stMaxLiq'] = int(telemetry['stMaxLiq']) # Maximum fuel capacity on stage
		
		# Set periapsis to 0 if below 0 for realism
		if telemetry['pe'] < 0: 
			telemetry['pe'] = 0
		
		# Get the percentage of liquid fuel and electricity
		telemetry['percElec'] = getPercent(telemetry['maxElec'], telemetry['currElec'])
		telemetry['stPercLiq'] = getPercent(telemetry['stMaxLiq'], telemetry['stCurrLiq'])
		
		
		# Send info to peripherals
		if telemetry['Antenna'] == 1:
			lcd_display.dispMessage('Game paused', lcd_display.LINE1)
			lcd_display.dispMessage('', lcd_display.LINE2)
			# Display appropriate message if game is paused			

		if telemetry['Antenna'] > 1:
			lcd_display.dispMessage('Flight telemetry', lcd_display.LINE1)
			lcd_display.dispMessage('lost', lcd_display.LINE2)
			# Display appropriate message if antenna is not returning telemetry
		
		if telemetry['Antenna'] == 0:
			# Display apoapsis and periapsis on LCD
			apMessage = 'AP: ' + str(formatAlt(telemetry['ap']))
			peMessage = 'PE: ' + str(formatAlt(telemetry['pe']))
			lcd_display.dispMessage(apMessage, lcd_display.LINE1)
			lcd_display.dispMessage(peMessage, lcd_display.LINE2)			

			# Display radar altitude on seven segment if alt is 4 digits or less
			# Digit length detection is built into Adafruit library
			altimeter.clear()
			altimeter.print_number_str(telemetry['terrainHeight'])
			altimeter.write_display()

			# Display percent of liquid fuel on bargraph LED
			fuelLevel.display(telemetry['stPercLiq'])

			# Convert telemetry values of True/False to 1 or 0 to send to MCP23017
			# port expander chip
			SasLED = int(telemetry['SAS'] == True)
			RcsLED = int(telemetry['RCS'] == True)
			LightLED = int(telemetry['lights'] == True)
			GearLED = int(telemetry['gear'] == True)
			BrakeLED = int(telemetry['brakes'] == True)
			
			# If the percentage of liquid fuel or electricity is below 10, set 
			# warning LED to 1
			if telemetry['percElec'] <= 10:
				ElecWarnLED = 1
			else:
				ElecWarnLED = 0

			if telemetry['stPercLiq'] <= 10:
				FuelWarnLED = 1
			else:
				FuelWarnLED = 0
			
			# Print values and states to command line
			os.system('clear')

			print('Resource Levels:\n')
			print('Electric charge: %r%%' % telemetry['percElec'])
			print('Stage liquid fuel: %r%%' % telemetry['stPercLiq'])
			print('\n')
			
			print('Ship Systems:\n')
			print('SAS:', telemetry['SAS'])
			print('RCS:', telemetry['RCS'])
			print('Lights:', telemetry['lights'])
			print('Gear:', telemetry['gear'])
			print('Brakes:', telemetry['brakes'])
			print('\n')
		
			print('Orbit Information:\n')
			print('Apoapsis:', telemetry['ap'], 'm')
			print('Periapsis:', telemetry['pe'], 'm')
			print('Height from terrain:', telemetry['terrainHeight'], 'm')
			print('Sea level altitude:', telemetry['ASL'], 'm')
			
			# Take all LED state values and concatenate into one binary number to send to chip
			I2C_DATA = (FuelWarnLED << 6) + (ElecWarnLED << 5) + (SasLED << 4) + (RcsLED << 3) + (GearLED << 2) + (LightLED << 1) + BrakeLED
			# Send binary data to the first 8 chip pins (GPA register)
			bus.write_byte_data(device, GPA, I2C_DATA)

		time.sleep(.2)

	except KeyError:
		# The game produces NaN values during scene changes, this prevents panel 
		# from halting during transitions
		pass
