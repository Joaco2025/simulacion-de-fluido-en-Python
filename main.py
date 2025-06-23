#main.py

import pygame
import math

# Inicializar pygame
pygame.init()
width, height = 800, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Flujo Laminar con Estrechamiento Dinámico")

# Colores
WHITE = (255, 255, 255)
BLUE = (50, 50, 255)
BLACK = (0, 0, 0)

# Parámetros del tubo
tube_x = 100
tube_width = 600
tube_y_center = 200
r_max = 100  # radio máximo (entrada)
r_min = 50   # radio mínimo (salida)
v_max = 5    # velocidad máxima al centro (entrada)

# Crear partículas
class Particula:
    def __init__(self, y_offset):
        self.x = tube_x
        self.y_offset = y_offset  # posición relativa desde el centro
        self.y = 0
        self.v = 0

    def update_posicion_y(self, r_local):
        self.y = tube_y_center + self.y_offset * r_local / r_max

    def update_velocidad(self, r_local):
        # Ajuste dinámico de v_max para conservar el caudal Q = A * v
        v_max_local = v_max * (r_max / r_local) ** 2
        self.v = v_max_local * (1 - (self.y_offset / r_local) ** 2)

    def mover(self):
        self.x += self.v
        if self.x > tube_x + tube_width:
            self.x = tube_x

    def dibujar(self, screen):
        pygame.draw.line(screen, BLUE, (int(self.x), int(self.y)), (int(self.x + 10), int(self.y)), 2)

# Crear partículas espaciadas entre -r_max y +r_max
particulas = [Particula(y) for y in range(-r_max + 5, r_max - 5, 10)]

clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)

    # Dibujar los bordes del tubo (superior e inferior)
    upper_points = []
    lower_points = []
    for dx in range(tube_width + 1):
        x = tube_x + dx
        progreso = dx / tube_width
        r_local = r_max - (r_max - r_min) * progreso
        upper_y = tube_y_center - r_local
        lower_y = tube_y_center + r_local
        upper_points.append((x, upper_y))
        lower_points.append((x, lower_y))

    # Dibujar las curvas del tubo
    pygame.draw.lines(screen, BLACK, False, upper_points, 2)
    pygame.draw.lines(screen, BLACK, False, lower_points, 2)

    # Actualizar y dibujar partículas
    for p in particulas:
        dx = p.x - tube_x
        progreso = dx / tube_width
        r_local = r_max - (r_max - r_min) * progreso
        if r_local < 1:
            r_local = 1  # evitar división por cero

        p.update_posicion_y(r_local)
        p.update_velocidad(r_local)
        p.mover()
        p.dibujar(screen)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()

