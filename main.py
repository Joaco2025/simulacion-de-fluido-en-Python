#main.py
import pygame
import sys

# Inicializar Pygame
pygame.init()
#Configuración de pantalla (el tamaño que tendrá la pantalla en pixeles)
pygame.display.set_mode((800, 600))
#El nombre que tendrá la pantalla iniciada
pygame.display.set_caption("Amaya Joto")
#Codigo extremadamente simple para abrir una pantalla, y que se cierre cuanto presiones exit
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

