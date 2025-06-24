#main.py

# === LIBRERÍAS NECESARIAS ===
import pygame       # Para gráficos y animación
import math         # Para usar funciones matemáticas como pi

# === ENTRADA DE DATOS DEL USUARIO ===
# Se piden tres datos físicos importantes para simular el flujo:
# 1. Radio de entrada del tubo
# 2. Radio de salida del tubo
# 3. Velocidad del fluido al entrar

try:
    radio_entrada_cm = float(input("Radio de entrada (en cm, ej. 5): "))
    radio_salida_cm = float(input("Radio de salida (en cm, ej. 3): "))
    velocidad_entrada_cm_s = float(input("Velocidad de entrada (en cm/s, ej. 20): "))
except:
    # Si el usuario no escribe un número válido, el programa termina
    print("Entrada inválida. Saliendo.")
    exit()

# === CONVERSIÓN DE UNIDADES FÍSICAS A GRÁFICAS ===
cm_a_px = 10    # Cada centímetro real se representa con 10 píxeles
fps = 60        # La animación mostrará 60 cuadros por segundo

# Convertimos los radios del tubo a píxeles
radio_entrada_px = radio_entrada_cm * cm_a_px
radio_salida_px = radio_salida_cm * cm_a_px

# Calculamos el área de entrada y salida del tubo en cm²
area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
area_salida_cm2 = math.pi * radio_salida_cm ** 2

# Calculamos el caudal (volumen por segundo) en litros por segundo
caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s    # cm³/s
caudal_lps = caudal_cm3_s / 1000                            # 1000 cm³ = 1 litro

# Factor visual para que el movimiento sea perceptible en la pantalla
factor_visual = 100

# Convertimos la velocidad de entrada a píxeles por cuadro
velocidad_entrada_px = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual

# Calculamos la velocidad de salida en el centro del tubo usando la conservación del caudal
velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2

# === CONFIGURACIÓN DE LA VENTANA Y PYGAME ===
pygame.init()
ancho_pantalla, alto_pantalla = 1400, 800
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo Laminar (Poiseuille)")

# Fuente para mostrar texto informativo
fuente = pygame.font.SysFont("Arial", 18)

# === COLORES UTILIZADOS ===
BLANCO = (255, 255, 255)  # Fondo
AZUL = (50, 50, 255)      # Partículas
NEGRO = (0, 0, 0)         # Bordes del tubo y texto

# === PARÁMETROS DEL TUBO (posición en pantalla) ===
x_tubo = 100      # posición horizontal inicial del tubo
ancho_tubo = 600  # longitud del tubo en píxeles
y_centro_tubo = 200 # altura del centro del tubo

# === CLASE QUE REPRESENTA UNA PARTÍCULA DE FLUIDO ===
class Particula:
    def __init__(self, desplazamiento_y_normalizado):
        self.x = x_tubo  # posición horizontal inicial
        self.desplazamiento_y = desplazamiento_y_normalizado  # valor entre -1 y 1 (posición relativa dentro del radio)
        self.y = 0       # se calculará en función del radio local
        self.velocidad = 0
        self.radio_particula = 4 # <-- Nuevo: Radio para las "pelotitas"

    def actualizar_posicion_y(self, radio_local):
        # Calcula la posición vertical dependiendo del radio en esa parte del tubo
        self.y = y_centro_tubo + self.desplazamiento_y * radio_local

    def actualizar_velocidad(self, radio_local):
        # Evita que haya divisiones por cero
        if radio_local < 1:
            radio_local = 1

        # Calcula la velocidad máxima en el centro para esa sección del tubo
        velocidad_maxima_local = velocidad_entrada_px * (radio_entrada_px / radio_local) ** 2

        # Calcula la velocidad de la partícula según su distancia al centro
        # Usamos un exponente < 2 para que el perfil sea más visual y menos físico, en caso contrario usamos 2
        perfil_exponente = 1.4
        self.velocidad = velocidad_maxima_local * (1 - abs(self.desplazamiento_y) ** perfil_exponente)

    def mover(self):
        # Mueve la partícula hacia la derecha
        self.x += self.velocidad
        # Si llega al final del tubo, la reinicia al principio
        if self.x > x_tubo + ancho_tubo:
            self.x = x_tubo

    def dibujar(self, pantalla):
        # Dibuja la partícula como una pequeña "pelotita" (círculo)
        pygame.draw.circle(pantalla, AZUL, (int(self.x), int(self.y)), self.radio_particula)


