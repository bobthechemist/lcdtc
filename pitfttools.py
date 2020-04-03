# Simplify initializing and using the piTFT
# Likely hardcoded to the tools I have, sorry.
import pygame
from pygame.locals import *
import os
import fnmatch

# My color theme (Brockport Proud)
DKGREEN = (  0,  83,  62)
LTGREEN = ( 87, 121,  53)
GOLD    = (255, 199,  38)
BLUE    = (  0,  65,  89)
RUST    = (123,  29,  32)
PURPLE  = ( 87,  82, 126)
GRAY    = ( 38,  38,  38)
TAN     = (202, 179, 136)

def screenInit():
  os.putenv('SDL_VIDEODRIVER', 'fbcon')
  os.putenv('SDL_FBDEV'      , '/dev/fb1')
  os.putenv('SDL_MOUSEDRV'   , 'TSLIB')
  os.putenv('SDL_MOUSEDEV'   , '/dev/input/touchscreen')
  pygame.init()
  pygame.mouse.set_visible(False)
  return pygame.display.set_mode((0,0), pygame.FULLSCREEN)
  

# User interface stuff

# Icon is a bitmap class that associates name and pygame
# image (PNG).  List is populated at runtime from contents
# of 'icons' directory.

iconPath = 'icons'

class Icon:
  def __init__(self, name):
    self.name = name
    try:
      self.bitmap = pygame.image.load(iconPath + '/' + name + '.png')
    except:
      pass


# Button is a tappable screen region having:
#  - bounding rect ((X, Y, W, H) in pixels)
#  - optional background color and/or Icon (or None), always centered
#  - optional foreground Icon, always centered
#  - optional single callback function
#  - optional single value passed to callback
# Buttons are processed lowest first

class Button:

  def __init__(self, rect, **kwargs):
    self.rect = rect # Bounds
    self.color = None # Background fill color, if any
    self.iconBg = None # Background icon (atop color fill)
    self.iconFg = None # Foreground Icon (atop background)
    self.bg = None # Background icon name
    self.fg = None # Foreground icon name
    self.callback = None # Callback function
    self.value = None # Value passed to callback
    for key, value in kwargs.items():
      if key == 'color'  : self.color    = value
      elif key == 'bg'   : self.bg       = value
      elif key == 'fg'   : self.fg       = value
      elif key == 'cb'   : self.callback = value
      elif key == 'value': self.value    = value

  def selected(self, pos):
    x1 = self.rect[0]
    y1 = self.rect[1]
    x2 = x1 + self.rect[2] - 1
    y2 = y1 + self.rect[3] - 1
    if ((pos[0] >= x1) and (pos[0] <= x2) and
        (pos[1] >= y1) and (pos[1] <= y2)):
      if self.callback:
        if self.value is None : self.callback()
        else:                   self.callback(self.value)
      return True
    return False

  def draw(self, scr):
    # Consider scr.fill(color, rect, speical_flags=pygame.RGB_BLEND_ADD)
    if self.color:
      if type(self.color) is tuple:
        scr.fill(self.color,self.rect)
      else:
        c = self.color()
        scr.fill(c, self.rect)
    if self.iconBg:
      scr.blit(self.iconBg.bitmap,
        (self.rect[0] + (self.rect[2] - self.iconBg.bitmap.get_width())/2,
         self.rect[1] + (self.rect[3] - self.iconBg.bitmap.get_height())/2))
    if self.iconFg:
      scr.blit(self.iconFg.bitmap,
        (self.rect[0] + (self.rect[2] - self.iconFg.bitmap.get_width())/2,
         self.rect[1] + (self.rect[3] - self.iconFg.bitmap.get_height())/2))
  
  def setBg(self, name):
    if name is None:
      self.iconBg = None
    else:
      for i in icons:
        if name == i.name:
          self.iconBg = i
          break


def loadIcons():
  icons = []
  for file in os.listdir(iconPath):
    if fnmatch.fnmatch(file, '*.png'):
      icons.append(Icon(file.split('.')[0]))
  return icons

def makeButtons(buttons, icons):
  for s in buttons:
    for b in s:
      for i in icons:
        if b.bg == i.name:
          b.iconBg = i
          b.bg = None
        if b.fg == i.name:
          b.iconFg = i
          b.fg = None
  
