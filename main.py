#main.py

# === LIBRERÍAS NECESARIAS ===
import pygame
import math
import random

# === OPCIÓN PARA ACTIVAR O DESACTIVAR FRICCIÓN ===
friccion = False

# === ENTRADA DE DATOS DEL USUARIO ===
try:
    radio_entrada_cm = float(input("Radio de entrada (en cm, ej. 5): "))
    radio_salida_cm = float(input("Radio de salida (en cm, ej. 3): "))
    velocidad_entrada_cm_s = float(input("Velocidad de entrada (en cm/s, ej. 20): "))
    Altura_cm = float(input("Diferencia de altura (en cm, ej. 10): "))
except:
    print("Entrada inválida. Saliendo.")
    exit()

# === CONSTANTES FÍSICAS ===
gravedad_cm_s2 = 980  # Aceleración gravitacional en cm/s²
gravedad_px_frame2 = (gravedad_cm_s2 / 10) / (60**2)  # Convertir a px/frame²

# === CONVERSIÓN DE UNIDADES ===
cm_a_px = 10
fps = 60

radio_entrada_px = radio_entrada_cm * cm_a_px
radio_salida_px = radio_salida_cm * cm_a_px

area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
area_salida_cm2 = math.pi * radio_salida_cm ** 2

Altura_px = Altura_cm * cm_a_px

caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s
caudal_lps = caudal_cm3_s / 1000

factor_visual = 100
velocidad_entrada_px_frame = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual
velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2
velocidad_salida_px_frame = ((velocidad_salida_cm_s / cm_a_px) / fps) * factor_visual

# === CONFIGURACIÓN DE LA VENTANA ===
pygame.init()
ancho_pantalla, alto_pantalla = 1400, 900
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo con Caída Libre")

fuente = pygame.font.SysFont("Arial", 18)

# === COLORES ===
BLANCO = (255, 255, 255)
AZUL = (50, 50, 255)
NEGRO = (0, 0, 0)

# === PARÁMETROS DEL TUBO ===
ancho_total = 600

x_tubo = 50
ancho_tubo = 150
y_centro_tubo = 300

x_diagonal = 200
ancho_diagonal = 300
y_centro_diagonal = 300

x_tubo_salida = 500
ancho_tubo_salida = 150
y_centro_tubo_salida = y_centro_tubo - Altura_px

# === SUELO ===
y_suelo = y_centro_tubo + radio_entrada_px

# === CLASE DE PARTÍCULAS ===
class Particula:
    def __init__(self, desplazamiento_y_normalizado):
        self.x = x_tubo
        self.desplazamiento_y = desplazamiento_y_normalizado
        self.y = 0
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.radio_particula = 4
        self.en_caida_libre = False
        self.tiempo_caida = 0

    def actualizar_posicion_y(self, radio_local, altura_local):
        if not self.en_caida_libre:
            self.y = (y_centro_tubo + self.desplazamiento_y * radio_local) - altura_local

    def actualizar_velocidad(self, radio_local):
        if radio_local < 1:
            radio_local = 1

        velocidad_maxima_local = velocidad_entrada_px_frame * (radio_entrada_px / radio_local) ** 2

        if friccion:
            perfil_exponente = 2
            minimo_relativo = 0.2
            factor = 1 - abs(self.desplazamiento_y) ** perfil_exponente
            factor = max(factor, minimo_relativo)
            self.velocidad_x = velocidad_maxima_local * factor
        else:
            self.velocidad_x = velocidad_maxima_local

    def iniciar_caida_libre(self):
        if not self.en_caida_libre and Altura_cm > 0:
            self.en_caida_libre = True
            self.velocidad_y = 0
            self.tiempo_caida = 0

    def actualizar_caida_libre(self):
        if self.en_caida_libre:
            self.tiempo_caida += 1 / fps
            self.x += self.velocidad_x
            self.velocidad_y += gravedad_px_frame2
            self.y += self.velocidad_y

    def mover(self):
        if not self.en_caida_libre:
            self.x += self.velocidad_x
            if self.x > x_tubo_salida + ancho_tubo_salida and Altura_cm > 0:
                self.iniciar_caida_libre()
            elif self.x > x_tubo + ancho_total:
                self.resetear()
        else:
            self.actualizar_caida_libre()
            # Reiniciar cuando toca el suelo
            if self.y >= y_suelo or self.x > ancho_pantalla + 100:
                self.resetear()

    def resetear(self):
        self.x = x_tubo
        self.y = 0
        self.velocidad_x = 0
        self.velocidad_y = 0
        self.en_caida_libre = False
        self.tiempo_caida = 0

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, AZUL, (int(self.x), int(self.y)), self.radio_particula)

# === CREACIÓN DE PARTÍCULAS ===
particulas = []
paso = 0.005
margen = 0.9
pos = -margen
while pos <= margen:
    particulas.append(Particula(pos))
    pos += paso

