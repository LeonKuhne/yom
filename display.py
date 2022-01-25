import pyglet

DISPLAY = None

class Display:
    def __init__(self):
        global DISPLAY
        DISPLAY = self

        self.win = pyglet.window.Window(resizable=True)

    def get():
        return DISPLAY
