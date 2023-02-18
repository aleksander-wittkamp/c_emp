import random
import sys
import os
import copy

import pygame
from pygame.locals import *

from config import *


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


class Grid:
    grid_key = {}

    def __init__(self, grid):
        self.grid = copy.deepcopy(grid)

    def draw(self):
        for i in range(16):
            for j in range(12):
                self.grid_key[self.grid[j][i]].draw(i, j)


class Drawable:
    def __init__(self, img):
        self.image = pygame.transform.scale(pygame.image.load(img), (CHARWIDTH, CHARHEIGHT))

    def draw(self, x, y):
        rect = pygame.Rect((x * CHARWIDTH, y * CHARHEIGHT, CHARWIDTH, CHARHEIGHT))
        DISPLAYSURF.blit(self.image, rect)

sprite_folder = "./sprites"
lava = Drawable(os.path.join(sprite_folder, 'lava.png'))
lava_rock = Drawable(os.path.join(sprite_folder, 'lava_rock.png'))
grass = Drawable(os.path.join(sprite_folder, 'grass.png'))
rock = Drawable(os.path.join(sprite_folder, 'rock.png'))
tree = Drawable(os.path.join(sprite_folder, 'tree.png'))
heart = Drawable(os.path.join(sprite_folder, 'heart.png'))


class Background(Grid):
    grid_key = {0: grass, 1: lava}


class Foreground(Grid):
    grid_key = {1: rock, 2: tree, 3: lava_rock}

    def __init__(self, grid, features):
        super().__init__(grid)
        for i in features:
            feature = create_feature(i[0])
            self.grid[i[2]][i[1]] = feature

    def draw(self):
        for i in range(16):
            for j in range(12):
                if self.grid[j][i] in self.grid_key:
                    self.grid_key[self.grid[j][i]].draw(i, j)
                elif isinstance(self.grid[j][i], Drawable):
                    self.grid[j][i].draw(i, j)

    def update(self, player, dmg_mng):
        for i in range(16):
            for j in range(12):
                if isinstance(self.grid[j][i], Unit):
                    surrounding_info = self.get_surrounding_info(i, j)
                    self.grid = self.grid[j][i].update(
                        self.grid, surrounding_info, i, j, player, dmg_mng)

    def get_surrounding_info(self, x, y):
        info = {LEFT: None, RIGHT: None, UP: None, DOWN: None}
        if x > LEFT_BOUND:
            if isinstance(self.grid[y][x-1], PlayerCharacter):
                info[LEFT] = 'player'
            elif self.allow_move(x - 1, y):
                info[LEFT] = 'open'
        if x < RIGHT_BOUND:
            if isinstance(self.grid[y][x+1], PlayerCharacter):
                info[RIGHT] = 'player'
            elif self.allow_move(x + 1, y):
                info[RIGHT] = 'open'
        if y > UP_BOUND:
            if isinstance(self.grid[y-1][x], PlayerCharacter):
                info[UP] = 'player'
            elif self.allow_move(x, y - 1):
                info[UP] = 'open'
        if y < LOW_BOUND:
            if isinstance(self.grid[y+1][x], PlayerCharacter):
                info[LEFT] = 'player'
            elif self.allow_move(x - 1, y):
                info[LEFT] = 'open'
        return info

    def allow_move(self, x, y):
        return self.grid[y][x] == 0

    def detect_collision(self, x, y):
        return isinstance(self.grid[y][x], Unit)

    def place_player(self, x, y, player):
        self.grid[y][x] = player

    def set_empty(self, x, y):
        self.grid[y][x] = 0


