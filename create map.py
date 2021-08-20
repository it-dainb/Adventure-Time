import pygame
import sys
import os
from pygame.locals import *

# Function MapTool ------------------------------------------------------------------------------------------------------------------ #
database = {} # ID: [img_loaded, img_name, type] type can be obj, tile, entity
game_map = {}

def generate_chunk(x, y): # Chunk = tile*tile | x, y is pos chunk
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos # Pos tile not pixel
            target_y = y * CHUNK_SIZE + y_pos
            chunk_data.append([target_x, target_y])
    return chunk_data

def create_database():
    tile_path = 'data/tiles'
    object_path = 'data/object'
    entity_path = 'data/entity'
    ID = 1
    for tiles in os.listdir(tile_path):
        img = pygame.image.load(tile_path + '/' + tiles)
        img.set_colorkey([0, 0, 0])
        database[ID] = [img, tiles[:-4], 'tile']
        ID += 1
    for obj in os.listdir(object_path):
        img = pygame.image.load(object_path + '/' + obj)
        img.set_colorkey([0, 0, 0])
        database[ID] = [img, obj[:-4], 'object']
        ID += 1
    for entity in os.listdir(entity_path):
        img = pygame.image.load(entity_path + '/' + entity)
        img.set_colorkey([0, 0, 0])
        database[ID] = [img, entity[:-4], 'entity']
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
map_size = [16 * 100, 16 * 100]

tile = pygame.Surface([16 * 8 - 6, 16 * 20])
map = pygame.Surface(map_size)

# Setting game ------------------------------------------------------------------------------------------------------------------ #

row, col = 0, 0
max_row, max_col = 16*7, 0
ID = 1

scroll = 0
camera = [0, 0]

CHUNK_SIZE = 8
IMG_SIZE = [16, 16]
SCALE = 1

tile_rects = []

spacing = 5
select = False
click = False
remove = False
num_tile = 0

