DRAWABLES = []
COUNT = 0

class Drawable:
    def __init__(self):
        global DRAWABLES, COUNT
         
        DRAWABLES.append(self)
        self.id = COUNT
        COUNT += 1

    # abstract
    def draw(self):
        pass

    # abstract
    def update(self):
        pass

    # abstract
    def collided(self, drawable):
        pass
    
    # abstract
    def accel(self, amount):
        pass

    def get(shape_id):
        return list(filter(lambda d: d.id == shape_id, DRAWABLES))[0]

    def has_collision(point, shape_id):
        drawable = Drawable.get(shape_id)
        for other_drawable in DRAWABLES:
            if other_drawable.id != drawable.id:
                tangent = drawable.check_collision(point, other_drawable):
                    if tangent != None:
                        return other_drawable, tangent
        return None

    def draw_all():
        # draw the items
        for drawable in DRAWABLES:
            drawable.draw()

    def update_all(dt, *args):
        for drawable in DRAWABLES:
            drawable.update()
