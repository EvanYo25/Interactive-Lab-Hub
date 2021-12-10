import board
from adafruit_seesaw import seesaw, rotaryio, digitalio
import pyaudio
import wave
import os
import time
from os import walk
from pathlib import Path
# ##################
import numpy as np
import cv2
import sys
import imutils
from pyzbar import pyzbar
import argparse
import datetime
import imutils
import time
import cv2

# #################
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.OUT)


seesaw = seesaw.Seesaw(board.I2C(), addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
print("Found product {}".format(seesaw_product))
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = digitalio.DigitalIO(seesaw, 24)

encoder = rotaryio.IncrementalEncoder(seesaw)
last_position = 0
isPressing = False

form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
samp_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
# wav_output_filename = 'record.wav' # name of .wav file
audio = pyaudio.PyAudio() # create pyaudio instantiation
frames = []
stream = None

playbackCtr = 0
getRecordings = True
recordings = []

# ######################################
img=None
currQRCode = None
webCam = False
print("hi")
if(len(sys.argv)>1):
   try:
      print("I'll try to read your image");
      img = cv2.imread(sys.argv[1])
      if img is None:
         print("Failed to load image file:", sys.argv[1])
   except:
      print("Failed to load the image are you sure that:", sys.argv[1],"is a path to an image?")
else:
   try:
      print("Trying to open the Webcam.")
      cap = cv2.VideoCapture(0)
      if cap is None or not cap.isOpened():
         raise("No camera")
      webCam = True

   except:
      print("Cant't open webcam")
print("Is Webcam running? "+ str(webCam))
# ######################################

def vibrate(secs):
    GPIO.output(5, True)
    time.sleep(secs)
    GPIO.output(5, False)

def GetRecordings(dir):
    global recordings
    exist = Path("./localfiles/" + dir).is_dir()
    if exist:
        cmd = os.popen("rm -r ./localfiles/" + dir)
        cmd.read()
    print("Downloading")
    cmd = os.popen("sshpass -p 'ch956@cornell.edu' scp -r pi@10.56.252.86:~/myfiles/" + dir + " ./localfiles/")
    cmd.read()
    print("Finished downloading")
    recordings = next(walk("./localfiles/"+currQRCode), (None, None, []))[2]
    print(recordings)

def PlayRecording(direction):
    global playbackCtr
    recordingLen = len(recordings)
    if recordingLen <= 0:
        return
    playbackCtr = (playbackCtr+direction)%recordingLen
    os.system('aplay '+ './localfiles/' + currQRCode + '/' + recordings[playbackCtr])
    # if direction > 0:
    #     print("next")
    # elif direction < 0:
    #     print("prev")

def StartRecording():
    global stream
    # create pyaudio stream
    stream = audio.open(format = form_1,rate = samp_rate,channels = chans, \
                        input_device_index = dev_index,input = True, \
                        frames_per_buffer=chunk)
    print("recording")

def StopRecording():
    global stream
    global audio
    stream.stop_stream()
    stream.close()
    audio.terminate()
    print("stopped")
    filename = time.strftime("%Y%m%d-%H%M%S")+".wav"
    wavefile = wave.open(filename,'wb')
    wavefile.setnchannels(chans)
    wavefile.setsampwidth(audio.get_sample_size(form_1))
    wavefile.setframerate(samp_rate)
    wavefile.writeframes(b''.join(frames))
    wavefile.close()
    audio = pyaudio.PyAudio() # create pyaudio instantiation
    stream = None
    time.sleep(2)
    while not os.path.isfile(filename):
        print("not yet")
        continue
    SendFile(filename, currQRCode)

def SendFile(filename, dir):
    print("New file created: "+filename)
    print("uploading")
    cmd = os.popen("sshpass -p 'ch956@cornell.edu' scp ./" + filename + " pi@10.56.252.86:~/myfiles/" + dir)
    cmd.read()
    print("uplaoded")

def ReadQRCode():
    global currQRCode
    # if there is a QR code, return true
    if webCam:
        ret, img = cap.read()
        frame = imutils.resize(img, width=400)
        barcodes = pyzbar.decode(frame)
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
            barcodeData = barcode.data.decode("utf-8")
            barcodeType = barcode.type
            text = "{}".format(barcodeData)
            if text != currQRCode:
                currQRCode = text
                vibrate(2)
                print(currQRCode)
                return True
    return False

while True:
    if ReadQRCode():
        GetRecordings(currQRCode)
    position = -encoder.position
    if not button.value and not isPressing:
        isPressing = True
        StartRecording()
    elif not button.value and isPressing:
        data = stream.read(chunk)
        frames.append(data)
    elif button.value and isPressing:
        isPressing = False
        StopRecording()
    elif position != last_position:
        print(position)
        PlayRecording(position-last_position)
        last_position = position

cv2.destroyAllWindows()
