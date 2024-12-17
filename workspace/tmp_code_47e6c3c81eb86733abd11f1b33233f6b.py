import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
SPEED = 10
BLOCK_SIZE = 20

# Create the game window
win = pygame.display.set_mode((WIDTH, HEIGHT))

# Define some colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

class Snake:
    def __init__(self):
        self.x = WIDTH / 2
        self.y = HEIGHT / 2
        self.length = 1
        self.body = [(self.x, self.y)]

    def move(self):
        for i in range(len(self.body) - 1, 0, -1):
            self.body[i] = self.body[i - 1]
        if len(self.body) > 0:
            self.body[0] = (self.x, self.y)

class Food:
    def __init__(self):
        self.x = random.randint(0, WIDTH // BLOCK_SIZE - 1) * BLOCK_SIZE
        self.y = random.randint(0, HEIGHT // BLOCK_SIZE - 1) * BLOCK_SIZE

def draw_snake(snake):
    for pos in snake.body:
        pygame.draw.rect(win, WHITE, (pos[0], pos[1], BLOCK_SIZE, BLOCK_SIZE))

def draw_food(food):
    pygame.draw.rect(win, RED, (food.x, food.y, BLOCK_SIZE, BLOCK_SIZE))

def main():
    clock = pygame.time.Clock()
    snake = Snake()
    food = Food()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)

        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and snake.body[0][1] != 0:
            snake.y -= BLOCK_SIZE
        elif keys[pygame.K_DOWN] and snake.body[0][1] < HEIGHT - BLOCK_SIZE:
            snake.y += BLOCK_SIZE
        elif keys[pygame.K_LEFT] and snake.body[0][0] > 0:
            snake.x -= BLOCK_SIZE
        elif keys[pygame.K_RIGHT] and snake.body[0][0] < WIDTH - BLOCK_SIZE:
            snake.x += BLOCK_SIZE

        snake.move()

        win.fill((0, 0, 0))
        draw_snake(snake)
        draw_food(food)

        pygame.display.update()
        clock.tick(SPEED)

if __name__ == "__main__":
    main()