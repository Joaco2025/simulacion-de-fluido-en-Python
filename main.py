import pygame
import sys
import math

friccion = True  # Fricción activada - Ahora controlable por botón

# === CONSTANTES FÍSICAS PARA BERNOULLI ===
DENSIDAD_AGUA_GCMS = 1.0     # Densidad del agua en g/cm³
GRAVEDAD_CMS2 = 981.0       # Aceleración de la gravedad en cm/s²
PRESION_ENTRADA_KPA = 100.0 # Presión inicial en la entrada en kPa (ej. 1 atmósfera estándar)

# Esta variable global guardará la energía total de Bernoulli calculada en la entrada
energia_total_bernoulli = 0.0 # En dinas/cm^2 (unidades de energía por volumen)

# === CONFIGURACIÓN INICIAL Y VALORES POR DEFECTO ===
# Listas de valores permitidos para control con botones
radios_entrada_cm_lista = [3, 4, 5, 6]
indice_radio_entrada = 0  # Comienza en 3 cm (primer elemento de la lista)

radios_salida_cm_lista = [2, 3, 4]
indice_radio_salida = 1  # Comienza en 3 cm (segundo elemento de la lista)

velocidades_entrada_cm_s_lista = [10, 15, 20, 25, 30]
indice_velocidad_entrada = 2  # Comienza en 20 cm/s (tercer elemento de la lista)

alturas_cm_lista = [0, 5, 10, 15, 20] # Lista de alturas permitidas
indice_altura = 2 # Comienza en 10 cm (tercer elemento de la lista)


# Variables que se inicializan con los valores de las listas (se recalcularán en recalcular_parametros)
radio_entrada_cm = radios_entrada_cm_lista[indice_radio_entrada]
radio_salida_cm = radios_salida_cm_lista[indice_radio_salida]
velocidad_entrada_cm_s = velocidades_entrada_cm_s_lista[indice_velocidad_entrada]
Altura_cm = alturas_cm_lista[indice_altura]


cm_a_px = 10
fps = 60
factor_visual = 100 # Para ajustar la velocidad visual de las partículas

# === PARÁMETROS DEL TUBO (BASADOS EN LA ESTRUCTURA DE EMI) ===
# Coordenadas y dimensiones de los tres segmentos del tubo
x_tubo = 50                 # Inicio del primer segmento horizontal
ancho_tubo_segmento1 = 150  # Longitud del primer segmento
y_centro_tubo_base = 300    # Altura central de referencia para el primer segmento (en px)

x_diagonal = x_tubo + ancho_tubo_segmento1 # Inicio del segmento diagonal (donde termina el 1ro)
ancho_diagonal = 300        # Longitud del segmento diagonal

x_tubo_salida = x_diagonal + ancho_diagonal # Inicio del segmento de salida (donde termina la diagonal)
ancho_tubo_salida = 150     # Longitud del segmento de salida
# y_centro_tubo_salida se calculará dinámicamente en recalcular_parametros

# === CONFIGURACIÓN DE LA VENTANA PYGAME ===
pygame.init()
ancho_pantalla, alto_pantalla = 1100, 400
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo Laminar (Multi-Segmento con Bernoulli)")

fuente = pygame.font.SysFont("Arial", 18)

# === COLORES ===
BLANCO = (255, 255, 255)
AZUL = (50, 50, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200) # Color para los botones
VERDE_ENCENDIDO = (0, 200, 0)
ROJO_APAGADO = (200, 0, 0)

# === BOTONES DE LA INTERFAZ ===
botones = {
    "radio_entrada_mas": pygame.Rect(950, 35, 30, 30),
    "radio_entrada_menos": pygame.Rect(910, 35, 30, 30),
    "radio_salida_mas": pygame.Rect(950, 65, 30, 30),
    "radio_salida_menos": pygame.Rect(910, 65, 30, 30),
    "velocidad_entrada_mas": pygame.Rect(1000, 140, 30, 30),
    "velocidad_entrada_menos": pygame.Rect(960, 140, 30, 30),
    "altura_mas": pygame.Rect(950, 255, 30, 30),
    "altura_menos": pygame.Rect(910, 255, 30, 30),
    "toggle_friccion": pygame.Rect(910, 225, 120, 25), # Nuevo botón para fricción
}


