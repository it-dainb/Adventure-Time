import pygame
import os
import random
import json
import math
from pygame.locals import *

#  Setting enviroment ------------------------------------------------------------------------------------------------------------------ #
FPS = 30

img_FPS = 12
FPS = FPS // img_FPS * img_FPS

global IMG_SIZE
IMG_SIZE = [16, 16]

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

def map_render(surface, scroll, display_render):
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
                    if block_rect.colliderect(display_render):
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
def chunk_render(surface, WINDOWN_SIZE, SCALE, CHUNK_SIZE, scroll):
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
    
def move(rect, movement, tile_rect):
    collision_type = {'top': False, 'bottom': False, 'right': False, 'left': False}
    
    # Update location x ---------------------------------------------------------------------------------------------------- #
    rect.x += movement[0]
    hit_list = collide_test(rect, tile_rect)
    for tile in hit_list:
        if movement[0] > 0:
            collision_type['right'] = True
            rect.right = tile.left
        elif movement[0] < 0:
            collision_type['left'] = True
            rect.left = tile.right
            
    # Update location y ------------------------------------------------------------------------------------------------------------------ #
    rect.y += movement[1]
    hit_list = collide_test(rect, tile_rect)
    for tile in hit_list:
        if movement[1] >= 0:
            collision_type['bottom'] = True
            rect.bottom = tile.top
        elif movement[1] < 0:
            collision_type['top'] = True
            rect.top = tile.bottom
    
    return rect, collision_type
    
# Text 2 image ------------------------------------------------------------------------------------------------------------------ #
def text_draw(surface, text, size, pos, scroll = [0,0],draw = True, camera = 0, bug = False):
    
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
    if camera == 0:
        surface.blit(n_surf, [pos[0] - scroll[0], pos[1] - scroll[1]])
    else:
        if camera.colliderect(text_rect):
            surface.blit(n_surf, [pos[0] - scroll[0], pos[1] - scroll[1]])
    return text_rect

