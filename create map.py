import pygame
import sys
import os
from pygame.locals import *

# Function MapTool ------------------------------------------------------------------------------------------------------------------ #
database = {} # ID: img_loaded

def create_database():
    tile_path = 'data/tiles'
    object_path = 'data/object'
    entity_path = 'data/entity'
    ID = 1
    for tiles in os.listdir(tile_path):
        img = pygame.image.load(tile_path + '/' + tiles)
        img.set_colorkey([0, 0, 0])
        database[ID] = img
        ID += 1
    for obj in os.listdir(object_path):
        img = pygame.image.load(object_path + '/' + obj)
        img.set_colorkey([0, 0, 0])
        database[ID] = img
        ID += 1
    for entity in os.listdir(entity_path):
        print(ID, entity)
        img = pygame.image.load(entity_path + '/' + entity)
        img.set_colorkey([0, 0, 0])
        database[ID] = img
        ID += 1

# Setting envoroment ------------------------------------------------------------------------------------------------------------------ #
pygame.init()

create_database()

WINDOWN_SIZE = [900, 600]

pygame.display.set_caption('Create MapTool by DAIOTAKU')
screen = pygame.display.set_mode(WINDOWN_SIZE, pygame.RESIZABLE)

tile_size = [int(WINDOWN_SIZE[0] / 5), int(WINDOWN_SIZE[1])]
map_size = [WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]]

tile = pygame.Surface([16 * 8, 16 * 20])

# display_tile = pygame.Rect([0, 0, WINDOWN_SIZE[0] / 5, WINDOWN_SIZE[1]])
# display_map = pygame.Rect([WINDOWN_SIZE[0] / 5, 0, WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]])

    
create_database()
# Setting game ------------------------------------------------------------------------------------------------------------------ #

row, col = 0, 0
max_row, max_col = 16*7, 0
ID = 1

scroll = 0

tile_rects = []

spacing = 5
# Main game ------------------------------------------------------------------------------------------------------------------ #
while True:
    # Get mouse pos ------------------------------------------------------------------------------------------------------------------ #
    m_x, m_y = pygame.mouse.get_pos()
    m_x /= tile_size[0] / tile.get_width()
    m_y /= tile_size[1] / tile.get_height()

    screen.fill([0,0,0])
    
    tile.fill([255, 255, 255])
    
    num = 2
    num_row = 0
    while ID < len(database) + 1:
        obj = database[ID]
        obj_width = obj.get_width()
        obj_height = obj.get_height()
        if obj_height > max_col:
            max_col = obj_height
        
        row += obj_width
        if row + num * spacing > max_row:
            col += max_col
            max_col = 0
            row = 0
            num = 1
            num_row += 1
        else:
            tile_rects.append(pygame.Rect([row - obj_width + spacing * num , col - scroll + spacing * num_row, obj_width, obj_height]))
            tile.blit(obj, [row - obj_width + spacing * num, col - scroll + spacing * num_row])
            ID += 1
        num += 1

    for rect in tile_rects:
       # pygame.draw.rect(tile, [255, 0, 0], rect, 1)
        if rect.collidepoint([m_x, m_y]):
            pygame.draw.rect(tile, [255, 0, 0], rect, 2)
    
    tile_rects = []
    ID = 1
    row, col = 0, 0




    # Update keys ------------------------------------------------------------------------------------------------------------------ #    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEWHEEL:
            scroll -= event.y * 20
            if scroll < 0:
                scroll = 0
        if event.type == VIDEORESIZE:
            WINDOWN_SIZE = [event.w, event.h]
            tile_size = [int(WINDOWN_SIZE[0] / 5), int(WINDOWN_SIZE[1])]
            map_size = [WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]]
    
    #screen.blit(tile, [0, 0])
    tile_surf = pygame.transform.scale(tile, tile_size)
    
    screen.blit(tile_surf, [0, 0])
    
    # pygame.draw.rect(screen, [255, 0, 0], [10, scroll, 30, 30])
    # screen.blit(map, [WINDOWN_SIZE[0] / 5, 0])
    
    # pygame.draw.rect(screen, [255,0,0], display_tile)
    # pygame.draw.rect(screen, [255,255,0], display_map)
    
    pygame.display.update()
