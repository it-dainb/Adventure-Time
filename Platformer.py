import pygame
import sys
import os
import time
import math
import json
import random
import data.DaiEngine as e
from pygame.locals import *

# Setting enviromental ------------------------------------------------------------------------------------------------------------------ #
pygame.mixer.init()
pygame.init()
pygame.mixer.set_num_channels(64)
clock = pygame.time.Clock()

pygame.display.set_caption("Adventure Time !!! Made by DAIOTAKU")

WINDOWN_SIZE = (960, 540)

screen = pygame.display.set_mode(WINDOWN_SIZE)

SCALE = 3
display = pygame.Surface([640 / 2, 360 /2 ])#[WINDOWN_SIZE[0]/SCALE, WINDOWN_SIZE[1]/SCALE])
HUD = pygame.Surface([640/2/1, (360/2)/4], pygame.SRCALPHA)

# Setting data base ------------------------------------------------------------------------------------------------------------------ #
animation = e.animation()
animation.create_database()
database = e.create_database() # ID: [img_loaded, img_name, type] type can be obj, tile, entity
# for k in database:
    # print(k, database[k][1])

# Global variable ------------------------------------------------------------------------------------------------------------------ #
coin = 0
life = 3
health = 100
level = 0
INVENTORY = {}

# Sound for UI ------------------------------------------------------------------------------------------------------------------ #
click_wav = pygame.mixer.Sound('data/music/click.ogg')

# Sound for game ------------------------------------------------------------------------------------------------------------------ #
grass_wav = [pygame.mixer.Sound('data/music/grass_0.wav'), pygame.mixer.Sound('data/music/grass_1.wav')]
grass_wav[0].set_volume(0.1) 
grass_wav[1].set_volume(0.1)
coin_wav = pygame.mixer.Sound('data/music/coin.wav')
jump_wav = pygame.mixer.Sound('data/music/jump.wav')
jump_wav.set_volume(0.3)
hit_wav = pygame.mixer.Sound('data/music/hit.wav')
explosion_wav = pygame.mixer.Sound('data/music/explosion.wav')
explosion_wav.set_volume(0.04)
dash_wav = pygame.mixer.Sound('data/music/dash.flac')
dash_wav.set_volume(0.4)
attack_wav = pygame.mixer.Sound('data/music/sword.wav')
attack_wav.set_volume(0.3)
button_wav = pygame.mixer.Sound('data/music/button.wav')
button_wav.set_volume(0.5)
lever_wav = pygame.mixer.Sound('data/music/lever.wav')
lever_wav.set_volume(0.5)
strange_door_close = pygame.mixer.Sound('data/music/strange door close.wav')
strange_door_open = pygame.mixer.Sound('data/music/strange door open.wav')
strange_door_close.set_volume(0.3)
strange_door_open.set_volume(0.3)
push_wav = pygame.mixer.Sound('data/music/push.wav')
push_wav.set_volume(0.2)
fall_wav = pygame.mixer.Sound('data/music/fall.wav')
fall_wav.set_volume(0.3)
spawn_wav = pygame.mixer.Sound('data/music/spawn.mp3')
spawn_wav.set_volume(0.4)
vase_wav = pygame.mixer.Sound('data/music/vase.wav')
vase_wav.set_volume(0.2)
chest_wav = pygame.mixer.Sound('data/music/chest.wav')
chest_wav.set_volume(0.4)

pygame.mixer.music.load('data/music/bg_music.wav')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)

