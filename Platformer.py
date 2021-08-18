import pygame, sys, os, time
import DaiEngine as e
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

# LOAD TILES ------------------------------------------------------------------------------------------------------------------ #

tile_index = e.load_tiles()
bug = False

# GAME MAP ------------------------------------------------------------------------------------------------------------------ #
game_map = {}
CHUNK_SIZE = 8
IMG_SIZE = [16, 16]

# Game variable ------------------------------------------------------------------------------------------------------------------ #

player = e.entity('herochar', [0, 0])

moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

true_scroll = [0, 0]

background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

jump_count = 0

# MAIN GAME -------------------------------------------------------------------------------------------------------------------------------#
OBJECT = [] # [obj, status]
num_obj = 0
check = 0

for obj in os.listdir('data/object'):
    obj = obj[:(len(obj) - 4)]
    if obj in os.listdir('data/animation'):
        for status in os.listdir('data/animation/' + obj):
            if status[-4:] != '.png':
                status = status[len(obj) + 1:]
                OBJECT.append([e.object(obj, [26 * num_obj, 9*16 - 40]), status])
                num_obj += 1
            else:
                if check == 0:
                    OBJECT.append([e.object(obj, [26 * num_obj, 9*16 - 40]), 'idle'])
                    num_obj += 1
                    check = 1
        check = 0
    else:
        OBJECT.append([e.object(obj, [26 * num_obj, 9*16 - 40]), 'idle'])
        num_obj += 1

ENTITY = []
num_en = 0
for en in os.listdir('data/animation/entity'):
    for status in os.listdir('data/animation/entity/' + en):
        status = status[len(en) + 1:]
        ENTITY.append([e.entity(en, [26 * num_en, 9*16 - 60]), status])
        num_en += 1

effect_check = 0
#print(len(OBJECT))
while True: 
    #print(player_y_momentum)

    display.fill([0, 0, 0])

    true_scroll[0] += (player.rect.x - true_scroll[0] - display.get_width()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
    true_scroll[1] += (player.rect.y - true_scroll[1] - display.get_height()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Backround ------------------------------------------------------------------------------------------------------------------ #
    # pygame.draw.rect(display,(7,80,75),pygame.Rect(0,120,300,80))
    # for background_object in background_objects:
        # obj_rect = pygame.Rect(background_object[1][0] - scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        # if background_object[0] == 0.5:
            # pygame.draw.rect(display, (14, 222, 150), obj_rect)
        # else:
            # pygame.draw.rect(display, (9, 91, 85), obj_rect)

    # TILE RENDERING ------------------------------------------------------------------------------------------------------------------ #
    
    e.chunk_render(display, WINDOWN_SIZE, SCALE, CHUNK_SIZE, IMG_SIZE, scroll)

    # Move momentum ------------------------------------------------------------------------------------------------------------------ #
    gravity = 0.6
    vel = 3
    jump_power = 8
    if gravity >= 0.5:
        ground = gravity * 3
    else:
        ground = int(round(1 / gravity))
    
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += vel
    if moving_left:
        player_movement[0] -= vel
    player_movement[1] += player_y_momentum
    player_y_momentum += gravity # GRAVITY :))))
    if player_y_momentum > 8:
        player_y_momentum = 10
    
    
    # Action Create ------------------------------------------------------------------------------------------------------------------ #
    if player_movement[0] >= 0:
        player.flip = False
    else:
        player.flip = True
    
    if player_movement[0] > 0 and player_movement[1] == 0:
        player.change_action('run')
    if player_movement[0] < 0 and player_movement[1] == 0:
        player.change_action('run')
    if player_movement[0] == 0 and player_movement[1] == 0:
        player.change_action('idle')
    if player_movement[1] < 0 and jump_count < 2:
        player.change_action('jump_up')
    if player_movement[1] > ground and jump_count == 28:
        player.change_action('jump_down')
    if 28 > jump_count >= 2:
        player.change_action('jump_double')
        jump_count += 1
    
    if player_movement[1] == 0:
        if player.collision['bottom']:
            jump_count = 0
    
    # Move Player ------------------------------------------------------------------------------------------------------------------ #
    if player.status == 'jump_up':
        if effect_check == 0:
            effect_check = 1
            player_effect = e.object('herochar_before_jump_dust', [player.rect.x, player.rect.y])
        effect_rect = player_effect.get_rect('herochar_before_jump_dust')
        pygame.draw.rect(display, [255,0,255], effect_rect)
        
        if air_timer < 8 or 2 <= jump_count < 11:
            player_effect.load_animation(display, 'herochar_before_jump_dust', scroll)
        else:
            effect_check = 0
    else:
        effect_check = 0
        pass
    
    player.move(player_movement)

    if player.collision['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1
    if player.collision['top']:
        player_y_momentum = 0
    
    # Render entity ------------------------------------------------------------------------------------------------------------------ #
    display_render = pygame.Rect(scroll[0], scroll[1], WINDOWN_SIZE[0] / SCALE, WINDOWN_SIZE[1] / SCALE)
    
    text = ['Adventure time', 3]
    text_rect = e.text_draw(display, text[0], text[1], [0, 9*16 - 90], scroll,False)
    if display_render.colliderect(text_rect):
        e.text_draw(display, text[0], text[1], [0, 9*16 - 90], scroll)
    
    pygame.draw.rect(display, [255,0,0], player.rect, 2)
    for obj in OBJECT:
        if display_render.colliderect(obj[0].get_rect(obj[1])):
            obj[0].load_animation(display, obj[1], scroll)
        #pygame.draw.rect(display, [255,0,0], obj[0].get_rect(obj[1], scroll))

    for entity in ENTITY:
        if display_render.colliderect(entity[0].rect):
            entity[0].load_animation(display, entity[1], scroll)

    player.load_animation(display, player.status,scroll)
    pygame.draw.rect(display, [255,0,0], player.rect, 1)
    
            # print(obj[0].ID)
    # print('-----------------------------------------')
    
    # Update key ------------------------------------------------------------------------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            WINDOWN_SIZE = [event.w, event.h]
            #display = pygame.Surface([WINDOWN_SIZE[0]/SCALE, WINDOWN_SIZE[1]/SCALE])
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if jump_count < 2 :
                    print('jump:', jump_count)
                    player_y_momentum = - jump_power
                    jump_count += 1
                    print(jump_count)
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    
    #e.text_draw(display, text, size, [0, 9*16 - 50], True, True)#[WINDOWN_SIZE[0] / 2 - text_size[0] - 2, 70], True, True)

    surf = pygame.transform.scale(display, WINDOWN_SIZE)
    screen.blit(surf, [0, 0])
    
    # Render text ------------------------------------------------------------------------------------------------------------------ #
    fr = clock.get_fps()
    e.text_draw(screen, str(int(fr)), 2, [0, 0])
    # Update game ------------------------------------------------------------------------------------------------------------------ #
    pygame.display.update()
    clock.tick(e.FPS)