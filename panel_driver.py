import time
import json
import urllib.request as request
import os
import display_tools
import smbus
import RPi.GPIO as GPIO

bus = smbus.SMBus(1)  
device = 0x20 # I2C device address
GPA = 0x14 # GPA output register

GPIO.setmode(GPIO.BCM)
lcd_display = display_tools.LCD_16x2(18, 23, 24, 25, 12, 16)
fuelLevel = display_tools.bargraph_LED(4, 17, 27, 22, 5, 6, 13, 19, 26, 21)

# Setting GPA pins to outputs
bus.write_byte_data(device, 0x00, 0x00)

def getPercent(max, current):
	percent = current/max
	percent *= 100
	percent = int(percent)
	
	if current == -1 or current == 0:
		percent = 0
		
	return percent

def formatAlt(alt):
	alt = int(alt)

	if alt < 1000:
		output = '%d m' % alt

	if alt >= 1000 and alt < 1000000:
		alt *= (10 ** -3)
		round(alt, 1)
		output = '%.1f km' % alt

	if alt >= 1000000 and alt < 1000000000:
		alt *= (10 ** -6) 
		round(alt, 1)
		output = '%.1f Mm' % alt

	if alt >= 1000000000:
		alt *= (10 ** -9)
		round(alt, 1)
		output = '%.1f Gm' % alt

	return output

query = (
	"http://192.168.1.185:8085/telemachus/datalink?Antenna=p.paused&RCS=v.rcsValue&"
	"SAS=v.sasValue&lights=v.lightValue&brakes=v.brakeValue&gear=v.gearValue&pe=o.PeA"
	"&ap=o.ApA&terrainHeight=v.heightFromTerrain&ASL=v.altitude&maxElec=r.resourceMax["
	"ElectricCharge]&currElec=r.resource[ElectricCharge]&stCurrLiq=r.resourceCurrent["
	"LiquidFuel]&stMaxLiq=r.resourceCurrentMax[LiquidFuel]"
	)

while 1:
	try:
		response = request.urlopen(query).read().decode('utf-8')
		telemetry = json.loads(response)
				
		#This turns floats into ints for readability and other number operations
		telemetry['ap'] = int(telemetry['ap'])
		telemetry['pe'] = int(telemetry['pe'])
		telemetry['terrainHeight'] = int(telemetry['terrainHeight'])
		telemetry['ASL'] = int(telemetry['ASL'])
		telemetry['currElec'] = int(telemetry['currElec'])
		telemetry['maxElec'] = int(telemetry['maxElec'])
		telemetry['stCurrLiq'] = int(telemetry['stCurrLiq'])
		telemetry['stMaxLiq'] = int(telemetry['stMaxLiq'])
		
		if telemetry['pe'] < 0:
			telemetry['pe'] = 0
		
		telemetry['percElec'] = getPercent(telemetry['maxElec'], telemetry['currElec'])
		telemetry['stPercLiq'] = getPercent(telemetry['stMaxLiq'], telemetry['stCurrLiq'])

		#This prints all the readouts to the terminal window
		
		os.system('clear')

		if telemetry['Antenna'] == 1:
			lcd_display.dispMessage('Game paused', lcd_display.LINE1)
			lcd_display.dispMessage('', lcd_display.LINE2)			

		if telemetry['Antenna'] > 1:
			lcd_display.dispMessage('Flight telemetry', lcd_display.LINE1)
			lcd_display.dispMessage('lost', lcd_display.LINE2)
		
		if telemetry['Antenna'] == 0:
			apMessage = 'AP: ' + str(formatAlt(telemetry['ap']))
			peMessage = 'PE: ' + str(formatAlt(telemetry['pe']))
			lcd_display.dispMessage(apMessage, lcd_display.LINE1)
			lcd_display.dispMessage(peMessage, lcd_display.LINE2)
			
			fuelLevel.display(telemetry['stPercLiq'])

			SasLED = int(telemetry['SAS'] == True)
			RcsLED = int(telemetry['RCS'] == True)
			LightLED = int(telemetry['lights'] == True)
			GearLED = int(telemetry['gear'] == True)
			BrakeLED = int(telemetry['brakes'] == True)
			
			if telemetry['percElec'] <= 10:
				ElecWarnLED = 1
			else:
				ElecWarnLED = 0

			if telemetry['stPercLiq'] <= 10:
				FuelWarnLED = 1
			else:
				FuelWarnLED = 0

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
			
			I2C_DATA = (FuelWarnLED << 6) + (ElecWarnLED << 5) + (SasLED << 4) + (RcsLED << 3) + (GearLED << 2) + (LightLED << 1) + BrakeLED
			bus.write_byte_data(device, GPA, I2C_DATA)

		time.sleep(.2)
		
	except KeyError:
		# So program doesn't hang on NaN values
		pass

	except ZeroDivisionError:
		# If fuel level is zero it will throw this
		pass
	
	except ValueError:
		# So it doesn't hang on NaN values
		pass
