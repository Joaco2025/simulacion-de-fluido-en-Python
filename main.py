#main.py

# === LIBRERÍAS NECESARIAS ===
import pygame      # Para gráficos y animación
import math        # Para funciones matemáticas como pi

# === OPCIÓN PARA ACTIVAR O DESACTIVAR FRICCIÓN ===
friccion = True # Si es False, las partículas se moverán todas con la misma velocidad (flujo ideal sin fricción)

# === ENTRADA DE DATOS DEL USUARIO ===
try:
    radio_entrada_cm = float(input("Radio de entrada (en cm, ej. 5): "))
    radio_salida_cm = float(input("Radio de salida (en cm, ej. 3): "))
    velocidad_entrada_cm_s = float(input("Velocidad de entrada (en cm/s, ej. 20): "))
except:
    print("Entrada inválida. Saliendo.")
    exit()

# === CONVERSIÓN DE UNIDADES FÍSICAS A GRÁFICAS ===
cm_a_px = 10
fps = 60

radio_entrada_px = radio_entrada_cm * cm_a_px
radio_salida_px = radio_salida_cm * cm_a_px

area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
area_salida_cm2 = math.pi * radio_salida_cm ** 2

caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s
caudal_lps = caudal_cm3_s / 1000

factor_visual = 100
velocidad_entrada_px = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual

velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2

# === CONFIGURACIÓN DE LA VENTANA ===
pygame.init()
ancho_pantalla, alto_pantalla = 1400, 800
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo Laminar (Poiseuille)")

fuente = pygame.font.SysFont("Arial", 18)

# === COLORES ===
BLANCO = (255, 255, 255)
AZUL = (50, 50, 255)
NEGRO = (0, 0, 0)

# === PARÁMETROS DEL TUBO ===
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

    def actualizar_posicion_y(self, radio_local):
        self.y = y_centro_tubo + self.desplazamiento_y * radio_local

    
    def actualizar_velocidad(self, radio_local):
        if radio_local < 1:
            radio_local = 1

        velocidad_maxima_local = velocidad_entrada_px * (radio_entrada_px / radio_local) ** 2

        if friccion:
            perfil_exponente = 2      # curva clásica en forma de parábola
            minimo_relativo = 0.2     # evita que las partículas más lejanas sean demasiado lentas

            # Calculamos un factor entre 0 (en los bordes) y 1 (en el centro)
            factor = 1 - abs(self.desplazamiento_y) ** perfil_exponente
            factor = max(factor, minimo_relativo)  # aseguramos un valor mínimo

            self.velocidad = velocidad_maxima_local * factor
        else:
            # Si no hay fricción, todas las partículas van a la misma velocidad
            self.velocidad = velocidad_maxima_local
            
    def mover(self):
        self.x += self.velocidad
        if self.x > x_tubo + ancho_tubo:
            self.x = x_tubo

    def dibujar(self, pantalla):
        pygame.draw.line(pantalla, AZUL, (int(self.x), int(self.y)), (int(self.x + 10), int(self.y)), 2)

# === CREACIÓN DE PARTÍCULAS ===
particulas = []
paso = 0.02
margen = 0.9
pos = -margen
while pos <= margen:
    particulas.append(Particula(pos))
    pos += paso

# === BUCLE PRINCIPAL DE LA SIMULACIÓN ===
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
    pantalla.fill(BLANCO)

    # === DIBUJAR LOS BORDES DEL TUBO ===
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

    # === ACTUALIZAR Y DIBUJAR PARTÍCULAS ===
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

    # === MOSTRAR TEXTO INFORMATIVO ===
    def dibujar_texto(texto, x, y):
        superficie = fuente.render(texto, True, NEGRO)
        pantalla.blit(superficie, (x, y))

    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 750, 40)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 750, 65)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 750, 90)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 750, 115)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 750, 145)
    dibujar_texto(f"Velocidad salida (centro): {velocidad_salida_cm_s:.1f} cm/s", 750, 170)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 750, 200)
    dibujar_texto(f"Fricción: {'Sí' if friccion else 'No'}", 750, 230)

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    pygame.display.flip()
    reloj.tick(fps)

pygame.quit()

