import busio
import board
import adafruit_amg88xx
import math
import numpy as np
from scipy.interpolate import griddata
from colour import Color

MINTEMP = 14.
MAXTEMP = 22.
COLORDEPTH = 1024

points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0,64)]
grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]

sensorHeight = 320
sensorWidth = 480
sensorPixelWidth = 15
sensorPixelHeight = 10

blue = Color("indigo")
colors = list(blue.range_to(Color("red"), COLORDEPTH))

colors = [(int(c.red * 255), int(c.green * 255), int(c.blue * 255)) for c in colors]

def constrain(val, min_val, max_val):
  return min(max_val, max(min_val,val))

def map_value(x, in_min, in_max, out_min, out_max):
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def displayPixels(sensor):
  pixels = []
  # Might want to np.flipud(sensor.pixels) to align pixels and bicubic
  for row in sensor.pixels:
    pixels = pixels + row
  # coverts temperature into a color
  pixels = [map_value(p, MINTEMP, MAXTEMP, 0, COLORDEPTH - 1) for p in pixels]
  #pixels = np.flip(pixels)
  bicubic = griddata(points, pixels, (grid_x, grid_y), method='cubic')
  bicubic = np.flipud(bicubic)
  return pixels,  bicubic


