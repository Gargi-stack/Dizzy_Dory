import pygame
import sys

# Initialize pygame
pygame.init()

# Set up game window
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Flappy Bird Basic')

# Clock to control FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 235)  # Background sky blue

# Bird setup
bird_img = pygame.Surface((40, 30))  # Create a simple rectangle for the bird
bird_img.fill((255, 255, 0))  # Yellow colored bird
bird_rect = bird_img.get_rect(center=(100, SCREEN_HEIGHT//2))

# Bird physics
gravity = 0.25
bird_movement = 0
flap_power = -6

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Bird flap when SPACE key is pressed
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bird_movement = flap_power

    # Apply gravity to bird
    bird_movement += gravity
    bird_rect.centery += bird_movement

    # Fill background
    screen.fill(BLUE)

    # Draw bird
    screen.blit(bird_img, bird_rect)

    # Update display
    pygame.display.update()

    # Maintain framerate
    clock.tick(FPS)
