# This module contains several classes to drive various displays, such as LCDs, LEDs,
# seven-segment displays, and more.

# Make sure to set GPIO mode BEFORE instantiating classes in this module, as it contains
# no GPIO setmode commands.

# Huge thanks to Matt at raspberrypi-spy.co.uk for providing code that is modified for
# use in the LCD class.

import RPi.GPIO as GPIO
import time

# LCD Class:
# Simply instantiate class with BCM pin numbers of each pin specified in arguments.
# Then call self.dispMessage("Message", self.LINEx), where x is the line you want the
# message to display on.
class LCD_16x2():

	def __init__(self, RS, E, D4, D5, D6, D7):
		# Defining constants and setting up pins
		self.LCD_RS = RS
		self.LCD_E  = E
		self.LCD_D4 = D4
		self.LCD_D5 = D5
		self.LCD_D6 = D6
		self.LCD_D7 = D7
		
		self.LCD_WIDTH = 16
		self.LCD_CHR = True
		self.LCD_CMD = False

		self.LINE1 = 0x80 # LCD RAM address for the 1st line
		self.LINE2 = 0xC0 # LCD RAM address for the 2nd line

		self.E_PULSE = 0.0005
		self.E_DELAY = 0.0005
  
		GPIO.setwarnings(False)
		GPIO.setup(self.LCD_E, GPIO.OUT)  # E
		GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
		GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
		GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
		GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
		GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7
		
		self.lcd_byte(0x33,self.LCD_CMD) # 110011 Initialise
		self.lcd_byte(0x32,self.LCD_CMD) # 110010 Initialise
		self.lcd_byte(0x06,self.LCD_CMD) # 000110 Cursor move direction
		self.lcd_byte(0x0C,self.LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
		self.lcd_byte(0x28,self.LCD_CMD) # 101000 Data length, number of lines, font size
		self.lcd_byte(0x01,self.LCD_CMD) # 000001 Clear display
		time.sleep(self.E_DELAY)

	def lcd_byte(self, bits, mode):
	# Send byte to data pins
	# bits = data
	# mode = True  for character
	#        False for command

		GPIO.output(self.LCD_RS, mode) # RS

	  # High bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x10==0x10:
			GPIO.output(self.LCD_D4, True)
		if bits&0x20==0x20:
			GPIO.output(self.LCD_D5, True)
		if bits&0x40==0x40:
			GPIO.output(self.LCD_D6, True)
		if bits&0x80==0x80:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		self.lcd_toggle_enable()

		# Low bits
		GPIO.output(self.LCD_D4, False)
		GPIO.output(self.LCD_D5, False)
		GPIO.output(self.LCD_D6, False)
		GPIO.output(self.LCD_D7, False)
		if bits&0x01==0x01:
			GPIO.output(self.LCD_D4, True)
		if bits&0x02==0x02:
			GPIO.output(self.LCD_D5, True)
		if bits&0x04==0x04:
			GPIO.output(self.LCD_D6, True)
		if bits&0x08==0x08:
			GPIO.output(self.LCD_D7, True)

		# Toggle 'Enable' pin
		self.lcd_toggle_enable()

	def lcd_toggle_enable(self):
		# Toggle enable
		time.sleep(self.E_DELAY)
		GPIO.output(self.LCD_E, True)
		time.sleep(self.E_PULSE)
		GPIO.output(self.LCD_E, False)
		time.sleep(self.E_DELAY)

	def dispMessage(self, message, line):
		message = message.ljust(self.LCD_WIDTH," ")

		self.lcd_byte(line, self.LCD_CMD)

		for i in range(self.LCD_WIDTH):
			self.lcd_byte(ord(message[i]),self.LCD_CHR)

	def end(self):
		self.lcd_byte(0x01, self.LCD_CMD)
		GPIO.cleanup()

# LED class:
# Instantiate the class with the pin number of the pin that drives the LED, then call
# self.state(state) where state is a boolean representing desired LED state.
class LED():
	def __init__(self, output):
		GPIO.setwarnings(False)
		self.pin = output
		GPIO.setup(self.pin, GPIO.OUT)

	def state(self, ledState):
	
		if ledState == True:
			GPIO.output(self.pin, GPIO.HIGH)		
		elif ledState == False:
			GPIO.output(self.pin, GPIO.LOW)

# Common cathode seven segment class:
# Instantiate class with pin numbers for each letter of the display in alphabetical order.
# To display a number, call self.dispNum(x) where x is the number to be displayed. Call
# self.clear() to clear the display.
class CC_Seven_Segment():
	def __init__(self, a, b, c, d, e, f, g):
		GPIO.setwarnings(False)
		GPIO.setup(a, GPIO.OUT)
		GPIO.setup(b, GPIO.OUT)
		GPIO.setup(c, GPIO.OUT)
		GPIO.setup(d, GPIO.OUT)
		GPIO.setup(e, GPIO.OUT)
		GPIO.setup(f, GPIO.OUT)
		GPIO.setup(g, GPIO.OUT)
		
		self.numbers = {
			0: [a, b, c, d, e, f],
			1: [b, c],
			2: [a, b, d, e, g],
			3: [a, b, c, d, g],
			4: [b, c, f, g],
			5: [a, c, d, f, g],
			6: [a, c, d, e, f, g],
			7: [a, b, c],
			8: [a, b, c, d, e, f, g],
			9: [a, b, c, f, g]
			}

	def dispNum(self, num):
		number = int(num)
		outputs = self.numbers[number]

		for x in outputs:
			GPIO.output(x, GPIO.HIGH)

	def clear(self):
		allSegs = self.numbers[8]

		for y in allSegs:
			GPIO.output(y, GPIO.LOW)

# 10 segment bargraph LED class:
# Instantiate the class with the ten pins, in ascending order, of each segment. Call
# self.display(x), where x is the percentage to be shown to light the display. The
# function automatically rounds the percentage so any integer or float value can be
# passed to it.
class bargraph_LED():
	def __init__(self, one_, two_, three_, four_, five_, six_, seven_, eight_, nine_, ten_):
		self.one = one_
		self.two = two_
		self.three = three_
		self.four = four_
		self.five = five_
		self.six = six_
		self.seven = seven_
		self.eight = eight_
		self.nine = nine_
		self.ten = ten_

		GPIO.setwarnings(False)
		GPIO.setup(one_, GPIO.OUT)
		GPIO.setup(two_, GPIO.OUT)
		GPIO.setup(three_, GPIO.OUT)
		GPIO.setup(four_, GPIO.OUT)
		GPIO.setup(five_, GPIO.OUT)
		GPIO.setup(six_, GPIO.OUT)
		GPIO.setup(seven_, GPIO.OUT)
		GPIO.setup(eight_, GPIO.OUT)
		GPIO.setup(nine_, GPIO.OUT)
		GPIO.setup(ten_, GPIO.OUT)

	def display(self, percent):
		percent = round(percent, -1)
		
		if percent > 0:
			GPIO.output(self.one, GPIO.HIGH)
		else:
			GPIO.output(self.one, GPIO.LOW)

		if percent > 10:
			GPIO.output(self.two, GPIO.HIGH)
		else:
			GPIO.output(self.two, GPIO.LOW)

		if percent  > 20:
			GPIO.output(self.three, GPIO.HIGH)
		else:
			GPIO.output(self.three, GPIO.LOW)

		if percent > 30:
			GPIO.output(self.four, GPIO.HIGH)
		else:
			GPIO.output(self.four, GPIO.LOW)

		if percent > 40:
			GPIO.output(self.five, GPIO.HIGH)
		else:
			GPIO.output(self.five, GPIO.LOW)

		if percent > 50:
			GPIO.output(self.six, GPIO.HIGH)
		else:
			GPIO.output(self.six, GPIO.LOW)

		if percent > 60:
			GPIO.output(self.seven, GPIO.HIGH)
		else:
			GPIO.output(self.seven, GPIO.LOW)

		if percent > 70:
			GPIO.output(self.eight, GPIO.HIGH)
		else:
			GPIO.output(self.eight, GPIO.LOW)

		if percent > 80:
			GPIO.output(self.nine, GPIO.HIGH)
		else:
			GPIO.output(self.nine, GPIO.LOW)

		if percent > 90:
			GPIO.output(self.ten, GPIO.HIGH)
		else:
			GPIO.output(self.ten, GPIO.LOW)
