import pygame

pygame.init()

window = pygame.display.set_mode((640, 480))
pygame.key.set_repeat(1, 10)

while 1:
    for event in pygame.event.get():
        print event