# Game ------------------------------------------------------------------------------------------------------------------ #
def game(map_name):
    global clock, WINDOWN_SIZE, screen, SCALE, display, animation, database, HUD
    global coin, life, health, level, INVENTORY
    
    # GAME MAP ------------------------------------------------------------------------------------------------------------------ #
    game_map = {}
    game_map = e.load_map(map_name)#input('LOAD MAP: '))
    CHUNK_SIZE = 8
    IMG_SIZE = [16, 16]

    # Game variable ------------------------------------------------------------------------------------------------------------------ #

    moving_right = False
    moving_left = False
    attack = False
    flash = False

    air_timer = 0
    attack_timer = 0
    flash_start = 0

    true_scroll = [0, 0]

    jump_count = 0
    check = True
    lost_life = e.HUD('lost_life')
    

    # List of entity, object, efffect ------------------------------------------------------------------------------------------------------------------ #
    ENTITY = []
    OBJECT = []
    COIN = []
    STONE = []
    stone_rects = []
    tile_rects = []
    PROJECTILE = {}
    strange_door_ex = False

    for type_ in game_map:
        if type_ == 'entity':
            for data in game_map[type_]:
                if data[1] == 90:
                    player = e.entity(data[2], data[0])
                else:
                    ENTITY.append(e.entity(data[2], data[0]))
        elif type_ == 'object':
            for data in game_map[type_]:
                if data[1] == 79:
                    OBJECT.append([e.object(data[2], data[0]), 'closed'])
                    strange_door_rect = pygame.Rect(OBJECT[-1][0].get_rect('closed'))
                    strange_door_ex = True
                elif data[1] == 62:
                    OBJECT.append([e.object(data[2], data[0]), 'on_ground'])
                elif data[1] == 64:
                    COIN.append([e.object(data[2], data[0]), 'idle'])
                elif data[1] == 78:
                    STONE.append([e.object(data[2], data[0]), 'idle'])
                else:
                    OBJECT.append([e.object(data[2], data[0]), 'idle'])

    EFFECT = [] # [object, duration]
    hit_sparkle = False
    hit_sparkle_bomb = False
    hit_player = False
    check_point = [[player.x, player.y - 16]]
    player.check = 3

    # Player, entity var ------------------------------------------------------------------------------------------------------------------ #
    vel = 3
    vel_push = 1
    entity_vel = 1
    jump_power = 5.1
    push = False
    push_check = 0
    dash_per = 1

    # Obj variable ------------------------------------------------------------------------------------------------------------------ #
    get = False
    lever_active = False
    hit_lever = 0
    buttom_active = False
    strange_door_opening = False
    strange_door_closing = False
    strange_door_closed = True
    saved = False
    saving = False
    loot_box = False
    loot_box_opened = False
    vase_break = False
    start = False

    # INVENTORY ------------------------------------------------------------------------------------------------------------------ #
    num_select = 0
    value_item = 0
    use_item = False

    # Background ------------------------------------------------------------------------------------------------------------------ #
    BG_0_img = pygame.image.load('data/background/bg_0.png')
    BG_1_img = pygame.image.load('data/background/bg_1.png')
    BG_0 = pygame.transform.scale(BG_0_img, [display.get_width(), display.get_height()])
    BG_1 = pygame.transform.scale(BG_1_img, [display.get_width(), display.get_height()])
    
    grass_timer = 0
    
    running = True
    # MAIN GAME -------------------------------------------------------------------------------------------------------------------------------#
    while running:
        display.fill([0, 0, 0, 0])
        HUD.fill([0,0,0,0])
        
        # Sound setting ------------------------------------------------------------------------------------------------------------------ #
        if moving_right or moving_left:
            if player.collision['bottom']:
                if grass_timer == 0:
                    random.choice(grass_wav).play()
                    grass_timer = 10
        if grass_timer > 0:
            grass_timer -= 1
        # CAMERA ------------------------------------------------------------------------------------------------------------------ #
        true_scroll[0] += (player.rect.x - true_scroll[0] - display.get_width()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
        true_scroll[1] += (player.rect.y - true_scroll[1] - display.get_height()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
        scroll = true_scroll.copy()
        scroll[0] = int(scroll[0])
        scroll[1] = int(scroll[1])
        
        #print(2500 - scroll[1]*0.25)
        # Backround ------------------------------------------------------------------------------------------------------------------ #
        display.blit(BG_0, [0 - scroll[0]*0.25 + display.get_width() * (player.x // display.get_width() // 4 - 1), 0])
        display.blit(BG_0, [0 - scroll[0]*0.25 + display.get_width() * (player.x // display.get_width() // 4), 0])
        display.blit(BG_0, [0 - scroll[0]*0.25 + display.get_width() * (player.x // display.get_width() // 4 + 1), 0])
        display.blit(BG_1, [0 - scroll[0]*0.5 - 55 + display.get_width() * (player.x // display.get_width() // 2 - 1), 0])
        display.blit(BG_1, [0 - scroll[0]*0.5 - 55 + display.get_width() * (player.x // display.get_width() // 2), 0])
        display.blit(BG_1, [0 - scroll[0]*0.5 - 55 + display.get_width() * (player.x // display.get_width() // 2 + 1), 0])

        # TILE RENDERING ------------------------------------------------------------------------------------------------------------------ #
        #e.chunk_render(display, WINDOWN_SIZE, SCALE, CHUNK_SIZE, IMG_SIZE, scroll)
        e.map_render(display, scroll)
       # player_rect = pygame.Rect([player.rect.x + 2, player.rect.y, player.rect.width - 3, player.rect.height])
       # pygame.draw.rect(display, [255,0,0], [player_rect.x - scroll[0], player_rect - scroll[1], player_rect.width, player_rect.height], 1)
        
        if player.health <= 0 and player.check == 0:
            player.check = 1
        
        if player.check == 1 or player.check == 2:
            if player.check == 1:
                health = 0
                life -= 1
                player.check = 2
            if not player.one_time('death'):
                player.load_animation(display, player.status, scroll)
            else:
                player.check = 3

        if player.check == 3 or player.check == 4:
            if player.check == 3:
                player.rect.x, player.rect.y = check_point[-1][0], check_point[-1][1]
                player.check = 4
            if not player.one_time('spawn'):
                player.load_animation(display, player.status, scroll)
            else:
                health = 100
                player.check = 0
        
        # Move momentum ------------------------------------------------------------------------------------------------------------------ #
        gravity = 0.5
        ground = 1.5
        
        if player.check == 0:
            for entity in ENTITY:
                if entity.ID == 'slime':
                    entity.offset = [0, -8]
                entity.movement = [0, 0]
                entity.movement[1] += entity.y_momentum
                entity.y_momentum = round(entity.y_momentum + gravity, 1)
                if entity.y_momentum > 10:
                    entity.y_momentum = 10

            for obj in STONE:
                if obj[0].ID == 'stone':
                    obj[0].movement = [0, 0]
                    obj[0].movement[1] += obj[0].y_momentum
                    obj[0].y_momentum = round(obj[0].y_momentum + gravity, 1)
                if obj[0].y_momentum > 10:
                    obj[0].y_momentum = 10

            # Player move ------------------------------------------------------------------------------------------------------------------ #
            player.movement = [0, 0]

            if not push:
                if moving_right:
                    if player.status != 'run':
                        player.movement[0] += vel - 1
                    else:
                        player.movement[0] += vel
                if moving_left:
                    if player.status != 'run':
                        player.movement[0] -= vel - 1
                    else:
                        player.movement[0] -= vel
            else:
                if moving_right:
                    player.movement[0] += vel_push
                if moving_left:
                    player.movement[0] -= vel_push

            player.movement[1] += player.y_momentum
            player.y_momentum = round(player.y_momentum + gravity, 1) # GRAVITY :))))
            if player.y_momentum > 10:
                player.y_momentum = 10


        # Action center ------------------------------------------------------------------------------------------------------------------ #
            prev_status = player.status

            if moving_right:
                player.flip = False
            elif moving_left:
                player.flip = True

            if not hit_player:
                if not player.attack:
                    #print(player_movement[1], ground)
                    if not push:
                        player.offset = [0, 0]
                        if player.movement[0] != 0 and player.movement[1] == 0:
                            player.change_action('run')
                        if player.movement[0] == 0 and player.movement[1] == 0:
                            player.change_action('idle')
                        if player.movement[1] < 0 and jump_count < 2:
                            player.change_action('jump_up')
                            if player.time == 0:
                                fall_wav.play()
                                player.time = 20
                        if player.movement[1] > ground and ( jump_count == 18 or jump_count == 1) or player.movement[1] > ground or player.collision['top']:
                            player.change_action('jump_down')
                            if player.time == 0:
                                fall_wav.play()
                                player.time = 20
                        if 18 > jump_count >= 2:
                            if player.collision['top']:
                                check = False
                            if check:
                                player.change_action('jump_double')
                                if player.time == 0:
                                    fall_wav.play()
                                    player.time = 20
                                jump_count += 1
                    else:
                        player.change_action('pushing_foward')
            if player.time > 0:
                player.time -= 1
            if player.movement[1] == 0:
                if player.collision['bottom']:
                    jump_count = 0
                    check = True

            now_status = player.status

            if player.attack:
                attack_rect = player.attack_rect(14, [-16, 0])
                # if player.attack:
                    # pygame.draw.rect(display, [255,0,255], [attack_rect.x + 50, attack_rect.y - 9999, attack_rect.width, attack_rect.height], 1)

            #pygame.draw.rect(display, [255,255,255], [player.rect.x - scroll[0], player.rect.y - scroll[1], player.rect.width, player.rect.height], 1)
            # pygame.draw.rect(display, [255,0,255], [player.x + 50, player.y - 9999, player.rect.width, player.rect.height], 1)

            # Flash skill ------------------------------------------------------------------------------------------------------------------ #
            if flash:
                if time.time() - flash_start >= 5:
                    dash_wav.play()
                    for i in range(50):
                        if player.flip:
                            player.move([-2, 0], tile_rects)
                        else:
                            player.move([ 2, 0], tile_rects)
                        if i % 10 == 0:
                            player.load_animation(display, 'hit', scroll)
                    flash_start = time.time()
            else:
                dash_per = (time.time() - flash_start)/5
                if dash_per > 1:
                    dash_per = 1

            # Create effect ------------------------------------------------------------------------------------------------------------------ #
            if prev_status != 'jump_up' and now_status == 'jump_up' or ( prev_status == 'jump_up' and now_status == 'jump_double'):
                EFFECT.append([e.object('herochar_before_jump_dust', [player.rect.x, player.rect.y]), 8])
            if prev_status == 'jump_down' and now_status != 'jump_down':
                EFFECT.append([e.object('herochar_after_jump_dust', [player.rect.x, player.rect.y]), 8])

            # Move Player ------------------------------------------------------------------------------------------------------------------ #
            player.move(player.movement, tile_rects)
            if player.collision['bottom']:
                player.y_momentum = 0
                air_timer = 0
            else:
                air_timer += 1
            if player.collision['top']:
                player.y_momentum = 0

        # Render entity ------------------------------------------------------------------------------------------------------------------ #
        display_render = pygame.Rect(scroll[0], scroll[1], WINDOWN_SIZE[0] / SCALE, WINDOWN_SIZE[1] / SCALE)

        # STONE ------------------------------------------------------------------------------------------------------------------ #
        push_check = 0
        tile_rects = []
        stone_rects = []
        if strange_door_ex:
            tile_rects.append(strange_door_rect)

        for rect in e.tile_rects:
            tile_rects.append(rect)

        for stone in STONE:
            stone[0].status = stone[1]
            obj_rect = stone[0].get_rect(stone[0].status)
            obj_rect = pygame.Rect([obj_rect.x, obj_rect.y, obj_rect.width, obj_rect.height])
            tile_rects.append(obj_rect)
            stone_rects.append(obj_rect)

        # Push stone ------------------------------------------------------------------------------------------------------------------ #
        for stone in STONE:

            stone[0].status = stone[1]
            obj_rect = stone[0].get_rect(stone[0].status)
            obj_rect = pygame.Rect([obj_rect.x, obj_rect.y, obj_rect.width , obj_rect.height])
            push_rect = pygame.Rect([obj_rect.x - 1, obj_rect.y + 4, obj_rect.width + 2, obj_rect.height - 8])
            obj = stone[0]

            tile_rects.remove(obj_rect)
            stone_rects.remove(obj_rect)

            obj.rect, obj.collision = e.move(obj_rect, obj.movement, tile_rects)
            obj.x, obj.y = obj.rect.x, obj.rect.y

            #pygame.draw.rect(display, [255,0,0], [obj_rect.x - scroll[0], obj_rect.y - scroll[1], obj_rect.width, obj_rect.height], 1)
            #pygame.draw.rect(display, [255,0,0], [push_rect.x - scroll[0], push_rect.y - scroll[1], push_rect.width, push_rect.height], 1)
            
            if player.rect.colliderect(push_rect):
                if moving_right:
                    if push_rect.right >= player.rect.right >= push_rect.left:
                        if obj.time == 0:
                            push_wav.play()
                            obj.time = 15
                        obj.movement[0] += vel_push
                        obj.rect, obj.collision = e.move(obj_rect, obj.movement, tile_rects)
                        obj.x, obj.y = obj.rect.x, obj.rect.y
                        player.offset[0] = 2
                        player.rect.right = obj_rect.left
                    else:
                        obj.time = 0
                        push_wav.stop()
                        push_check += 1
                elif moving_left:
                    if push_rect.left <= player.rect.left <= push_rect.right:
                        if obj.time == 0:
                            push_wav.play()
                            obj.time = 15
                        obj.movement[0] -= vel_push
                        obj.rect, obj.collision = e.move(obj_rect, obj.movement, tile_rects)
                        obj.x, obj.y = obj.rect.x, obj.rect.y
                        player.offset[0] = -2
                        player.rect.left = obj_rect.right
                    else:
                        obj.time = 0
                        push_wav.stop()
                        push_check += 1
                if player.movement[1] < 0:
                    obj.time = 0
                    push_wav.stop()
                    push_check += 1
                if player.movement[0] == 0:
                    obj.time  = 0
                    push_wav.stop()
                    push_check += 1
            else:
                push_check += 1
            
            if obj.time > 0:
                obj.time  -= 1
            tile_rects.append(obj_rect)
            stone_rects.append(obj_rect)

        # Check Push ------------------------------------------------------------------------------------------------------------------ #
        if push_check == len(STONE):
            push = False
        else:
            push = True

        # Object system ------------------------------------------------------------------------------------------------------------------ #
        for obj in OBJECT:
            if not get:
                obj_rect = obj[0].get_rect(obj[1])
                obj[0].status = obj[1]
            else:
                obj_rect = obj[0].get_rect(obj[0].status)
            #pygame.draw.rect(display, [255,0,0], [obj_rect.x - scroll[0], obj_rect.y - scroll[1], obj_rect.width, obj_rect.height], 1)
            if obj[0].ID == 'waterfall' or obj[0].ID == 'waterfall_bottom':
                obj[0].load_animation(display, obj[0].status, scroll)
            if display_render.colliderect(obj_rect) and obj[0].ID != 'waterfall' and obj[0].ID != 'waterfall_bottom':

                # Buttom ------------------------------------------------------------------------------------------------------------------ #
                if obj[0].ID == 'buttom':
                    for stone_rect in stone_rects:
                        if stone_rect.colliderect(obj_rect) or player.rect.colliderect(obj_rect):
                            if not buttom_active:
                                button_wav.play()
                            obj[0].change_action('pressed')
                            buttom_active = True
                        else:
                            if buttom_active:
                                button_wav.play()
                            obj[0].change_action('idle')
                            buttom_active = False
                    if stone_rects == []:
                        if player.rect.colliderect(obj_rect):
                            if not buttom_active:
                                button_wav.play()
                            obj[0].change_action('pressed')
                            buttom_active = True
                        else:
                            if buttom_active:
                                button_wav.play()
                            obj[0].change_action('idle')
                            buttom_active = False
                        
                    obj[0].load_animation(display, obj[0].status, scroll)

                # Items ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'antidote_potion' or obj[0].ID == 'apple_item' or obj[0].ID == 'health_potion' or obj[0].ID == 'meat_item':
                    colli_rect = pygame.Rect([player.rect.x + 3, player.rect.y, player.rect.width - 6, player.rect.height])
                    #pygame.draw.rect(display, [255,0,0], [colli_rect.x - scroll[0], colli_rect.y - scroll[1], colli_rect.width, colli_rect.height], 1)
                   # pygame.draw.rect(display, [255,0,0], [obj_rect.x - scroll[0], obj_rect.y - scroll[1], obj_rect.width, obj_rect.height], 1)
                    if colli_rect.colliderect(obj_rect):
                        if obj[0].ID not in INVENTORY:
                            INVENTORY[obj[0].ID] = 1
                            obj[0].check = 1
                        else:
                            INVENTORY[obj[0].ID] += 1
                            obj[0].check = 1
                    obj[0].load_animation(display, obj[0].status, scroll)

                # Lever ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'lever':
                    if player.attack:
                        if ( player.rect.colliderect(obj_rect) or attack_rect.colliderect(obj_rect) ):
                            if hit_lever == 0:
                                if (player.rect.x <= obj_rect.x + obj_rect.width / 2 and not player.flip) or (player.rect.x >= obj_rect.x + obj_rect.width / 2 and player.flip) or obj_rect.x - 10 <= player.rect.x <= obj_rect.x + obj_rect.width:
                                    lever_wav.play()
                                    if lever_active:
                                        lever_active = False
                                        obj[0].change_action('idle')
                                    else:
                                        lever_active = True
                                        obj[0].change_action('active')
                            hit_lever += 1
                    else:
                        hit_lever = 0
                    obj[0].load_animation(display, obj[0].status, scroll)

                # Strange door ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'strange_door':

                    # Opening animation ------------------------------------------------------------------------------------------------------------------ #
                    if buttom_active or lever_active:
                        tile_rects.remove(strange_door_rect)

                        if not obj[0].one_time('opening') and not strange_door_opening:
                            obj[0].load_animation(display, 'opening', scroll)
                            strange_door_rect.y += 1
                            strange_door_rect.height -= 1
                            if obj[0].check == 0:
                                strange_door_open.play()
                                obj[0].check = 1
                        else:
                            obj[0].check = 0
                            #strange_door_open.stop()
                            strange_door_rect.top = obj_rect.bottom
                            strange_door_opening = True
                            strange_door_closing = False
                            strange_door_closed =False

                        tile_rects.append(strange_door_rect)


                    # Closing animation ------------------------------------------------------------------------------------------------------------------ #
                    elif not strange_door_closed:
                        tile_rects.remove(strange_door_rect)
                        if not obj[0].one_time('closing') and not strange_door_closing:
                            obj[0].load_animation(display, 'closing', scroll)
                            strange_door_rect.y -= 1
                            strange_door_rect.height += 1
                            if obj[0].check == 0:
                                strange_door_close.play()
                                obj[0].check = 1
                        else:
                            obj[0].check = 0
                            #strange_door_close.stop()
                            strange_door_rect.top = obj_rect.top
                            strange_door_opening = False
                            strange_door_closing = True
                            strange_door_closed = True

                        tile_rects.append(strange_door_rect)

                    # Closed  ------------------------------------------------------------------------------------------------------------------ #
                    else:
                        obj[0].check = 0
                        strange_door_close.stop()
                        strange_door_open.stop()
                        tile_rects.remove(strange_door_rect)
                        strange_door_rect = obj_rect
                        obj[0].load_animation(display, 'closed', scroll)
                        strange_door_closed = True
                        tile_rects.append(strange_door_rect)

                # Check spawn point ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'save_point':
                    if player.rect.colliderect(obj_rect) and obj[0].check == 0:
                        obj[0].check = 1
                    if obj[0].check != 0:
                        obj[0].load_animation(display, 'saving', scroll)
                        if obj[0].check == 1:
                            spawn_wav.play()
                            obj[0].check = 2
                            check_point.append([obj_rect.x, obj_rect.y - 16])
                    else:
                        obj[0].load_animation(display, 'idle', scroll)

                # Loot box ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'loot_box':
                    if player.attack and obj[0].check == 0:
                        if ( player.rect.colliderect(obj_rect) or attack_rect.colliderect(obj_rect) ):
                            obj[0].check = 1
                            if not loot_box:
                                loot_box = True
                    if obj[0].check == 1 or obj[0].check == 2:
                        if not obj[0].one_time('opening', [0, -2]):
                            if obj[0].check == 1:
                                chest_wav.play()
                                obj[0].check = 2
                            obj[0].load_animation(display, 'opening', scroll)
                        else:
                            obj[0].check = 3
                            loot_box = False
                            loot_box_opened = True
                    elif obj[0].check == 3 or obj[0].check == 4:
                        obj[0].load_animation(display, 'opened', scroll)
                        if obj[0].check == 3:
                            obj[0].check = 4
                            num = random.randint(1,100)
                            coin += random.randint(5, 15)
                            if num <= 5:
                                if 'antidote_potion' not in INVENTORY:
                                    INVENTORY['antidote_potion'] = 1
                                else:
                                    INVENTORY['antidote_potion'] += 1
                            elif num <= 15:
                                if 'health_potion' not in INVENTORY:
                                    INVENTORY['health_potion'] = 1
                                else:
                                    INVENTORY['health_potion'] += 1
                            elif num <= 35:
                                if 'meat_item' not in INVENTORY:
                                    INVENTORY['meat_item'] = 1
                                else:
                                    INVENTORY['meat_item'] += 1
                            elif num<= 100:
                                if 'apple_item' not in INVENTORY:
                                    INVENTORY['apple_item'] = 1
                                else:
                                    INVENTORY['apple_item'] += 1
                    else:
                        obj[0].load_animation(display, 'idle', scroll)

                # Vase ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'vase':
                    if player.attack and obj[0].attack == 0:
                        if player.rect.colliderect(obj_rect) or attack_rect.colliderect(obj_rect):
                            obj[0].attack = 1
                    if obj[0].attack == 1:
                        if not obj[0].one_time('breaking'):
                            if obj[0].check == 0:
                                vase_wav.play()
                                obj[0].check += 1
                            obj[0].load_animation(display, 'breaking', scroll)
                        else:
                            obj[0].check = 0
                            obj[0].attack = 2
                            if obj[0].check == 0:
                                obj[0].check = 1
                                num = random.randint(1,100)
                                if num <= 3:
                                    if 'antidote_potion' not in INVENTORY:
                                        INVENTORY['antidote_potion'] = 1
                                    else:
                                        INVENTORY['antidote_potion'] += 1
                                elif num <= 10:
                                    if 'health_potion' not in INVENTORY:
                                        INVENTORY['health_potion'] = 1
                                    else:
                                        INVENTORY['health_potion'] += 1
                                elif num <= 20:
                                    if 'meat_item' not in INVENTORY:
                                        INVENTORY['meat_item'] = 1
                                    else:
                                        INVENTORY['meat_item'] += 1
                                elif num < 50:
                                    if 'apple_item' not in INVENTORY:
                                        INVENTORY['apple_item'] = 1
                                    else:
                                        INVENTORY['apple_item'] += 1
                                else:
                                    coin += random.randint(0, 5)
                            # Add random items ------------------------------------------------------------------------------------------------------------------ #
                    elif obj[0].attack == 0:
                        obj[0].load_animation(display, 'idle', scroll)

                # Spike ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'spikes':
                    if not obj[0].attack:
                        attack_area = obj[0].attack_area([0, 32], [0, 32])
                        obj[0].load_animation(display, 'idle', scroll)
                        #pygame.draw.rect(display, [255,255,0], [attack_area.x - scroll[0], attack_area.y - scroll[1], attack_area.width, attack_area.height], 1)
                    if player.rect.colliderect(attack_area):
                        obj[0] = e.object('spikes_trap', [obj[0].x, obj[0].y])

                elif obj[0].ID == 'spikes_trap':
                    obj[0].move([0, 3])
                    obj[0].load_animation(display, 'idle', scroll)
                    if obj[0].get_rect('idle').colliderect(player.rect) and not obj[0].collision['bottom'] and not obj[0].attack != 0:
                        hit_player = True
                        hit_sparkle = True
                        obj[0].attack = 1

                # # Trap_suspended ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'trap_suspended':
                    obj[0].load_animation(display, obj[1], scroll)
                    obj[0].w_x = 0.1741
                    obj[0].w_y = 0.348
                    if obj[0].time == 36:
                        obj[0].time = 0
                    offset_x = 39 * math.cos(obj[0].w_x * obj[0].time + math.pi/2)
                    offset_y = 8 * math.cos(obj[0].w_y * obj[0].time)
                    t_x = obj[0].x + offset_x + 37
                    t_y = obj[0].y + offset_y + 15
                    obj[0].time += 1
                    #print(f"x: {offset_x} | y: {offset_y}")
                    trap_suspended_rect = pygame.Rect(t_x, t_y, 13, 20)
                    if player.rect.colliderect(trap_suspended_rect):
                        hit_player = True
                        hit_sparkle = True
                    pygame.draw.rect(display, [0,255,0],[trap_suspended_rect.x - scroll[0], trap_suspended_rect.y - scroll[1], trap_suspended_rect.width, trap_suspended_rect.height], 1)

                    # pass

                # # Bomb ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'bomb':
                    if obj[0].attack != 2:
                        if not obj[0].one_time('on_ground'):
                            obj[0].load_animation(display, 'on_ground', scroll)
                        else:
                            obj[0].attack = 1
                            bomb_area = obj[0].attack_area([16, 16])
                            EFFECT.append([e.object('explosion', [obj[0].x - 13, obj[0].y - 24]), 30])
                            #pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)
                        # pass

                # Trap_spike ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'trap_spike':
                    if obj[0].check > 0:
                        obj[0].check -= 1
                    if player.rect.colliderect(obj_rect) and obj[0].check == 0:
                        if obj[0].attack == 0:
                            hit_player = True
                            hit_sparkle = True
                            obj[0].check = 30
                        obj[0].attack = 1
                    if obj[0].attack == 1:
                        if not obj[0].one_time('attack'):
                            obj[0].load_animation(display, 'attack', scroll)
                        else:
                            obj[0].attack = 0
                    if obj[0].attack == 0:
                        obj[0].load_animation(display, 'idle', scroll)
                
                # Door ------------------------------------------------------------------------------------------------------------------ #
                elif obj[0].ID == 'door':
                    obj[0].load_animation(display, obj[0].status, scroll)
                    if player.rect.x > obj_rect.x and player.rect.colliderect(obj_rect):
                        level += 1
                        return True
                # Another stuff ------------------------------------------------------------------------------------------------------------------ #
                else:
                    obj[0].load_animation(display, obj[1], scroll)

            if obj[0].ID == 'buttom':
                # Move pos stone when active buttom ------------------------------------------------------------------------------------------------------------------ #
                for stone_rect in stone_rects:
                    if stone_rect.colliderect(obj_rect) and buttom_active:# and obj[0].check == 0:
                        #obj[0].check += 1
                        for stone in STONE:
                            stone[0].status = stone[1]
                            a_rect = stone[0].get_rect(stone[0].status)
                            a_rect = pygame.Rect([a_rect.x, a_rect.y, a_rect.width , a_rect.height])
                            obj_stone = stone[0]

                            tile_rects.remove(a_rect)
                            stone_rects.remove(a_rect)

                            if a_rect == stone_rect:
                                obj_stone.check = 1
                                obj_stone.movement = [0, -3]
                                obj_stone.rect, obj_stone.collision = e.move(a_rect, obj_stone.movement, tile_rects)
                                obj_stone.x, obj_stone.y = obj_stone.rect.x, obj_stone.rect.y

                            tile_rects.append(a_rect)
                            stone_rects.append(a_rect)
                            obj_stone.load_animation(display, obj_stone.status, scroll)
                    else:
                        for stone in STONE:
                            stone[0].status = stone[1]
                            a_rect = stone[0].get_rect(stone[0].status)
                            a_rect = pygame.Rect([a_rect.x, a_rect.y, a_rect.width , a_rect.height])
                            obj_stone = stone[0]
                            if stone_rect == a_rect:
                                obj_stone.check = 0
                            if obj_stone.check == 0:
                                obj_stone.load_animation(display, obj_stone.status, scroll)

            # Player can pass strange door ------------------------------------------------------------------------------------------------------------------ #
            # if obj[0].ID == 'strange_door':
                # if player.rect.colliderect(strange_door_rect):
                    # if player.movement[0] > 0:
                        # player.rect.right = strange_door_rect.left
                        # player.move([0, 5], tile_rects)
                    # if player.movement[0] < 0:
                        # player.rect.left = strange_door_rect.right
                        # player.move([0, 5], tile_rects)
                    # if strange_door_rect.x <= player.x + player.img.get_width() <= strange_door_rect.x + strange_door_rect.width and  strange_door_rect.y >= player.y:
                        # player.rect.bottom = strange_door_rect.top

            # Bomb hit player ------------------------------------------------------------------------------------------------------------------ #
            if obj[0].ID == 'bomb':
                if obj[0].attack == 1:
                    #pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)
                    if player.rect.colliderect(bomb_area):
                        hit_sparkle = True
                        hit_player = True
                        obj[0].attack = 2
                    else:
                        obj[0].attack = 2
            
            if player.check != 0:
                hit_player = False
                hit_sparkle = False
                
            
            if hit_player:# and (attack_area.colliderect(player.rect)):
                if player.one_time('hit'):
                    #print('true')
                    hit_wav.play()
                    hit_player = False
                if hit_sparkle:
                    if obj[0].ID == 'spikes_trap' or obj[0].ID == 'trap_spike':
                        health -= 5
                    elif obj[0].ID == 'trap_suspended':
                        health -= 20
                    if obj[0].ID == 'bomb':
                        if player.x >= obj[0].rect.x + obj[0].rect.width / 2:
                            for _ in range(20):
                                player.move([ 1, 0], tile_rects)
                        else:
                            for _ in range(20):
                                player.move([ -1, 0], tile_rects)
                    elif obj[0].ID == 'spikes_trap':
                        player.move([0, 10], tile_rects)
                    elif obj[0].ID == 'trap_suspended':
                        #print(player.x ,trap_suspended_rect.x + trap_suspended_rect.width)
                        if player.x >= trap_suspended_rect.x: #+ trap_suspended_rect.width:
                            for _ in range(40):
                                player.move([1, 0], tile_rects)
                        else:
                            for _ in range(40):
                                player.move([-1, 0], tile_rects)
                        if player.y < trap_suspended_rect.y + trap_suspended_rect.height - 10:
                            for _ in range(10):
                                player.move([0, -1], tile_rects)



                    # else:
                        # if not entity.flip:
                            # player.move([10, 0])
                        # else:
                            # player.move([ -10, 0])
                    EFFECT.append([e.object('herochar_hit_sparkle', [player.rect.x, player.rect.y]), 8])
                    hit_sparkle = False

            #pygame.draw.rect(display, [255,255,0], [strange_door_rect.x - scroll[0], strange_door_rect.y - scroll[1], strange_door_rect.width, strange_door_rect.height], 2)
            #pygame.draw.rect(display, [255,0,0], [obj_rect.x - scroll[0], obj_rect.y - scroll[1], obj_rect.width, obj_rect.height], 1)
        get = True
        # Coin system ------------------------------------------------------------------------------------------------------------------ #
        for coin_o in COIN:
            if player.attack:
                if attack_rect.colliderect(coin_o[0].get_rect(coin_o[1])):
                    coin_o[0].change_action('pickup')
            elif player.rect.colliderect(coin_o[0].get_rect(coin_o[1])):
                coin_o[0].change_action('pickup')
            if display_render.colliderect(coin_o[0].get_rect(coin_o[1])):
                if coin_o[0].status == 'idle':
                    coin_o[0].load_animation(display, 'idle', scroll)
                else:
                    if not coin_o[0].one_time('pickup', [0, -8]):
                        if coin_o[0].check == 0:
                            coin_wav.play()
                            coin_o[0].check += 1
                        coin_o[0].load_animation(display, coin_o[0].status, scroll)
                    else:
                        coin_o[0].check = 0
                        COIN.remove(coin_o)
                        coin += 1
            e.text_draw(HUD, str(coin), 2, [36, 17])

        e.text_draw(HUD, str(coin), 2, [36, 17])
        # Entity system ------------------------------------------------------------------------------------------------------------------ #
        for entity in ENTITY:
            if entity.ID == 'bomber_goblin':
                if entity.check > 0:
                    entity.check += 1
                if entity.check == 50:
                    entity.check = 0
                if PROJECTILE == {}:
                    PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 1, 0]
                if entity not in PROJECTILE:
                    PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 1, 0]

                # Thrown bomb ------------------------------------------------------------------------------------------------------------------ #
                if PROJECTILE[entity][1] != 0 and PROJECTILE[entity][1] != 1:
                    x, y, land = PROJECTILE[entity][1].throw(PROJECTILE[entity][0], entity)
                    if PROJECTILE[entity][-1] == 0:
                        PROJECTILE[entity].append(e.object('bomb', [x, y]))
                        PROJECTILE[entity][1].flip = entity.flip
                    else:
                        bomb = PROJECTILE[entity][-1]
                        if bomb.collision['bottom']:
                            land = True
                        if bomb.attack == 0:
                            bomb.load_animation(display, 'thrown', scroll)
                            bomb.attack = 1
                        if bomb.attack == 1:
                            if land:
                                if not bomb.one_time('on_ground'):
                                    bomb.load_animation(display, 'on_ground', scroll)
                                else:
                                    PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 1, 0]
                                    bomb_area = bomb.attack_area([16, 16])
                                    explosion_wav.play()
                                    EFFECT.append([e.object('explosion', [bomb.x - 13, bomb.y - 24]), 20])
                                    #pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)

                                    if player.rect.colliderect(bomb_area):
                                        hit_sparkle_bomb = True
                                        hit_player = True
                            elif bomb.get_rect(bomb.status).colliderect(player.rect):
                                PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 1, 0]
                                bomb_area = bomb.attack_area([16, 16])
                                explosion_wav.play()
                                EFFECT.append([e.object('explosion', [bomb.x - 13, bomb.y - 24]), 20])
                                #pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)
                                if player.rect.colliderect(bomb_area):
                                    hit_sparkle_bomb = True
                                    hit_player = True

                            else:
                                if bomb.collision['left'] or bomb.collision['right']:
                                    bomb.time = 1
                                if bomb.collision['top']:
                                    bomb.time = 2
                                if bomb.time == 0:
                                    #print('true')
                                    bomb.move([x - bomb.x, y - bomb.y])#, display, scroll)
                                else:
                                    if bomb.time == 2:
                                        bomb.move([0, 4])#, display, scroll)
                                    else:
                                        bomb.move([0, y - bomb.y])#, display, scroll)

                                bomb.load_animation(display, 'thrown', scroll)

                        # if bomb.y > player.y + IMG_SIZE[0]*3:
                            # PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 1, 0]

            if entity.rect.colliderect(display_render):

                # Entity action ------------------------------------------------------------------------------------------------------------------ #
                if entity.collision['bottom']:
                    entity.y_momentum = 0
                if entity.collision['top']:
                    entity.y_momentum = 0

                # Logic enemy ------------------------------------------------------------------------------------------------------------------ #
                if entity.ID != 'bomber_goblin':
                    attack_area = entity.area(0.4, 0)
                    vision_area = entity.area(5, 2)
                else:
                    attack_area = entity.area(5, 3, True)
                    vision_area = entity.area(7, 3, True)
                if entity.ID == 'mushroom' or entity.ID == 'slime':
                    attack_area = entity.area(0, 0)
                    vision_area = entity.area(5, 2)

                #pygame.draw.rect(display, [255,0,0], [vision_area.x - scroll[0], vision_area.y - scroll[1], vision_area.width, vision_area.height], 1)
                #pygame.draw.rect(display, [255,255,0], [attack_area.x - scroll[0], attack_area.y - scroll[1], attack_area.width, attack_area.height], 1)

                # Pause animation when attacked by player ------------------------------------------------------------------------------------------------------------------ #
                if player.attack and (attack_rect.colliderect(entity.rect)  or player.rect.colliderect(entity.rect)):
                    pass # Pause
                elif entity.attack and entity.ID != 'mushroom' and entity.ID != 'slime':
                    if entity.flip and entity.ID == 'goblin':
                        if entity.one_time('attack', [- 8, 0]):
                            entity.attack = False
                    else:
                        if entity.one_time('attack'):
                            entity.attack = False
                elif entity.attack:
                    if entity.one_time('idle'):
                        entity.attack = False
                else:
                    if entity.ID != 'slime':
                        entity.offset = [0, 0]
                    if player.rect.colliderect(vision_area):
                        if entity.ID != 'bomber_goblin':

                            # Attack Player ------------------------------------------------------------------------------------------------------------------ #
                            if player.check == 0:
                                if player.rect.colliderect(attack_area) and entity.attack_timer > 15 and not flash and entity.ID != 'worm':
                                    entity.attack = True
                                    entity.attack_timer = 0
                                    hit_sparkle = True
                                    hit_player = True
                                    if player.x + player.rect.width / 2>= entity.x + attack_area.width / 2:
                                        entity.flip = False
                                    else:
                                        entity.flip = True
                                else:
                                    if player.x < entity.x:
                                        entity.movement[0] = -1
                                        entity.flip = True
                                    elif player.x > entity.x:
                                        entity.movement[0] = 1
                                        entity.flip = False
                        else:
                            if not player.rect.colliderect(attack_area) or player.check != 0:

                                # Move can fall ------------------------------------------------------------------------------------------------------------------ #
                                if not entity.check_fall(tile_rects):#display, scroll):
                                    if player.x < entity.x:
                                        entity.movement[0] = -1
                                        entity.flip = True
                                    elif player.x > entity.x:
                                        entity.movement[0] = 1
                                        entity.flip = False
                            else:

                                # Throw bomb to player ------------------------------------------------------------------------------------------------------------------ #
                                if player.x >= entity.x:
                                    entity.flip = False
                                else:
                                    entity.flip = True
                                if player.rect.colliderect(attack_area):
                                    # create bomb ------------------------------------------------------------------------------------------------------------------ #
                                    if PROJECTILE[entity][1] == 1 and entity.check == 0:
                                        if player.x < entity.x or player.x > entity.x + entity.rect.width:
                                            if player.check == 0:
                                                PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 0, 0]
                                                entity.check += 1

                    else:
                        # Return ------------------------------------------------------------------------------------------------------------------ #
                        if entity.ID != 'slime':
                            if entity.flip:
                                if entity.check_fall(tile_rects):#(display, scroll):
                                    entity.movement[0] = - entity_vel
                                    entity.flip = False
                                elif not entity.collision['left']:
                                    entity.movement[0] = - entity_vel
                                else:
                                    entity.flip = False
                            else:
                                if entity.check_fall(tile_rects):#(display, scroll):
                                    entity.movement[0] = entity_vel
                                    entity.flip = True
                                elif not entity.collision['right']:
                                    entity.movement[0] = entity_vel
                                else:
                                    entity.flip = True
                        else:
                            if not entity.flip:
                                if entity.check_fall(tile_rects):#(display, scroll):
                                    entity.movement[0] = - entity_vel
                                    entity.flip = True
                                elif not entity.collision['left']:
                                    entity.movement[0] = - entity_vel
                                else:
                                    entity.flip = True
                            else:
                                if entity.check_fall(tile_rects):#(display, scroll):
                                    entity.movement[0] = entity_vel
                                    entity.flip = False
                                elif not entity.collision['right']:
                                    entity.movement[0] = entity_vel
                                else:
                                    entity.flip = False


                entity.move(entity.movement, tile_rects)
               # pygame.draw.rect(display, [255,0,255], [player.x - scroll[0], player.y - scroll[1], 16, 16])

                # Entity move ------------------------------------------------------------------------------------------------------------------ #
                if not player.attack:
                    if not entity.attack:
                        if entity.ID != 'bomber_goblin':
                            if entity.movement[0] > 0:
                                if entity.ID != 'blue_fly' and entity.ID != 'orange_fly':
                                    entity.change_action('run')
                                else:
                                    entity.change_action('fly')
                            if entity.movement[0] < 0:
                                if entity.ID != 'blue_fly' and entity.ID != 'orange_fly':
                                    entity.change_action('run')
                                else:
                                    entity.change_action('fly')
                            if entity.movement[0] == 0:
                                entity.change_action('idle')
                        else:
                            entity.change_action('idle')
                elif player.attack and  (attack_rect.colliderect(entity.rect)  or player.rect.colliderect(entity.rect)):
                    if entity.one_time('hit'):
                        player.attack = False
                        entity.attack = False
                    if hit_sparkle:
                        entity.health -= 20
                        if not player.flip:
                            entity.move([ 10, 0], tile_rects)
                        else:
                            entity.move([ -10, 0], tile_rects)
                        EFFECT.append([e.object('herochar_hit_sparkle', [entity.rect.x, entity.rect.y]), 8])
                        hit_sparkle = False

            # Player HIT ------------------------------------------------------------------------------------------------------------------ #
            if player.check != 0:
                hit_player = False
                hit_sparkle = False
            
            if hit_player:# and (attack_area.colliderect(player.rect)):
                if player.one_time('hit'):
                    #print('true')
                    hit_wav.play()
                    hit_player = False
                    entity.attack = False
                if hit_sparkle:
                    if entity.ID != 'bomber_goblin':
                        health -= 10
                    if not entity.flip:
                        player.move([10, 0], tile_rects)
                    else:
                        player.move([ -10, 0], tile_rects)
                    EFFECT.append([e.object('herochar_hit_sparkle', [player.rect.x, player.rect.y]), 8])
                    hit_sparkle = False
                elif hit_sparkle_bomb:
                    health -= 8
                    if player.x >= bomb_area.x + bomb_area.width / 2:
                        for _ in range(4):
                            player.move([ 5, 0], tile_rects)
                    else:
                        for _ in range(4):
                            player.move([ - 5, 0], tile_rects)

                    EFFECT.append([e.object('herochar_hit_sparkle', [player.rect.x, player.rect.y]), 8])
                    hit_sparkle_bomb = False

            # Entity load animation ------------------------------------------------------------------------------------------------------------------ #
            entity.load_animation(display, entity.status, scroll)
            if entity.health <= 0:
                entity.life -= 1

            if entity.life == 0:
                ENTITY.remove(entity)

            # # Entity health bar ------------------------------------------------------------------------------------------------------------------ #
            # health_bar = pygame.image.load('data/hud/health_bar.png')
            # health_sur = pygame.Surface([health_bar.get_width(), health_bar.get_height()], pygame.SRCALPHA)
            # health_sur.blit(health_bar, [0, 0])
            # #health_bar_rect = pygame.Rect([entity.x - 5 - scroll[0] + 1, entity.y - 10 - scroll[1] + 1, (health_bar.get_width() / 2 - 1) * (entity.health / 100) / 2, (health_bar.get_height() / 2 - 1) / 2])
            # #pygame.draw.rect(display, [208, 70, 72], health_bar_rect)
            # health_sur = pygame.transform.scale(health_sur, [24, 4])
            # display.blit(health_sur, [entity.x - 5 - scroll[0], entity.y - 10 - scroll[1]])

        # Create bomb ------------------------------------------------------------------------------------------------------------------ #
        for pro in PROJECTILE:
            if PROJECTILE[pro][1] == 0:
                PROJECTILE[pro][1] = e.projectile()
        
        
        
        #pygame.draw.rect(display, [255,0,0], [player.rect.x - scroll[0], player.rect.y - scroll[1], player.rect.width, player.rect.height], 1)
        player.load_animation(display, player.status, scroll)

        # Effect render ------------------------------------------------------------------------------------------------------------------ #
        for effect in EFFECT:
            if effect[1] != 0:
                effect[0].load_animation(display, effect[0].status, scroll)
                effect[1] -= 1
            else:
                EFFECT.pop(EFFECT.index(effect))

        if player.attack and hit_player:
            player.attack = False

        flash = False

        # Inventory ------------------------------------------------------------------------------------------------------------------ #
        n = 0
        remove_item = []
        for item, value in INVENTORY.items():
            if n == num_select:
                img_item = pygame.image.load('data/items/' + item + '.png')
                HUD.blit(img_item, [9, 5])
                if use_item:
                    INVENTORY[item] -= 1
                    use_item = False
                    if item == 'health_potion':
                        health = 100
                    elif item == 'meat_item':
                        health += 50
                    elif item == 'apple_item':
                        health += 20
                    elif item == 'antidote_potion':
                        pass

                if INVENTORY[item] <= 0:
                    remove_item.append(item)
                value_item = value
            if num_select > len(INVENTORY) - 1:
                num_select -= 1
            if n < len(INVENTORY):
                n += 1
            else:
                n= 0
        for item in remove_item:
            INVENTORY.pop(item)

        if INVENTORY == {} and use_item:
            use_item = False

        # Update key ------------------------------------------------------------------------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if not hit_player and player.attack_timer > 15:
                        attack_wav.play()
                        player.attack = True
                        player.attack_timer = 0
                    hit_sparkle = True
                if event.key == K_RIGHT:
                    moving_right = True
                if event.key == K_LEFT:
                    moving_left = True
                if event.key == K_UP:
                    jump_wav.play()
                    if jump_count < 2:
                        if jump_count == 0:
                            player.y_momentum = - jump_power
                        else:
                            player.y_momentum = - jump_power + 1
                        jump_count += 1
                if event.key == K_f:
                    flash = True
                if event.key == K_d:
                    num_select += 1
                    if num_select > len(INVENTORY) - 1:
                        num_select = 0
                if event.key == K_a:
                    num_select -= 1
                    if num_select < 0:
                        num_select = len(INVENTORY) - 1
                if event.key == K_s:
                    use_item = True
            if event.type == KEYUP:
                if event.key == K_RIGHT:
                    moving_right = False
                if event.key == K_LEFT:
                    moving_left = False
        
        if level == 0:
            e.text_draw(display, 'Press arrow keys to move', 2, [- 40, 9920], scroll, True, display_render)
            e.text_draw(display, 'Press space to attack', 2, [- 40, 9930], scroll, True, display_render)
            e.text_draw(display, 'You can move stone', 2, [250, 9900], scroll, True, display_render)
            e.text_draw(display, 'Stone or you can active button', 2, [250, 9910], scroll, True, display_render)
            e.text_draw(display, 'lever can active by attack', 2, [250, 9920], scroll, True, display_render)
            e.text_draw(display, 'You need active buttom', 2, [250, 9930], scroll, True, display_render)
            e.text_draw(display, 'or lever to open the door', 2, [250, 9940], scroll, True, display_render)
            e.text_draw(display, 'Press up key 2 times', 2, [350, 10010], scroll, True, display_render)
            e.text_draw(display, 'For double jump', 2, [350, 10020], scroll, True, display_render)
            e.text_draw(display, 'A,D for select items', 2, [660, 9930], scroll, True, display_render)
            e.text_draw(display, 'S for use items', 2, [660, 9940], scroll, True, display_render)           
            e.text_draw(display, 'F for dash', 2, [800, 9950], scroll, True, display_render)
            e.text_draw(display, 'Dash has 5s cooldown', 2, [800, 9960], scroll, True, display_render)
            e.text_draw(display, 'Break chest or vase', 2, [970, 10020], scroll, True, display_render)
            e.text_draw(display, 'For items and gold', 2, [970, 10030], scroll, True, display_render)
            if player.y > 10070:
                health = 0
        
        if level == 6:
            win_rect = e.text_draw(screen, 'THANK FOR PLAYING', 4, [0, 0], scroll, False)
            e.text_draw(display, 'THANK FOR PLAYING', 4, [- 40, 10048 + 50], scroll)
        

        
        
        surf = pygame.transform.scale(display, WINDOWN_SIZE)
        screen.blit(surf, [0, 0])

        # HUD surface ------------------------------------------------------------------------------------------------------------------ #
                
        #print(health)
        if health > 100:
            health = 100
        player.health = health
        player.life = life

        HUD_HEALTH = pygame.image.load('data/hud/hud_health_menu.png')
        HUD_DASH = pygame.image.load('data/hud/dash_cooldown.png')
        life_icon = pygame.image.load('data/hud/lifes_icon.png')
        no_life_icon = pygame.image.load('data/hud/no_lifes_icon.png')

        health_rect = pygame.Rect([26, 3 , int(42 * player.health/100), 10])
        pygame.draw.rect(HUD, [208, 70, 72], health_rect)
        
        dash_rect = pygame.Rect([4, 35 , 64 * dash_per, 6])
        pygame.draw.rect(HUD, [255, 196, 0], dash_rect)
      #  health = 100

        HUD.blit(HUD_HEALTH, [0,-2])
        HUD.blit(HUD_DASH, [0,30])
        
        
        
        health_text = str(int(player.health)) + '/100'
        
        if lost_life.check == 3:
            return False
        
        # Life counter ------------------------------------------------------------------------------------------------------------------ #
        if player.life == 3:
            HUD.blit(life_icon, [303, 2])
            HUD.blit(life_icon, [287, 2])
            HUD.blit(life_icon, [271, 2])
        elif player.life == 2:
            HUD.blit(life_icon, [303, 2])
            HUD.blit(life_icon, [287, 2])
            if not lost_life.one_time() and lost_life.check == 0:
                lost_life.load_animation(HUD, [271, 2],[0, 0])
            else:
                lost_life.check = 1
                HUD.blit(no_life_icon, [271, 2])
        elif life == 1:
            HUD.blit(life_icon, [303, 2])
            HUD.blit(no_life_icon, [271, 2])
            if not lost_life.one_time() and lost_life.check == 1:
                lost_life.load_animation(HUD, [287, 2],[0, 0])
            else:
                lost_life.check = 2
                HUD.blit(no_life_icon, [271, 2])
                HUD.blit(no_life_icon, [287, 2])
        else:
            HUD.blit(no_life_icon, [271, 2])
            HUD.blit(no_life_icon, [287, 2])
            if not lost_life.one_time() and lost_life.check == 2:
                lost_life.load_animation(HUD, [303, 2],[0, 0])
            else:
                lost_life.check = 3
                HUD.blit(no_life_icon, [303, 2])
                HUD.blit(no_life_icon, [271, 2])
                HUD.blit(no_life_icon, [287, 2])

        # Render HUD ------------------------------------------------------------------------------------------------------------------ #
        HUD_surf = pygame.transform.scale(HUD, [WINDOWN_SIZE[0], int(WINDOWN_SIZE[0]/7)])
        screen.blit(HUD_surf, [0,0])

        if health == 100:
            e.text_draw(screen, health_text, 4 * (WINDOWN_SIZE[0] / (display.get_width() * 3)), [85 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 83, 17 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 15])
        elif health >= 10:
            e.text_draw(screen, health_text, 4 * (WINDOWN_SIZE[0] / (display.get_width() * 3)), [95 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 83, 17 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 15])
        elif health >= 0:
            e.text_draw(screen, health_text, 4 * (WINDOWN_SIZE[0] / (display.get_width() * 3)), [105 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 83, 17 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 15])


        # Render text ------------------------------------------------------------------------------------------------------------------ #
        
        fr = clock.get_fps()
        e.text_draw(screen, str(int(fr)), 4, [0, 0])
        
        for entity in ENTITY:
            # Entity health bar ------------------------------------------------------------------------------------------------------------------ #
            health_bar = pygame.image.load('data/hud/health_bar.png')
            health_sur = pygame.Surface([health_bar.get_width(), health_bar.get_height()], pygame.SRCALPHA)
            health_sur.blit(health_bar, [0, 0])
            health_bar_rect = pygame.Rect([(entity.x - 5 - scroll[0] + 1) * SCALE + 14, (entity.y - 10 - scroll[1] + 1) * SCALE + 8, (health_sur.get_width() / 2 - 3) * (entity.health / 100) * 2, (health_bar.get_height() / 2 + 3)])
            pygame.draw.rect(screen, [208, 70, 72], health_bar_rect)
            health_sur = pygame.transform.scale(health_sur, [48 + int((WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 50), 16])
            screen.blit(health_sur, [(entity.x*(WINDOWN_SIZE[0] / (display.get_width() * 3)) - 5 - scroll[0]) * SCALE + 14 , (entity.y - 10 - scroll[1]) * SCALE + 8])

  #      print((WINDOWN_SIZE[0] / (display.get_width() * 3) - 1))
 #       value_item = 6

        if INVENTORY != {}:
#            e.text_draw(screen, str(value_item), 4, [31 - (len(str(value_item)) - 1) * 8, 55])
            e.text_draw(screen, str(value_item), 4 * (WINDOWN_SIZE[0] / (display.get_width() * 3)), [31 - (len(str(value_item)) - 1) * 8 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 31, 55 + (WINDOWN_SIZE[0] / (display.get_width() * 3) - 1) * 54])#+ (WINDOWN_SIZE[1] / (display.get_height() * 3) - 1) * 20])

        for obj in OBJECT:
            if obj[0].ID == 'antidote_potion' or obj[0].ID == 'apple_item' or obj[0].ID == 'health_potion' or obj[0].ID == 'meat_item':
                if obj[0].check == 1:
                    OBJECT.remove(obj)
        

        # Update game ------------------------------------------------------------------------------------------------------------------ #
        pygame.display.update()
        clock.tick(e.FPS)

# Main Menu ------------------------------------------------------------------------------------------------------------------ #
def main_menu():
    global health, life, INVENTORY, level
    
    # Backround ------------------------------------------------------------------------------------------------------------------ #
    BG_0_img = pygame.image.load('data/background/bg_0.png')
    BG_1_img = pygame.image.load('data/background/bg_1.png')
    BG_0 = pygame.transform.scale(BG_0_img, [screen.get_width(), screen.get_height()])
    BG_1 = pygame.transform.scale(BG_1_img, [screen.get_width(), screen.get_height()])

    i = 0
    j = 0

    # UI ------------------------------------------------------------------------------------------------------------------ #
    start_buttom_b = pygame.image.load('data/UI/blue/blue_button00.png')
    start_buttom_b_c = pygame.image.load('data/UI/blue/blue_button01.png')
    start_buttom_y = pygame.image.load('data/UI/yellow/yellow_button00.png')
    start_buttom_r = pygame.image.load('data/UI/red/red_button11.png')
    start_buttom_g = pygame.image.load('data/UI/green/green_button00.png')
    
    click = False

    # Main Menu Loop ------------------------------------------------------------------------------------------------------------------ #
    running = True
    while running:
        
        # Background ------------------------------------------------------------------------------------------------------------------ #
        if i == BG_0.get_width():
            i = 0
        if j == BG_0.get_width() * 1:
            j = 0

        screen.fill([0,0,0])
        screen.blit(BG_0, [0 - i*0.5, 0])
        screen.blit(BG_0, [0 + BG_0.get_width() - i*0.5, 0])
        screen.blit(BG_1, [0 - i, 0])
        screen.blit(BG_1, [0 + BG_0.get_width() - i, 0])

        j += 0.5
        i += 1

        # Tile ------------------------------------------------------------------------------------------------------------------ #
        text_rect = e.text_draw(screen, 'ADVENTURE TIME', 14, [WINDOWN_SIZE[0]/2 - 100, 0], [0, 0], False)
        e.text_draw(screen, 'ADVENTURE TIME', 14, [WINDOWN_SIZE[0]/2 - text_rect.width/2, 90])
        
        mx, my = pygame.mouse.get_pos()
        
        start_button = e.UI(start_buttom_y, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - start_buttom_b.get_width()/2, 200], False)
        start_button = e.UI(start_buttom_y, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - start_button.width/2, WINDOWN_SIZE[1]/2 - start_button.height/2], False)
        if not start_button.collidepoint(mx, my):
            e.UI(start_buttom_y, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - start_button.width/2, WINDOWN_SIZE[1]/2 - start_button.height/2])
        else:
            if click:
                click_wav.play()
                e.UI(start_buttom_b_c, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - start_button.width/2, WINDOWN_SIZE[1]/2 - start_button.height/2])
                if level == 0:
                    if not game('tutorial'):
                        if end():
                            health = 100
                            life = 3
                if level == 1:
                    INVENTORY = {}
                    health = 100
                    life = 3
                    if not game('level_1'):
                        if end():
                            level = 1
                            health = 100
                            life = 3
                if level == 2:
                    if not game('level_2'):
                        if end():
                            level = 1
                            health = 100
                            life = 3
                if level == 3:
                    if not game('level_3'):
                        if end():
                            level = 1
                            health = 100
                            life = 3
                if level == 4:
                    if not game('level_4'):
                        if end():
                            health = 100
                            life = 3
                            level = 1
                if level == 5:
                    if not game('level_5'):
                        if end():
                            health = 100
                            life = 3
                            level = 1
                if level == 6:
                    life = 3
                    health = 100
                    game('win')
            else:
                e.UI(start_buttom_b, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - start_button.width/2, WINDOWN_SIZE[1]/2 - start_button.height/2])
                
        
       # pygame.draw.rect(screen, [255,0,0], blue_rect, 1)
        text_rect = e.text_draw(screen, 'START', 8, [0, 0], [0, 0],False)
        e.text_draw(screen, 'START', 8, [WINDOWN_SIZE[0]/2 - text_rect.width/2, 251])
        
        click = False
        # Key event ------------------------------------------------------------------------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        clock.tick(60)


        # Update screen ------------------------------------------------------------------------------------------------------------------ #

        #screen.blit(display, [0, 0])
        pygame.display.update()


    pass

# end ------------------------------------------------------------------------------------------------------------------ #
def end():
    global health, life, level, INVENTORY
    
    # Backround ------------------------------------------------------------------------------------------------------------------ #
    BG_0_img = pygame.image.load('data/background/bg_0.png')
    BG_1_img = pygame.image.load('data/background/bg_1.png')
    BG_0 = pygame.transform.scale(BG_0_img, [screen.get_width(), screen.get_height()])
    BG_1 = pygame.transform.scale(BG_1_img, [screen.get_width(), screen.get_height()])

    i = j = 0
    
    restart_button_b = pygame.image.load('data/UI/blue/blue_button00.png')
    restart_button_b_c = pygame.image.load('data/UI/blue/blue_button01.png')
    restart_button_y = pygame.image.load('data/UI/yellow/yellow_button00.png')
    
    click = False
    running = True
    while running:
        
        screen.fill([0,0,0])
        
        # Background ------------------------------------------------------------------------------------------------------------------ #
        if i == BG_0.get_width():
            i = 0
        if j == BG_0.get_width() * 1:
            j = 0

        screen.fill([0,0,0])
        screen.blit(BG_0, [0 - i*0.5, 0])
        screen.blit(BG_0, [0 + BG_0.get_width() - i*0.5, 0])
        screen.blit(BG_1, [0 - i, 0])
        screen.blit(BG_1, [0 + BG_0.get_width() - i, 0])

        j += 0.5
        i += 1
        
        # Tile ------------------------------------------------------------------------------------------------------------------ #
        text_rect = e.text_draw(screen, 'YOU LOSE', 14, [WINDOWN_SIZE[0]/2 - 100, 0], [0, 0], False)
        e.text_draw(screen, 'YOU LOSE', 14, [WINDOWN_SIZE[0]/2 - text_rect.width/2, 90])
        
        
        
        mx, my = pygame.mouse.get_pos()
        
        restart_button = e.UI(restart_button_y, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - restart_button_b.get_width()/2, 200], False)
        restart_button = e.UI(restart_button_y, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - restart_button.width/2, WINDOWN_SIZE[1]/2 - restart_button.height/2], False)
        if not restart_button.collidepoint(mx, my):
            e.UI(restart_button_y, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - restart_button.width/2, WINDOWN_SIZE[1]/2 - restart_button.height/2])
        else:
            if click:
                click_wav.play()
                e.UI(restart_button_b_c, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - restart_button.width/2, WINDOWN_SIZE[1]/2 - restart_button.height/2])
                return True
                # health = 100
                # life = 3
                # INVENTORY = {}
                # if level == 0:
                    # game('tutorial')
                # if level == 1:
                    # game('test')
                # if level == 2:
                    # game('win')
                    
            else:
                e.UI(restart_button_b, screen, [1.5, 1.5], [WINDOWN_SIZE[0]/2 - restart_button.width/2, WINDOWN_SIZE[1]/2 - restart_button.height/2])
        
        text_rect = e.text_draw(screen, 'RESTART', 8, [0, 0], [0, 0],False)
        e.text_draw(screen, 'RESTART', 8, [WINDOWN_SIZE[0]/2 - text_rect.width/2, 251])
        
        click = False
        # Key event ------------------------------------------------------------------------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        clock.tick(60)
        
        pygame.display.update()

#game('trap')#
main_menu()
#end()