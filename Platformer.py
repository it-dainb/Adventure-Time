import pygame, sys, os
import DaiEngine as e
from pygame.locals import *

# Setting enviromental ------------------------------------------------------------------------------------------------------------------ #
pygame.init()
clock = pygame.time.Clock()

pygame.display.set_caption("Platformer")

WINDOWN_SIZE = (750, 500)

screen = pygame.display.set_mode(WINDOWN_SIZE,  pygame.RESIZABLE, 32)


SCALE = 2.5
display = pygame.Surface([WINDOWN_SIZE[0]/SCALE, WINDOWN_SIZE[1]/SCALE])

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

player_action = 'herochar_idle'
player_flip = False

moving_right = False
moving_left = False

player_y_momentum = 0
air_timer = 0

true_scroll = [0, 0]

player_rect = pygame.Rect(0, 0, 16, 16)
background_objects = [[0.25,[120,10,70,400]],[0.25,[280,30,40,400]],[0.5,[30,40,40,400]],[0.5,[130,90,100,400]],[0.5,[300,80,120,400]]]

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

#print(len(OBJECT))
frame = 0
while True: 
    #print(player_y_momentum)
    
    display.fill([102, 255, 255])

    true_scroll[0] += (player_rect.x - true_scroll[0] - display.get_width()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
    true_scroll[1] += (player_rect.y - true_scroll[1] - display.get_height()/2) * ( 10 * (e.img_FPS / e.FPS) ) * 1 / 20
    scroll = true_scroll.copy()
    scroll[0] = int(scroll[0])
    scroll[1] = int(scroll[1])

    # Backround ------------------------------------------------------------------------------------------------------------------ #
    pygame.draw.rect(display,(7,80,75),pygame.Rect(0,120,300,80))
    for background_object in background_objects:
        obj_rect = pygame.Rect(background_object[1][0] - scroll[0]*background_object[0],background_object[1][1]-scroll[1]*background_object[0],background_object[1][2],background_object[1][3])
        if background_object[0] == 0.5:
            pygame.draw.rect(display, (14, 222, 150), obj_rect)
        else:
            pygame.draw.rect(display, (9, 91, 85), obj_rect)

    # TILE RENDERING ------------------------------------------------------------------------------------------------------------------ #
    
    tile_rects = e.chunk_render(display, WINDOWN_SIZE, SCALE, CHUNK_SIZE, IMG_SIZE, scroll)

    # Move momentum ------------------------------------------------------------------------------------------------------------------ #
    gravity = 0.4
    
    if gravity >= 0.5:
        ground = gravity * 2
    else:
        ground = int(1 / gravity)
    
    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += gravity # GRAVITY :))))
    if player_y_momentum > 8:
        player_y_momentum = 10
    
    # Action Create ------------------------------------------------------------------------------------------------------------------ #
    if player_movement[0] > 0:
        player_action, frame = animation.change_action(player_action, frame, 'herochar_run')
        player_flip =False
    if player_movement[0] < 0:
        player_action, frame = animation.change_action(player_action, frame, 'herochar_run')
        player_flip = True
    if player_movement[0] == 0:
        player_action, frame = animation.change_action(player_action, frame, 'herochar_idle')
    if player_movement[1] < 0:
        player_action, player_frame = animation.change_action(player_action, frame, 'herochar_jump_up')
    if player_movement[1] > ground:
        player_action, frame = animation.change_action(player_action, frame, 'herochar_jump_down')

    # Move Player ------------------------------------------------------------------------------------------------------------------ #
    #print(player_y_momentum)
    player_rect, collitions = e.move(player_rect, player_movement, tile_rects)

    if collitions['bottom']:
        player_y_momentum = 0
        air_timer = 0
    else:
        air_timer += 1
    if collitions['top']:
        player_y_momentum = 0
    
    # Render entity ------------------------------------------------------------------------------------------------------------------ #
    
    if frame > len(e.animation_database[player_action]) - 1:
        frame = 0
    
    display_render = pygame.Rect(scroll[0], scroll[1], WINDOWN_SIZE[0]/SCALE, WINDOWN_SIZE[1]/SCALE)
    for obj in OBJECT:
        if display_render.colliderect(obj[0].get_rect(obj[1])):
            obj[0].load_animation(display, obj[1], scroll)

    player_image = animation.load_animation(display, player_action, frame, [player_rect.x - scroll[0], player_rect.y - scroll[1]], player_flip)

    player_rect = pygame.Rect(player_rect.x, player_rect.y, player_image.get_width(), player_image.get_height())
    
            # print(obj[0].ID)
    # print('-----------------------------------------')

    # Update key ------------------------------------------------------------------------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == VIDEORESIZE:
            WINDOWN_SIZE = [event.w, event.h]
            display = pygame.Surface([WINDOWN_SIZE[0]/SCALE, WINDOWN_SIZE[1]/SCALE])
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_UP:
                if air_timer < 8:
                    player_y_momentum = - gravity * 15
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False
    
    surf = pygame.transform.scale(display, WINDOWN_SIZE)
    screen.blit(surf, [0, 0])
    
    # Render text ------------------------------------------------------------------------------------------------------------------ #
    text = 'Adventure time'
    size = 2
    text_size = e.text_draw(screen, text, size, [10, 0], False)
    e.text_draw(screen, text, size,[WINDOWN_SIZE[0] / 2 - text_size[0] - 2, 70])
    fr = clock.get_fps()
    e.text_draw(screen, str(int(fr)), 1, [0, 0])
    # Update game ------------------------------------------------------------------------------------------------------------------ #
    pygame.display.update()
    clock.tick(e.FPS)
    frame += 1