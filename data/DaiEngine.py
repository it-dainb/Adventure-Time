import pygame
import os
import random
import json
from pygame.locals import *

#  Setting enviroment ------------------------------------------------------------------------------------------------------------------ #
FPS = 30

img_FPS = 12
FPS = FPS // img_FPS * img_FPS

# Create database ------------------------------------------------------------------------------------------------------------------ #
database = {} # ID: [img_loaded, img_name, type] type can be obj, tile, entity
def create_database():
    global database
    
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
    return database

# Load Map ------------------------------------------------------------------------------------------------------------------ #
game_map = {'tile': {}, # {'0;0': [[[pos_x, pos_y], ID] * n]}
            'object': [], # [[[pos_x, pos_y], ID] * n]
            'entity': [] # [[[pos_x, pos_y], ID] * n]
                        }
def load_map(name):
    global game_map
    
    f = open('data/map/' + name + '.json', 'r')
    game_map = json.load(f)
    return game_map

def map_render(surface, scroll):
    global tile_rects
    
    tile_rects = [] # Must clear else lag :<
    for a in game_map:
        if a == 'tile':
            for b in game_map[a]:
                for data in game_map[a][b]:
                    LOC_CHUNK = str(data[0][0]) + ';' + str(data[0][1])
                    pos_x = data[0][0]
                    pos_y = data[0][1]
                    ID_im = data[1]
                    img = database[ID_im][0]
                    data_width = database[ID_im][0].get_width()
                    data_height = database[ID_im][0].get_height()
                    block_rect = pygame.Rect(pos_x, pos_y, data_width, data_height)
                    surface.blit(img, [pos_x - scroll[0], pos_y - scroll[1]])
                    if ID_im not in [1,2,3,23,37,50,55,56,57,58]:
                        tile_rects.append(block_rect)

# Create map ------------------------------------------------------------------------------------------------------------------ #
tile_index = {}
def load_tiles():
    tile_path = 'data/tiles'
    ID = 1
    for tile in os.listdir(tile_path):
        tile_image = pygame.image.load(tile_path + '/' + tile)
        tile_image.set_colorkey([0, 0, 0])
        tile_index[ID] = tile_image
        ID += 1
    return tile_index

# Creat Chunk ------------------------------------------------------------------------------------------------------------------ #
def generate_chunk(x, y, CHUNK_SIZE): # Chunk = tile*tile
    chunk_data = []
    for y_pos in range(CHUNK_SIZE):
        for x_pos in range(CHUNK_SIZE):
            target_x = x * CHUNK_SIZE + x_pos # Pos tile not pixel
            target_y = y * CHUNK_SIZE + y_pos
            tile_type = 0
            if target_y > 10:
                tile_type = 45 # Dirt
            elif target_y == 10:
                tile_type = 53 # Grass
            elif target_y == 9:
                if random.randint(1,5) == 1:
                    tile_type = 50 # Plant
            if tile_type !=  0:
                chunk_data.append([[target_x*16, target_y*16], tile_type]) # tile = 16*16
    return chunk_data
    pass

# Render tiles in chunk ------------------------------------------------------------------------------------------------------------------ #
#game_map = {} # { '1;1' : [[[x, y], tile_type] * 64], .... }
def chunk_render(surface, WINDOWN_SIZE, SCALE, CHUNK_SIZE, IMG_SIZE, scroll):
    global tile_rects
    
    # take loc of chunk
    tile_rects = []
    for y in range(int(round(WINDOWN_SIZE[1] / (SCALE * CHUNK_SIZE * IMG_SIZE[1]))) + 1):
       for x in range(int(round(WINDOWN_SIZE[0] / (SCALE * CHUNK_SIZE * IMG_SIZE[0])) + 2)):
            target_x = x - 1 + int(round(scroll[0] / (CHUNK_SIZE * IMG_SIZE[0])))
            target_y = y + int(round(scroll[1] / (CHUNK_SIZE * IMG_SIZE[1])))
            target_chunk = str(target_x) + ';' + str(target_y)
            if target_chunk not in game_map:
                game_map[target_chunk] = generate_chunk(target_x, target_y, CHUNK_SIZE)
            for tile in game_map[target_chunk]:
                if tile[1] == 50: # 62
                    surface.blit(tile_index[tile[1]], (tile[0][0] - scroll[0], tile[0][1] + 8 - scroll[1]))
                else:
                    surface.blit(tile_index[tile[1]], (tile[0][0] - scroll[0], tile[0][1] - scroll[1]))
                if tile[1] not in [1, 2, 3, 23, 24, 50, 55, 56, 59, 60]: # [47,50]
                    tile_rects.append(pygame.Rect(tile[0][0], tile[0][1], 16, 16))        

# PHYSIC ------------------------------------------------------------------------------------------------------------------ #
def collide_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile):
            hit_list.append(tile)
    return hit_list
    
