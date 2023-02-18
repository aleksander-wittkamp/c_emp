class WorldMap:
    def __init__(self, world_map, x=0, y=0):
        self.x = x
        self.y = y
        self.world_map = world_map

    def move_left(self):
        self.x -= 1
        return self.get_room()

    def move_right(self):
        self.x += 1
        return self.get_room()

    def move_up(self):
        self.y -= 1
        return self.get_room()

    def move_down(self):
        self.y += 1
        return self.get_room()

    def get_room(self):
        return self.world_map[self.y][self.x]