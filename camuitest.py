import fnmatch
import pygame
from pygame.locals import *
import os
import os.path
from camui import *


def addCallback(): # example add to a value
  global myInt
  myInt = myInt + 1

def quitCallback():  # to exit
  raise SystemExit

myInt = 0

iconPath = 'icons' # Subdirectory of icons in PNG format
icons = [] # Will get populated at startup

buttons = [
  # Sample screen
  [Button((  0,188,320, 52), bg='quit'   , cb=addCallback),
   Button((110, 60,100,120), bg='quit-ok'   , cb=quitCallback)]
]

os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb1')
os.putenv('SDL_MOUSEDRV', 'TSLIB')
os.putenv('SDL_MOUSEDEV', '/dev/input/touchscreen')

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
screen.fill((128,128,128))

# Load all icons at startup
for file in os.listdir(iconPath):
  if fnmatch.fnmatch(file, '*.png'):
    icons.append(Icon(file.split('.')[0]))


# Assign Icons to Buttons
for s in buttons:        # for each screenfull of buttons...
  for b in s:            # for each button on screen...
    for i in icons:      # for each icon...
      if b.bg == i.name: # compare names
        b.iconBg = i     # assign icon to button
        b.bg = None      # name is no longer used (garbage collection)
      if b.fg == i.name:
        b.iconFg = i
        b.fg == None

# Main loop

done = False

while not done: 

  for event in pygame.event.get():
    if(event.type is MOUSEBUTTONDOWN):
      done = True

  screen.fill((255,0,0))
  for i,b in enumerate(buttons[0]):
    b.draw(screen)
  pygame.display.update()
