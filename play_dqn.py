# play_dqn.py

import pygame
import random
import numpy as np
from tensorflow.keras.models import load_model

# Game constants
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 500
OBSTACLE_WIDTH = 100
OBSTACLE_GAP = 180
OBSTACLE_VELOCITY = 4
GRAVITY = 0.5
FLAP_STRENGTH = -8

class DizzyDoryEnv:
    def __init__(self):
        pygame.init()
        self.display = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.fish_y = SCREEN_HEIGHT // 2
        self.fish_velocity = 0
        self.obstacles = []
        self.score = 0
        self.done = False
        self.spawn_obstacle()

    def reset(self):
        self.fish_y = SCREEN_HEIGHT // 2
        self.fish_velocity = 0
        self.obstacles = []
        self.score = 0
        self.done = False
        self.spawn_obstacle()
        return self._get_state()

    def spawn_obstacle(self):
        height = random.randint(100, SCREEN_HEIGHT - OBSTACLE_GAP - 100)
        top_rect = pygame.Rect(SCREEN_WIDTH, 0, OBSTACLE_WIDTH, height)
        bottom_rect = pygame.Rect(SCREEN_WIDTH, height + OBSTACLE_GAP, OBSTACLE_WIDTH, SCREEN_HEIGHT - height - OBSTACLE_GAP)
        self.obstacles.append((top_rect, bottom_rect))

    def _get_state(self):
    # Fish's current vertical position and velocity (normalized)
        fish_y_normalized = self.fish_y / SCREEN_HEIGHT
        velocity_normalized = self.fish_velocity / 10.0  # assume max speed ~10

    # Find the next pipe (the one ahead of the fish)
        next_pipe = None
        for top, bottom in self.obstacles:
             if top.x + OBSTACLE_WIDTH > 100:  # fish x-position = 100
                 next_pipe = (top, bottom)
                 break
        if not next_pipe:
             next_pipe = self.obstacles[0]  # fallback

        top_rect, bottom_rect = next_pipe

    # Horizontal distance to next pipe (normalized)
        horizontal_distance = (top_rect.x - 100) / SCREEN_WIDTH

    # Vertical distance to the center of the gap (normalized)
        gap_center_y = top_rect.height + OBSTACLE_GAP / 2
        vertical_distance = (gap_center_y - self.fish_y) / SCREEN_HEIGHT

        state = np.array([
        fish_y_normalized,
        velocity_normalized,
        horizontal_distance,
        vertical_distance
    ], dtype=np.float32)
        

        return state

    def step(self, action):
        reward = 0.1  # surviving is good

        if action == 1:
           self.fish_velocity = FLAP_STRENGTH

        self.fish_velocity += GRAVITY
        self.fish_y += self.fish_velocity

        for i in range(len(self.obstacles)):
            top, bottom = self.obstacles[i]
            top.x -= OBSTACLE_VELOCITY
            bottom.x -= OBSTACLE_VELOCITY

        if self.obstacles[0][0].x < -OBSTACLE_WIDTH:
            self.obstacles.pop(0)
            self.spawn_obstacle()
            reward += 5  # more reward for passing a pipe
            self.score += 1

        top, bottom = self.obstacles[0]
        fish_rect = pygame.Rect(100, self.fish_y, 60, 45)

        if self.fish_y < 0 or self.fish_y > SCREEN_HEIGHT or \
           fish_rect.colliderect(top) or fish_rect.colliderect(bottom):
            self.done = True
            reward = -100  # strong punishment

        return self._get_state(), reward, self.done, {}


    def close(self):
        pygame.quit()

# Load trained model
model = load_model(r"C:\Users\gargi\Desktop\Python\Dizzy Dory\dizzy_dory_dqn_model.h5", compile=False)
# Initialize environment
env = DizzyDoryEnv()
state = env.reset()
done = False

# Pygame display setup
# Load images
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Dizzy Dory AI Playing")
background_img = pygame.image.load("bg.png")
dory_img = pygame.image.load("fish1.png")
pipe_top_img = pygame.image.load("pipe.png")
pipe_bottom_img = pygame.image.load("pipe.png")

# Resize if needed
background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
dory_img = pygame.transform.scale(dory_img, (60, 45))
pipe_top_img = pygame.transform.scale(pipe_top_img, (OBSTACLE_WIDTH, 300))     # You can adjust height
pipe_bottom_img = pygame.transform.scale(pipe_bottom_img, (OBSTACLE_WIDTH, 300))


# Game loop
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    q_values = model.predict(np.expand_dims(state, axis=0), verbose=0)
    if q_values[0][1] > q_values[0][0] or random.random() < 0.1:
       action = 1
       print(f"Q-values: {q_values} | Chosen action: {action}")
    else:
       action = 0
       print(f"Q-values: {q_values} | Chosen action: {action}")


    next_state, reward, done, _ = env.step(action)
    state = next_state

    # Draw everything
    screen.blit(background_img, (0, 0))  # Draw background
    screen.blit(dory_img, (100, env.fish_y))  # Draw Dory

    for top, bottom in env.obstacles:
       screen.blit(pipe_top_img, (top.x, top.bottom - pipe_top_img.get_height()))
       screen.blit(pipe_bottom_img, (bottom.x, bottom.y))


    pygame.display.flip()
    pygame.time.delay(30)
    env.clock.tick(30)

env.close()
print("Game Over!")
