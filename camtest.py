import os
import io
import atexit
import picamera
import yuv2rgb
import csv
from datetime import datetime
from time import sleep
from pitfttools import *
from thermalcamera import *

# --- Define callbacks
def quitCallback():
  raise SystemExit

def nullCallback():
  return

def finishedCallback():
  global done
  done = True

def activeCamCallback():
  global camActive
  camActive = not camActive

def activeThmCallback():
  global thmActive
  thmActive = not thmActive

def maxtempCallback(n):
  global tc
  global screenModeMessage
  tc.MAXTEMP = constrain(tc.MAXTEMP + n, tc.MINTEMP, 80)
  screenModeMessage[2] = "MAXTEMP: " + str(tc.MAXTEMP)

def mintempCallback(n):
  global tc
  global screenModeMessage
  tc.MINTEMP = constrain(tc.MINTEMP + n, 0, tc.MAXTEMP - 1)
  screenModeMessage[1] = "MINTEMP: " + str(tc.MINTEMP)

# pixels data can be recreated in MMA with (? check) 
# ListDensityPlot[Reverse@Transpose@Reverse@Partition[Flatten@Import["file","CSV"],8],InterpolationOrder->1]
# bicubic uses the same transformation but is already partitioned
def saveCallback():
  # will eventually do both cameras
  # presently assumes img directory exists and does not care about privs
  global pixels
  global bicubic
  # Use the date for the filename
  now = datetime.now()
  # Save raw data (pixel temperatures)
  pfile = open(now.strftime('img/%y%m%d-%H%M%S-pixels.txt'), 'w')
  for item in pixels:
    pfile.write('%s\n' % item)
  pfile.close
  # Save bicubic transformation (probably not needed)
  with open(now.strftime('img/%y%m%d-%H%M%S-bicubic.csv'), 'w') as bfile:
    bWriter = csv.writer(bfile, delimiter=',', quotechar='"')
    for r in bicubic:
      bWriter.writerow(r)
  # Save image
  camera.capture(now.strftime('img/%y%m%d-%H%M%S-img.jpg'), use_video_port=False, format='jpeg',
    thumbnail=None)

      
  
# Technically a callback, named inconsistently because I'm a bad programmer
def setScreenMode(n):
  global screenMode
  screenMode = n

# --- define button color functions
def camButtonColor():
  global camActive
  if camActive:
    return GOLD
  else:
    return DKGREEN

def thmButtonColor():
  global thmActive
  if thmActive:
    return GOLD
  else:
    return DKGREEN

# More efficient would be to have a single function; however I think that
#  requires a change in the Button class.
def buttonColor(flag, trueColor, falseColor):
  if flag:
    return trueColor
  else:
    return falseColor

# --- Place globals here

tc = ThermalCamera()        # Initialize thermal camera
screenMode = 0              # Which set of buttons to display
camActive = False           # Is optical camera active?
thmActive = False           # Is thermal camera active?

# --- screenMode names
MAXMENU   = 10
smMAIN    = 0
smMIN     = 1
smMAX     = 2
smQUIT    = 3
smSAVE    = 4

# --- Create button screens

buttons = [[]] * MAXMENU
# main menu
buttons[smMAIN] =   [
    Button((5, 250, 86, 50), color=None, bg='prev', cb=nullCallback),
    Button((101,250, 86, 50), color=camButtonColor, bg='camera', cb=activeCamCallback),
    Button((197,250, 86, 50), color=RUST, bg='quit', cb=quitCallback),
    Button((293,250, 86, 50), color=thmButtonColor, bg='flame', cb=activeThmCallback),
    Button((389,250, 86, 50), color=None, bg='next', cb=setScreenMode, value=smMIN)
  ]
# Thermal camera MINTEMP adjust
buttons[smMIN] =   [
    Button((5, 250, 86, 50), color=None, bg='prev', cb=setScreenMode, value=smMAIN),
    Button((101,250, 86, 50), color=None, bg='minus', cb=mintempCallback, value=-1),
    Button((293,250, 86, 50), color=None, bg='plus', cb=mintempCallback, value=1),
    Button((389,250, 86, 50), color=None, bg='next', cb=setScreenMode, value=smMAX)
  ]
# Thermal camera MAXTEMP adjust
buttons[smMAX] =   [
    Button((5, 250, 86, 50), color=None, bg='prev', cb=setScreenMode, value=smMIN),
    Button((101,250, 86, 50), color=None, bg='minus', cb=maxtempCallback, value=-1),
    Button((293,250, 86, 50), color=None, bg='plus', cb=maxtempCallback, value=1),
    Button((389,250, 86, 50), color=None, bg='next', cb=setScreenMode, value=smSAVE)
  ]
# Save thermal snapshot
buttons[smSAVE] =   [
    Button((5, 250, 86, 50), color=None, bg='prev', cb=setScreenMode, value=smMAX),
    Button((197,250, 86, 50), color=GOLD, bg='storage', cb=saveCallback),
    Button((389,250, 86, 50), color=None, bg='next', cb=setScreenMode, value=smMAIN)
  ]

# Title the button screens.  List constructed since I don't know what order I really want these in
screenModeMessage = [""] * MAXMENU 
screenModeMessage[smMAIN]     = "Main"
screenModeMessage[smMIN]      = "Set MINTEMP: " + str(tc.MINTEMP)
screenModeMessage[smMAX]      = "Set MAXTEMP: " + str(tc.MAXTEMP)
screenModeMessage[smSAVE]     = "Export thermal CSV"

# --- load icons and connect buttons
icons = loadIcons()
makeButtons(buttons, icons)

# --- Start screen
lcd = screenInit()
lcd.fill(DKGREEN)



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

# --- Loop

done = False

while not done:

  # Look for button presses
  for event in pygame.event.get():
    if(event.type is MOUSEBUTTONDOWN):
      pos = pygame.mouse.get_pos()
      for b in buttons[screenMode]:
        if b.selected(pos):
          break
  
  # start with blank screen
  lcd.fill(DKGREEN)

  # create camera display
  if camActive:
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

  # Create thermal overlay
  # https://stackoverflow.com/questions/6339057/draw-a-transparent-rectangle-in-pygame for transparent overlay
  if thmActive:
    tempSurface = pygame.Surface((tc.sensorWidth,tc.sensorHeight))
    tempSurface.set_alpha(128)
    tempSurface.fill((255, 255, 255, 128))
    pixels, bicubic = tc.displayPixels()
    for ix, row in enumerate(bicubic):
      for jx, pixel in enumerate(row):
        pygame.draw.rect(tempSurface, 
          tc.colors[constrain(int(pixel), 0, tc.COLORDEPTH-1)], 
          (tc.sensorPixelWidth * ix, tc.sensorPixelHeight * jx, tc.sensorPixelWidth, tc.sensorPixelHeight))
    lcd.blit(tempSurface,(0,0))

  # Draw the buttons
  for b in buttons[screenMode]:
    b.draw(lcd)

  # Draw message
  font = pygame.font.SysFont("quicksandmedium", 25)
  text = font.render(screenModeMessage[screenMode], True, GOLD)
  lcd.blit(text, (240 - text.get_width() // 2, 225 - text.get_height() //2))

  pygame.display.update()


