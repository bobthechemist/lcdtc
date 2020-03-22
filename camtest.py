import os
import io
import atexit
import picamera
import pygame
import yuv2rgb
from pygame.locals import *


# --- Initialization ---

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

# Init pygame and the screen
pygame.init()
pygame.mouse.set_visible(False)
lcd = pygame.display.set_mode((0,0), pygame.FULLSCREEN)

# Camera parameters for different size settings
sw = 480
sh = 320

sizeData = [
  [(2592, 1944), (sw , sh ), (0.0   , 0.0   , 1.0   , 1.0   )], # Mine
  [(2592, 1944), (320, 240), (0.0   , 0.0   , 1.0   , 1.0   )], # Large
  [(1920, 1080), (320, 180), (0.1296, 0.2222, 0.7408, 0.5556)], # Med
  [(1440, 1080), (320, 240), (0.2222, 0.2222, 0.5556, 0.5556)]] # Small

sizeMode = 0 # Mine

# Init camera
camera = picamera.PiCamera()
atexit.register(camera.close)
camera.resolution = sizeData[sizeMode][1]
camera.rotation = 270
camera.crop = (0.0, 0.0, 1.0, 1.0)

# Buffers 
rgb = bytearray(sw*sh*3)
yuv = bytearray(int(sw*sh*3/2))


done = False

while not done:
  for event in pygame.event.get():
    if(event.type is MOUSEBUTTONDOWN):
      done = True
  stream = io.BytesIO()
  camera.capture(stream, use_video_port=True, format='raw')
  stream.seek(0)
  stream.readinto(yuv)
  stream.close()
  yuv2rgb.convert(yuv, rgb, sizeData[sizeMode][1][0],sizeData[sizeMode][1][1])
  img = pygame.image.frombuffer(rgb[0:
    (sizeData[sizeMode][1][0] * sizeData[sizeMode][1][1] * 3)],
    sizeData[sizeMode][1], 'RGB')
  lcd.blit(img, ((sw - img.get_width())/2,
    (sh - img.get_height()) /2))
  pygame.display.update()

  