test = []
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

        obj = database[ID][0]
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
                ID_select = num_tile + 1
                mouse_img = database[rect[1]][0]
                select = True
        if select:
            if ID_select == num_tile + 1:
                pygame.draw.rect(tile, [255, 0, 0], rect[0], 1) # Edge slected item
        num_tile += 1
    
    # Map Area UI ------------------------------------------------------------------------------------------------------------------ #
    map_area = pygame.Rect([WINDOWN_SIZE[0] / 5, 0, map_size[0], map_size[1]])
    font = pygame.font.SysFont('consolas', 20)
    text_surface = pygame.Surface([WINDOWN_SIZE[0] * 4 / 5, 85], pygame.SRCALPHA)
    edge_ligting = pygame.Surface([WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[0]], pygame.SRCALPHA)
    pygame.draw.rect(edge_ligting, [255,0,0], [0, 0, WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]], 5)
    
    if select:
        text_surface.blit(font.render(f"Name: {database[ID_select][1]}", 0, [255, 255, 255]), [10, 55])
        text_surface.blit(font.render(f"ID: {ID_select} ; Type: {database[ID_select][2]}", 0, [255, 255, 255]), [10, 30])
        if map_area.collidepoint(m_x, m_y):
            in_map = True
            pygame.draw.rect(edge_ligting, [0,255,0], [0, 0, WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]], 5)
            m_x -= tile_size[0]
            text_surface.blit(font.render(f"x, y: {int(m_x / SCALE + camera[0])}, {int(m_y / SCALE + camera[1])}", 0, [255, 255, 255]), [10, 5])
            edge_ligting.blit(mouse_img, [m_x - IMG_SIZE[0] / 2, m_y - IMG_SIZE[1] / 2])
        else:
            in_map = False
            text_surface.blit(font.render(f"x, y: 0, 0", 0, [255, 255, 255]), [10, 5])               
    else:
        if map_area.collidepoint(m_x, m_y):
            in_map = True
            pygame.draw.rect(edge_ligting, [0,255,0], [0, 0, WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]], 5)
            text_surface.blit(font.render(f"x, y: {int((m_x - tile_size[0]) / SCALE + camera[0])}, {int(m_y / SCALE + camera[1])}", 0, [255, 255, 255]), [10, 5])
        else:
            in_map = False
            text_surface.blit(font.render(f"x, y: 0, 0", 0, [255, 255, 255]), [10, 5])
    
    # Map Zoom ------------------------------------------------------------------------------------------------------------------ #
    display = pygame.Surface([WINDOWN_SIZE[0] * 4 / 5 / SCALE, WINDOWN_SIZE[0] / SCALE])
    
    # Map Area chunk ------------------------------------------------------------------------------------------------------------------ #
    blocks = []
    if select:
        for y in range(int(round(WINDOWN_SIZE[1] / (SCALE * CHUNK_SIZE * IMG_SIZE[1]))) + 2):
           for x in range(int(round((WINDOWN_SIZE[0] * 4 / 5 )/ (SCALE * CHUNK_SIZE * IMG_SIZE[0])) + 2)):
                target_x = x - 1 + int(round(camera[0] / (CHUNK_SIZE * IMG_SIZE[0])))
                target_y = y - 1 + int(round(camera[1] / (CHUNK_SIZE * IMG_SIZE[1])))
                target_chunk = str(target_x) + ';' + str(target_y)
                if 'air' not in game_map:
                    game_map['air'] = {}
                if target_chunk not in game_map['air']:
                    game_map['air'][target_chunk] = generate_chunk(target_x, target_y)
                for data in game_map['air'][target_chunk]:
                    data_rect = pygame.Rect([data[0] * 16 - camera[0], data[1] * 16 - camera[1], 16, 16])#IMG_SIZE[0], IMG_SIZE[1]])
                    blocks.append(data_rect)
    
    if remove:
        color = [255, 0, 0]
    else:
        color = [0, 255, 0]
    for block in blocks:
        if in_map: 
            if block.collidepoint(m_x / SCALE, m_y / SCALE):
                    #display.blit(database[ID_select][0], [block.x, block.y])
                pygame.draw.rect(display, color, block, 1)
                # camera[0] = int(m_x - camera[0] - WINDOWN_SIZE[0] / 2)
                # camera[1] = int(m_y - camera[1] - WINDOWN_SIZE[1] * 4 / 5 / 2)
                if click:
                    test.append([[(m_x / SCALE + camera[0] ) // 16 * 16, (m_y / SCALE + camera[1]) // 16 * 16], ID_select])
                if remove:
                    for a in test:
                        if [(m_x / SCALE + camera[0] ) // 16 * 16, (m_y / SCALE + camera[1]) // 16 * 16] in a:
                            test.remove(a)


    
    for tet in test:
        display.blit(database[tet[1]][0], [tet[0][0] - camera[0], tet[0][1] - camera[1]])
        pass
        
    
    # Reset status ------------------------------------------------------------------------------------------------------------------ #
    tile_rects = []
    ID = 1
    row, col = 0, 0
    num_tile = 0
    click = False
    remove = False
    
    # Update keys ------------------------------------------------------------------------------------------------------------------ #    
    prev_scroll = scroll
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == MOUSEWHEEL:
            scroll -= event.y * 20
            if scroll <= 0:
                scroll = 0
        if event.type == VIDEORESIZE:
            WINDOWN_SIZE = [event.w, event.h]
            tile_size = [int(WINDOWN_SIZE[0] / 5), int(WINDOWN_SIZE[1])]

        if event.type == KEYDOWN:
            if event.key == K_q:
                SCALE -= 1
                if SCALE <= 0:
                    SCALE = 1
            if event.key == K_e:
                SCALE += 1
        
    keys = pygame.key.get_pressed()
    if keys[K_w]:
        camera[1] -= 16
    if keys[K_a]:
        camera[0] -= 16
    if keys[K_s]:
        camera[1] += 16
    if keys[K_d]:
        camera[0] += 16
    
    if pygame.mouse.get_pressed() == (1, 0, 0):
        click = True
    if pygame.mouse.get_pressed() == (0, 0, 1):
        remove = True
    #screen.blit(tile, [0, 0])
    tile_surf = pygame.transform.scale(tile, tile_size)
    map_surf = pygame.transform.scale(display, [int(WINDOWN_SIZE[0] * 4 / 5), WINDOWN_SIZE[0]])
    
    screen.blit(tile_surf, [0, 0])
    screen.blit(map_surf, [WINDOWN_SIZE[0] / 5, 0])
    screen.blit(text_surface, [WINDOWN_SIZE[0] / 5, 0])
    screen.blit(edge_ligting, [WINDOWN_SIZE[0] / 5, 0])
    # pygame.draw.rect(screen, [255, 0, 0], [10, scroll, 30, 30])
    # screen.blit(map, [WINDOWN_SIZE[0] / 5, 0])
    
    # pygame.draw.rect(screen, [255,0,0], display_tile)
    # pygame.draw.rect(screen, [255,255,0], display_map)
    
    # Update Game ------------------------------------------------------------------------------------------------------------------ #
    pygame.display.update()
   # clock.tick(30)

