import os
import board
import busio
import adafruit_apds9960.apds9960
import time
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_apds9960.apds9960.APDS9960(i2c)

sensor.enable_proximity = True

while True:
	prox = sensor.proximity
	print(prox)
	if prox > 0:
		sentence = "Okay! I see you studying! Good Job!"
	else:
		sentence = "Go study, Rui"

	cmd = "espeak -ven+f2 -k5 -s150 --stdout  \'" + sentence + "\' | aplay"
	returned_value = os.system(cmd)

	if prox > 0:
		break

	time.sleep(0.2)
