import pygame
from pygame import *
import random

#Colors:
black = [0, 0, 0]
white = [255, 255, 255]

#Initialize pygame
pygame.init()

class Paddle(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.height = 80
        self.bisect = self.height / 2
        self.width = 10
        self.color = white
        self.image = pygame.Surface([self.width, self.height])
        self.moving = 0
        self.reset()

    def deflect(self):
        self.paddle_position = self.rect.bottom - ball.rect.center[1]
        if (self.paddle_position > self.bisect):
            self.deflect_angle = ((self.bisect - (self.paddle_position - self.bisect)) / 80.0) #Top half of the paddle, starts to decend from the halfway point down to 0.
        else:
            self.deflect_angle = ((self.paddle_position) / 80.0)
	print self.deflect_angle

    def reset(self):
        if self.player == 1:
            self.position_x = 560
            self.position_y = 250
        if self.player == 2:
            self.position_x = 60
            self.position_y = 250
        self.cords = [self.position_x, self.position_y]
        self.rect = self.image.get_rect(center=self.cords)

    def update(self):
        if (ball.rect.right == self.rect.left + ball.offset_x or ball.rect.left == self.rect.right + ball.offset_x) and ball.rect.colliderect(self.rect): #Ball hits the paddle , the ball.offset_x is to adjust for the fact that if the edges line up exactly at the same pixel coordination, they won't actually collide.
            self.deflect()	
            ball.offset_x = -ball.offset_x
        if self.moving == 1: #Check to see if paddle is moving.
            self.position_y += self.offset
            if self.position_y >= 445:
                self.position_y = 440
            elif self.position_y <= 35:
                self.position_y = 40
            else:
                self.rect.move_ip(0, self.offset)

class Ball(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.height = 10
        self.width = 10
        self.image = pygame.Surface([self.width, self.height])
        self.offset_x = 5
        self.serve = 1 #Player one hits the ball first (right paddle)
        self.reset()
        self.color = white

    def reset(self):
        self.offset_y = random.uniform(5, 6)
        if self.serve == 2:
            self.offset_x = abs(self.offset_x) 
        if self.serve == 1:
            self.offset_x = -self.offset_x
        self.position_x = 320
        self.position_y = 40
        self.cords = [self.position_x, self.position_y]
        self.rect = self.image.get_rect(center=self.cords)

    def update(self):
        self.position_y += self.offset_y
        self.position_x += self.offset_x
        if self.rect.top < window_area.top or self.rect.bottom > window_area.bottom:
            self.offset_y = -self.offset_y
        if self.rect.right > window_area.right or self.rect.left < window_area.left:
            self.offset_x = -self.offset_x
        self.rect.move_ip(self.offset_x, self.offset_y)

class Goal(pygame.sprite.Sprite):
    def __init__(self, player):
        pygame.sprite.Sprite.__init__(self)
        self.player = player
        self.height = window.get_height()
        self.width = 1
        if self.player == 1:
            self.position_x = 625
        if self.player == 2:
            self.position_x = 25
        self.position_y = 0
        self.cords = [self.position_x, self.position_y]
        self.image = pygame.Surface([self.width, self.height])
        self.rect = self.image.get_rect(topleft=self.cords)
        self.window = pygame.display.get_surface()

    def update(self):
        if self.rect.colliderect(ball.rect):
            for paddle in paddles:
                paddle.reset()
            if self.player == 2:
                ball.serve = 2
                score.add(1)
            if self.player == 1:
                ball.serve = 1
                score.add(2)
            ball.reset()


class Score(object):
    def __init__(self):
        self.textpos = [240, 50] 
        self.score = {1: 0, 2: 0}
        self.font = pygame.font.Font(None, 36)
        self.window = pygame.display.get_surface()
        self.update_text()

    def add(self, player):
        self.score[player] += 1 
        self.update_text()

    def reset(self):
        self.score = {1: 0, 2: 0}

    def update_text(self):
        self.text = "%s                       %s" % (str(self.score[1]), str(self.score[2]))

    def render(self):
        render = self.font.render(self.text, 1, white)
        window.blit(render, self.textpos)

# Setup window and sprite grouping
window = pygame.display.set_mode((640, 480))
window_area = pygame.display.get_surface().get_rect()

goal1 = Goal(1)
goal2 = Goal(2)

paddle1 = Paddle(1)
paddle2 = Paddle(2)
paddles = [paddle1, paddle2]

ball = Ball()
score = Score()

allsprites = pygame.sprite.Group()
allsprites.add(paddle1, paddle2, ball, goal1, goal2)

# Initial Draw
window.fill(black)
paddle1.image.fill(paddle1.color)
paddle2.image.fill(paddle2.color)
ball.image.fill(ball.color)
score.render()
allsprites.draw(window)
pygame.display.update()

#Pygame settings
clock = pygame.time.Clock()

def key_check():
    for event in pygame.event.get():
        if event.type == KEYDOWN: 
            if event.key == K_UP:
                paddle1.moving = 1
                paddle1.offset = -5
            if event.key == K_DOWN:
                paddle1.moving = 1
                paddle1.offset = 5
            if event.key == K_a:
                paddle2.moving = 1
                paddle2.offset = -5
            if event.key == K_SEMICOLON:
                paddle2.moving = 1
                paddle2.offset = 5
        if event.type == KEYUP: 
            if event.key == K_UP or event.key == K_DOWN:
                paddle1.moving = 0
            if event.key == K_a or event.key == K_SEMICOLON:
                paddle2.moving = 0

def draw():
        clock.tick(50)
        key_check()
        window.fill(black)
        score.render()
        allsprites.draw(window)
        allsprites.update()
        pygame.display.update()

def main():
    while 1:
        draw()

if __name__ == '__main__':
    main()
