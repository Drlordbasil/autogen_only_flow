import pygame

pygame.init()

screen_width = 800
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw something on the screen here (e.g., a rectangle)
    pygame.draw.rect(screen, (255, 0, 0), (100, 100, 50, 50))

    pygame.display.flip()

pygame.quit()