def move(rect, movement):
    collision_type = {'top': False, 'bottom': False, 'right': False, 'left': False}
    
    # Update location x ---------------------------------------------------------------------------------------------------- #
    rect.x += movement[0]
    hit_list = collide_test(rect, tile_rects)
    for tile in hit_list:
        if movement[0] > 0:
            collision_type['right'] = True
            rect.right = tile.left
        elif movement[0] < 0:
            collision_type['left'] = True
            rect.left = tile.right
            
    # Update location y ------------------------------------------------------------------------------------------------------------------ #
    rect.y += movement[1]
    hit_list = collide_test(rect, tile_rects)
    for tile in hit_list:
        if movement[1] >= 0:
            collision_type['bottom'] = True
            rect.bottom = tile.top
        elif movement[1] < 0:
            collision_type['top'] = True
            rect.top = tile.bottom
    
    return rect, collision_type
    
# Text 2 image ------------------------------------------------------------------------------------------------------------------ #
def text_draw(surface, text, size, pos, scroll = [0,0],draw = True,bug = False):
    
    char_img = pygame.image.load('data/font/h.png')
    img_size = [char_img.get_width(), char_img.get_height()]
    spacing = int(img_size[0] / 7)
    num = 0
    text_size = [0, 0]
    phay = 0

    text_size[0] = (img_size[0] + spacing) * (len(text)) - spacing
    text_size[1] = img_size[1]
    if not bug:
        text_sur = pygame.Surface([text_size[0], text_size[1]], pygame.SRCALPHA)
    else:
        text_sur = pygame.Surface([text_size[0], text_size[1]])
    for char in text:
        if num == text[len(text) - 1]:
            text_size[0] -= spacing * size
            spacing = 0
            pass
        if char != ' ':
            if char == '?':
                path = 'data/font/' + 'question' + '.png'
            elif char == '|':
                path = 'data/font/' + 'gach' + '.png'
            elif char == '#':
                path = 'data/font/' + 'thang' + '.png'
            elif char == ':':
                path = 'data/font/' + 'hai_cham' + '.png'
            elif char == '*':
                path = 'data/font/' + 'sao' + '.png'
            elif char == '<':
                path = 'data/font/' + 'be' + '.png'
            elif char == '>':
                path = 'data/font/' + 'lon' + '.png'
            elif char == '/':
                path = 'data/font/' + 'gach_ngang' + '.png'
            else:
                path = 'data/font/' + char + '.png'
            if draw:
                char_img = pygame.image.load(path).convert()
                char_img.set_colorkey([0, 0, 0])
                text_sur.blit(char_img, [(img_size[0] + spacing) * num, 0])
        num += 1
    display = [int(text_size[0] / 2 * size), int(text_size[1] / 2 * size)]
    n_surf = pygame.transform.scale(text_sur, display)
    text_rect = pygame.Rect([pos[0], pos[1], n_surf.get_width(), n_surf.get_height()])
    surface.blit(n_surf, [pos[0] - scroll[0], pos[1] - scroll[1]])
    return text_rect

# Animation load ------------------------------------------------------------------------------------------------------------------ #
animation_path = 'data/animation'
animation_dir = os.listdir(animation_path)
global animation_database
animation_database = {} #{ 'ID': [loc _img *60], ..... } . ID is filename + status. ec=x: ID: coin_idle