# UI size ------------------------------------------------------------------------------------------------------------------ #
def UI(img, surface, size, pos, draw = True):
    img_rect = img.get_rect()
    img_sur = pygame.Surface([img_rect.width, img_rect.height], pygame.SRCALPHA)
    img_sur.blit(img, [0, 0])
    sur = pygame.transform.scale(img_sur, [int(img_rect.width * size[0]), int(img_rect.height * size[1])])
    if draw:
        surface.blit(sur, pos)
    img_rect = pygame.Rect([pos[0], pos[1], sur.get_width(), sur.get_height()])
    return img_rect

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
                for frame in entity_animation:
                    for _ in range(int(FPS//img_FPS)):
                        animation_database[entity].append(animation_path + '/' + entity + '/' + frame)
            else:
                for frame in entity_animation:
                    entity_frame = os.listdir(animation_path + '/' + entity + '/' + frame) 
                    if entity_frame[0][-4:] == '.png':
                        animation_database[frame] = []
                        for more_frame in entity_frame:
                            for _ in range(int(FPS//img_FPS)):
                                animation_database[frame].append(animation_path + '/' + entity + '/' + frame + '/' + more_frame)
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
        self.offset = [0, 0]
        self.attack = 0
        self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.time = 0
        self.w_x = 0
        self.w_y = 0
        self.DDDH = [0, 0]
        self.hit_rect = 0
        self.movement = [0, 0]
        self.y_momentum = 0
        self.check = 0
    
    def DDDH(self, w, A, width, height, offset = [0, 0]):
        self.w_x = w[0]
        self.w_y = w[1]
        a_x = A[0]
        a_y = A[1]
        if self.time == 54:
            self.time = 0
        offset_x = a_x * math.cos(self.w_x * self.time + math.pi/2)
        offset_y = a_y * math.cos(self.w_y * self.time)
        hit_box = pygame.Rect([self.x + offset_x + offset[0], self.y + offset_y + offset[1], width, height])
        self.time += 1
    
    def move(self, movement):
        self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.rect =self.get_rect(self.status)
        
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
        self.x = self.rect.x
                
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
        self.y = self.rect.y
    
    def attack_area(self, area, offset = [0,0]):
        attack_x = self.x + offset[0] - area[0]
        attack_y = self.y + offset[1] - area[1]
        attack_width = area[0] * 2 + self.get_rect(self.status).width
        attack_height = area[1] * 2 + self.get_rect(self.status).height
        
        attack_area = pygame.Rect(attack_x, attack_y, attack_width, attack_height)
        return attack_area
    
    def create_database(self):
        obj_list = os.listdir(obj_path)
        for obj in obj_list:
            obj_database.append(obj[:len(obj) - 4])
    
    def change_action(self, status, offset = [0, 0]):
        self.offset = offset
        if self.status != status:
            self.status = status
            self.frame = 0
    
    def one_time(self, status, offset = [0, 0]):
        self.offset = offset
        animation_list = os.listdir(animation_path)
        if self.ID in animation_list:
            check_list = os.listdir(animation_path + '/' + self.ID)
            if check_list[0][-4:] != '.png':
                ID = self.ID + '_' + status
            else:
                ID = self.ID
        else:
            ID = self.ID
        if self.frame == len(animation_database[ID]) - 1:
            self.frame = 0
            return True
    
    
    # Load animation ------------------------------------------------------------------------------------------------------------------ #
    def load_animation(self, surface, status, scroll, draw = True):
        
        animation_list = os.listdir(animation_path)
        if self.ID in animation_list:
            check_list = os.listdir(animation_path + '/' + self.ID)
            if check_list[0][-4:] != '.png':
                ID = self.ID + '_' + status
            else:
                ID = self.ID
            if self.frame > len(animation_database[ID]) - 1:
                self.frame = 0
            obj_anim = animation()
            self.status, self.frame = obj_anim.change_action(self.status, self.frame, status)
            obj_img = obj_anim.load_animation(surface, ID, self.frame, [self.x - scroll[0] + self.offset[0], self.y - scroll[1] + self.offset[1]], draw)
        else:
            self.frame = 0
            ID = self.ID
            obj_img = pygame.image.load(obj_path + '/' + ID + '.png')
            if draw:
                surface.blit(obj_img, [self.x - scroll[0], self.y - scroll[1]])
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
    global IMG_SIZE
    
    def __init__(self, ID, pos):
        self.x = pos[0]
        self.y = pos[1]
        self.offset = [0, 0]
        self.ID = ID
        self.pos = pos
        self.status = 'idle'
        self.frame = 0
        self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
        self.flip = False
        self.img = pygame.image.load(animation_database[self.ID + '_' + self.status][0])
        self.rect = pygame.Rect(self.x + self.offset[0], self.y + self.offset[1], self.img.get_width(), self.img.get_height())
        self.attack = False
        self.movement = [0, 0]
        self.y_momentum = 0
        self.attack_timer = 0
        self.check = 0
        self.health = 100
        self.life = 1
        self.hitbox = self.rect
        self.time = 0
    

    def area(self, width, height, double_height = False):
        vis_x = self.x - width * IMG_SIZE[0]
        vis_y = self.y - IMG_SIZE[1] * height
        vis_width = width * IMG_SIZE[0] * 2 + self.img.get_width()
        if double_height:
            vis_height = IMG_SIZE[1] * height * 2 + self.img.get_height()
        else:
            vis_height = IMG_SIZE[1] * height + self.img.get_height()
        area_rect = pygame.Rect([vis_x, vis_y, vis_width, vis_height])
        return area_rect
    
    def change_action(self, status):
        if self.status != status:
            self.status = status
            self.frame = 0
        
    
    def one_time(self, status, offset = [0, 0]):
        ID = self.ID + '_' + status
        self.offset = offset
        self.change_action(status)
        if self.frame >= len(animation_database[ID]) - 1:
            self.offset = [0, 0]
            self.status = 'idle'
            self.frame = 0
            return True
    
    def attack_rect(self, area, offset):
        self.area = area
        self.attack = True
        if self.flip:
            if not self.one_time('sword_attack', offset):
                attack_rect = pygame.Rect(self.x - area, self.y, self.img.get_width(), self.img.get_height())
                return attack_rect
            else:
                self.attack = False
        else:
            if not self.one_time('sword_attack'):
                attack_rect = pygame.Rect(self.x + area, self.y, self.img.get_width(), self.img.get_height())
                return attack_rect
            else:
                self.attack = False

    def load_animation(self, surface, status, scroll, draw = True):
        ID = self.ID + '_' + status
        if self.frame > len(animation_database[ID]) - 1:
            self.frame = 0
        entity_anim = animation()
        entity_anim.load_animation(surface, ID, self.frame, [self.rect.x + self.offset[0] - scroll[0], self.rect.y + self.offset[1] - scroll[1]], self.flip)
        self.frame += 1
        self.attack_timer += 1
    
    def check_fall(self, tile_rect):
        fall = True
        if not self.flip:
            check_x = self.rect.x + self.img.get_width()
            check_y = self.rect.y + self.img.get_height()
        else:
            check_x = self.rect.x - self.img.get_width()
            check_y = self.rect.y + self.img.get_height()
        
        check_rect = pygame.Rect(check_x, check_y, self.img.get_width(), self.img.get_height())
        for tile_check in tile_rect:
            if check_rect.colliderect(tile_check):
                fall = False
        if fall:
            return True

    def move(self, movement, tile_rect):
        self.collision = {'top': False, 'bottom': False, 'right': False, 'left': False}
        
        # Update location x ---------------------------------------------------------------------------------------------------- #
        self.rect.x += movement[0]
        hit_list = collide_test(self.rect, tile_rect)
        for tile in hit_list:
            if movement[0] > 0:
                self.collision['right'] = True
                self.rect.right = tile.left
            elif movement[0] < 0:
                self.collision['left'] = True
                self.rect.left = tile.right
        self.x = self.rect.x
                
        # Update location y ------------------------------------------------------------------------------------------------------------------ #
        self.rect.y += movement[1]
        hit_list = collide_test(self.rect, tile_rect)
        for tile in hit_list:
            if movement[1] >= 0:
                self.collision['bottom'] = True
                self.rect.bottom = tile.top
            elif movement[1] < 0:
                self.collision['top'] = True
                self.rect.top = tile.bottom
        self.y = self.rect.y

class projectile(object):
    
    def __init__(self):
        self.x = 0
        self.y = 0
        self.check = 0
        self.flip = False
        
    def throw(self, player, entity):
        land = False            
        if player[0] < entity.x or player[0] > entity.x + entity.rect.width:
            if player[1] > entity.y:
                h = - 6
                if entity.flip:
                    offset = entity.x
                    d_x = abs(player[0] + player[2] - entity.x - entity.rect.width)
                    d_y = abs( player[1] + player[3] - entity.y)
                else:
                    offset = entity.x + entity.rect.width
                    d_x = abs(player[0] - entity.x - entity.rect.width)
                    d_y = abs( player[1] + player[3] - entity.y)
            elif player[1] == entity.y:
                h = -6
                if entity.flip:
                    offset = entity.x
                    d_x = abs(player[0] + player[2] - entity.x - entity.rect.width)
                    d_y = abs( player[1] + player[3] - entity.y)
                else:
                    offset = entity.x + entity.rect.width
                    d_x = abs(player[0] - entity.x - entity.rect.width)
                    d_y = abs( player[1] + player[3] - entity.y)
            else:
                h = player[1] - entity.y - 6
                if entity.flip:
                    offset = entity.x
                    d_x = abs(player[0] - entity.x - entity.rect.width)
                    d_y = abs( player[1] + player[3] - entity.y)
                else:
                    offset = entity.x + entity.rect.width
                    d_x = abs(player[0] + player[2] - entity.x - entity.rect.width)
                    d_y = abs( player[1] + player[3] - entity.y)
            s_d = math.sqrt(d_x ** 2 - (d_x ** 2 * d_y) / h)
            b_1 = ((- d_x + s_d) * h * 2) / ( - d_x ** 2)
            b_2 = ((- d_x - s_d) * h * 2) / ( - d_x ** 2)
            
            if b_1 < 0:
                b = b_1
            else:
                b = b_2
            
            if self.check == 0:
                self.x = offset
                self.check = 1
            else:
                if self.flip:
                    self.x -= d_x/20
                else:
                    self.x += d_x/20
                    
            a = (- b ** 2) / (4 * h)
            self.y = a * abs((self.x - offset)) ** 2 + b * abs((self.x - offset)) + entity.y
        else:
            land = True

        return self.x, self.y, land

class HUD(object):
    def __init__(self, ID):
        self.ID = ID
        self.frame = 0
        self.offset = [0, 0]
        self.flip = False
        self.check = 0
    
    def load_animation(self, surface, pos, scroll, offset = [0, 0], draw = True):
        self.offset = offset
        ID = self.ID
        if self.frame > len(animation_database[ID]) - 1:
            self.frame = 0
        entity_anim = animation()
        entity_anim.load_animation(surface, ID, self.frame, [pos[0] + self.offset[0] - scroll[0], pos[1] + self.offset[1] - scroll[1]], self.flip)
        self.frame += 1
    
    def one_time(self, offset = [0, 0]):
        ID = self.ID
        self.offset = offset
        if self.frame == len(animation_database[ID]) - 1:
            self.offset = [0, 0]
            self.frame = 0
            return True

class particle(object):
    global par_tile
    
    def __init__(self, loc, ver_x, ver_y, space, radius, many, color):
        self.ver_x = ver_x
        self.ver_y = ver_y
        self.space = space
        self.radius = radius
        self.many = many
        self.color = color
        self.gravity = False
        self.TILE_SIZE = 16
        self.PARTICLES = []
        self.loc = loc
    
    
    def blend(self, surface, scroll):
        CHUNK_SIZE = 8
        
        loc_par = self.loc.copy() # Must do else var will point to one location in memory
        def blend_surf(radius, color):
            surf = pygame.Surface([radius * 4, radius * 4])
            pygame.draw.circle(surf, color, [radius * 2, radius * 2], radius * 2)
            surf.set_colorkey([0, 0, 0])
            return surf
        
        for _ in range(self.many):
            self.PARTICLES.append([loc_par, [random.randint(0, self.ver_x) / self.space - self.ver_x/self.space/2, random.randint(self.ver_y[0], self.ver_y[1])] , random.randint(self.radius[0], self.radius[1])])
        
        for partice in self.PARTICLES:
            partice[0][0] += partice[1][0]
            partice[0][1] += partice[1][1]
            partice[2] -= self.radius[2]
            if self.gravity:
                partice[1][1] += 0.2
            if partice[2] > 0:
                pygame.draw.circle(surface, self.color[0], [partice[0][0] - scroll[0], partice[0][1] - scroll[1]], partice[2])
                surface.blit(blend_surf(partice[2], self.color[1]), [partice[0][0] - partice[2] * 2 - scroll[0], partice[0][1] - partice[2] * 2 - scroll[1]], special_flags = BLEND_RGB_ADD )
        for partice in self.PARTICLES:
            if partice[2] <= 0:
                self.PARTICLES.remove(partice)
        