class Room:
    def __init__(self, background, foreground):
        self.bg = background
        self.fg = foreground
        self.damage_manager = DamageManager()
        self.char_x = None
        self.char_y = None
        self.player = None

    def game_over(self):
        return self.player.health < 0

    def draw(self):
        self.bg.draw()
        self.fg.draw()
        self.damage_manager.draw()
        self.display_hearts()

    def update(self):
        self.fg.update(self.player, self)

    def place_player(self, x, y, player):
        self.char_x = x
        self.char_y = y
        self.player = player
        self.fg.place_player(x, y, player)

    def remove_player(self):
        self.fg.set_empty(self.char_x, self.char_y)
        self.char_x = None
        self.char_y = None
        self.player = None

    def char_move(self, direction):
        if direction == LEFT:
            if self.fg.detect_collision(self.char_x - 1, self.char_y):
                self.damage_manager.add_bar(self.char_x, self.char_y, LEFT)
                self.player.take_damage(1)
            elif self.fg.allow_move(self.char_x - 1, self.char_y):
                self.fg.set_empty(self.char_x, self.char_y)
                self.char_x -= 1
                self.fg.place_player(self.char_x, self.char_y, self.player)
        elif direction == RIGHT:
            if self.fg.detect_collision(self.char_x + 1, self.char_y):
                self.damage_manager.add_bar(self.char_x, self.char_y, RIGHT)
                self.player.take_damage(1)
            elif self.fg.allow_move(self.char_x + 1, self.char_y):
                self.fg.set_empty(self.char_x, self.char_y)
                self.char_x += 1
                self.fg.place_player(self.char_x, self.char_y, self.player)
        elif direction == UP:
            if self.fg.detect_collision(self.char_x, self.char_y - 1):
                self.damage_manager.add_bar(self.char_x, self.char_y, UP)
                self.player.take_damage(1)
            elif self.fg.allow_move(self.char_x, self.char_y - 1):
                self.fg.set_empty(self.char_x, self.char_y)
                self.char_y -= 1
                self.fg.place_player(self.char_x, self.char_y, self.player)
        elif direction == DOWN:
            if self.fg.detect_collision(self.char_x, self.char_y + 1):
                self.damage_manager.add_bar(self.char_x, self.char_y, DOWN)
                self.player.take_damage(1)
            elif self.fg.allow_move(self.char_x, self.char_y + 1):
                self.fg.set_empty(self.char_x, self.char_y)
                self.char_y += 1
                self.fg.place_player(self.char_x, self.char_y, self.player)

    def char_atk(self, direction):
        if direction == LEFT and self.fg.allow_move(self.char_x - 1, self.char_y):
            self.throw(LEFT, self.char_x - 1, self.char_y)
        elif direction == RIGHT and self.fg.allow_move(self.char_x + 1, self.char_y):
            self.throw(RIGHT, self.char_x + 1, self.char_y)
        elif direction == UP and self.fg.allow_move(self.char_x, self.char_y - 1):
            self.throw(UP, self.char_x, self.char_y - 1)
        elif direction == DOWN and self.fg.allow_move(self.char_x, self.char_y + 1):
            self.throw(DOWN, self.char_x, self.char_y + 1)

    def throw(self, direction, x, y):
        projectile = self.player.get_projectile()
        projectile.set_direction(direction)
        self.fg.place_player(x, y, projectile)

    def display_hearts(self):
        for i in range(self.player.health):
            heart.draw(i, 12)


class Unit(Drawable):
    def __init__(self, img):
        super().__init__(img)

    def update(self, grid, surrounding_info, x, y, player, dmg):
        raise NotImplementedError


class Projectile(Unit):
    def __init__(self, img):
        super().__init__(img)
        self.direction = None
        self.reset_val = 15
        self.counter = self.reset_val

    def set_direction(self, direction):
        self.direction = direction

    def update(self, grid, surrounding_info, x, y, player, dmg):
        open_spaces = [i for i, j in surrounding_info.items() if j]
        self.counter -= 1
        if self.counter == 0:
            self.counter = self.reset_val
            if surrounding_info[self.direction] == 'player':
                flippy = {LEFT: RIGHT, RIGHT: LEFT, UP: DOWN, DOWN: UP}
                dmg.damage_manager.add_bar(dmg.char_x, dmg.char_y, flippy[self.direction])
                player.take_damage(1)
                grid[y][x] = 0
            else:
                if self.direction not in open_spaces:
                    grid[y][x] = 0
                elif self.direction == LEFT:
                    grid[y][x - 1] = self
                    grid[y][x] = 0
                elif self.direction == RIGHT:
                    grid[y][x + 1] = self
                    grid[y][x] = 0
                elif self.direction == UP:
                    grid[y - 1][x] = self
                    grid[y][x] = 0
                elif self.direction == DOWN:
                    grid[y + 1][x] = self
                    grid[y][x] = 0
        return grid