class animation(object):
    global animation_database, FPS, img_FPS

    def __init__(self):
        pass
    
    def create_database(self):
        for entity in animation_dir:
            entity_animation = os.listdir(animation_path + '/' + entity)
            if entity_animation[0][- 4:] == '.png':
                animation_database[entity] = []
                #while len(animation_database[entity]) < len(entity_animation)* int(FPS//img_FPS):
                for frame in entity_animation:
                    for _ in range(int(FPS//img_FPS)):
                        animation_database[entity].append(animation_path + '/' + entity + '/' + frame)
                        #print(frame)
                            # if len(animation_database[entity]) < len(entity_animation)* int(FPS/img_FPS):
                                # animation_database[entity].append(animation_path + '/' + entity + '/' + frame)
                            # else:
                                # break
                #print(entity, len(animation_database[entity]))
            else:
                for frame in entity_animation:
                    entity_frame = os.listdir(animation_path + '/' + entity + '/' + frame) 
                    if entity_frame[0][-4:] == '.png':
                        animation_database[frame] = []
                        for more_frame in entity_frame:
                            for _ in range(int(FPS//img_FPS)):
                                animation_database[frame].append(animation_path + '/' + entity + '/' + frame + '/' + more_frame)
                                    #print(more_frame)
                                    # if len(animation_database[frame]) < len(entity_frame)* int(FPS/img_FPS):
                                        # animation_database[frame].append(animation_path + '/' + entity + '/' + frame + '/' + more_frame)
                                    # else:
                                        # break
                            #print(more_frame, len(entity_frame))
                            #print(frame, len(animation_database[frame]))
                    else:
                        for more_frame in entity_frame:
                            entity_status = os.listdir(animation_path + '/' + entity + '/' + frame + '/' + more_frame)
                            animation_database[more_frame] = []
                            for frame_status in entity_status:
                                for _ in range(int(FPS//img_FPS)):
                                    animation_database[more_frame].append(animation_path + '/' + entity + '/' + frame + '/' + more_frame + '/' + frame_status)
                            
                    
    def load_animation(self, surface, ID_anim, frame, pos, flip = False, draw = True):
        ID_anim = str(ID_anim)
        frame_path = animation_database[ID_anim][frame]
        frame_img = pygame.image.load(frame_path).convert()
        frame_img.set_colorkey([0, 0, 0])
        if draw:
            surface.blit(pygame.transform.flip(frame_img, flip, False), pos)
        return frame_img
    
    def change_action(self, entity_status, frame, entity_action_new):
        if entity_status != entity_action_new:
            entity_status = entity_action_new
            frame = 0
        return entity_status, frame
    
    def get_rect(self, ID_anim, pos):
        ID_anim = str(ID_anim)
        frame_path = animation_database[ID_anim][0]
        frame_img = pygame.image.load(frame_path).convert()
        return pygame.Rect(pos[0], pos[1], frame_img.get_width(), frame_img.get_height())

# Object stuff ------------------------------------------------------------------------------------------------------------------ #
obj_path = 'data/object'
global obj_database
obj_database = [] # {'ID': obj_rect}
class object(object):
    global obj_database
    
    def __init__(self, ID, pos):
        self.frame = 0
        self.status = 'idle'
        self.ID = ID
        self.x = pos[0]
        self.y = pos[1]
        self.pos = pos
        #self.rect = self.get_rect(self.status)
        pass
    
    def create_database(self):
        obj_list = os.listdir(obj_path)
        for obj in obj_list:
            obj_database.append(obj[:len(obj) - 4])
    
    # Load animation ------------------------------------------------------------------------------------------------------------------ #
    def load_animation(self, surface, status, scroll, draw = True):
        
        animation_list = os.listdir(animation_path)
        if self.ID in animation_list:
            check_list = os.listdir(animation_path + '/' + self.ID)
            if check_list[0][-4:] != '.png':
                ID = self.ID + '_' + status
            else:
                ID = self.ID
            if self.frame > len(animation_database[ID]):
                self.frame = 0
            obj_anim = animation()
            self.status, self.frame = obj_anim.change_action(self.status, self.frame, status)
            obj_img = obj_anim.load_animation(surface, ID, self.frame, [self.x - scroll[0], self.y - scroll[1]], draw)
        else:
            self.frame = 0
            ID = self.ID
            obj_img = pygame.image.load(obj_path + '/' + ID + '.png')
            if draw:
                surface.blit(obj_img, [self.x - scroll[0], self.y - scroll[1]])
        #print(ID, self.frame)
        self.frame += 1
        
    def get_rect(self, status):
        animation_list = os.listdir(animation_path)
        if self.ID in animation_list:
            check_list = os.listdir(animation_path + '/' + self.ID)
            if check_list[0][-4:] != '.png':
                ID = self.ID + '_' + status
            else:
                ID = self.ID
            if self.frame > len(animation_database[ID]) - 1:
                self.frame = 0
            obj_img = pygame.image.load(animation_database[str(ID)][self.frame])
            self.rect = pygame.Rect(self.x, self.y, obj_img.get_width(), obj_img.get_height())
        else:
            obj_img = pygame.image.load(obj_path + '/' + self.ID + '.png')
            self.rect = pygame.Rect(self.x, self.y, obj_img.get_width(), obj_img.get_height())
        return self.rect

# Entity stuff ------------------------------------------------------------------------------------------------------------------ #
class entity(object):
    def __init__(self, ID, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.ID = ID
        self.pos = pos
        self.status = 'idle'
        self.frame = 0
        self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.flip = False
        self.img = pygame.image.load(animation_database[self.ID + '_' + self.status][0])
        self.rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
    
    def change_action(self, status):
        if self.status != status:
            self.status = status
            self.frame = 0
    
    def load_animation(self, surface, status, scroll, draw = True):
        ID = self.ID + '_' + status
        if self.frame > len(animation_database[ID]) - 1:
            self.frame = 0
        entity_anim = animation()
        entity_anim.load_animation(surface, ID, self.frame, [self.rect.x - scroll[0], self.rect.y - scroll[1]], self.flip)
        self.frame += 1


    def move(self, movement):
        self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
        
        # Update location x ---------------------------------------------------------------------------------------------------- #
        self.rect.x += movement[0]
        hit_list = collide_test(self.rect, tile_rects)
        for tile in hit_list:
            if movement[0] > 0:
                self.collision['right'] = True
                self.rect.right = tile.left
            elif movement[0] < 0:
                self.collision['left'] = True
                self.rect.left = tile.right
                
        # Update location y ------------------------------------------------------------------------------------------------------------------ #
        self.rect.y += movement[1]
        hit_list = collide_test(self.rect, tile_rects)
        for tile in hit_list:
            if movement[1] >= 0:
                self.collision['bottom'] = True
                self.rect.bottom = tile.top
            elif movement[1] < 0:
                self.collision['top'] = True
                self.rect.top = tile.bottom
            

# obj = object('coin', [0, 0], [0, 0])
# obj.create_database()
# print(obj_database)
anim = animation()
anim.create_database()
# print(len(animation_database['herochar_idle']))