import pygame
import sys
import os
import time
import data.DaiEngine as e
from pygame.locals import *

# Setting enviromental ------------------------------------------------------------------------------------------------------------------ #
pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption("Platformer")

WINDOWN_SIZE = (960, 540)

screen = pygame.display.set_mode(WINDOWN_SIZE,  pygame.RESIZABLE, 32)


SCALE = 3
display = pygame.Surface([640 / 2, 360 /2 ])#[WINDOWN_SIZE[0]/SCALE, WINDOWN_SIZE[1]/SCALE])

# Setting data base ------------------------------------------------------------------------------------------------------------------ #
animation = e.animation()
animation.create_database()
database = e.create_database() # ID: [img_loaded, img_name, type] type can be obj, tile, entity

# LOAD TILES ------------------------------------------------------------------------------------------------------------------ #
tile_index = e.load_tiles()
bug = False

# GAME MAP ------------------------------------------------------------------------------------------------------------------ #
game_map = {}
game_map = e.load_map('fall')
CHUNK_SIZE = 8
IMG_SIZE = [16, 16]

# Game variable ------------------------------------------------------------------------------------------------------------------ #

moving_right = False
moving_left = False
attack = False

air_timer = 0

true_scroll = [0, 0]

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

jump_count = 0
check = True

# List of entity, object, efffect ------------------------------------------------------------------------------------------------------------------ #
ENTITY = []
OBJECT = []
COIN = []

for type_ in game_map:
    if type_ == 'entity':
        for data in game_map[type_]:
            if data[1] == 91:
                player = e.entity(data[2], data[0])
            else:
                ENTITY.append(e.entity(data[2], data[0]))
    elif type_ == 'object':
        for data in game_map[type_]:
            if data[1] == 83:
                OBJECT.append([e.object(data[2], data[0]), 'closed'])
            elif data[1] == 65:
                OBJECT.append([e.object(data[2], data[0]), 'on_ground'])
            elif data[1] == 67:
                COIN.append([e.object(data[2], data[0]), 'idle'])
            else:
                OBJECT.append([e.object(data[2], data[0]), 'idle'])

EFFECT = [] # [object, duration]
hit_sparkle = False

vel = 3
jump_power = 5.1


