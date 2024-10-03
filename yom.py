#!/bin/python

from random import random
import time
import pyglet
from pyglet.gl import *
import math

UPDATE_INTERVAL = 1/30 # in seconds
MAX_SPEED = 8
MIN_SPEED = 1
WOBBLE_WIDTH = 30

# create a window
win = pyglet.window.Window(resizable=True)

p1 = {'x':0.0, 'y':0.0, 'z': 0}
p2 = {'x':0.0, 'y':0.0, 'z': 0}
v1x = random()+MIN_SPEED*(MAX_SPEED-MIN_SPEED)
v1y = random()+MIN_SPEED*(MAX_SPEED-MIN_SPEED)
v2x = random()+MIN_SPEED*(MAX_SPEED-MIN_SPEED)
v2y = random()+MIN_SPEED*(MAX_SPEED-MIN_SPEED)

# increment the next frame
def update(x, y):
    global p1, p2
    p1['x'] += v1x
    p1['y'] += v1y
    p2['x'] += v2x
    p2['y'] += v2y


# override the method that draws when the window loads
@win.event
def on_draw():
    # clear the screen
    glClear(GL_COLOR_BUFFER_BIT)

    # create a line context
    glBegin(GL_LINES)

    x1 = abs(p1['x'] % (win.width * 2) - win.width)
    y1 = abs(p1['y'] % (win.height * 2) - win.height)
    x2 = abs(p2['x'] % (win.width * 2) - win.width)
    y2 = abs(p2['y'] % (win.height * 2) - win.height)

    # simulate gravity on y's
    y1 = (1-(y1/win.height) ** 2.5) * win.height
    y2 = (1-(y2/win.height) ** 2.5) * win.height

    # wobble x's based on timestamp
    x1 = x1 + math.sin(time.time()*5) * WOBBLE_WIDTH
    x2 = x2 + math.cos(time.time()*5) * WOBBLE_WIDTH

    # create a line, x,y,z
    glVertex3f(x1, y1, p1['z'])
    glVertex3f(x2, y2, p2['z'])

    glEnd()

# run
glColor4f(random(), random(), random(), 1)
pyglet.clock.schedule(update, UPDATE_INTERVAL)
pyglet.app.run()