class PlayerCharacter(Drawable):
    def __init__(self):
        super().__init__(os.path.join(sprite_folder, 'base_char.png'))
        self.max_health = 3
        self.health = 3
        self.projectile = 'heart_weapon'

    def take_damage(self, amount):
        self.health -= amount

    def heal(self, amount):
        self.health += amount

    def get_projectile(self):
        return create_feature(self.projectile)


class Thrower:
    def __init__(self, projectile):
        self.projectile = projectile

    def throw(self, grid, direction, x, y):
        weapon = create_feature(self.projectile)
        weapon.set_direction(direction)
        if direction == LEFT:
            grid[y][x-1] = weapon
        elif direction == RIGHT:
            grid[y][x+1] = weapon
        elif direction == UP:
            grid[y-1][x] = weapon
        elif direction == DOWN:
            grid[y+1][x] = weapon
        return grid


class Monster(Unit):
    def __init__(self, img, atk, health):
        super().__init__(img)
        self.reset_val = 30
        self.counter = self.reset_val + random.randint(-5, 5)
        self.attack = atk
        self.health = health

    def update(self, grid, info, x, y, player, dmg):
        open_spaces = [i for i, j in info.items() if j]
        self.counter -= 1
        if self.counter == 0:
            self.counter = self.reset_val + random.randint(-5, 5)
            grid = self.move(grid, open_spaces, x, y)
        return grid

    def move(self, grid, open_spaces, x, y):
        if open_spaces:
            decision = random.randint(0, len(open_spaces))
            if decision == len(open_spaces):
                pass
            elif open_spaces[decision] == LEFT:
                grid[y][x-1] = self
                grid[y][x] = 0
            elif open_spaces[decision] == RIGHT:
                grid[y][x+1] = self
                grid[y][x] = 0
            elif open_spaces[decision] == UP:
                grid[y-1][x] = self
                grid[y][x] = 0
            elif open_spaces[decision] == DOWN:
                grid[y+1][x] = self
                grid[y][x] = 0
        return grid


class Ninja(Monster):
    def __init__(self):
        super().__init__(os.path.join(sprite_folder, 'ninja.png'), 1, 2)


class ThrowNinja(Ninja, Thrower):
    def __init__(self):
        Ninja.__init__(self)
        Thrower.__init__(self, 'heart_weapon')
        self.reset_val = 55
        self.throw_counter = self.reset_val

    def update(self, grid, info, x, y, player, dmg):
        open_spaces = [i for i, j in info.items() if j]
        self.counter -= 1
        self.throw_counter -= 1
        if self.throw_counter == 0:
            self.throw_counter = self.reset_val
            if open_spaces:
                decision = random.randint(0, len(open_spaces) - 1)
                grid = self.throw(grid, open_spaces[decision], x, y)
                open_spaces.remove(open_spaces[decision])
        if self.counter == 0:
            self.counter = self.reset_val + random.randint(-5, 5)
            grid = self.move(grid, open_spaces, x, y)
        return grid


class Boss(Monster):
    def __init__(self):
        super().__init__(os.path.join(sprite_folder, 'boss.png'), 1, 5)


def create_feature(object_type):
    object_list = {
        'ninja': Ninja(),
        'throw_ninja': ThrowNinja(),
        'heart_weapon': Projectile(os.path.join(sprite_folder, 'heart.png'))
    }
    return object_list.get(object_type)


class DamageBar:
    def __init__(self, x, y, direction):
        self.timer = 8
        if direction == UP:
            self.bar = pygame.Rect(x * CHARWIDTH + 8, y * CHARHEIGHT - 2, 24, 6)
        elif direction == RIGHT:
            self.bar = pygame.Rect((x+1) * CHARWIDTH - 4, y * CHARHEIGHT + 8, 6, 24)
        elif direction == LEFT:
            self.bar = pygame.Rect(x * CHARWIDTH - 4, y * CHARHEIGHT + 8, 6, 24)
        else:
            self.bar = pygame.Rect(x * CHARWIDTH + 8, (y+1) * CHARHEIGHT - 1, 24, 6)

    def draw(self):
        self.timer -= 1
        pygame.draw.rect(DISPLAYSURF, RED, self.bar)


class DamageManager:
    def __init__(self):
        self.bars = []

    def add_bar(self, x, y, direction):
        self.bars.append(DamageBar(x, y, direction))

    def remove_bars(self):
        to_remove = []
        for i in self.bars:
            if i.timer == 0:
                to_remove.append(i)

        for i in to_remove:
            self.bars.remove(i)

    def draw(self):
        for i in self.bars:
            i.draw()
        self.remove_bars()


