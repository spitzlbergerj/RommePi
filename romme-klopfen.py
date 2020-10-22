#!/usr/bin/python3
# coding=utf-8
# romme-klopfen.py
#
# Liest die GPIO Ports an denen Taster hängen, zeigt ersten Taster per LED an, Reset-Knopf aktiviert neue Runde
#-------------------------------------------------------------------------------

from subprocess import call
from datetime import datetime
import time

# import for GPIO Input tactile switches
import RPi.GPIO as GPIO

# -----------------------------------------------
# library from Adafruit
# -----------------------------------------------
import board
import busio
import digitalio
from adafruit_mcp230xx.mcp23017 import MCP23017

# -------------------------
# GPIO Pins
# -------------------------
tasterList = [27, 22, 5, 6, 13, 26, 16, 17]
LEDNrList = [4, 5, 6, 7, 1, 0, 2, 3]
resetButton = 4
statusLEDredNr = 10
statusLEDgreenNr = 9
statusLEDblueNr = 8

# -------------------------
# Stati
# -------------------------

# staus ist entweder "BuzzerPressed" oder "BuzzerWait"
# zur Vereinfachung: Buzzerpressed = True, BuzzerWait = False
status = False

justReset = False
justBuzzer = False

interruptPin = 0

# -------------------------
# automatisches Rücksetzen nach Buzzer Drücken
# -------------------------
buzzerPressedTime = None
waitMinSeconds = 3

# -------------------------
# Reset Taster lange drücken = Shutdown
# -------------------------
buttonPressedTime = None
shutdownMinSeconds = 3

# -------------------------
# Funktionen
# -------------------------

def statusLED(mode):
	global statusLEDgreen, statusLEDred, statusLEDblue
	statusLEDred.value = False
	statusLEDgreen.value = False
	statusLEDblue.value = False

	if mode == "red":
		statusLEDred.value = True
	elif mode == "green":
		statusLEDgreen.value = True
	elif mode == "blue":
		statusLEDblue.value = True


def LEDeinaus(BuzzerNr):
	# -------------------------
	# LED für bestimmten Buzzer einschalten
	# falls BuzzerNr == 99, dann alle LED ein
	# falls BuzzerNr == 0, dann alle LED aus
	# -------------------------
	
	global tasterList, LEDList

	# LED für Taster BuzzerNr ein
	for tasti in range(8):
		if tasterList[tasti] == BuzzerNr or BuzzerNr == 99:
			LEDList[tasti].value = True
		else:
			LEDList[tasti].value = False


def interruptBuzzer(pin):
	# -------------------------
	# alle Events auf alle Buzzer löschen
	# Status setzen auf "BuzzerPressed" (True)
	# -------------------------

	global tasterList, status, interruptPin, justBuzzer, buzzerPressedTime

	print(datetime.now().strftime("%Y%m%d%H%M%S "), "INTERRUPT: Taster gedrückt: ", pin)

	# ein Taster wurde gedrückt, alle Taster deaktivieren bis Reset-Taster gedrückt wird
	for tasti in tasterList:
		GPIO.remove_event_detect(tasti)

	status = True
	justBuzzer = True
	interruptPin = pin

	if buzzerPressedTime is None:
		print("Buzzer zeit merken")
		buzzerPressedTime = datetime.now()



def interruptBuzzerVerarb(pin):
	# -------------------------
	# StatusLED setzen
	# Buzzer LED setzen
	# Interrupt Reset Taster aktivieren
	# -------------------------

	global resetButton, tasterList, justBuzzer

	justBuzzer = False

	# StatusLED auf rot setzen
	statusLED("red")

	# LED des gedrückten Buzzers an
	if pin in tasterList:
		LEDeinaus(pin)
	else:
		# falsche pin Nummer
		statusLED("blue")

	# Reset Taster aktivieren
	GPIO.add_event_detect(resetButton, GPIO.BOTH, callback = interruptReset)


