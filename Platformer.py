import pygame
import sys
import os
import time
import math
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
game_map = e.load_map('bomb')
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

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

jump_count = 0
check = True

# List of entity, object, efffect ------------------------------------------------------------------------------------------------------------------ #
ENTITY = []
OBJECT = []
COIN = []
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
            if data[1] == 82:
                OBJECT.append([e.object(data[2], data[0]), 'closed'])
                strange_door_rect = pygame.Rect(OBJECT[-1][0].get_rect('closed'))
                strange_door_ex = True
            elif data[1] == 65:
                OBJECT.append([e.object(data[2], data[0]), 'on_ground'])
            elif data[1] == 67:
                COIN.append([e.object(data[2], data[0]), 'idle'])
            else:
                OBJECT.append([e.object(data[2], data[0]), 'idle'])
                
                
            

EFFECT = [] # [object, duration]
hit_sparkle = False
hit_player = False

vel = 3
entity_vel = 2
jump_power = 5.1


coin = 0

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
        bg_rect = pygame.Rect(background_object[1][0] - scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), bg_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), bg_rect)

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
        if player.status != 'run':
            player.movement[0] += vel - 1
        else:
            player.movement[0] += vel
    if moving_left:
        if player.status != 'run':
            player.movement[0] -= vel - 1
        else:
            player.movement[0] -= vel
    
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
        attack_rect = player.attack_rect(14, [-16, 0])   
        # if player.attack:
            # pygame.draw.rect(display, [255,0,255], [attack_rect.x + 50, attack_rect.y - 9999, attack_rect.width, attack_rect.height], 1)
    
    # pygame.draw.rect(display, [255,255,255], [player.rect.x + 50, player.rect.y - 9999, player.rect.width, player.rect.height])
    # pygame.draw.rect(display, [255,0,255], [player.x + 50, player.y - 9999, player.rect.width, player.rect.height], 1)

    # Flash skill ------------------------------------------------------------------------------------------------------------------ #
    if flash:
       # if time.time() - flash_start >= 5:
            for i in range(50):
                if player.flip:
                    if strange_door_ex:
                        if player.rect.colliderect(strange_door_rect):
                            if player.movement[0] > 0:
                                player.rect.right = strange_door_rect.left
                            if player.movement[0] < 0:
                                player.rect.left = strange_door_rect.right
                            if strange_door_rect.x <= player.x + player.img.get_width() <= strange_door_rect.x + strange_door_rect.width and  strange_door_rect.y >= player.y:
                                player.rect.bottom = strange_door_rect.top
                    else:
                        player.move([-2, 0])
                else:
                    if strange_door_ex:
                        if player.rect.colliderect(strange_door_rect):
                            if player.movement[0] > 0:
                                player.rect.right = strange_door_rect.left
                            if player.movement[0] < 0:
                                player.rect.left = strange_door_rect.right
                            if strange_door_rect.x <= player.x + player.img.get_width() <= strange_door_rect.x + strange_door_rect.width and  strange_door_rect.y >= player.y:
                                player.rect.bottom = strange_door_rect.top
                    else:
                        player.move([ 2, 0])
                if i % 10 == 0:
                    player.load_animation(display, 'hit', scroll)
                #pygame.display.update()
            flash_start = time.time()
            
    
    
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
        if not get:
            obj_rect = obj[0].get_rect(obj[1])
            obj[0].status = obj[1]
        else:
            obj_rect = obj[0].get_rect(obj[0].status)
        if display_render.colliderect(obj_rect):
            
            # Buttom ------------------------------------------------------------------------------------------------------------------ #
            if obj[0].ID == 'buttom':
                if player.rect.colliderect(obj_rect):
                    obj[0].change_action('pressed')
                    buttom_active = True
                    obj[0].load_animation(display, obj[0].status, scroll)
                else:
                    obj[0].change_action('idle')
                    buttom_active = False
                    obj[0].load_animation(display, obj[0].status, scroll)
            
            # Lever ------------------------------------------------------------------------------------------------------------------ #
            elif obj[0].ID == 'lever':
                if player.attack:
                    if ( player.rect.colliderect(obj_rect) or attack_rect.colliderect(obj_rect) ):
                        if hit_lever == 0:
                            if (player.rect.x <= obj_rect.x + obj_rect.width / 2 and not player.flip) or (player.rect.x >= obj_rect.x + obj_rect.width / 2 and player.flip) or obj_rect.x - 10 <= player.rect.x <= obj_rect.x + obj_rect.width:
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
                        
                    if not obj[0].one_time('opening') and not strange_door_opening:
                        obj[0].load_animation(display, 'opening', scroll)
                        strange_door_rect.y += 1
                        strange_door_rect.height -= 1
                       # obj[0].y += 1
                    else:
                        strange_door_rect.top = obj_rect.bottom
                        strange_door_opening = True
                        strange_door_closing = False
                        strange_door_closed =False
                
                # Closing animation ------------------------------------------------------------------------------------------------------------------ #
                elif not strange_door_closed:
                    if not obj[0].one_time('closing') and not strange_door_closing:
                        obj[0].load_animation(display, 'closing', scroll)
                        strange_door_rect.y -= 1
                        strange_door_rect.height += 1
                    else:
                        strange_door_rect.top = obj_rect.top
                        strange_door_opening = False
                        strange_door_closing = True
                        strange_door_closed = True
                
                # Closed  ------------------------------------------------------------------------------------------------------------------ #
                else:
                    strange_door_rect = obj_rect
                    obj[0].load_animation(display, 'closed', scroll)
                    strange_door_closed = True
            
            # Check spawn point ------------------------------------------------------------------------------------------------------------------ #
            elif obj[0].ID == 'save_point':
                if player.rect.colliderect(obj_rect) and not saved:
                    saved = True
                    saving = True
                if saving:
                    if not obj[0].one_time('saving'):
                        obj[0].load_animation(display, 'saving', scroll)
                        # Still dev
                    else:
                        saving = False
                else:
                    obj[0].load_animation(display, 'idle', scroll)
            
            # Loot box ------------------------------------------------------------------------------------------------------------------ #
            elif obj[0].ID == 'loot_box':
                if player.attack and not loot_box_opened:
                    if ( player.rect.colliderect(obj_rect) or attack_rect.colliderect(obj_rect) ):
                        if not loot_box:
                            loot_box = True
                if loot_box:                
                    if not obj[0].one_time('opening', [0, -2]):
                        obj[0].load_animation(display, 'opening', scroll)
                    else:
                        loot_box = False
                        loot_box_opened = True
                elif loot_box_opened:
                    obj[0].load_animation(display, 'opened', scroll)
                else:
                    obj[0].load_animation(display, 'idle', scroll)
            
            # Vase ------------------------------------------------------------------------------------------------------------------ #
            elif obj[0].ID == 'vase':
                if player.attack and obj[0].attack == 0:
                    if player.rect.colliderect(obj_rect) or attack_rect.colliderect(obj_rect):
                        obj[0].attack = 1
                if obj[0].attack == 1:
                    if not obj[0].one_time('breaking'):
                        obj[0].load_animation(display, 'breaking', scroll)
                    else:
                        obj[0].attack = 2
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
                obj[0].move([0, 4])
                obj[0].load_animation(display, 'idle', scroll)
                if obj[0].get_rect('idle').colliderect(player.rect) and not obj[0].collision['bottom'] and not obj[0].attack != 0:
                    hit_player = True
                    hit_sparkle = True
                    obj[0].attack = 1
                
            # # Trap_suspended ------------------------------------------------------------------------------------------------------------------ #
            elif obj[0].ID == 'trap_suspended':
                obj[0].load_animation(display, obj[1], scroll)
                obj[0].w_x = 0.117
                obj[0].w_y = 0.235
                if obj[0].time == 54:
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
                        pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)
                    # pass
            
            # Another stuff ------------------------------------------------------------------------------------------------------------------ #
            else:
                obj[0].load_animation(display, obj[1], scroll)
        
        # Player can pass strange door ------------------------------------------------------------------------------------------------------------------ #
        if obj[0].ID == 'strange_door_rect':
            if player.rect.colliderect(strange_door_rect):
                if player.movement[0] > 0:
                    player.rect.right = strange_door_rect.left
                if player.movement[0] < 0:
                    player.rect.left = strange_door_rect.right
                if strange_door_rect.x <= player.x + player.img.get_width() <= strange_door_rect.x + strange_door_rect.width and  strange_door_rect.y >= player.y:
                    player.rect.bottom = strange_door_rect.top

        # Bomb hit player ------------------------------------------------------------------------------------------------------------------ #
        if obj[0].ID == 'bomb':
            if obj[0].attack == 1:
                pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)
                if player.rect.colliderect(bomb_area):
                    hit_sparkle = True
                    hit_player = True
                    obj[0].attack = 2
                else:
                    obj[0].attack = 2
        
        if hit_player:# and (attack_area.colliderect(player.rect)):
            if player.one_time('hit'):
                #print('true')
                hit_player = False
            if hit_sparkle:
                if obj[0].ID == 'bomb':
                    if player.x >= obj[0].rect.x + obj[0].rect.width / 2:
                        print('true')
                        player.move([ 20, 0])
                    else:
                        print('false')
                        player.move([ - 20, 0])
                elif obj[0].ID == 'spikes_trap':
                    player.move([0, 10])
                elif obj[0].ID == 'trap_suspended':
                    #print(player.x ,trap_suspended_rect.x + trap_suspended_rect.width)
                    if player.x >= trap_suspended_rect.x: #+ trap_suspended_rect.width:
                        player.move([20, 0])
                    else:
                        player.move([-20, 0])
                    
                # else:
                    # if not entity.flip:
                        # player.move([10, 0])
                    # else:
                        # player.move([ -10, 0])
                EFFECT.append([e.object('herochar_hit_sparkle', [player.rect.x, player.rect.y]), 8])
                hit_sparkle = False
        
        #pygame.draw.rect(display, [255,255,0], [strange_door_rect.x - scroll[0], strange_door_rect.y - scroll[1], strange_door_rect.width, strange_door_rect.height], 2)
        pygame.draw.rect(display, [255,0,0], [obj_rect.x - scroll[0], obj_rect.y - scroll[1], obj_rect.width, obj_rect.height], 1)
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
                    coin_o[0].load_animation(display, coin_o[0].status, scroll)
                else:
                    COIN.remove(coin_o)
                    coin += 1

    # Entity system ------------------------------------------------------------------------------------------------------------------ #
    for entity in ENTITY:
        if entity.rect.colliderect(display_render):
            # Entity action ------------------------------------------------------------------------------------------------------------------ #
            if entity.collision['bottom']:
                entity.y_momentum = 0
            if entity.collision['top']:
                entity.y_momentum = 0
            
            # Logic enemy ------------------------------------------------------------------------------------------------------------------ #
            attack_area = entity.attack_area(2)
            vision_area = entity.vision_area()
            pygame.draw.rect(display, [255,0,0], [vision_area.x - scroll[0], vision_area.y - scroll[1], vision_area.width, vision_area.height], 1)
            pygame.draw.rect(display, [255,255,0], [attack_area.x - scroll[0], attack_area.y - scroll[1], attack_area.width, attack_area.height], 1)
            
            # Pause animation when attacked by player ------------------------------------------------------------------------------------------------------------------ #
            if player.attack and (attack_rect.colliderect(entity.rect)  or player.rect.colliderect(entity.rect)):
                pass
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
                if player.rect.colliderect(vision_area) and entity.ID != 'bomber_goblin':
                    
                    # Attack Player ------------------------------------------------------------------------------------------------------------------ #
                    if player.rect.colliderect(attack_area) and entity.attack_timer > 15 and not flash:
                        print('true')
                        entity.attack = True
                        entity.attack_timer = 0
                        hit_sparkle = True
                        hit_player = True
                        if player.x + player.rect.width / 2>= entity.x + attack_area.width / 2:
                            entity.flip = False
                        else:
                            entity.flip = True
                        pass
                    else:
                        if player.x < entity.x:
                            entity.movement[0] = -2
                            entity.flip = True
                        elif player.x > entity.x:
                            entity.movement[0] = 2
                            entity.flip = False
                else:
                    # Return ------------------------------------------------------------------------------------------------------------------ #
                    if entity.ID != 'slime':
                        if entity.ID != 'bomber_goblin':
                            if entity.flip:
                                if entity.check_fall():
                                    entity.movement[0] = - entity_vel
                                    entity.flip = False
                                elif not entity.collision['left']:
                                    entity.movement[0] = - entity_vel
                                else:
                                    entity.flip = False
                            else:
                                if entity.check_fall():
                                    entity.movement[0] = entity_vel
                                    entity.flip = True
                                elif not entity.collision['right']:
                                    entity.movement[0] = entity_vel
                                else:
                                    entity.flip = True
                    
                    # Throw bomb to player ------------------------------------------------------------------------------------------------------------------ #
                    if entity.ID == 'bomber_goblin':
                        if player.x + player.rect.width / 2>= entity.x + attack_area.width / 2:
                            entity.flip = False
                        else:
                            entity.flip = True     
                            
                        if PROJECTILE == {}:
                            PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 0, 0]
                        if entity not in PROJECTILE:
                            PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 0, 0]
                        
                        if PROJECTILE[entity][1] != 0:
                            x, y, land = PROJECTILE[entity][1].throw(PROJECTILE[entity][0], entity)
                            if PROJECTILE[entity][-1] == 0:
                                PROJECTILE[entity].append(e.object('bomb', [x, y]))
                            else:
                                bomb = PROJECTILE[entity][-1]
                                if bomb.collision['bottom']:
                                    land = True
                                if bomb.attack == 0:
                                    bomb.load_animation(display, 'thrown', scroll)
                                    bomb.attack = 1
                                else:
                                    if bomb.attack == 1:
                                        if land:
                                            if not bomb.one_time('on_ground'):
                                                bomb.load_animation(display, 'on_ground', scroll)
                                            else:
                                                PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 0, 0]
                                                bomb_area = bomb.attack_area([16, 16])
                                                EFFECT.append([e.object('explosion', [bomb.x - 13, bomb.y - 24]), 30])
                                                pygame.draw.rect(display, [255,255,0], [bomb_area.x - scroll[0], bomb_area.y - scroll[1], bomb_area.width, bomb_area.height], 1)
                                                
                                                if player.rect.colliderect(bomb_area):
                                                    hit_sparkle_bomb = True
                                                    hit_player = True
                                        
                                        else:
                                            if bomb.collision['left'] or bomb.collision['right']:
                                                bomb.time = 1
                                            if bomb.time == 0:
                                                #print('true')
                                                bomb.move([x - bomb.x, y - bomb.y])#, display, scroll)
                                            else:
                                                bomb.move([0, y - bomb.y])#, display, scroll)
                                        
                                            bomb.load_animation(display, 'thrown', scroll)
                                        
                                if bomb.y > player.y * 2:
                                    PROJECTILE[entity] = [[player.x, player.y, player.rect.width, player.rect.height], 0, 0]

                    else:   
                        #entity.offset = [0, -8]
                        if not entity.flip:
                            if entity.check_fall():
                                entity.movement[0] = - entity_vel
                                entity.flip = True
                            elif not entity.collision['left']:
                                entity.movement[0] = - entity_vel
                            else:
                                entity.flip = True
                        else:
                            if entity.check_fall():
                                entity.movement[0] = entity_vel
                                entity.flip = False
                            elif not entity.collision['right']:
                                entity.movement[0] = entity_vel
                            else:
                                entity.flip = False

            entity.move(entity.movement)
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
                    if not player.flip:
                        entity.move([ 10, 0])
                    else:
                        entity.move([ -10, 0])
                    EFFECT.append([e.object('herochar_hit_sparkle', [entity.rect.x, entity.rect.y]), 8])
                    hit_sparkle = False
            
            # Player HIT ------------------------------------------------------------------------------------------------------------------ #
            if hit_player:# and (attack_area.colliderect(player.rect)):
                if player.one_time('hit'):
                    #print('true')
                    hit_player = False
                    entity.attack = False
                if hit_sparkle:
                    if not entity.flip:
                        player.move([10, 0])
                    else:
                        player.move([ -10, 0])
                    EFFECT.append([e.object('herochar_hit_sparkle', [player.rect.x, player.rect.y]), 8])
                    hit_sparkle = False
                elif hit_sparkle_bomb:
                    if player.x >= bomb_area.x + bomb_area.width / 2:
                        player.move([ 20, 0])
                    else:
                        player.move([ - 20, 0])
            
                    EFFECT.append([e.object('herochar_hit_sparkle', [player.rect.x, player.rect.y]), 8])
                    hit_sparkle_bomb = False

        # Entity load animation ------------------------------------------------------------------------------------------------------------------ #
        entity.load_animation(display, entity.status, scroll)
    
    for pro in PROJECTILE:
        if PROJECTILE[pro][1] == 0:
            PROJECTILE[pro][1] = e.projectile()
    
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
    
    # Update key ------------------------------------------------------------------------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            WINDOWN_SIZE = [event.w, event.h]
        if event.type == KEYDOWN:
            if event.key == K_SPACE:
                if not hit_player and player.attack_timer > 15:
                    player.attack = True
                    player.attack_timer = 0
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
            if event.key == K_f:
                flash = True
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