import pygame
import sys
import random
from pygame.locals import *

pygame.init()

# Game setup
clock = pygame.time.Clock()
fps = 60
screen_width = 500
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Dizzy Dory')

# Game variables
bg_scroll = 0
scroll_speed = 4
obstacle_velocity = 4
obstacle_width = 70
obstacle_gap = 180
obstacle_frequency = 1500
last_obstacle_time = pygame.time.get_ticks()
obstacles = []
game_over = False
game_started = False

# Load background
bg = pygame.image.load('bg.png').convert()
bg = pygame.transform.scale(bg, (screen_width, screen_height))

# Fonts
font_big = pygame.font.SysFont('comicsans', 60)
font_small = pygame.font.SysFont('comicsans', 30)

# Fish class
class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        for num in range(1, 4):
            img = pygame.image.load(f'fish{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (60, 45))
            self.images.append(img)
        self.index = 0
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.gravity = 0.5
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.velocity += self.gravity
        self.rect.y += self.velocity

        # Screen boundaries
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

# Create fish
fish_group = pygame.sprite.Group()
flappy = Fish(100, screen_height // 2)
fish_group.add(flappy)

# Obstacle generator
def create_obstacle():
    height = random.randint(100, screen_height - obstacle_gap - 100)
    top = pygame.Rect(screen_width, 0, obstacle_width, height)
    bottom = pygame.Rect(screen_width, height + obstacle_gap, obstacle_width, screen_height - height - obstacle_gap)
    return top, bottom

# Countdown function
def countdown():
    for i in range(3, 0, -1):
        screen.fill((0, 0, 128))
        text = font_big.render(str(i), True, (255, 255, 255))
        rect = text.get_rect(center=(screen_width//2, screen_height//2))
        screen.blit(text, rect)
        pygame.display.update()
        pygame.time.delay(800)
    screen.fill((0, 0, 128))
    text = font_big.render("GO!", True, (0, 255, 0))
    rect = text.get_rect(center=(screen_width//2, screen_height//2))
    screen.blit(text, rect)
    pygame.display.update()
    pygame.time.delay(800)

# Start button
def draw_start_button():
    button_rect = pygame.Rect(screen_width//2 - 75, screen_height//2 - 25, 150, 50)
    pygame.draw.rect(screen, (0, 200, 200), button_rect)
    text = font_small.render("Start Game", True, (0, 0, 0))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)
    return button_rect

# Main loop
run = True
while run:
    screen.fill((0, 0, 128))  # Sea blue background
    if not game_started:
        button_rect = draw_start_button()
    else:
        # Scroll background
        bg_scroll -= scroll_speed
        if abs(bg_scroll) > screen_width:
            bg_scroll = 0

        screen.blit(bg, (bg_scroll, 0))
        screen.blit(bg, (bg_scroll + screen_width, 0))

        # Update fish
        if not game_over:
            fish_group.update()
        fish_group.draw(screen)

        # Spawn obstacles
        if not game_over:
            if pygame.time.get_ticks() - last_obstacle_time > obstacle_frequency:
                obstacles.append(create_obstacle())
                last_obstacle_time = pygame.time.get_ticks()

            for top, bottom in obstacles:
                top.x -= obstacle_velocity
                bottom.x -= obstacle_velocity
                pygame.draw.rect(screen, (0, 255, 0), top)
                pygame.draw.rect(screen, (0, 255, 0), bottom)

            obstacles = [pair for pair in obstacles if pair[0].x > -obstacle_width]

            # Check collisions
            for top, bottom in obstacles:
                if flappy.rect.colliderect(top) or flappy.rect.colliderect(bottom):
                    game_over = True

        if game_over:
            text = font_big.render("Game Over", True, (255, 0, 0))
            screen.blit(text, text.get_rect(center=(screen_width//2, screen_height//2)))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN and not game_started:
            if button_rect.collidepoint(event.pos):
                countdown()
                game_started = True
                obstacles.clear()
                flappy.rect.center = [100, screen_height//2]
                flappy.velocity = 0

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                flappy.velocity = -8
            if event.key == pygame.K_r and game_over:
                game_over = False
                obstacles.clear()
                flappy.rect.center = [100, screen_height//2]
                flappy.velocity = 0

    pygame.display.update()
    clock.tick(fps)
