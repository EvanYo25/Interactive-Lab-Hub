from __future__ import print_function
import os
import qwiic_joystick
import time
import sys
import paho.mqtt.client as mqtt
import uuid

import board
import busio
import adafruit_mpr121

import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from time import strftime, sleep
import webcolors, os
from adafruit_rgb_display.rgb import color565
import json

# MiniPiTFT setup star

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)


# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding

# Move left to right keeping track of the current x position for drawing shapes.
# x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

# MiniPiTFT Setup done

# server setup
topic_root = "IDD/EvanEthan/"
count = {"rpt": 0, "qqq": 0, "aha": 0}

def on_connect(client, userdata, flags, rc):
	# print(f"connected with result code {rc}")
	# subscribe to all subtopics under EvanEthan
	client.subscribe(topic_root + "RPT")
	client.subscribe(topic_root + "QQQ")
	client.subscribe(topic_root + "AHA")

def on_message(client, userdata, msg):
	# print(f"topic: {msg.topic} msg: {msg.payload.decode('UTF-8')}")
	
	if msg.topic == topic_root + "RPT":
		count["rpt"] = int(msg.payload.decode('UTF-8'))
	elif msg.topic == topic_root + "QQQ":
		count["qqq"] = int(msg.payload.decode('UTF-8'))
	elif msg.topic == topic_root + "AHA":
		count["aha"] = int(msg.payload.decode('UTF-8'))

def speak(m):
	os.system("./google_say.sh '{}'".format(m))

def main():
	# mqtt setup
	client = mqtt.Client(str(uuid.uuid1()))         
	client.tls_set()                                
	client.username_pw_set('idd', 'device@theFarm') 
	client.on_connect = on_connect
	client.on_message = on_message
	client.connect('farlab.infosci.cornell.edu', port=8883) 

	# joy stick setup
	myJoystick = qwiic_joystick.QwiicJoystick()
	if myJoystick.connected == False:
		print("The Joystick isn't connected to the system.", file=sys.stderr)
		return
	myJoystick.begin()
	print("Joystick initialized. Firmware Version: %s" % myJoystick.version)

	# necessary initialization steps
	print("\n ===> Teacher needs to initialize value with joystick by pressing the joystick")
	while myJoystick.button:
		client.publish(topic_root + "RPT", 0)
		client.publish(topic_root + "QQQ", 0)
		client.publish(topic_root + "AHA", 0)
	print("Initialization done.")
	print("Loop start:")

	init_flag = False
	client.loop_start()

	# main loop
	while True:

		# Draw a black filled box to clear the image.
		draw.rectangle((0, 0, width, height), outline=0, fill=0)

		# fix position
		x, y = 0, 0

		# update states
		# clock.change_mode(not buttonA.value, not buttonB.value)

		msg = "Press joystick to initialize."
		rpt = " Repeat: {}".format(count["rpt"])
		qqq = " ????  : {}".format(count["qqq"])
		aha = " AHA!! : {}".format(count["aha"])

		draw.text((x, y), msg, font=font, fill="#FFFF00")
		y += font.getsize(msg)[1]

		draw.text((x, y), rpt, font=font, fill="#FFFF00")
		y += font.getsize(rpt)[1]

		draw.text((x, y), qqq, font=font, fill="#FFFF00")
		y += font.getsize(qqq)[1]

		draw.text((x, y), aha, font=font, fill="#FFFF00")
		y += font.getsize(aha)[1]

		# Display image.
		disp.image(image, rotation)

		limit = 2
		if count["rpt"] > limit:
			speak("Please repeat the content")
			count["rpt"] = 0
			client.publish(topic_root + "RPT", 0)

		if count["qqq"] > limit:
			speak("What was that?")
			count["qqq"] = 0
			client.publish(topic_root + "QQQ", 0)

		if count["aha"] > limit:
			speak("Aha I got it")
			count["qqq"] = 0
			client.publish(topic_root + "AHA", 0)
		
		if not myJoystick.button:
			client.publish(topic_root + "RPT", 0)
			client.publish(topic_root + "QQQ", 0)
			client.publish(topic_root + "AHA", 0)

		print(count)
		time.sleep(0.25)


if __name__ == '__main__':
	try:
		main()
	except (KeyboardInterrupt, SystemExit) as exErr:
		print("\nEnding Teacher side client")
		sys.exit(0)