def interruptReset(pin):
	# -------------------------
	# Event auf Reset Taster löschen
	# Status setzen auf "BuzzerWait" (False)
	#
	# Verarbeitung von langem Reset Taster Druck = shutdown
	# -------------------------

	global resetButton, status, justReset
	global buttonPressedTime, buzzerPressedTime

	if not (GPIO.input(pin)):
		# button wurde gedrückt 
		if buttonPressedTime is None:
			print("Reset zeit merken")
			buttonPressedTime = datetime.now()
		
		print(datetime.now().strftime("%Y%m%d%H%M%S "), "INTERRUPT: Reset Taster gedrückt: ", pin)

		# BuzzerPressedTime zurücksetzen, damit Zeitablauf den interrupt nicht erneut aufruft
		buzzerPressedTime = None
	else:
		# button wurde losgelassen

		print(datetime.now().strftime("%Y%m%d%H%M%S "), "INTERRUPT: Reset Taster losgelassen: ", pin)

		# Reset Taster Interrupt entfernen
		GPIO.remove_event_detect(resetButton)

		if buttonPressedTime is not None:
			print("gemerkte Reset zeit vorhanden")
			elapsed = (datetime.now() - buttonPressedTime).total_seconds()
			buttonPressedTime = None
			if elapsed >= shutdownMinSeconds:
				print("ShutDown da Reset Taster länger als Wartezeit gedrückt")
				statusLED("blue")
				# button pressed for more than specified time, shutdown
				# ACHTUNG: python muss als root laufen
				GPIO.cleanup()
				LEDeinaus(0)
				call(['/sbin/shutdown', '-h', 'now'], shell=False)
				statusLED("off")

			else:
				# Reset wurde gedrückt (und losgelassen)
				justReset = True
				status = False
		else:
			# Reset wurde gedrückt (und losgelassen)
			justReset = True
			status = False



def interruptResetVerarb(pin):
	# -------------------------
	# alle LEDs aus
	# Interrupts auf alle Buzzer setzen
	# StatusLED auf grün
	# -------------------------

	global tasterList, justReset

	justReset = False

	LEDeinaus(0)

	#statusLED("blue")

	for tasti in tasterList:
		GPIO.add_event_detect(tasti, GPIO.FALLING, callback = interruptBuzzer)

	statusLED("green")


def main():
	# -------------------------
	# main 
	# -------------------------

	global resetButton
	global LEDNrList, LEDList
	global statusLEDgreenNr, statusLEDredNr, statusLEDblueNr, statusLEDgreen, statusLEDred, statusLEDblue
	global i2c, mymcp1
	global status, justBuzzer, justReset
	global buzzerPressedTime

	# -----------------------------------------------
	# Initialize the I2C bus and the GPIO port expander
	# -----------------------------------------------
	i2c = busio.I2C(board.SCL, board.SDA)
	mymcp1=MCP23017(i2c, address=0x20)

	# -----------------------------------------------
	# Initialize the GPIO ports
	# -----------------------------------------------
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)

	# -------------------------
	# GPIO initialisieren
	# -------------------------

	for tasti in tasterList:
		# print("GPIO setup taster", tasti)
		GPIO.setup(tasti, GPIO.IN)

	LEDList = []

	for ledi in range(8):
		LEDList.append(mymcp1.get_pin(LEDNrList[ledi]))
		LEDList[ledi].direction = digitalio.Direction.OUTPUT

	GPIO.setup(resetButton, GPIO.IN, pull_up_down = GPIO.PUD_UP)

	statusLEDred = mymcp1.get_pin(statusLEDredNr)
	statusLEDred.direction = digitalio.Direction.OUTPUT
	statusLEDgreen = mymcp1.get_pin(statusLEDgreenNr)
	statusLEDgreen.direction = digitalio.Direction.OUTPUT
	statusLEDblue = mymcp1.get_pin(statusLEDblueNr)
	statusLEDblue.direction = digitalio.Direction.OUTPUT

	# -----------------------------
	# LEDs initialisieren
	# -----------------------------
	LEDeinaus(0)
	LEDeinaus(99)
	time.sleep(1)
	LEDeinaus(0)
	statusLED("off")

	# -------------------------
	# Interrupts der anderen Taster setzen
	# -------------------------
	interruptResetVerarb(resetButton)

	# -------------------------
	# Main loop
	# -------------------------

	print("Auf gehts")
	try:
		while True:

			# status ist entweder "BuzzerPressed" oder "BuzzerWait"
			# zur Vereinfachung: Buzzerpressed = True, BuzzerWait = False

			if justBuzzer:
				# Buzzer wurde gedrückt
				interruptBuzzerVerarb(interruptPin)

			if justReset:
				interruptResetVerarb(resetButton)

			if buzzerPressedTime is not None:
				elapsed = (datetime.now() - buzzerPressedTime).total_seconds()
				if elapsed >= waitMinSeconds:
					print("Wartezeit verstrichen - Reset")
					buzzerPressedTime = None
					justReset = True
					status = False
					interruptReset(resetButton)

			time.sleep(.2)
	except KeyboardInterrupt:
		GPIO.cleanup()
	except:
		print("unprocessed Error:", sys.exc_info()[0])
		GPIO.cleanup()

	# -------------------------
	# Cleaning at the end
	# -------------------------
	GPIO.cleanup()

if __name__ == "__main__":
	main()
