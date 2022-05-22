# -> imports
import bots
import pygame
import math

pygame.init()

# -> sensor class to allow bots's to percept surroundings
class Sensor:
    def __init__(self, bot, fov, rayLength, rayCount):
        self.bot = bot
        self.fov = fov
        self.rayLength = rayLength
        self.rayCount = rayCount
        self.clearColour = (0, 255, 0)
        self.hitColour = (255, 0, 0)
    
    def rayCast(self, colliders=[]):
        '''
        self.bot.rays = [(
            self.bot.pos.x - math.sin(math.radians(self.bot.angle + (- self.fov / 2) + self.fov * (ray / self.rayCount))) * self.rayLength,
            self.bot.pos.y - math.cos(math.radians(self.bot.angle + (- self.fov / 2) + self.fov * (ray / self.rayCount))) * self.rayLength
        ) for ray in range(1, self.rayCount + 1)]
        '''
        # -> verbose version for when intersections need to be implemented
        rays = []
        rayIntersects = []
        for ray in range(1, self.rayCount + 1):
            angle = self.bot.angle + (- self.fov / 2) + self.fov * (ray / self.rayCount)
            radians = math.radians(angle)
            for dist in range(0, self.rayLength, 2): # -> we use a step for optimization
                pos = (self.bot.pos.x - math.sin(radians) * dist,
                       self.bot.pos.y - math.cos(radians) * dist)
                hit = False
                for collider in colliders:
                    if isinstance(collider, bots.Bot):
                        bot = collider
                        collider = collider.rect
                        if bot.type == self.bot.type:
                            continue
                    if collider.collidepoint(pos):
                        hit = True
                        rays.append((pos, self.hitColour))
                        rayIntersects.append(1 - dist / self.rayLength)
                        break
                if hit:
                    break
            if not hit:
                rays.append((pos, self.clearColour))
                rayIntersects.append(0)

        rayIntersects.reverse()
        return rays, rayIntersects