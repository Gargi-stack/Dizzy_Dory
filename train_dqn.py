# train_dqn.py - Training a DQN agent to play Dizzy Dory

import numpy as np
import tensorflow as tf
from collections import deque
import random
import pygame

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
        self.obstacles = []
        self.score = 0
        self.done = False
        self.reset()

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
        next_top, next_bottom = self.obstacles[0]
        state = [
            self.fish_y / SCREEN_HEIGHT,
            self.fish_velocity / 10.0,
            (next_top.x - 100) / SCREEN_WIDTH,
            (next_top.height) / SCREEN_HEIGHT,
        ]
        return np.array(state, dtype=np.float32)

    def step(self, action):
        reward = 0.1  # reward for staying alive

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
            reward += 1
            self.score += 1

        top, bottom = self.obstacles[0]
        fish_rect = pygame.Rect(100, int(self.fish_y), 60, 45)
        if self.fish_y < 0 or self.fish_y > SCREEN_HEIGHT:
            self.done = True
            reward = -100
        elif fish_rect.colliderect(top) or fish_rect.colliderect(bottom):
            self.done = True
            reward = -100

        return self._get_state(), reward, self.done, {}

    def render(self):
        pass  # Skip visuals during training

    def close(self):
        pygame.quit()

# Hyperparameters
GAMMA = 0.99
EPSILON = 1.0
EPSILON_MIN = 0.01
EPSILON_DECAY = 0.995
LR = 0.001
BATCH_SIZE = 64
MEMORY_SIZE = 100_000
EPISODES = 500

# Q-network model
def build_model(input_shape, output_size):
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(128, input_shape=input_shape, activation='relu'),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dense(output_size, activation='linear')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=LR), loss='mse')
    return model

# Main training loop
def train():
    env = DizzyDoryEnv()
    state_shape = (4,)
    n_actions = 2
    
    model = build_model(state_shape, n_actions)
    memory = deque(maxlen=MEMORY_SIZE)

    global EPSILON

    for episode in range(EPISODES):
        state = env.reset()
        total_reward = 0
        done = False

        while not done:
            if np.random.rand() <= EPSILON:
                action = np.random.randint(n_actions)
            else:
                q_values = model.predict(state.reshape(1, -1), verbose=0)
                action = np.argmax(q_values[0])

            next_state, reward, done, _ = env.step(action)
            memory.append((state, action, reward, next_state, done))
            state = next_state
            total_reward += reward

            if len(memory) >= BATCH_SIZE:
                minibatch = random.sample(memory, BATCH_SIZE)
                states = np.array([m[0] for m in minibatch])
                actions = [m[1] for m in minibatch]
                rewards = [m[2] for m in minibatch]
                next_states = np.array([m[3] for m in minibatch])
                dones = [m[4] for m in minibatch]

                q_targets = model.predict(states, verbose=0)
                q_next = model.predict(next_states, verbose=0)

                for i in range(BATCH_SIZE):
                    q_targets[i][actions[i]] = rewards[i] + (1 - dones[i]) * GAMMA * np.max(q_next[i])

                model.fit(states, q_targets, epochs=1, verbose=0)

        if EPSILON > EPSILON_MIN:
            EPSILON *= EPSILON_DECAY

        print(f"Episode {episode+1}/{EPISODES} - Reward: {total_reward:.2f} - Epsilon: {EPSILON:.3f}")

    model.save("dizzy_dory_dqn_model.h5")
    env.close()
    print("Training complete! Model saved.")

if __name__ == '__main__':
    train()