# === CLASE DE PARTÍCULAS ===
class Particula:
    def __init__(self, desplazamiento_y_normalizado):
        self.x = x_tubo # Las partículas siempre inician al principio del primer segmento
        self.desplazamiento_y = desplazamiento_y_normalizado # Posición relativa al centro del tubo
        self.y = 0
        self.velocidad = 0 # Velocidad en píxeles por fotograma
        self.radio_particula = 4
        self.radio_local_actual = radio_entrada_px # Para guardar el radio en la posición actual
        self.presion_local_kpa = 0.0 # Nuevo atributo para almacenar la presión local de la partícula

    def obtener_propiedades_segmento(self, x_pos):
        # Determina en qué segmento está la partícula y devuelve su radio local y y_centro local
        
        # Segmento 1: Horizontal de Entrada
        if x_tubo <= x_pos < x_diagonal:
            return radio_entrada_px, y_centro_tubo_base
        
        # Segmento 2: Diagonal (Cambio de radio y altura)
        elif x_diagonal <= x_pos < x_tubo_salida:
            longitud_segmento = ancho_diagonal
            if longitud_segmento == 0: progreso_en_segmento = 0 # Evitar división por cero
            else: progreso_en_segmento = (x_pos - x_diagonal) / longitud_segmento
            
            r_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso_en_segmento
            y_c_local = y_centro_tubo_base - (Altura_px * progreso_en_segmento)
            
            return r_local, y_c_local
        
        # Segmento 3: Horizontal de Salida (Elevado, radio constante)
        elif x_tubo_salida <= x_pos < x_tubo_salida + ancho_tubo_salida:
            return radio_salida_px, y_centro_tubo_base - Altura_px
        
        else: # Si la partícula está fuera de los límites (ej. justo al reiniciar)
            return radio_entrada_px, y_centro_tubo_base

    def actualizar_posicion_y(self):
        # Obtener el radio local y la altura central para la posición actual de la partícula
        self.radio_local_actual, y_centro_local_px = self.obtener_propiedades_segmento(self.x)
        
        # Ajustar la posición Y de la partícula
        self.y = y_centro_local_px + self.desplazamiento_y * self.radio_local_actual

        # Guardar la altura local en cm para usarla en el cálculo de Bernoulli
        self.h_local_cm = y_centro_local_px / cm_a_px

    def actualizar_velocidad(self):
        radio_local_px = self.radio_local_actual
        if radio_local_px < 1:
            radio_local_px = 1
        
        # === PRIMERO: Calcular la velocidad local de la partícula basada en CONTINUIDAD y FRICCIÓN ===
        # Área local para la continuidad
        area_local_cm2 = math.pi * (radio_local_px / cm_a_px)**2
        
        V_continuidad_local_cm_s = 0
        if area_local_cm2 > 0.001: # Evitar división por cero si el área es muy pequeña
            V_continuidad_local_cm_s = caudal_cm3_s / area_local_cm2
        
        # Aplicar perfil de fricción a esta velocidad de continuidad
        velocidad_base_cm_s = V_continuidad_local_cm_s
        if friccion: # Solo aplica el perfil si friccion está True
            perfil_exponente = 2
            minimo_relativo = 0.2
            factor = 1 - abs(self.desplazamiento_y) ** perfil_exponente
            factor = max(factor, minimo_relativo)
            velocidad_base_cm_s = V_continuidad_local_cm_s * factor
        
        # Opcional: Limitar la velocidad base si se vuelve muy alta
        if velocidad_base_cm_s > 1000: # Límite arbitrario para evitar disparates visuales
            velocidad_base_cm_s = 1000

        # Convertir a píxeles por fotograma para el movimiento visual
        self.velocidad = ((velocidad_base_cm_s / cm_a_px) / fps) * factor_visual
        
        # === SEGUNDO: Calcular la PRESION LOCAL de la partícula usando BERNOULLI ===
        # P_local = E_total - 0.5 * rho * V_local^2 - rho * g * h_local
        
        try:
            P_local_dinas_cm2 = energia_total_bernoulli - \
                                0.5 * DENSIDAD_AGUA_GCMS * (velocidad_base_cm_s ** 2) - \
                                DENSIDAD_AGUA_GCMS * GRAVEDAD_CMS2 * self.h_local_cm 
                                
            # Convertir a kPa para mostrar (1 dina/cm^2 = 0.0001 kPa)
            self.presion_local_kpa = P_local_dinas_cm2 / 10000
            
            # Asegurarse que la presión no sea negativa (físicamente, presión absoluta no puede ser negativa)
            if self.presion_local_kpa < 0:
                self.presion_local_kpa = 0 # O un valor muy pequeño
                
        except Exception as e:
            self.presion_local_kpa = 0

    def mover(self):
        self.x += self.velocidad
        # Reiniciar la partícula al inicio si sale del último segmento
        if self.x > x_tubo_salida + ancho_tubo_salida:
            self.x = x_tubo

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, AZUL, (int(self.x), int(self.y)), self.radio_particula)

