# -> imports
from pygame.locals import *
import numpy
import network
import sensor
import pygame
import random
import math

pygame.init()

def clamp(x, lower, upper):
    if x > upper:
        return upper
    if x < lower:
        return lower
    return x


def buildNetwork(rayCount):
    # -> modular network creation
    _network = network.Network()
    _network.add(network.Dense(rayCount, int(rayCount * 0.8)))
    _network.add(network.Dense(int(rayCount * 0.8), int(rayCount * 0.5)))
    _network.add(network.ActivationLayer(network.sigmoid))
    _network.add(network.Dense(int(rayCount * 0.5), 2))
    _network.add(network.ActivationLayer(network.sigmoid))
    return _network

# -> base bot class
class Bot:
    def __init__(self, x, y):
        # -> basic setup
        self.pos = pygame.math.Vector2(x, y)
        self.speed = 0
        self.topSpeed = 2
        self.dead = False
        self.maxAcceleration = 2
        self.colour = (255, 255, 255)
        self.radius = 10
        self.rect = pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
        self.angle = 0 # -> degrees
        self.rays = []
        self.selected = False
        self.rayIntersects = []

        # -> building the network
        self.network = buildNetwork(10)
    
    # -> basic bot render
    def draw(self, screen):
        pygame.draw.circle(screen, self.colour, self.pos, self.radius)
        if self.selected:pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)
    
    # -> brain of the bot
    def effector(self, stimulus): # -> in this case the stimulus is the rayIntersects
        anglularChange, speedChange = self.network.predict([numpy.array(stimulus)])[0]
        self.angle += -0.5 * self.fov + self.fov * anglularChange
        self.speed += -0.5 * self.maxAcceleration + self.maxAcceleration * speedChange
        self.speed = clamp(self.speed, 0, self.topSpeed)

    # -> optional raycasting render
    def drawRays(self, screen):
        for ray in self.rays:
            pygame.draw.line(screen, ray[1], self.pos, ray[0])
    
    # -> allows spectator to take control of a bot
    def remoteControl(self):
        key = pygame.key.get_pressed()
        if key[K_a]:
            self.angle += 1
        if key[K_d]:
            self.angle -= 1
        if key[K_w]:
            self.speed = self.topSpeed
        elif not key[K_w]:
            self.speed = 0
    
    def update(self, tiles, creatures):
        self.rays, self.rayIntersects = self.sensor.rayCast(tiles + creatures)
        if self.selected:
            self.remoteControl()
        else:
            self.effector(self.rayIntersects)

        # -> handling x movment
        xMovement = -math.sin(math.radians(self.angle)) * self.speed
        self.pos.x += xMovement
        self.rect.center = self.pos
        for tile in tiles:
            if tile.colliderect(self.rect):
                if xMovement < 0:
                    self.rect.left = tile.right
                else:
                    self.rect.right = tile.left
        self.pos = pygame.math.Vector2(self.rect.center)
        
        # -> handling y movement
        yMovement = - math.cos(math.radians(self.angle)) * self.speed
        self.pos.y += yMovement
        self.rect.center = self.pos
        for tile in tiles:
            if tile.colliderect(self.rect):
                if yMovement < 0:
                    self.rect.top = tile.bottom
                else:
                    self.rect.bottom = tile.top
        self.pos = pygame.math.Vector2(self.rect.center)

        self.rect.center = self.pos


class Hider(Bot):
    def __init__(self, x, y):
        self.fov = 360
        super().__init__(x, y)
        self.colour = (0, 255, 0)
        self.topSpeed = 4
        self.type = 'HIDER'
        self.sensor = sensor.Sensor(self, self.fov, 50, 10)

class Seeker(Bot):
    def __init__(self, x, y):
        self.fov = 60
        super().__init__(x, y)
        self.colour = (255, 0, 0)
        self.fov = 60
        self.topSpeed = 5
        self.type = 'SEEKER'
        self.sensor = sensor.Sensor(self, self.fov, 100, 10)
