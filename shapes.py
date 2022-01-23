from pyglet.gl import *
from draw import Drawable
from random import random
from time import time
import math

MAX_SPEED = 3
MIN_SPEED = 1
WOBBLE_WIDTH = 30.0

class Point:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0
        self.vel_x = MIN_SPEED + random() * (MAX_SPEED-MIN_SPEED)
        self.vel_y = MIN_SPEED + random() * (MAX_SPEED-MIN_SPEED)
        self.effects = []
    
    def update(self):
        self.x += self.vel_x
        self.y += self.vel_y

    def shader(self):
        (x, y, z) = (self.x, self.y, self.z)

        # apply any effects
        for effect in self.effects:
            print('before', x, y)
            (x, y) = effect(x, y)
            print('after', x, y)

        return (x, y, z)

    # add effects to run on update
    def add_effect(self, *effects):
        self.effects += effects

class Triangle(Drawable):

    def __init__(self, win):
        Drawable.__init__(self)
        self.points = [Point() for _ in range(3)]
        
        # create movement effects
        mirror = lambda var, size: abs((var % (size * 2)) - size)
        wrap = lambda x, y: (mirror(x, win.width), mirror(y, win.height))
        gravity = lambda x, y: (x, (1-(y/win.height) ** 2.5) * win.height)
        wobble = lambda x, y: (x + math.sin(time()*5) * WOBBLE_WIDTH, y)

        # add effects
        for point in self.points:
            point.add_effect(wrap, gravity, wobble)

    def draw(self):
        # create a triangle context
        glBegin(GL_TRIANGLES)

        points = []
        # render points
        for point in self.points:
            (x, y, z) = point.shader()
            points.append((int(x), int(y)))
            glVertex3f(x, y, z)

        print(points)

    def update(self, dt, *args):
        for point in self.points:
            point.update()