# === CREACIÓN DE PARTÍCULAS ===
def crear_particulas():
    nuevas_particulas = []
    paso = 0.02
    margen = 0.9 # Margen para que las partículas no estén pegadas a la pared
    pos = -margen
    while pos <= margen:
        nuevas_particulas.append(Particula(pos))
        pos += paso
    return nuevas_particulas

# === FUNCIÓN PARA RECALCULAR PARÁMETROS ===
def recalcular_parametros():
    global radio_entrada_cm, radio_salida_cm, velocidad_entrada_cm_s, Altura_cm
    global radio_entrada_px, radio_salida_px, Altura_px
    global area_entrada_cm2, area_salida_cm2
    global caudal_cm3_s, caudal_lps, velocidad_entrada_px, velocidad_salida_cm_s
    global particulas, energia_total_bernoulli 
    global DENSIDAD_AGUA_GCMS, GRAVEDAD_CMS2, PRESION_ENTRADA_KPA 
    
    # Actualizar valores CM de las listas
    radio_entrada_cm = radios_entrada_cm_lista[indice_radio_entrada]
    radio_salida_cm = radios_salida_cm_lista[indice_radio_salida]
    velocidad_entrada_cm_s = velocidades_entrada_cm_s_lista[indice_velocidad_entrada]
    Altura_cm = alturas_cm_lista[indice_altura]

    # Convertir a Píxeles
    radio_entrada_px = radio_entrada_cm * cm_a_px
    radio_salida_px = radio_salida_cm * cm_a_px
    Altura_px = Altura_cm * cm_a_px

    # Recalcular áreas y caudales
    area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
    area_salida_cm2 = math.pi * radio_salida_cm ** 2
    caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s
    caudal_lps = caudal_cm3_s / 1000
    
    # Recalcular velocidad de entrada visual
    velocidad_entrada_px = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual
    
    # === Cálculo de la Energía Total de Bernoulli en la ENTRADA ===
    P_entrada_dinas_cm2 = PRESION_ENTRADA_KPA * 10000
    h_entrada_cm_ref = y_centro_tubo_base / cm_a_px # Altura de referencia en la entrada

    energia_total_bernoulli = P_entrada_dinas_cm2 + \
                              0.5 * DENSIDAD_AGUA_GCMS * (velocidad_entrada_cm_s ** 2) + \
                              DENSIDAD_AGUA_GCMS * GRAVEDAD_CMS2 * h_entrada_cm_ref

    # La velocidad de salida mostrada para display, calculada por continuidad
    velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2
    
    # Después de recalcular los parámetros que definen el tubo, reiniciar las partículas
    particulas = crear_particulas()

# Realizar el cálculo inicial al arrancar el programa
recalcular_parametros()


