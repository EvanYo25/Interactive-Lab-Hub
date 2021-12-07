import time
import board
import busio

import adafruit_mpr121

i2c = busio.I2C(board.SCL, board.SDA)

mpr121 = adafruit_mpr121.MPR121(i2c)


while True:
	if mpr121[0].value:
		arr = []
		time.sleep(1)
		print("start")
		while True:
			if mpr121[0].value:
				print(arr)
				print("end")
				time.sleep(1)
				break
			for i in range(1, 5):
				if mpr121[i].value:
					arr.append(i)
					#print(i, "touched")
				time.sleep(0.05)

#while True:
#	for i in range(4):
#		if mpr121[i].value:
#			print(i, "touched")
#		time.sleep(0.25)

