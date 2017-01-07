from Adafruit_LED_Backpack import SevenSegment

display = SevenSegment.SevenSegment()

for x in range(0, 9999):
	display.clear()
	display.write_display()
	display.print_number_str(str(x))
	display.write_display()
