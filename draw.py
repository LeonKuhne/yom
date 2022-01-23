DRAWABLES = []

class Drawable:
    def __init__(self):
        DRAWABLES.append(self)

    # abstract
    def draw(self):
        pass

    def draw_all():
        # draw the items
        for drawable in DRAWABLES:
            drawable.draw()
