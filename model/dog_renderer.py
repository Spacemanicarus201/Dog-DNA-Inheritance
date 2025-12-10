import pygame
import math
from model.dog_points import DOG_POINTS

class DogRenderer:
    def __init__(self, traits):
        self.traits = traits
        self.angle = 0

    def draw(self, win):
        # rotate + project 3D → 2D
        self.angle += 0.01

        points = self.traits.apply(DOG_POINTS)

        projected = []
        for x, y, z in points:
            sx = x * math.cos(self.angle) - z * math.sin(self.angle)
            sy = y
            sz = x * math.sin(self.angle) + z * math.cos(self.angle)
            f = 200 / (sz + 400)
            px = int(sx * f + 500)
            py = int(sy * f + 350)
            projected.append((px, py))

        # draw wireframe lines
        for i in range(len(projected) - 1):
            pygame.draw.line(win, (255,255,255), projected[i], projected[i+1], 2)
