# for pygame
import pygame
from pygame.locals import *
import os
from time import sleep
# for file export
from datetime import datetime
# for thermal camera
import busio
import board
import adafruit_amg88xx
import math
import numpy as np
from scipy.interpolate import griddata
from colour import Color

# my classes
from button import button
from thermalcamera import *

# setup thermal camera
i2c = busio.I2C(board.SCL, board.SDA)
tc = adafruit_amg88xx.AMG88XX(i2c)

# colors
GOLD = (255, 199, 38)
LTGREEN = (87, 121, 53)
DKGREEN = (0, 83, 62)

# set the display to pitft and initialize
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
pygame.mouse.set_visible(False)

lcdWidth = 480
lcdHeight = 320
lcdDimensions = (lcdWidth, lcdHeight)

lcd = pygame.display.set_mode(lcdDimensions)
lcd.fill(DKGREEN)

# make some buttons
# 40 height is appropriate for font size.  Approximate 20 pixels per character for width

bHeight = 40
bWidth = 80
bSpacing = 10

# make button positioning a bit easier
# dim is 0 for x, 1 for y, x pos can go from 0 to 5, y pos from 0 to 4

def bPosition(dim, n,  h = bHeight, w = bWidth, s = bSpacing):
  if (dim == 0):
    return n * (w + s) + s
  else:
    return n * (h + s) + s

b1 = button(GOLD, bPosition(0,0), bPosition(1,0), bWidth, bHeight, text='Cam')
b1.draw(lcd)
b2 = button(GOLD, bPosition(0,0), bPosition(1,5), bWidth, bHeight, text='Exit')
b2.draw(lcd)
b3 = button(GOLD, bPosition(0,0), bPosition(1,1), bWidth, bHeight, text='Temp')
b3.draw(lcd)
b4 = button(GOLD, bPosition(0,0), bPosition(1,4), bWidth, bHeight, text='BYE')
b4.draw(lcd)
b5 = button(GOLD, bPosition(0,0), bPosition(1,2), bWidth, bHeight, text='Snap')
b5.draw(lcd)

# initial screen is set up, so display it
pygame.display.update()

done = False
showTemp = False
showCamera = False

while not done:
  for event in pygame.event.get():
    if(event.type is MOUSEBUTTONUP):
      pos = pygame.mouse.get_pos()
      if b1.isOver(pos):
        showCamera = not showCamera        
      elif b3.isOver(pos):
        showTemp = not showTemp
        if not showTemp:
          b3 = button(GOLD, bPosition(0,0), bPosition(1,1), bWidth, bHeight, text='Temp')
          b3.draw(lcd)
      elif b5.isOver(pos):
        now = datetime.now()
        datafile = open(now.strftime('%y%m%d-%H%M%S.txt'), 'w')
        for item in pixels:
          datafile.write('%s\n' % item)
        datafile.close
      elif b4.isOver(pos):
        print("shutting down")
        done = True
      elif b2.isOver(pos):
        done = True
  # Replace temperature via button
  if showTemp:
    # Create updated text for the button
    b3 = button(GOLD, bPosition(0,0), bPosition(1,1), bWidth, bHeight, text='')
    b3.draw(lcd)
    b3 = button(GOLD, bPosition(0,0),bPosition(1,1),bWidth,bHeight,text="{:.2f}".format(tc.temperature))
    b3.draw(lcd)
  if showCamera:
    # create camera display
    pixels, bicubic = displayPixels(tc)
    for ix, row in enumerate(bicubic):
      for jx, pixel in enumerate(row):
        pygame.draw.rect(lcd, colors[constrain(int(pixel), 0, COLORDEPTH-1)], (200+sensorPixelWidth * ix, 40+sensorPixelWidth * jx, sensorPixelHeight, sensorPixelWidth))


  pygame.display.update()
  sleep(0.05)

pygame.quit()
  
