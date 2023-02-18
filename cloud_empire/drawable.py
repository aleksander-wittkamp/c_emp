import pygame
from pygame.locals import DISPLAYSURF
from cloud_empire.config import CHARWIDTH, CHARHEIGHT, SPRITE_FOLDER

class Drawable:
    def __init__(self, img):
        self.image = pygame.transform.scale(pygame.image.load(img), (CHARWIDTH, CHARHEIGHT))

    def draw(self, x, y):
        rect = pygame.Rect((x * CHARWIDTH, y * CHARHEIGHT, CHARWIDTH, CHARHEIGHT))
        DISPLAYSURF.blit(self.image, rect)

