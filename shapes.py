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

    def accel_x(self, acc_x):
        self.vel_x *= acc_x
        if abs(self.vel_x) < MIN_VELOCITY:
            self.vel_x = (MIN_VELOCITY + random()/5) * (-1 if random() >= .5 else 1)
        elif self.vel_x < 0:
            self.vel_x = -min(abs(self.vel_x), self.max_speed)
        else:
            self.vel_x = min(self.vel_x, self.max_speed)
    
    def accel_y(self, acc_y):
        self.vel_y *= acc_y
        if abs(self.vel_y) < MIN_VELOCITY:
            self.vel_y = (MIN_VELOCITY + random()/5) * (1 + random()) * (-1 if random() >= .5 else 1)
        elif self.vel_y < 0:
            self.vel_y = -min(abs(self.vel_y), self.max_speed)
        else:
            self.vel_y = min(self.vel_y, self.max_speed)

    def move_x(self):
        self.x += self.vel_x

        if self.x < 0 or self.x > self.win.width:
            self.accel_x(-1 - (random())/10)
            self.move_x()

    def move_y(self):
        self.y += self.vel_y

        if self.y < 0 or self.y > self.win.height:
            self.accel_y(-1 - (random())/10)
            self.move_y()

    def fix(self):
        accel = 1.0 + random()/10
        if random() >= 0.5:
            self.accel_x(accel)
            self.move_x()
        else:
            self.accel_y(accel)
            self.move_y()

    def update(self, shape_id):
        # apply velocities
        self.move_x()
        self.move_y()

        # check for collision
        other_drawable = Drawable.has_collision(self, shape_id)
        if other_drawable:
            print("detected collision")
            # accelerate the point in the opposite direction
            self.accel_x(-1)
            self.accel_y(-1)

            # unstick
            while Drawable.has_collision(self, shape_id):
                # revert
                self.fix()

                # shrink
                #drawable.shrink()

            # find the point's triangle's mass
            drawable = Drawable.get(shape_id)
            mass = drawable.area() / other_drawable.area() * MASS_FACTOR

            # reverse the direction of the hit triangle
            self.accel_x(-mass + random() - 0.5)
            self.accel_y(-mass + random() - 0.5)

            # bounce the drawable
            drawable.accel(-mass * BOOM_FACTOR * (1 + (random() - .5)/10))

    def shader(self):
        (x, y, z) = (self.x, self.y, self.z)

        # apply any effects
        for effect in self.effects:
            (x, y) = effect(x, y)

        return (x, y, z)

    # add effects to run on update
    def add_effect(self, *effects):
        self.effects += effects

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

    def slope(point_a, point_b):
        return (point_a.y - point_b.y) / (point_a.x - point_b.x)

    def line_collision(p1, p2, o1, o2):
        slope = Triangle.slope(p1, p2)
        intercept_y = p1.y - slope * p1.x

        other_slope = Triangle.slope(o1, o2)
        other_intercept_y = o1.y - other_slope * o1.x

        # calculate where the lines intersect
        if other_slope == slope:
            return False
        intercept_x = (intercept_y - other_intercept_y) / (other_slope - slope)

        # check if the intersection is drawn
        return (min(abs(p1.x), abs(p2.x)) < abs(intercept_x)
        and max(abs(p1.x), abs(p2.x)) > abs(intercept_x)
        and min(abs(o1.x), abs(o2.x)) < abs(intercept_x)
        and max(abs(o1.x), abs(o2.x)) > abs(intercept_x))

    def check_collision(self, point, drawable):
        # check if the lines intersect
        idx = self.points.index(point)
        points = self.points[:idx] + self.points[idx+1:]

        for point_idx in range(len(points)):
            next_idx = (point_idx + 1) % len(points)
            point_a = points[point_idx]
            point_b = points[next_idx]

            if point.id == point_a.id:
                return False

            for other_idx in range(len(drawable.points)):
                other_next_idx = (other_idx + 1) % len(drawable.points)

                other_point_a = drawable.points[other_idx]
                other_point_b = drawable.points[other_next_idx]
                
                if Triangle.line_collision(point_a, point_b, other_point_a, other_point_b):
                    return True
        return False

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

    def accel(self, accel):
        for point in self.points:
            point.accel_x(accel)
            point.accel_y(accel)
