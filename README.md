# RPi based thermal camera

Thermal camera using the AMG8833 8x8 thermal camera, a Pi and a TFT touch screen

# Caveat

Use this code at your own risk.  If you are new to python, you will find a jumble of undocumented commands.  If you are experienced with python, the viewing this code might actually make your eyes bleed.  You have been warned.

# For the camera

https://stackoverflow.com/questions/28305731/compiler-cant-find-py-initmodule-is-it-deprecated-and-if-so-what-should-i

## Adafruit camera tutorial

Tutorial is written for Python 2, so I updated yuv2rgb and recompiled

```
gcc -DPYTHON_EXECUTABLE=/usr/bin/python3 -c yuv2rgb.c -o yuv2rgb.o
gcc -shared yuv2rgb.o -yuv2rgb.so
```

Do not know if `-D` flag is needed.
