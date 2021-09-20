from datetime import datetime
import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

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
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
font2 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True
buttonA = digitalio.DigitalInOut(board.D23)
buttonA.switch_to_input()


stage = False

while True:
    if not buttonA.value:
        stage = False if stage is True else True

    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=0)

    now = datetime.now()
    now_str = now.strftime("%m/%d/%Y %H:%M:%S")

    depart_time = datetime(2020, 8, 24, 5, 35, 0)
    depart_time_str = depart_time.strftime("%m/%d/%Y %H:%M:%S")

    interval = now - depart_time
    #print(interval.days)
    #print(int(interval.seconds/3600))
    #print(int(interval.seconds/60%60))
    #print(interval.seconds%60)

    if stage:
        line1 = now_str
        line2 = "Departed Time:"
        line3 = depart_time_str
        line4 = "It's been " + str(int(interval.days/365)) + " year"
        line5 = str(interval.days%365) + " days " + str(int(interval.seconds/3600)) + " hours"
        line6 = str(int(interval.seconds/60%60)) + " minutes " + str(interval.seconds%60) + " seconds"
        line7 = "since you left Taiwan"
    else:
        line1 = "I normally finish...."
        line2 = "a cup of coffee in a hour"
        line3 = "a can of beer in 3 minutes"
        line4 = ""
        line5 = ""
        line6 = ""
        #line5 = "with " + str(int(int(now.strftime("%M"))/5)) + " cans of beer"
        for i in range(min(6, int(now.strftime("%H"))%12)):
            line4 = line4 + "☕"
        for i in range(min(6, int(now.strftime("%H"))%12-6)):
            line5 = line5 + "☕"
        for i in range(int(int(now.strftime("%M"))/3)):
            line6 = line6 + "🍺"

    #TODO: Lab 2 part D work should be filled in here. You should be able to look in cli_clock.py and stats.py
    y = top
    draw.text((x, y), line1, font=font, fill="#FFFFFF")
    y += font.getsize(line1)[1]
    draw.text((x, y), line2, font=font, fill="#FF0000")
    y += font.getsize(line2)[1]
    draw.text((x, y), line3, font=font, fill="#FF0000")
    y += font.getsize(line3)[1]
    if stage:
        draw.text((x, y), line4, font=font, fill="#0000FF")
        y += font.getsize(line4)[1]
        draw.text((x, y), line5, font=font, fill="#0000FF")
        y += font.getsize(line5)[1]
        draw.text((x, y), line6, font=font, fill="#0000FF")
        y += font.getsize(line6)[1]
        draw.text((x, y), line7, font=font, fill="#0000FF")
        y += font.getsize(line7)[1]
    else:
        draw.text((x, y), line4, font=font2, fill="#FFFFFF")
        y += font2.getsize(line4)[1]
        draw.text((x, y), line5, font=font2, fill="#FFFFFF")
        y += font2.getsize(line5)[1]
        draw.text((x, y), line6, font=font, fill="#FFFFFF")
        y += font.getsize(line6)[1]

    #draw.text((x, y), line8, font=font, fill="#FFFFFF")

    # Display image.
    disp.image(image, rotation)
    time.sleep(1)
