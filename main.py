import pygame
from pygame.locals import *

pygame.init()
import random  # NEW

# obstacle variables
obstacle_width = 70
obstacle_gap = 180  # vertical space between top and bottom seaweed
obstacle_frequency = 1500  # milliseconds
last_obstacle_time = pygame.time.get_ticks()
obstacles = []

clock = pygame.time.Clock()
fps = 60

screen_width = 500
screen_height = 500

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dizzy Dory')

# game variables
bg_scroll = 0
scroll_speed = 4

# load and scale background
bg = pygame.image.load('bg.png').convert()
bg = pygame.transform.scale(bg, (screen_width, screen_height))


# FISH CLASS
class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'fish{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (60, 45))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.velocity = 0
        self.gravity = 0.5

    def update(self):
        # animation
        self.counter += 1
        flap_cooldown = 5
        if self.counter > flap_cooldown:
            self.counter = 0
            self.index += 1
            if self.index >= len(self.images):
                self.index = 0
        self.image = self.images[self.index]

        # gravity
        self.velocity += self.gravity
        self.rect.y += self.velocity

        # top/bottom screen boundaries
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

# function to create seaweed obstacles
def create_obstacle():
    height = random.randint(100, screen_height - obstacle_gap - 100)
    top_rect = pygame.Rect(screen_width, 0, obstacle_width, height)
    bottom_rect = pygame.Rect(screen_width, height + obstacle_gap, obstacle_width, screen_height - height - obstacle_gap)
    return (top_rect, bottom_rect)


# create fish
fish_group = pygame.sprite.Group()
flappy = Fish(100, int(screen_height / 2))
fish_group.add(flappy)

# game loop
run = True
while run:
    clock.tick(fps)

    # scroll background
    bg_scroll -= scroll_speed
    if abs(bg_scroll) > screen_width:
        bg_scroll = 0

    # draw background twice for scrolling effect
    screen.blit(bg, (bg_scroll, 0))
    screen.blit(bg, (bg_scroll + screen_width, 0))

    # update and draw fish
    fish_group.update()
    fish_group.draw(screen)

    # spawn new obstacle
    current_time = pygame.time.get_ticks()
    if current_time - last_obstacle_time > obstacle_frequency:
      obstacles.append(create_obstacle())
      last_obstacle_time = current_time

    # move and draw obstacles
    for top_rect, bottom_rect in obstacles:
       top_rect.x -= scroll_speed
       bottom_rect.x -= scroll_speed
       pygame.draw.rect(screen, (0, 255, 0), top_rect)      # green top seaweed
       pygame.draw.rect(screen, (0, 255, 0), bottom_rect)   # green bottom seaweed

    # remove obstacles that go off screen
    obstacles = [pair for pair in obstacles if pair[0].x > -obstacle_width]


    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                flappy.velocity = -8  # flap upward

    pygame.display.update()

pygame.quit()