# === BUCLE PRINCIPAL ===
reloj = pygame.time.Clock()
ejecutando = True

if Altura_cm > 0:
    tiempo_caida_s = math.sqrt((2 * Altura_cm) / gravedad_cm_s2)
    distancia_caida_cm = velocidad_salida_cm_s * tiempo_caida_s
else:
    distancia_caida_cm = 0

while ejecutando:
    pantalla.fill(BLANCO)

    # === DIBUJAR TUBO ===
    puntos_superiores, puntos_inferiores = [], []

    for dx in range(ancho_tubo + 1):
        x = x_tubo + dx
        radio_local = radio_entrada_px
        y_superior = y_centro_tubo - radio_local
        y_inferior = y_centro_tubo + radio_local
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    dy_parts = Altura_px / ancho_diagonal
    dy = 0
    for dx in range(ancho_diagonal):
        x = x_diagonal + dx
        progreso = dx / ancho_diagonal
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
        y_superior = (y_centro_tubo - radio_local) - dy
        y_inferior = (y_centro_tubo + radio_local) - dy
        dy += dy_parts
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    for dx in range(ancho_tubo_salida + 1):
        x = x_tubo_salida + dx
        radio_local = radio_salida_px
        y_superior = y_centro_tubo_salida - radio_local
        y_inferior = y_centro_tubo_salida + radio_local
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    pygame.draw.lines(pantalla, NEGRO, False, puntos_superiores, 2)
    pygame.draw.lines(pantalla, NEGRO, False, puntos_inferiores, 2)

    # === DIBUJAR SUELO ===
    if Altura_cm > 0:
        pygame.draw.line(pantalla, NEGRO, (0, y_suelo), (ancho_pantalla, y_suelo), 2)

    # === ACTUALIZAR Y DIBUJAR PARTÍCULAS ===
    for p in particulas:
        if not p.en_caida_libre:
            if p.x < x_diagonal:
                radio_local = radio_entrada_px
                altura_local = 0
            elif p.x < x_tubo_salida:
                progreso = (p.x - x_diagonal) / ancho_diagonal
                progreso = min(max(progreso, 0), 1)
                radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
                altura_local = Altura_px * progreso
            else:
                radio_local = radio_salida_px
                altura_local = Altura_px

            if radio_local < 1:
                radio_local = 1

            p.actualizar_posicion_y(radio_local, altura_local)
            p.actualizar_velocidad(radio_local)

        p.mover()
        p.dibujar(pantalla)

    # === MOSTRAR TEXTO INFORMATIVO ===
    def dibujar_texto(texto, x, y):
        superficie = fuente.render(texto, True, NEGRO)
        pantalla.blit(superficie, (x, y))

    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 10, 400)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 10, 425)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 10, 450)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 10, 475)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 10, 505)
    dibujar_texto(f"Velocidad salida: {velocidad_salida_cm_s:.1f} cm/s", 10, 530)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 10, 560)
    dibujar_texto(f"Fricción: {'Sí' if friccion else 'No'} (presiona F)", 10, 590)
    dibujar_texto(f"Altura: {Altura_cm:.1f} cm", 10, 620)
    #dibujar_texto(f"Partículas en caída: {sum(1 for p in particulas if p.en_caida_libre)}", 30, 650)
    dibujar_texto("Ecuación de Bernoulli:", 10, 710)
    dibujar_texto("P₁ + ½·ρ₁·v₁² + ρ·g·h₁ = P₂ + ½·ρ₂·v₂² + ρ·g·h₂", 5, 770)
    dibujar_texto(f"Distancia horizontal caída libre: {distancia_caida_cm:.1f} cm", 10, 680)
    dibujar_texto(f"Para esta simulación, suponemos que el líquido a lo largo de", 400, 530)
    dibujar_texto(f"todo su recorrido se mantiene siendo ese mismo líquido, por", 400, 560)
    dibujar_texto(f"lo cual decimos que ρ₁ = ρ₂ = ρ", 400, 590)
    dibujar_texto(f"La gravedad se mantiene constante, g=9.8m/s²", 400, 620)
    dibujar_texto(f"El flujo con el que ingresa el líquido es constante", 400, 650)
    dibujar_texto(f"La Presión 2 en el punto de salida es igual a la presinó atmosférica", 400, 680)
    if Altura_cm > 0:
        dibujar_texto(f"Aquí se considera que el líquido puede tener una caida en forma de", 400, 710)
        dibujar_texto(f"tiro parabólico, ya que tiene una diferencia de altura con la entrada", 400, 740)
    else:
        dibujar_texto(f"Aquí se considera que el líquido sigue fluyendo por el tubo al estar", 400, 710)
        dibujar_texto(f"a la misma altura o por debajo del punto de entrada", 400, 740)

    pygame.display.flip()
    reloj.tick(fps)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_f:
                friccion = not friccion

pygame.quit()

