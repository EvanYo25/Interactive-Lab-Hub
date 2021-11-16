import paho.mqtt.client as mqtt
import uuid

# capacitive sensor
import time
import board
import busio
import adafruit_mpr121

# screen
import digitalio
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789

# the # wildcard means we subscribe to all subtopics of IDD
topic1 = 'IDD/EvanEthan/RPT'
topic2 = 'IDD/EvanEthan/QQQ'
topic3 = 'IDD/EvanEthan/AHA'

count = [0, 0, 0]

line1 = "Press 0:"
line2 = "Can you repeat that again?"
line3 = "Press 1:"
line4 = "I don't understand"
line5 = "Press 2:"
line6 = "AHA! I got it!"

i2c = busio.I2C(board.SCL, board.SDA)
mpr121 = adafruit_mpr121.MPR121(i2c)

# screen setting
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

BAUDRATE = 64000000

spi = board.SPI()
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

height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

draw = ImageDraw.Draw(image)

draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)

padding = -2
top = padding
bottom = height - padding

x = 0

font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# some other examples
# topic = 'IDD/a/fun/topic'

#this is the callback that gets called once we connect to the broker. 
#we should add our subscribe functions here as well
def on_connect(client, userdata, flags, rc):
        print(f"connected with result code {rc}")
        client.subscribe(topic1)
        client.subscribe(topic2)
        client.subscribe(topic3)
        # you can subsribe to as many topics as you'd like
        # client.subscribe('some/other/topic')



def on_message(cleint, userdata, msg):
        print(f"topic: {msg.topic} msg: {msg.payload.decode('UTF-8')}")
        if msg.topic == topic1:
                count[0] = int(msg.payload.decode('UTF-8'))
        elif msg.topic == topic2:
                count[1] = int(msg.payload.decode('UTF-8'))
        elif msg.topic == topic3:
                count[2] = int(msg.payload.decode('UTF-8'))
        print(count[0], count[1], count[2])
        # you can filter by topics
        # if msg.topic == 'IDD/some/other/topic': do thing


# Every client needs a random ID
client = mqtt.Client(str(uuid.uuid1()))
# configure network encryption etc
client.tls_set()
# this is the username and pw we have setup for the class
client.username_pw_set('idd', 'device@theFarm')

# attach out callbacks to the client
client.on_connect = on_connect
client.on_message = on_message

#connect to the broker
client.connect(
    'farlab.infosci.cornell.edu',
    port=8883)

# this is blocking. to see other ways of dealing with the loop
#  https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#network-loop
client.loop_start()

while True:
        # print("hello")
        y = top
        draw.text((x, y), line1, font=font, fill="#FF0000")
        y += font.getsize(line1)[1]
        draw.text((x, y), line2, font=font, fill="#FFFFFF")
        y += font.getsize(line2)[1]
        draw.text((x, y), line3, font=font, fill="#FF0000")
        y += font.getsize(line3)[1]
        draw.text((x, y), line4, font=font, fill="#FFFFFF")
        y += font.getsize(line4)[1]
        draw.text((x, y), line5, font=font, fill="#FF0000")
        y += font.getsize(line5)[1]
        draw.text((x, y), line6, font=font, fill="#FFFFFF")
        y += font.getsize(line6)[1]

        if mpr121[0].value:
                print("button 0 is pressed")
                client.publish(topic1, str(count[0]+1))
        elif mpr121[1].value:
                print("button 1 is pressed")
                client.publish(topic2, str(count[1]+1))
        elif mpr121[2].value:
                print("button 2 is pressed")
                client.publish(topic3, str(count[2]+1))

        disp.image(image, rotation)
        time.sleep(0.25)