# === CREACIÓN DE TODAS LAS PARTÍCULAS DEL FLUIDO ===
# Aquí vamos a generar una serie de partículas que simulan el fluido moviéndose dentro del tubo.
# Estas partículas estarán distribuidas verticalmente a lo largo del radio del tubo.

particulas = []       # Lista vacía donde se guardarán todas las partículas

paso = 0.1             # Este valor define qué tan juntas están las partículas entre sí (espaciado vertical)
                       # Un valor más pequeño crea más partículas y una simulación más suave, pero más lenta.

margen = 0.9          # Queremos evitar colocar partículas justo en el borde superior/inferior del tubo,
                       # porque ahí la velocidad es casi cero y podrían no moverse mucho o salirse visualmente.

# Vamos a generar partículas desde la parte superior del radio (-0.9) hasta la inferior (+0.9)
# Nota: El rango [-1, 1] representa todo el radio vertical, pero usamos un poco menos por seguridad.
pos = -margen         # Comenzamos desde la parte superior normalizada

while pos <= margen:
    # Creamos una nueva partícula con ese valor de posición vertical normalizado
    particulas.append(Particula(pos))
    
    # Avanzamos al siguiente punto vertical donde colocaremos otra partícula
    pos += paso


# Creamos un reloj para controlar los FPS
reloj = pygame.time.Clock()
ejecutando = True

# === BUCLE PRINCIPAL DE LA SIMULACIÓN ===
while ejecutando:
    pantalla.fill(BLANCO)  # Limpiamos la pantalla en cada frame con color blanco para borrar el dibujo anterior.

    # === DIBUJAR LOS BORDES DEL TUBO ===
    puntos_superiores, puntos_inferiores = [], []  # Listas donde guardaremos los puntos para las líneas superior e inferior
    for dx in range(ancho_tubo + 1):              # Recorremos horizontalmente todo el ancho del tubo, pixel por pixel
        x = x_tubo + dx                            # Coordenada x actual en la pantalla
        progreso = dx / ancho_tubo                 # Progreso (0 a 1) desde la entrada hacia la salida del tubo

        # Calculamos el radio del tubo en esta posición (tubo tiene forma cónica)
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso

        # Coordenadas y de los bordes superior e inferior para esta posición x
        y_superior = y_centro_tubo - radio_local
        y_inferior = y_centro_tubo + radio_local

        # Guardamos los puntos para luego dibujar las líneas
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    # Dibuja las líneas que forman los bordes superior e inferior del tubo usando los puntos calculados
    pygame.draw.lines(pantalla, NEGRO, False, puntos_superiores, 2)
    pygame.draw.lines(pantalla, NEGRO, False, puntos_inferiores, 2)

    # === ACTUALIZAR Y DIBUJAR TODAS LAS PARTÍCULAS ===
    for p in particulas:                          # Para cada partícula en la lista...
        dx = p.x - x_tubo                         # Calculamos cuánto ha avanzado horizontalmente desde el inicio del tubo
        progreso = dx / ancho_tubo                # Convertimos ese avance en un valor normalizado de 0 a 1
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso  # Radio en esta posición

        # Nos aseguramos que el radio local no sea demasiado pequeño para evitar divisiones por cero
        if radio_local < 1:
            radio_local = 1

        # Actualizamos la posición vertical de la partícula según el radio local y su desplazamiento vertical normalizado
        p.actualizar_posicion_y(radio_local)

        # Calculamos la velocidad local de la partícula basada en su posición dentro del tubo (perfil parabólico)
        p.actualizar_velocidad(radio_local)

        # Movemos la partícula horizontalmente según la velocidad calculada
        p.mover()

        # Dibujamos la partícula en la pantalla
        p.dibujar(pantalla)

    # === MOSTRAR TEXTO INFORMATIVO EN PANTALLA ===
    def dibujar_texto(texto, x, y):
        # Crea una imagen de texto usando la fuente y color negro
        superficie = fuente.render(texto, True, NEGRO)
        # Pega la imagen del texto en la pantalla en la posición (x, y)
        pantalla.blit(superficie, (x, y))

    # Muestra varios datos útiles sobre la simulación en la parte derecha de la pantalla
    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 750, 40)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 750, 65)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 750, 90)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 750, 115)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 750, 145)
    dibujar_texto(f"Velocidad salida (centro): {velocidad_salida_cm_s:.1f} cm/s", 750, 170)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 750, 200)

    # === MANEJO DE EVENTOS (ej. cerrar la ventana) ===
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    # Actualiza la ventana con todo lo dibujado
    pygame.display.flip()
    reloj.tick(fps)  # limita los FPS para mantener la simulación estable

# Cierra Pygame al salir
pygame.quit()