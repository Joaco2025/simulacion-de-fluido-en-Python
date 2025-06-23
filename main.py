#main.py

import pygame
import math

# Inicializar pygame
pygame.init()
width, height = 800, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flujo Laminar (Poiseuille)")

# Colores
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
BLACK = (0, 0, 0)

# Parámetros del tubo
tube_x = 100
tube_y = 100
tube_width = 600
tube_height = 200
r_max = tube_height // 2  # radio del tubo
v_max = 5  # velocidad máxima

# Crear partículas (líneas) a diferentes alturas
class Particula:
    def __init__(self, y):
        self.y = y
        self.y_rel = y - (tube_y + r_max)
        self.v = v_max * (1 - (self.y_rel / r_max) ** 2)  # velocidad según perfil parabólico
        self.x = tube_x

    def mover(self):
        self.x += self.v
        if self.x > tube_x + tube_width:
            self.x = tube_x  # reinicia cuando sale del tubo

    def dibujar(self, screen):
        pygame.draw.line(screen, BLUE, (int(self.x), self.y), (int(self.x + 10), self.y), 2)

# Crear lista de partículas espaciadas verticalmente
particulas = [Particula(y) for y in range(tube_y + 5, tube_y + tube_height - 5, 10)]

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    pygame.draw.rect(screen, BLACK, (tube_x, tube_y, tube_width, tube_height), 2)

    for p in particulas:
        p.mover()
        p.dibujar(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

