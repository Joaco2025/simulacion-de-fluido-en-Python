import pygame
import sys
import math

friccion = True  # Fricción activada

# === CONFIGURACIÓN INICIAL ===
# Valores predefinidos y permitidos
radios_entrada_cm_lista = [3, 4, 5, 6]
indice_radio_entrada = 0  # Comienza en 3 cm

radios_salida_cm_lista = [2, 3, 4] # Nuevos valores permitidos para radio de salida
indice_radio_salida = 1 # Comienza en 3 cm (índice 1 de la lista)

velocidades_entrada_cm_s_lista = [10, 15, 20, 25, 30] # Nuevos valores permitidos para velocidad de entrada
indice_velocidad_entrada = 2 # Comienza en 20 cm/s (índice 2 de la lista)


# Se inicializan con los valores de las listas
radio_salida_cm = radios_salida_cm_lista[indice_radio_salida]
velocidad_entrada_cm_s = velocidades_entrada_cm_s_lista[indice_velocidad_entrada]


cm_a_px = 10
fps = 60
factor_visual = 100

# === CONFIGURACIÓN DE LA VENTANA ===
pygame.init()
ancho_pantalla, alto_pantalla = 1100, 400
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo Laminar (Poiseuille)")

fuente = pygame.font.SysFont("Arial", 18)

# Colores
BLANCO = (255, 255, 255)
AZUL = (50, 50, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200)

# Botones - Usando el diccionario directamente
botones = {
    "radio_entrada_mas": pygame.Rect(950, 35, 30, 30),
    "radio_entrada_menos": pygame.Rect(910, 35, 30, 30),
    "radio_salida_mas": pygame.Rect(950, 65, 30, 30),
    "radio_salida_menos": pygame.Rect(910, 65, 30, 30),
    "velocidad_entrada_mas": pygame.Rect(1000, 140, 30, 30), # ¡Posición ajustada!
    "velocidad_entrada_menos": pygame.Rect(960, 140, 30, 30), # ¡Posición ajustada!
}

# Parámetros del tubo
x_tubo = 100
ancho_tubo = 600
y_centro_tubo = 200

# === CLASE DE PARTÍCULAS ===
class Particula:
    def __init__(self, desplazamiento_y_normalizado):
        self.x = x_tubo
        self.desplazamiento_y = desplazamiento_y_normalizado
        self.y = 0
        self.velocidad = 0
        self.radio_particula = 4

    def actualizar_posicion_y(self, radio_local):
        self.y = y_centro_tubo + self.desplazamiento_y * radio_local

    def actualizar_velocidad(self, radio_local):
        if radio_local < 1:
            radio_local = 1
        # Esta velocidad máxima local ahora depende de la velocidad_entrada_px global
        velocidad_maxima_local = velocidad_entrada_px * (radio_entrada_px / radio_local) ** 2

        if friccion:
            perfil_exponente = 2
            minimo_relativo = 0.2
            factor = 1 - abs(self.desplazamiento_y) ** perfil_exponente
            factor = max(factor, minimo_relativo)
            self.velocidad = velocidad_maxima_local * factor
        else:
            self.velocidad = velocidad_maxima_local

    def mover(self):
        self.x += self.velocidad
        if self.x > x_tubo + ancho_tubo:
            self.x = x_tubo

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, AZUL, (int(self.x), int(self.y)), self.radio_particula)

# === CREACIÓN DE PARTÍCULAS ===
def crear_particulas():
    nuevas_particulas = []
    paso = 0.02
    margen = 0.9
    pos = -margen
    while pos <= margen:
        nuevas_particulas.append(Particula(pos))
        pos += paso
    return nuevas_particulas

particulas = crear_particulas()

