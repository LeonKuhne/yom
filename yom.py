#!/bin/python

from random import random
import pyglet
from pyglet.gl import *
import math
import time 
from shapes import Triangle
from draw import  Drawable
from display import Display

UPDATE_INTERVAL = 1/30 # in seconds

display = Display()

# create a window
count = int(random() * 3) + 1
for idx in range(count):
    x = display.win.width / (count+1) * (idx+1)
    y = display.win.height / 2
    Triangle(x, y, display.win)

@display.win.event # pyglet: draws when the window loads
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_TRIANGLES)
    Drawable.draw_all()
    glEnd()
    #time.sleep(.1)

# run
pyglet.clock.schedule(Drawable.update_all, UPDATE_INTERVAL)
pyglet.app.run()
