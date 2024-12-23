#!/bin/python
from random import random
import time
import moderngl
import numpy as np
import math
import pygame
import sys

FPS = 120 
MAX_SPEED = 6
MIN_SPEED = 2
WOBBLE_WIDTH = 10
COLOR_SPEED = 0.001
GRAVITY_STRENGTH = 2

vertex_shader='''
  #version 330

  in vec2 in_vert;

  void main() {
    gl_Position = vec4(in_vert, 0.0, 1.0);
  }
'''
fragment_shader='''
  #version 330

  uniform float time;
  uniform float seed;
  out vec4 color;

  void main() {
    color = vec4(
        0.5 + 0.5 * sin((time * 1.28 + 27.37)*seed),
        0.5 + 0.5 * sin((time * 1.56 + 77.25)*seed),
        0.5 + 0.5 * sin((time * 1.14 + 252.12)*seed),
        1.0
    );
  }
'''

class Yom():
  def __init__(self):
    self.ctx = moderngl.get_context()
    self.program = self.ctx.program(
        vertex_shader=vertex_shader, fragment_shader=fragment_shader)
    _, _, width, height = self.ctx.viewport
    self.p1 = { 'x': random()*width, 'y': random()*height }
    self.p2 = { 'x': random()*width, 'y': random()*height }
    self.v1 = {
      'x': random()*MIN_SPEED*(MAX_SPEED-MIN_SPEED), 
      'y': random()*MIN_SPEED*(MAX_SPEED-MIN_SPEED)}
    self.v2 = {
      'x': random()*MIN_SPEED*(MAX_SPEED-MIN_SPEED), 
      'y': random()*MIN_SPEED*(MAX_SPEED-MIN_SPEED)}
    vertices = np.array([
      self.p1['x'], self.p1['y'],
      self.p2['x'], self.p2['y']
    ], dtype='f4')
    self.vbo = self.ctx.buffer(vertices.tobytes())
    self.vao = self.ctx.simple_vertex_array(
        self.program, self.vbo, 'in_vert')
    self.ctx.line_width = 5
    self.start_time = time.time()
    self.color_seed = random()

  def draw(self):
    self.ctx = moderngl.get_context()
    _, _, width, height = self.ctx.viewport

    self.ctx.clear(0,0,0)

    self.p1['x'] += self.v1['x']
    self.p1['y'] += self.v1['y']
    self.p2['x'] += self.v2['x']
    self.p2['y'] += self.v2['y']

    x1 = abs(self.p1['x'] % (width * 2) - width)
    y1 = abs(self.p1['y'] % (height * 2) - height)
    x2 = abs(self.p2['x'] % (width * 2) - width)
    y2 = abs(self.p2['y'] % (height * 2) - height)

    # simulate gravity on y's
    y1 = (1-(y1/height) ** GRAVITY_STRENGTH) * height
    y2 = (1-(y2/height) ** GRAVITY_STRENGTH) * height

    # wobble x's based on timestamp
    timestep = (time.time()*5) % 2**24
    x1 += math.sin(timestep) * WOBBLE_WIDTH
    x2 += math.cos(timestep) * WOBBLE_WIDTH
    self.program['time'].value = timestep * COLOR_SPEED 
    self.program['seed'].value = self.color_seed

    # scale down
    x1 = x1 / width * 2 - 1
    y1 = y1 / height * 2 - 1
    x2 = x2 / width * 2 - 1
    y2 = y2 / height * 2 - 1

    # create a line, x,y,z
    self.vbo.write(np.array([x1, y1, x2, y2], dtype='f4'))
    self.vao.render(moderngl.LINES)

# run
def run():
  pygame.init()
  pygame.display.set_mode(
    (800, 800), vsync=True,
    flags=pygame.OPENGL | pygame.DOUBLEBUF | pygame.NOFRAME | pygame.RESIZABLE)
  pygame.display.set_caption('yom - bouncing line wallpaper')
  clock = pygame.time.Clock()

  yom = Yom()

  running = True
  while running:
    for event in pygame.event.get():
      # exit
      if (event.type == pygame.QUIT
        or event.type == pygame.KEYDOWN
        and (event.key == pygame.K_q
          or event.key == pygame.K_ESCAPE)
      ): running = False
      # reset
      if (event.type == pygame.KEYDOWN and event.key == pygame.K_r):
        yom = Yom()

    # render
    yom.draw()
    pygame.display.flip()
    clock.tick(FPS)

  pygame.quit()
  sys.exit()

if __name__ == '__main__':
  run()
