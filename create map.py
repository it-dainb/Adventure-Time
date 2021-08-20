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
clock = pygame.time.Clock()

create_database()

WINDOWN_SIZE = [900, 600]

# Nếu xài SOURCE thì làm ơn để credit :3. Cảm ơn !!!!
pygame.display.set_caption('MapTool by DAIOTAKU')
screen = pygame.display.set_mode(WINDOWN_SIZE, pygame.RESIZABLE)

tile_size = [int(WINDOWN_SIZE[0] / 5), WINDOWN_SIZE[1]]
map_size = [16 * 100, 16 * 100]#[WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]]

tile = pygame.Surface([16 * 8 - 6, 16 * 20])
map = pygame.Surface(map_size)

# display_tile = pygame.Rect([0, 0, WINDOWN_SIZE[0] / 5, WINDOWN_SIZE[1]])
# display_map = pygame.Rect([WINDOWN_SIZE[0] / 5, 0, WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]])

    
create_database()
# Setting game ------------------------------------------------------------------------------------------------------------------ #

row, col = 0, 0
max_row, max_col = 16*7, 0
ID = 1

scroll = 0
camera = [0, 0]

tile_rects = []

spacing = 5
select = False
click = False
num_tile = 0
# Main game ------------------------------------------------------------------------------------------------------------------ #
while True:
    # Reset screen ------------------------------------------------------------------------------------------------------------------ #
    tile.fill([0, 0, 0])
    map.fill([0, 0, 0])
    screen.fill([0,0,0])
    
    # Tile Menu ------------------------------------------------------------------------------------------------------------------ #
    num = 2
    num_row = 2
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
            tile_rects.append([pygame.Rect([row - obj_width + spacing * num , col - scroll + spacing * num_row, obj_width, obj_height]), ID])
            tile.blit(obj, [row - obj_width + spacing * num, col - scroll + spacing * num_row])
            ID += 1
        num += 1
    
    tile_area = pygame.Rect([0, 0, 16 * 8 - 8, tile_size[1]])
    separator = pygame.Rect([0, 0, tile_size[0], tile_size[1]])
    pygame.draw.rect(tile, [255, 0, 0],tile_area, 2)
    
    m_x, m_y = pygame.mouse.get_pos()
    if separator.collidepoint(m_x, m_y):
        m_x /= tile_size[0] / tile.get_width()
        m_y /= tile_size[1] / tile.get_height()
        pygame.draw.rect(tile, [0, 255, 0], tile_area, 2)
    
    # Select Item ------------------------------------------------------------------------------------------------------------------ #
    for rect in tile_rects:
        
        if rect[0].collidepoint([m_x, m_y]):
            if not click :
                pygame.draw.rect(tile, [255, 0, 0], rect[0], 1) # Edge slecting item
            else:
                pygame.draw.rect(tile, [255, 0, 0], rect[0], 1) # Edge slecting item
                ID_select = num_tile
                mouse_img = database[rect[1]]
                select = True
           # tile.blit(mouse_img, [m_x - mouse_img.get_width() / 2, m_y - mouse_img.get_height() / 2])
        if select:
            if ID_select == num_tile:
                pygame.draw.rect(tile, [255, 0, 0], rect[0], 1) # Edge slected item
        num_tile += 1
   
    if select:
        screen.blit(mouse_img, [m_x - mouse_img.get_width() / 2, m_y - mouse_img.get_height() / 2])
    
    # Map Area UI ------------------------------------------------------------------------------------------------------------------ #
    map_area = pygame.Rect([WINDOWN_SIZE[0] / 5, 0, map_size[0], map_size[1]])
    pygame.draw.rect(map, [255,0,0], [0, 0, map_size[0], map_size[1]], 5)
    font = pygame.font.SysFont('consolas', 20)
    
    if select:
        if map_area.collidepoint(m_x, m_y):
            pygame.draw.rect(map, [0,255,0], [0, 0, map_size[0], map_size[1]], 5)
            m_x -= tile_size[0]
            map.blit(mouse_img, [m_x - mouse_img.get_width() / 2, m_y - mouse_img.get_height() / 2])
            map.blit(font.render(f"x, y: {int(m_x)}, {int(m_y)}", 0, [255, 255, 255]), [10, 5])
        else:
            map.blit(font.render(f"x, y: 0, 0", 0, [255, 255, 255]), [10, 5])            
    else:
        if map_area.collidepoint(m_x, m_y):
            pygame.draw.rect(map, [0,255,0], [0, 0, map_size[0], map_size[1]], 5)
            map.blit(font.render(f"x, y: {int(m_x - tile_size[0])}, {int(m_y)}", 0, [255, 255, 255]), [10, 5])
        else:
            map.blit(font.render(f"x, y: 0, 0", 0, [255, 255, 255]), [10, 5])
    
    # Map Area chunk ------------------------------------------------------------------------------------------------------------------ #
    
    
    
    
    # Reset status ------------------------------------------------------------------------------------------------------------------ #
    tile_rects = []
    ID = 1
    row, col = 0, 0
    num_tile = 0
    
    # Update keys ------------------------------------------------------------------------------------------------------------------ #    
    click = False
    prev_scroll = scroll
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
            map = pygame.Surface(map_size)

    if pygame.mouse.get_pressed() == (1, 0, 0):
        click = True
    #screen.blit(tile, [0, 0])
    tile_surf = pygame.transform.scale(tile, tile_size)
    
    screen.blit(tile_surf, [0, 0])
    screen.blit(map, [WINDOWN_SIZE[0] / 5, 0])
    # pygame.draw.rect(screen, [255, 0, 0], [10, scroll, 30, 30])
    # screen.blit(map, [WINDOWN_SIZE[0] / 5, 0])
    
    # pygame.draw.rect(screen, [255,0,0], display_tile)
    # pygame.draw.rect(screen, [255,255,0], display_map)
    
    # Update Game ------------------------------------------------------------------------------------------------------------------ #
    pygame.display.update()
    clock.tick(30)
