from pyglet.gl import *
from draw import Drawable
from random import random
from time import time
import math
from display import Display

MAX_SPEED = 8 
WOBBLE_WIDTH = 30.0
RAND_START = 200.0
MASS_FACTOR = 2.0
BOOM_FACTOR = 5.0
MIN_VELOCITY = 1
SHRINK_SPEED = 1

COUNT = 0

class Point:
    def __init__(self, win, x=0.0, y=0.0):
        global COUNT
        self.id = COUNT
        COUNT += 1
        
        self.win = win
        self.x = x + (random() * 2 - 1) * RAND_START
        self.y = y + (random() * 2 - 1) * RAND_START
        self.max_speed = random() * MAX_SPEED
        self.z = 0.0
        self.vel_x = MIN_VELOCITY + (random() * 2 - 1) * (self.max_speed-MIN_VELOCITY) * (-1 if random() >= .5 else 1)
        self.vel_y = MIN_VELOCITY + (random() * 2 - 1) * (self.max_speed-MIN_VELOCITY) * (-1 if random() >= .5 else 1)
        self.effects = []

    def accel_x(self, vel_x):
        self.vel_x = vel_x
        if abs(self.vel_x) < MIN_VELOCITY:
            self.vel_x = (MIN_VELOCITY + random()/5) * (-1 if random() >= .5 else 1)
        elif self.vel_x < 0:
            self.vel_x = -min(abs(self.vel_x), self.max_speed)
        else:
            self.vel_x = min(self.vel_x, self.max_speed)
    
    def accel_y(self, vel_y):
        self.vel_y = vel_y
        if abs(self.vel_y) < MIN_VELOCITY:
            self.vel_y = (MIN_VELOCITY + random()/5) * (1 + random()) * (-1 if random() >= .5 else 1)
        elif self.vel_y < 0:
            self.vel_y = -min(self.vel_y, self.max_speed)
        else:
            self.vel_y = min(self.vel_y, self.max_speed)

    def move_x(self):
        self.x += self.vel_x
        if self.x < 0 or self.x > self.win.width:
            self.fix_x()

    def move_y(self):
        self.y += self.vel_y
        if self.y < 0 or self.y > self.win.height:
            self.fix_y()

    def fix_x(self):
        self.accel_x(-self.vel_x *(1+random()/10))
        self.move_x()

    def fix_y(self):
        self.accel_y(-self.vel_y *(1+random()/10))
        self.move_y()

    def fix(self):
        if random() >= 0.5:
            self.fix_x()
        else:
            self.fix_y()

    def update(self, shape_id):
        # apply velocities
        self.move_x()
        self.move_y()

        # check for collision
        (other_drawable, tangent) = Drawable.has_collision(self, shape_id)
        if other_drawable:
            print("detected collision")

            # find the point's triangle's mass
            drawable = Drawable.get(shape_id)
            mass = drawable.area() / other_drawable.area()

            # unstick
            #while Drawable.has_collision(self, shape_id):

                # revert
                #self.fix()

                # shrink
                #drawable.shrink()

            # accelerate in opposite directions
            other_vel_x = other_drawable.vel_x()
            other_vel_y = other_drawable.vel_y()
            drawable.accel(other_vel_x * 1/mass, other_vel_y* 1/mass)
            drawable.accel(other_vel_x * 1/mass, other_vel_y* 1/mass)
            other_drawable.accel(self.vel_x * mass, self.vel_y * mass)
            other_drawable.accel(self.vel_x * mass, self.vel_y * mass)

    def shader(self):
        (x, y, z) = (self.x, self.y, self.z)

        # apply any effects
        for effect in self.effects:
            (x, y) = effect(x, y)

        return (x, y, z)

    # add effects to run on update
    def add_effect(self, *effects):
        self.effects += effects

class Line(Drawable):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def slope(self):
        return (self.end.y - self.start.y) / (self.end.x - self.start.x)

    def intercept_y(self):
        return self.start.y - self.slope() * self.start.x

    def intersection_x(self, other):
        slope = self.slope()
        other_slope = other.slope()

        # check if parallel
        if slope == other_slope:
            return None

        return (self.intercept_y() - other.intercept_y()) / (other_slope - slope)

    def x_in_range(self, x):
        min_x = min(self.start.x, self.end.x)
        max_x = max(self.start.x, self.end.x)
        return min_x < x and x < max_x
        

    def collision(self, other_line):
        coll_x = self.intersection_x(other_line)

        # lines are parallel
        if coll_x == None:
            return False

        # check if lines extend to intersection
        return self.x_in_range(coll_x) and other_line.x_in_range(coll_x)

    def has(self, point):
        return point == self.start or point == self.end

class Triangle(Drawable):

    def __init__(self, x, y, win):
        self.type = 'point'
        Drawable.__init__(self)
        self.points = [Point(win, x, y) for _ in range(3)]
        self.color = (random(), random(), random())
        
        # create movement effects
        gravity = lambda x, y: (x, (1-(y/win.height) ** 2.5) * win.height)
        wobble_sin = lambda x, y: (x + math.sin(time()*5) * WOBBLE_WIDTH, y)
        wobble_cos = lambda x, y: (x + math.cos(time()*5) * WOBBLE_WIDTH, y)

        # add effects
        for point in self.points:
            #point.add_effect(gravity, wobble_sin if random() >= .5 else wobble_cos)
            pass

    def draw(self):
        glColor4f(self.color[0], self.color[1], self.color[2], 1)

        # render points
        for point in self.points:
            (x, y, z) = point.shader()
            glVertex3f(abs(x), abs(y), abs(z))

    def update(self):
        for point in self.points:
            point.update(self.id)

    def next_detail(self, points):
        idx = -1
        next_x = 0
        for _ in range(len(points) ** 2):
            if next_x == 0:
                idx += 1
                yield points[idx].x

            else:
                yield points[idx].y

            idx = (idx + 1) % len(points)
            next_x = (next_x + 1) % len(points)

    def area(self, points = None):
        if points == None:
            points = self.points

        calc_area_part  = lambda x: x.__next__() * (x.__next__() - x.__next__())
        calc_area = lambda gen: abs(sum([calc_area_part(gen) for _ in range(len(self.points))]))
        return max(calc_area(self.next_detail(points)), 0.00000001)

    def vel_x(self):
        return sum([point.vel_x for point in self.points]) / len(self.points)

    def vel_y(self):
        return sum([point.vel_y for point in self.points]) / len(self.points)

    def lines(self, condition=lambda line: True):
        lines = []
        for idx in range(len(self.points)):
            next_idx = (idx + 1) % len(self.points)
            line = Line(self.points[idx], self.points[next_idx])
            if condition(line):
                lines.append(line)
        return lines

    def check_collision(self, point, drawable):
        # go through this triangles lines that include the point
        for line in self.lines(lambda line: line.has(point)):
            
            # check for collisions with the other triangles lines
            for other_line in drawable.lines():
                if line.collision(other_line):


                    return 0 # TODO return the tangent

        return None

    def shrink(self):
        (total_x, total_y) = (0, 0)
        for point in self.points:
            total_x += point.x
            total_y += point.y
        center_x, center_y = (total_x / len(self.points), total_y / len(self.points))
        for point in self.points:
            diff_x = center_x - point.x
            diff_y = center_y - point.y
            point.x += diff_x * (SHRINK_SPEED/1000)
            point.y += diff_y * (SHRINK_SPEED/1000)

    def accel(self, accel_x, accel_y):
        for point in self.points:
            point.accel_x(accel_x)
            point.accel_y(accel_y)
