#!/bin/python

from random import random
import pyglet
from pyglet.gl import *
import math
import time 
from shapes import Triangle
from draw import  Drawable

UPDATE_INTERVAL = 1/30 # in seconds

# create a window
win = pyglet.window.Window(resizable=True)
triangle = Triangle(win)

@win.event # pyglet: draws when the window loads
def on_draw():
    glClear(GL_COLOR_BUFFER_BIT)
    Drawable.draw_all()
    glEnd()
    #time.sleep(1)

# run
#glColor4f(random(), random(), random(), 1)
glColor4f(1, 1, 1, 1)
pyglet.clock.schedule(triangle.update, UPDATE_INTERVAL)
pyglet.app.run()