# === FUNCIÓN PARA RECALCULAR PARÁMETROS ===
def recalcular_parametros():
    global radio_entrada_cm, radio_salida_cm, velocidad_entrada_cm_s
    global radio_entrada_px, radio_salida_px
    global area_entrada_cm2, area_salida_cm2
    global caudal_cm3_s, caudal_lps, velocidad_entrada_px, velocidad_salida_cm_s
    global particulas # Necesitamos reiniciar las partículas si la velocidad o el tubo cambian

    radio_entrada_cm = radios_entrada_cm_lista[indice_radio_entrada]
    radio_salida_cm = radios_salida_cm_lista[indice_radio_salida]
    velocidad_entrada_cm_s = velocidades_entrada_cm_s_lista[indice_velocidad_entrada] # ¡Nueva línea crucial!

    radio_entrada_px = radio_entrada_cm * cm_a_px
    radio_salida_px = radio_salida_cm * cm_a_px

    area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
    area_salida_cm2 = math.pi * radio_salida_cm ** 2
    
    caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s
    caudal_lps = caudal_cm3_s / 1000
    
    # velocidad_entrada_px debe recalcularse cuando velocidad_entrada_cm_s cambia
    velocidad_entrada_px = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual
    
    velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2
    
    # Después de recalcular los parámetros, volvemos a crear las partículas para que se adapten
    # a la nueva velocidad y tamaño del tubo, y así sus velocidades se apliquen correctamente desde el inicio.
    particulas = crear_particulas()


# Cálculo inicial
recalcular_parametros()

# === BUCLE PRINCIPAL ===
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        elif evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            # Lógica de botones para Radio de Entrada
            if botones["radio_entrada_mas"].collidepoint(evento.pos):
                if indice_radio_entrada < len(radios_entrada_cm_lista) - 1:
                    indice_radio_entrada += 1
                    recalcular_parametros()
            elif botones["radio_entrada_menos"].collidepoint(evento.pos):
                if indice_radio_entrada > 0:
                    indice_radio_entrada -= 1
                    recalcular_parametros()
            
            # Lógica de botones para Radio de Salida
            elif botones["radio_salida_mas"].collidepoint(evento.pos):
                if indice_radio_salida < len(radios_salida_cm_lista) - 1:
                    indice_radio_salida += 1
                    recalcular_parametros()
            elif botones["radio_salida_menos"].collidepoint(evento.pos):
                if indice_radio_salida > 0:
                    indice_radio_salida -= 1
                    recalcular_parametros()

            # Lógica de botones para Velocidad de Entrada
            elif botones["velocidad_entrada_mas"].collidepoint(evento.pos):
                if indice_velocidad_entrada < len(velocidades_entrada_cm_s_lista) - 1:
                    indice_velocidad_entrada += 1
                    recalcular_parametros()
            elif botones["velocidad_entrada_menos"].collidepoint(evento.pos):
                if indice_velocidad_entrada > 0:
                    indice_velocidad_entrada -= 1
                    recalcular_parametros()


    pantalla.fill(BLANCO)

    # Dibujar bordes del tubo
    puntos_superiores, puntos_inferiores = [], []
    for dx in range(ancho_tubo + 1):
        x = x_tubo + dx
        progreso = dx / ancho_tubo
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
        y_superior = y_centro_tubo - radio_local
        y_inferior = y_centro_tubo + radio_local
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    pygame.draw.lines(pantalla, NEGRO, False, puntos_superiores, 2)
    pygame.draw.lines(pantalla, NEGRO, False, puntos_inferiores, 2)

    # Actualizar y dibujar partículas
    for p in particulas:
        dx = p.x - x_tubo
        progreso = dx / ancho_tubo
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
        if radio_local < 1:
            radio_local = 1
        p.actualizar_posicion_y(radio_local)
        p.actualizar_velocidad(radio_local)
        p.mover()
        p.dibujar(pantalla)

    # Dibujar texto informativo
    def dibujar_texto(texto, x, y, color=NEGRO):
        superficie = fuente.render(texto, True, color)
        pantalla.blit(superficie, (x, y))

    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 750, 40)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 750, 65)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 750, 90)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 750, 115)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 750, 145)
    dibujar_texto(f"Velocidad salida (centro): {velocidad_salida_cm_s:.1f} cm/s", 750, 170)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 750, 200)
    dibujar_texto(f"Fricción: {'Sí' if friccion else 'No'}", 750, 230)

    # Dibujar todos los botones usando el diccionario
    for nombre, rect in botones.items():
        pygame.draw.rect(pantalla, GRIS, rect)
        if "mas" in nombre:
            dibujar_texto("+", rect.x + 7, rect.y + 2)
        elif "menos" in nombre:
            dibujar_texto("-", rect.x + 9, rect.y + 2)


    pygame.display.flip()
    reloj.tick(fps)

pygame.quit()