import pygame
import sys
import random

pygame.init()
clock = pygame.time.Clock()
fps = 60

# Screen setup
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

# Load background
bg = pygame.image.load('bg.png').convert()
bg = pygame.transform.scale(bg, (screen_width, screen_height))

# Fonts
font_large = pygame.font.SysFont('comicsans', 60)
font_small = pygame.font.SysFont('comicsans', 30)

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Fish class
class Fish(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'fish{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (60, 45))
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity = 0
        self.gravity = 0.5

    def update(self):
        self.counter += 1
        if self.counter > 5:
            self.counter = 0
            self.index = (self.index + 1) % len(self.images)
            self.image = self.images[self.index]

        self.velocity += self.gravity
        self.rect.y += self.velocity

        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height
            self.velocity = 0
        if self.rect.top < 0:
            self.rect.top = 0
            self.velocity = 0

# Obstacle creation
def create_obstacle():
    height = random.randint(100, screen_height - obstacle_gap - 100)
    top_rect = pygame.Rect(screen_width, 0, obstacle_width, height)
    bottom_rect = pygame.Rect(screen_width, height + obstacle_gap, obstacle_width, screen_height - height - obstacle_gap)
    return (top_rect, bottom_rect)

# Button drawing
def draw_button(text, x, y, w, h, color):
    button_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(screen, color, button_rect)
    label = font_small.render(text, True, WHITE)
    screen.blit(label, (x + (w - label.get_width()) // 2, y + (h - label.get_height()) // 2))
    return button_rect

# Countdown before game starts
def show_countdown():
    for num in ["3", "2", "1", "Go!"]:
        screen.blit(bg, (0, 0))
        text = font_large.render(num, True, RED)
        screen.blit(text, (screen_width//2 - text.get_width()//2, screen_height//2 - text.get_height()//2))
        pygame.display.update()
        pygame.time.delay(700)

# Setup
fish_group = pygame.sprite.Group()
flappy = Fish(100, screen_height // 2)
fish_group.add(flappy)

game_over = False
started = False
show_start_screen = True

# Main loop
run = True
while run:
    clock.tick(fps)

    screen.blit(bg, (0, 0))
    screen.blit(bg, (bg_scroll + screen_width, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if not started and show_start_screen and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if start_button.collidepoint((mx, my)):
                show_start_screen = False
                started = True
                show_countdown()

        if started and not game_over and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                flappy.velocity = -8

        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            if restart_button.collidepoint((mx, my)):
                game_over = False
                obstacles.clear()
                flappy.rect.center = [100, screen_height // 2]
                flappy.velocity = 0
                show_countdown()
            if exit_button.collidepoint((mx, my)):
                run = False

    if show_start_screen:
        title_text = font_large.render("Dizzy Dory", True, WHITE)
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 150))
        start_button = draw_button("Start Game", 175, 250, 150, 50, (0, 128, 255))
    elif not game_over:
        # Gameplay
        fish_group.update()
        fish_group.draw(screen)

        current_time = pygame.time.get_ticks()
        if current_time - last_obstacle_time > obstacle_frequency:
            obstacles.append(create_obstacle())
            last_obstacle_time = current_time

        for top_rect, bottom_rect in obstacles:
            top_rect.x -= obstacle_velocity
            bottom_rect.x -= obstacle_velocity
            pygame.draw.rect(screen, GREEN, top_rect)
            pygame.draw.rect(screen, GREEN, bottom_rect)

        obstacles = [pair for pair in obstacles if pair[0].x > -obstacle_width]

        for top_rect, bottom_rect in obstacles:
            if flappy.rect.colliderect(top_rect) or flappy.rect.colliderect(bottom_rect):
                game_over = True

    else:
        # Game Over screen
        game_over_text = font_large.render("Game Over", True, RED)
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, 150))

        restart_button = draw_button("Restart", 150, 250, 100, 40, (0, 128, 0))
        exit_button = draw_button("Exit", 270, 250, 80, 40, (128, 0, 0))

    pygame.display.update()

pygame.quit()
sys.exit()
