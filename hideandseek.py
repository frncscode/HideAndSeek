# -> imports
from cgitb import text
from random import randint
from tkinter.tix import Tree
from numpy import tile
import pygame
import bots
import sys

pygame.init()

# -> pygame setup
screen = pygame.display.set_mode((1000, 600))
screenSize = screen.get_size()
pygame.display.set_caption('Hide and Seek Simulation - Francis Lee')
pygame.display.set_icon(pygame.image.load('Assets/icon.png'))

# -> helper function definitions
def genPool(seekerCount, hiderCount, seekerSpawn, hiderSpawn):
    seekers = [bots.Seeker(seekerSpawn[0], seekerSpawn[1]) for _ in range(seekerCount)]
    hiders  = [bots.Hider(hiderSpawn[0], hiderSpawn[1]) for _ in range(hiderCount)]
    return seekers, hiders

def drawBG(screen, tilemap, tilesize):
    screen.fill((147, 147, 147))
    for rowIdx, row in enumerate(tilemap):
        for tileIdx, tile in enumerate(row):
            if tile == 1:
                pygame.draw.rect(screen, (80, 80, 80), (tileIdx * tilesize, rowIdx * tilesize, tilesize, tilesize))

def getFontObject(msg, fontSize=24, colour=(0, 0, 0)):
    # -> pygame wrapper to speed up text creation
    font = pygame.font.SysFont('Consolas', fontSize)
    fontSurface = font.render(msg, True, colour)
    return fontSurface

def generateTiles(tilemap):
    tiles = []
    for row_idx, row in enumerate(tilemap):
        for tile_idx, tile in enumerate(row):
            if tile == 1:
                tiles.append(pygame.Rect(tile_idx * tilesize, row_idx * tilesize, tilesize, tilesize))
    return tiles

# -> game setup
selected = None
creatures = []
hiders = []
seekers = []
stage = 0
tilesize = 20
tilemap = [[0 for _ in range(screenSize[0] // tilesize)] for _ in range(screenSize[1] // tilesize)]
clicked = False

# -> game loop
clock = pygame.time.Clock()
while True:
    # -> event loop
    clicked = False
    mousePos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    selectedTile = (mousePos[0] // tilesize, mousePos[1] // tilesize)

    if keys[pygame.K_SPACE]:
        if stage == 0:
            tiles = generateTiles(tilemap)
            stage += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                clicked = True
                if stage == 3:
                    for creature in creatures:
                        if creature.rect.collidepoint(mousePos):
                            creature.selected = True
                            selected = creature
                            break
                        else:
                            creature.selected = False
                            selected = None
            if event.button == 3:
                tilemap[selectedTile[1]][selectedTile[0]] = 0
    
    # -> update
    for idx, creature in sorted(enumerate(creatures), reverse=True):
        if creature.dead:creatures.pop(idx)
    for idx, hider in sorted(enumerate(hiders), reverse=True):
        if hider.dead:hiders.pop(idx)

    # --> main creature updates
    for creature in creatures:
        creature.update(tiles, creatures)
    
    # --> checking for kills
    if stage == 3:
        for hider in hiders:
            for seeker in seekers:
                if seeker.rect.colliderect(hider.rect):
                    hider.dead = True

    if stage == 0 and clicked:
        tilemap[selectedTile[1]][selectedTile[0]] = 1
    elif stage == 1 and clicked:
        hiderSpawnLoc = (selectedTile[0] * tilesize + tilesize / 2,
                         selectedTile[1] * tilesize + tilesize / 2)
        stage += 1
    elif stage == 2 and clicked:
        seekerSpawnLoc = (selectedTile[0] * tilesize + tilesize / 2,
                         selectedTile[1] * tilesize + tilesize / 2)
        stage += 1
        # -> spawn the creatures
        seekers, hiders = genPool(5, 5, seekerSpawnLoc, hiderSpawnLoc)
        creatures = seekers + hiders

    # -> render
    drawBG(screen, tilemap, tilesize)

    if stage == 3:
        pygame.draw.circle(screen, (238, 255, 5), hiderSpawnLoc, 5)
        pygame.draw.circle(screen, (0, 255, 234), seekerSpawnLoc, 5)
        for creature in creatures:
            creature.draw(screen)
            creature.drawRays(screen)
    if stage == 0:
        textObject = getFontObject("Draw A Map! Press 'Space' When Finished", 32, (200, 200, 200))
        screen.blit(textObject, (screenSize[0] / 2 - textObject.get_width() / 2, 
                                 screenSize[1] / 2 - textObject.get_height() / 2))
    if stage == 1:
        textObject = getFontObject("Select A Hider Spawn Location!", 32, (200, 200, 200))
        screen.blit(textObject, (screenSize[0] / 2 - textObject.get_width() / 2, 
                                 screenSize[1] / 2 - textObject.get_height() / 2))
    if stage == 2:
        textObject = getFontObject("Select A Seeker Spawn Location!", 32, (200, 200, 200))
        screen.blit(textObject, (screenSize[0] / 2 - textObject.get_width() / 2, 
                                 screenSize[1] / 2 - textObject.get_height() / 2))
        pygame.draw.circle(screen, (238, 255, 5), hiderSpawnLoc, 5)
    
    # -> draw selected square indicator
    if stage < 3:
        pygame.draw.rect(screen, (160, 160, 160), (selectedTile[0] * tilesize, selectedTile[1] * tilesize, tilesize, tilesize), 2)
    # -> clean up
    clock.tick(60)
    pygame.display.update()