# === BUCLE PRINCIPAL DE LA SIMULACIÓN ===
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
            
            # Lógica de botones para Altura
            elif botones["altura_mas"].collidepoint(evento.pos):
                if indice_altura < len(alturas_cm_lista) - 1:
                    indice_altura += 1
                    recalcular_parametros()
            elif botones["altura_menos"].collidepoint(evento.pos):
                if indice_altura > 0:
                    indice_altura -= 1
                    recalcular_parametros()
            
            # Lógica para el botón de Fricción (¡NUEVO!)
            elif botones["toggle_friccion"].collidepoint(evento.pos):
                friccion = not friccion # Invierte el estado de la fricción
                recalcular_parametros() # Recalcula para aplicar el cambio al perfil de velocidad


    pantalla.fill(BLANCO)

    # === DIBUJAR LOS BORDES DEL TUBO ===
    puntos_superiores, puntos_inferiores = [], []

    # Segmento 1: Horizontal de Entrada
    for dx in range(x_tubo, x_diagonal + 1): # De x_tubo hasta el inicio de la diagonal
        radio_local = radio_entrada_px
        y_superior = y_centro_tubo_base - radio_local
        y_inferior = y_centro_tubo_base + radio_local
        puntos_superiores.append((dx, y_superior))
        puntos_inferiores.append((dx, y_inferior))

    # Segmento 2: Diagonal (Cambio de radio y altura)
    for dx in range(ancho_diagonal + 1): 
        x = x_diagonal + dx
        progreso = dx / ancho_diagonal
        
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
        y_centro_actual_px = y_centro_tubo_base - (Altura_px * progreso)
        
        y_superior = y_centro_actual_px - radio_local
        y_inferior = y_centro_actual_px + radio_local
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    # Segmento 3: Horizontal de Salida (Elevado)
    for dx in range(x_tubo_salida, x_tubo_salida + ancho_tubo_salida + 1):
        radio_local = radio_salida_px
        y_superior = (y_centro_tubo_base - Altura_px) - radio_local
        y_inferior = (y_centro_tubo_base - Altura_px) + radio_local
        puntos_superiores.append((dx, y_superior))
        puntos_inferiores.append((dx, y_inferior))

    pygame.draw.lines(pantalla, NEGRO, False, puntos_superiores, 2)
    pygame.draw.lines(pantalla, NEGRO, False, puntos_inferiores, 2)


    # === ACTUALIZAR Y DIBUJAR PARTÍCULAS ===
    for p in particulas:
        p.actualizar_posicion_y() 
        p.actualizar_velocidad()  
        p.mover()
        p.dibujar(pantalla)

    # === MOSTRAR TEXTO INFORMATIVO ===
    def dibujar_texto(texto, x, y, color=NEGRO):
        superficie = fuente.render(texto, True, color)
        pantalla.blit(superficie, (x, y))

    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 750, 40)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 750, 65)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 750, 90)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 750, 115)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 750, 145)
    dibujar_texto(f"Velocidad salida (Continuidad): {velocidad_salida_cm_s:.1f} cm/s", 750, 170)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 750, 200)
    
    dibujar_texto(f"Fricción:", 750, 230) # Texto para fricción

    dibujar_texto(f"Altura: {Altura_cm:.1f} cm", 750, 260)

    # Buscar una partícula cerca del centro de la salida para mostrar su presión
    presion_salida_mostrada_kpa = 0.0
    x_rango_salida_min = x_tubo_salida + ancho_tubo_salida * 0.5 # A la mitad del segmento de salida
    x_rango_salida_max = x_tubo_salida + ancho_tubo_salida     # Al final del segmento de salida

    particulas_cerca_salida = [p for p in particulas 
                               if x_rango_salida_min <= p.x < x_rango_salida_max 
                               and abs(p.desplazamiento_y) < 0.1] 

    if particulas_cerca_salida:
        presion_salida_mostrada_kpa = particulas_cerca_salida[0].presion_local_kpa
    
    dibujar_texto(f"Presión entrada: {PRESION_ENTRADA_KPA:.1f} kPa", 750, 295)
    dibujar_texto(f"Presión salida (teórica): {presion_salida_mostrada_kpa:.1f} kPa", 750, 320)
    dibujar_texto(f"Energía Bernoulli (E_ref): {energia_total_bernoulli:.0f} dinas/cm²", 750, 345)


    # === DIBUJAR LOS BOTONES ===
    for nombre, rect in botones.items():
        pygame.draw.rect(pantalla, GRIS, rect)
        if "mas" in nombre:
            dibujar_texto("+", rect.x + 7, rect.y + 2)
        elif "menos" in nombre:
            dibujar_texto("-", rect.x + 9, rect.y + 2)
        elif "toggle_friccion" in nombre: # Dibujar el botón de fricción
            # Cambiar color y texto según el estado de 'friccion'
            color_friccion_btn = VERDE_ENCENDIDO if friccion else ROJO_APAGADO
            pygame.draw.rect(pantalla, color_friccion_btn, rect)
            texto_friccion = "Fricción: Sí" if friccion else "Fricción: No"
            # Ajustar posición del texto dentro del botón
            texto_surf = fuente.render(texto_friccion, True, BLANCO)
            pantalla.blit(texto_surf, (rect.x + (rect.width - texto_surf.get_width()) / 2, rect.y + (rect.height - texto_surf.get_height()) / 2))


    pygame.display.flip()
    reloj.tick(fps)

pygame.quit()