coin = 0
# MAIN GAME -------------------------------------------------------------------------------------------------------------------------------#
while True: 

    display.fill([0, 0, 0])

    true_scroll[0] += (player.rect.x - true_scroll[0] - display.get_width()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
    true_scroll[1] += (player.rect.y - true_scroll[1] - display.get_height()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Backround ------------------------------------------------------------------------------------------------------------------ #
    pygame.draw.rect(display , (7,80,75), pygame.Rect(0,120,300,80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)

    # TILE RENDERING ------------------------------------------------------------------------------------------------------------------ #
    #e.chunk_render(display, WINDOWN_SIZE, SCALE, CHUNK_SIZE, IMG_SIZE, scroll)
    e.map_render(display, scroll)

    # Move momentum ------------------------------------------------------------------------------------------------------------------ #

    gravity = 0.5
    ground = 1.5
    
    for entity in ENTITY:
        if entity.ID == 'slime':
            entity.offset = [0, -8]
        entity.movement = [0, 0]
        entity.movement[1] += entity.y_momentum
        entity.y_momentum = round(entity.y_momentum + gravity, 1)
        if entity.y_momentum > 10:
            entity.y_momentum = 10
    
    player.movement = [0, 0]
    
    if moving_right:
        player.movement[0] += vel
    if moving_left:
        player.movement[0] -= vel
    
    player.movement[1] += player.y_momentum
    player.y_momentum = round(player.y_momentum + gravity, 1) # GRAVITY :))))
    if player.y_momentum > 10:
        player.y_momentum = 10
    
    
    # Action center ------------------------------------------------------------------------------------------------------------------ #
    prev_status = player.status 
    
    if not player.attack:
        if player.movement[0] > 0:
            player.flip = False
        elif player.movement[0] < 0 :
            player.flip = True
        #print(player_movement[1], ground)
        if player.movement[0] != 0 and player.movement[1] == 0:
            player.change_action('run')
        if player.movement[0] == 0 and player.movement[1] == 0:
            player.change_action('idle')
        if player.movement[1] < 0 and jump_count < 2:
            player.change_action('jump_up')
        if player.movement[1] > ground and ( jump_count == 18 or jump_count == 1) or player.movement[1] > ground or player.collision['top']:
            player.change_action('jump_down')
        if 18 > jump_count >= 2:
            if player.collision['top']:
                check = False
            if check:
                player.change_action('jump_double')
                jump_count += 1

    if player.movement[1] == 0:
        if player.collision['bottom']:
            jump_count = 0
            check = True
    
    now_status = player.status

    if player.attack:
        attack_rect = player.attack_rect(16, [-16, 0])   
        # if player.attack:
            # pygame.draw.rect(display, [255,0,255], [attack_rect.x + 50, attack_rect.y - 9999, attack_rect.width, attack_rect.height], 1)
    
    # pygame.draw.rect(display, [255,255,255], [player.rect.x + 50, player.rect.y - 9999, player.rect.width, player.rect.height])
    # pygame.draw.rect(display, [255,0,255], [player.x + 50, player.y - 9999, player.rect.width, player.rect.height], 1)


    # Create effect ------------------------------------------------------------------------------------------------------------------ #
    if prev_status != 'jump_up' and now_status == 'jump_up' or ( prev_status == 'jump_up' and now_status == 'jump_double'):
        EFFECT.append([e.object('herochar_before_jump_dust', [player.rect.x, player.rect.y]), 8])
    if prev_status == 'jump_down' and now_status != 'jump_down':
        EFFECT.append([e.object('herochar_after_jump_dust', [player.rect.x, player.rect.y]), 8])
    

    # Move Player ------------------------------------------------------------------------------------------------------------------ #
    player.move(player.movement)
    if player.collision['bottom']:
        player.y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1
    if player.collision['top']:
        player.y_momentum = 0
    
    # Render entity ------------------------------------------------------------------------------------------------------------------ #
    display_render = pygame.Rect(scroll[0], scroll[1], WINDOWN_SIZE[0] / SCALE, WINDOWN_SIZE[1] / SCALE)
    text = ['Adventure time', 3]
    text_pos = [0, - 150]
    text_rect = e.text_draw(display, text[0], text[1], text_pos, scroll,False)
    if display_render.colliderect(text_rect):
        e.text_draw(display, text[0], text[1], text_pos, scroll)
    
    # Object system ------------------------------------------------------------------------------------------------------------------ #
    for obj in OBJECT:
        if display_render.colliderect(obj[0].get_rect(obj[1])):
            obj[0].load_animation(display, obj[1], scroll)
    
    # Coin system ------------------------------------------------------------------------------------------------------------------ #
    for coin_o in COIN:
        if player.attack:
            if attack_rect.colliderect(coin_o[0].get_rect(coin_o[1])):
                coin_o[0].change_action('pickup', coin_o[0].x, coin_o[0].y - 8)
        elif player.rect.colliderect(coin_o[0].get_rect(coin_o[1])):
            coin_o[0].change_action('pickup', coin_o[0].x, coin_o[0].y - 8)
        if display_render.colliderect(coin_o[0].get_rect(coin_o[1])):
            if coin_o[0].status == 'idle':
                coin_o[0].load_animation(display, 'idle', scroll)
            else:
                if not coin_o[0].one_time('pickup'):
                    coin_o[0].load_animation(display, coin_o[0].status, scroll)
                else:
                    COIN.remove(coin_o)
                    coin += 1

    # Entity system ------------------------------------------------------------------------------------------------------------------ #
    for entity in ENTITY:
       # if display_render.colliderect(entity.rect):
            # Entity action ------------------------------------------------------------------------------------------------------------------ #
        if entity.collision['bottom']:
            entity.y_momentum = 0
        if entity.collision['top']:
            entity.y_momentum = 0
        
        if player.attack  and attack_rect.colliderect(entity.rect):
            pass
        else:
            if entity.ID != 'slime':
                if entity.ID != 'bomber_goblin':
                    if entity.flip:
                        if entity.check_fall():
                            entity.movement[0] = -2
                            entity.flip = False
                        elif not entity.collision['left']:
                            entity.movement[0] = -2
                        else:
                            entity.flip = False
                    else:
                        if entity.check_fall():
                            entity.movement[0] = 2
                            entity.flip = True
                        elif not entity.collision['right']:
                            entity.movement[0] = 2
                        else:
                            entity.flip = True
            else:
                if not entity.flip:
                    if not entity.collision['left']:
                        entity.movement[0] = -2
                    else:
                        entity.flip = True
                else:
                    if not entity.collision['right']:
                        entity.movement[0] = 2
                    else:
                        entity.flip = False
    
        entity.move(entity.movement)
       # pygame.draw.rect(display, [255,0,255], [player.x - scroll[0], player.y - scroll[1], 16, 16])
        
        # Entity move ------------------------------------------------------------------------------------------------------------------ #
        
        
        if not player.attack:
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
        elif player.attack and attack_rect.colliderect(entity.rect):
            entity.one_time('hit')
            if hit_sparkle:
                EFFECT.append([e.object('herochar_hit_sparkle', [entity.rect.x, entity.rect.y]), 8])
                hit_sparkle = False
        
        # Entity load animation ------------------------------------------------------------------------------------------------------------------ #
        entity.load_animation(display, entity.status, scroll)
    
    player.load_animation(display, player.status, scroll)
    
    # Effect render ------------------------------------------------------------------------------------------------------------------ #
    for effect in EFFECT:
        if effect[1] != 0:
            effect[0].load_animation(display, effect[0].status, scroll)
            effect[1] -= 1
        else:
            EFFECT.pop(EFFECT.index(effect))
    

    # Update key ------------------------------------------------------------------------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            WINDOWN_SIZE = [event.w, event.h]
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                player.attack = True
                hit_sparkle = True
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if jump_count < 2:
                    if jump_count == 0:
                        player.y_momentum = - jump_power
                    else:
                        player.y_momentum = - jump_power + 1
                    jump_count += 1
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOWN_SIZE)
    screen.blit(surf, [0, 0])
    
    # Render text ------------------------------------------------------------------------------------------------------------------ #
    fr = clock.get_fps()
    e.text_draw(screen, str(int(fr)), 2, [0, 0])

    # Update game ------------------------------------------------------------------------------------------------------------------ #
    pygame.display.update()
    clock.tick(e.FPS)