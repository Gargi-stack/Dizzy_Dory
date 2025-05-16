import pygame
import sys
import random
import numpy as np
from tensorflow.keras.models import load_model

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
obstacle_width = 100
obstacle_gap = 200
obstacle_frequency = 3000
last_obstacle_time = pygame.time.get_ticks()
obstacles = []
score = 0
high_score = 0

# Load background
bg = pygame.image.load('bg.png').convert()
bg = pygame.transform.scale(bg, (screen_width, screen_height))

# Obstacle image
pipe_img = pygame.image.load('pipe.png').convert_alpha()
pipe_img = pygame.transform.scale(pipe_img, (obstacle_width, screen_height * 2))

# Load arrow image for AI suggestion
arrow_img = pygame.image.load('arrow.png').convert_alpha()
arrow_img = pygame.transform.scale(arrow_img, (30, 30))

# Fonts
font_large = pygame.font.SysFont('comicsans', 60)
font_small = pygame.font.SysFont('comicsans', 30)

# Colors
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# Load trained AI model
model = load_model("dizzy_dory_dqn_model.h5", compile=False)

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

# Obstacle creation with images
def create_obstacle():
    height = random.randint(100, screen_height - obstacle_gap - 100)
    top_rect = pygame.Rect(screen_width, 0, obstacle_width, height)
    bottom_rect = pygame.Rect(screen_width, height + obstacle_gap, obstacle_width, screen_height - height - obstacle_gap)

    top_pipe_img = pygame.transform.flip(pipe_img.subsurface((0, pipe_img.get_height() - height, obstacle_width, height)), False, True)
    bottom_pipe_img = pipe_img.subsurface((0, 0, obstacle_width, screen_height - height - obstacle_gap))

    return (top_rect, bottom_rect, top_pipe_img, bottom_pipe_img, False)

# AI Flap Suggestion Function
def get_ai_flap_suggestion(fish, obstacles):
    if not obstacles:
        return False

    top_rect, bottom_rect, _, _, _ = obstacles[0]
    fish_y_normalized = fish.rect.centery / screen_height
    velocity_normalized = fish.velocity / 10.0
    horizontal_distance = (top_rect.x - fish.rect.left) / screen_width
    gap_center_y = top_rect.height + (obstacle_gap / 2)
    vertical_distance = (gap_center_y - fish.rect.centery) / screen_height

    state = np.array([[fish_y_normalized, velocity_normalized, horizontal_distance, vertical_distance]], dtype=np.float32)
    q_values = model.predict(state, verbose=0)

    return q_values[0][1] > q_values[0][0]

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
                score = 0
                show_countdown()
            if exit_button.collidepoint((mx, my)):
                run = False

    if show_start_screen:
        title_text = font_large.render("Dizzy Dory", True, WHITE)
        screen.blit(title_text, (screen_width//2 - title_text.get_width()//2, 150))
        start_button = draw_button("Start Game", 175, 250, 150, 50, (0, 128, 255))

    elif not game_over:
        fish_group.update()
        fish_group.draw(screen)

        current_time = pygame.time.get_ticks()
        if current_time - last_obstacle_time > obstacle_frequency:
            obstacles.append(create_obstacle())
            last_obstacle_time = current_time

        for i in range(len(obstacles)):
            top_rect, bottom_rect, top_img, bottom_img, passed = obstacles[i]
            top_rect.x -= obstacle_velocity
            bottom_rect.x -= obstacle_velocity
            screen.blit(top_img, top_rect)
            screen.blit(bottom_img, bottom_rect)

            if not passed and top_rect.right < flappy.rect.left:
                score += 1
                obstacles[i] = (top_rect, bottom_rect, top_img, bottom_img, True)

        obstacles = [obs for obs in obstacles if obs[0].x > -obstacle_width]

        for top_rect, bottom_rect, _, _, _ in obstacles:
            if flappy.rect.colliderect(top_rect) or flappy.rect.colliderect(bottom_rect):
                game_over = True
                if score > high_score:
                    high_score = score

        # Show AI suggestion
        if get_ai_flap_suggestion(flappy, obstacles):
            arrow_x = flappy.rect.centerx + 30
            arrow_y = flappy.rect.centery - 20
            screen.blit(arrow_img, (arrow_x, arrow_y))

        # Score display
        score_text = font_small.render(f"Score: {score}", True, WHITE)
        high_score_text = font_small.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

    else:
        game_over_text = font_large.render("Game Over", True, RED)
        screen.blit(game_over_text, (screen_width//2 - game_over_text.get_width()//2, 150))

        score_text = font_small.render(f"Score: {score}", True, WHITE)
        high_score_text = font_small.render(f"High Score: {high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(high_score_text, (10, 40))

        restart_button = draw_button("Restart", 150, 250, 100, 40, (0, 128, 0))
        exit_button = draw_button("Exit", 270, 250, 80, 40, (128, 0, 0))

    pygame.display.update()

pygame.quit()
sys.exit()
