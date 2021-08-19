import pygame
import sys
import os
import data.DaiEngine as e
from pygame.locals import *

# Setting envoroment ------------------------------------------------------------------------------------------------------------------ #
pygame.init()

WINDOWN_SIZE = [900, 600]

screen = pygame.display.set_mode(WINDOWN_SIZE, pygame.RESIZABLE)

display_tile = [WINDOWN_SIZE[0] / 5, WINDOWN_SIZE[1]]
display_map = [WINDOWN_SIZE[0] * 4 / 5, WINDOWN_SIZE[1]]

tile_index = e.load_tiles()
print(tile_index)

# Main game ------------------------------------------------------------------------------------------------------------------ #
while True:
    screen.fill([0,0,0])
    
# Update keys ------------------------------------------------------------------------------------------------------------------ #    
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    
    pygame.display.update()