def terminate():
    pygame.quit()
    sys.exit()


# Background grids
# 0: grass, 1: lava
all_grass_grid = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

all_grass = Background(all_grass_grid)

all_lava_grid = [[1] * 16] * 12
all_lava = Background(all_lava_grid)

# all_grass = [[0] * 16] * 12

# Foregrounds
# 0: None, 1: rock, 2: tree
rm1_grid = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 1],
            [1, 0, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 2, 1, 0, 1],
            [1, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

rm1_ft = [['ninja', 11, 5], ['throw_ninja', 1, 9]]

rm2_grid = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 2, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 1],
            [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [1, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 2, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

rm2_ft = [['ninja', 2, 3], ['ninja', 6, 10], ['ninja', 13, 5]]

rm3_grid = [[3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3],
            [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
            [3, 3, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 3],
            [3, 3, 0, 0, 3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
            [3, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
            [3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]]


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load(os.path.join(sprite_folder, 'gameicon.png')))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Cloud Empire')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    while True:
        run_game()


def run_game():
    game_over_mode = False
    win_mode = False

    game_over_surf = BASICFONT.render('You lose.', True, BLACK)
    game_over_rect = game_over_surf.get_rect()
    game_over_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf = BASICFONT.render('Victory!', True, WHITE)
    win_rect = win_surf.get_rect()
    win_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    # Rooms

    room1 = Room(all_grass, Foreground(rm1_grid, rm1_ft))
    room2 = Room(all_grass, Foreground(rm2_grid, rm2_ft))
    room3 = Room(all_lava, Foreground(rm3_grid, rm2_ft))

    # World Map

    world = [[room1, room2, room3]]

    char = PlayerCharacter()

    world_map = WorldMap(world)

    room = world_map.get_room()

    room.place_player(2, 3, char)

    while True:
        DISPLAYSURF.fill(BLACK)

        room.draw()
        if game_over_mode:
            DISPLAYSURF.blit(game_over_surf, game_over_rect)
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        terminate()
                    elif event.key == K_r:
                        return
        elif win_mode:
            DISPLAYSURF.blit(win_surf, win_rect)
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()
                elif event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        terminate()
                    elif event.key == K_r:
                        return
        else:
            for event in pygame.event.get():
                if event.type == QUIT:
                    terminate()

                elif event.type == KEYDOWN:
                    if event.key == K_LEFT:
                        if room.char_x - 1 < LEFT_BOUND:
                            stored_y = room.char_y
                            room.fg.set_empty(room.char_x, room.char_y)
                            room = world_map.move_left()
                            room.place_player(RIGHT_BOUND, stored_y, char)
                        else:
                            room.char_move(LEFT)
                    elif event.key == K_RIGHT:
                        if room.char_x + 1 > RIGHT_BOUND:
                            stored_y = room.char_y
                            room.fg.set_empty(room.char_x, room.char_y)
                            room = world_map.move_right()
                            room.place_player(LEFT_BOUND, stored_y, char)
                        else:
                            room.char_move(RIGHT)
                    elif event.key == K_UP:
                        if room.char_y - 1 < UP_BOUND:
                            stored_x = room.char_x
                            room.fg.set_empty(room.char_x, room.char_y)
                            room = world_map.move_up()
                            room.place_player(stored_x, LOW_BOUND, char)
                        else:
                            room.char_move(UP)
                    elif event.key == K_DOWN:
                        if room.char_y + 1 > LOW_BOUND:
                            stored_x = room.char_x
                            room.fg.set_empty(room.char_x, room.char_y)
                            room = world_map.move_down()
                            room.place_player(stored_x, UP_BOUND, char)
                        else:
                            room.char_move(DOWN)
                    elif event.key == K_a:
                        room.char_atk(LEFT)
                    elif event.key == K_s:
                        room.char_atk(DOWN)
                    elif event.key == K_w:
                        room.char_atk(UP)
                    elif event.key == K_d:
                        room.char_atk(RIGHT)
                    elif event.key == K_ESCAPE:
                        terminate()

            room.update()
            if room.game_over():
                game_over_mode = True

        pygame.display.update()
        FPSCLOCK.tick(FPS)


if __name__ == "__main__":
    main()
