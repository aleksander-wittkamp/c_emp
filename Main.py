import random, sys, time, math, pygame
from pygame.locals import *

FPS = 30
WINWIDTH = 640
WINHEIGHT = 480
HALF_WINWIDTH = int(WINWIDTH / 2)
HALF_WINHEIGHT = int(WINHEIGHT / 2)
# Screen is 16 wide by 12 high
CHARWIDTH = 40
CHARHEIGHT = 40

UP_BOUND = 0
LOW_BOUND = 11
RIGHT_BOUND = 15
LEFT_BOUND = 0

GRASSCOLOR = (19, 127, 40)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

MOVERATE = 9
STARTSIZE = 40
WINSIZE = 300

LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'

board1 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1],
          [0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 0],
          [0, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 2, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

board2 = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0, 1, 0],
          [0, 1, 1, 2, 1, 1, 1, 1, 1, 2, 2, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 0],
          [0, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 1, 1, 0],
          [0, 1, 2, 1, 1, 1, 0, 0, 1, 1, 1, 2, 1, 1, 1, 0],
          [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
          [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

object1 = [['ninja', 11, 5]]

object2 = [['ninja', 2, 3], ['ninja', 6, 10], ['ninja', 13, 5]]

board_board = [[board1, board2]]
object_board = [[object1, object2]]


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    pygame.display.set_icon(pygame.image.load('gameicon.png'))
    DISPLAYSURF = pygame.display.set_mode((WINWIDTH, WINHEIGHT))
    pygame.display.set_caption('Cloud Empire')
    BASICFONT = pygame.font.Font('freesansbold.ttf', 32)

    while True:
        run_game()


def run_game():
    game_over_mode = False
    win_mode = False

    game_over_surf = BASICFONT.render('Game Over', True, WHITE)
    game_over_rect = game_over_surf.get_rect()
    game_over_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf = BASICFONT.render('Victory!', True, WHITE)
    win_rect = win_surf.get_rect()
    win_rect.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    win_surf2 = BASICFONT.render('(Press "r" to restart.)', True, WHITE)
    win_rect2 = win_surf2.get_rect()
    win_rect2.center = (HALF_WINWIDTH, HALF_WINHEIGHT)

    char = PlayerCharacter(1, 1)

    world_map = WorldMap(0, 0, board_board, object_board)

    room = world_map.get_room()

    while True:
        DISPLAYSURF.fill(GRASSCOLOR)

        room.draw()
        char.draw()

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                if event.key in (K_LEFT, K_a):
                    if char.x - 1 < LEFT_BOUND:
                        char.x = RIGHT_BOUND
                        room = world_map.move_left()
                    elif room.allow_move(char.x - 1, char.y):
                        char.move_left()
                elif event.key in (K_RIGHT, K_d):
                    if char.x + 1 > RIGHT_BOUND:
                        char.x = LEFT_BOUND
                        room = world_map.move_right()
                    elif room.allow_move(char.x + 1, char.y):
                        char.move_right()
                elif event.key in (K_UP, K_w) and room.allow_move(char.x, char.y - 1):
                    if char.y - 1 < UP_BOUND:
                        char.y = LOW_BOUND
                        room = world_map.move_up()
                    elif room.allow_move(char.x, char.y - 1):
                        char.move_up()
                elif event.key in (K_DOWN, K_s) and room.allow_move(char.x, char.y + 1):
                    if char.y + 1 > LOW_BOUND:
                        char.y = UP_BOUND
                        room = world_map.move_down()
                    elif room.allow_move(char.x, char.y + 1):
                        char.move_down()

                elif event.key == K_ESCAPE:
                    terminate()

        room.update()

        pygame.display.update()
        FPSCLOCK.tick(FPS)


class WorldMap:
    def __init__(self, x, y, world_map, objects):
        self.x = x
        self.y = y
        self.world_map = world_map
        self.object_map = objects

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
        return Room(self.world_map[self.y][self.x],
                    self.object_map[self.y][self.x])


class Room:
    rock = pygame.transform.scale(pygame.image.load('rock.png'), (CHARWIDTH, CHARHEIGHT))
    grass = pygame.transform.scale(pygame.image.load('grass.png'), (CHARWIDTH, CHARHEIGHT))
    tree = pygame.transform.scale(pygame.image.load('tree.png'), (CHARWIDTH, CHARHEIGHT))
    board_key = {0: rock, 1: grass, 2: tree}

    def __init__(self, board, objects):
        self.objects = []
        for i in objects:
            self.objects.append(create_object(i))
        self.board = board

    def draw(self):
        for i in range(16):
            for j in range(12):
                space_rect = pygame.Rect((i * CHARWIDTH,
                                          j * CHARHEIGHT,
                                          CHARWIDTH, CHARHEIGHT))
                DISPLAYSURF.blit(self.board_key[self.board[j][i]], space_rect)

        for i in self.objects:
            i.draw()

    def update(self):
        for i in self.objects:
            x = i.x
            y = i.y
            allowables = {LEFT: x > LEFT_BOUND and self.allow_move(x - 1, y),
                          RIGHT: x < RIGHT_BOUND and self.allow_move(x + 1, y),
                          UP: y > UP_BOUND and self.allow_move(x, y - 1),
                          DOWN: y < LOW_BOUND and self.allow_move(x, y + 1)}
            i.update(allowables)

    def allow_move(self, x, y):
        return self.board[y][x] == 1


class BoardPiece:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Character(BoardPiece):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = None

    def draw(self):
        char_rect = pygame.Rect((self.x * CHARWIDTH,
                                 self.y * CHARHEIGHT,
                                 CHARWIDTH, CHARHEIGHT))
        DISPLAYSURF.blit(self.image, char_rect)

    def move_left(self):
        self.x -= 1

    def move_right(self):
        self.x += 1

    def move_up(self):
        self.y -= 1

    def move_down(self):
        self.y += 1


class PlayerCharacter(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('base_char.png')
        self.image = pygame.transform.scale(self.image, (CHARWIDTH, CHARHEIGHT))


class Monster(Character):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.reset_val = 30
        self.counter = self.reset_val

    def update(self, allowables):
        self.counter -= 1
        if self.counter == 0:
            self.counter = self.reset_val
            self.move(allowables)

    def move(self, allowables):
        decision = random.randint(0, 3)
        if decision == 0 and allowables[LEFT]:
            self.move_left()
        elif decision == 1 and allowables[RIGHT]:
            self.move_right()
        elif decision == 2 and allowables[UP]:
            self.move_up()
        elif decision == 3 and allowables[DOWN]:
            self.move_down()


class Ninja(Monster):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load('ninja.png')
        self.image = pygame.transform.scale(self.image, (CHARWIDTH, CHARHEIGHT))


def create_object(info):
    object_type = info[0]
    x = info[1]
    y = info[2]

    if object_type == 'ninja':
        return Ninja(x, y)


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
