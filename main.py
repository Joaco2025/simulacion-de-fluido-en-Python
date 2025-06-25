import pygame
import sys
import math

friccion = True  # Fricción activada - Ahora controlable por botón
caida_libre_activa = True # Caída libre activada por defecto - Ahora controlable por botón

# === CONSTANTES FÍSICAS PARA BERNOULLI Y CAÍDA LIBRE ===
DENSIDAD_AGUA_GCMS = 1.0     # Densidad del agua en g/cm³
GRAVEDAD_CMS2 = 981.0       # Aceleración de la gravedad en cm/s² (aprox 9.81 m/s²)
PRESION_ENTRADA_KPA = 100.0 # Presión inicial en la entrada en kPa (ej. 1 atmósfera estándar)
PRESION_ATMOSFERICA_KPA = 100.0 # Presión asumida a la salida del tubo (ej. atmosférica)

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

# === CONFIGURACIÓN DE LA VENTANA PYGAME ===
pygame.init()
ancho_pantalla, alto_pantalla = 1100, 600 # DEFINIDAS AQUÍ
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo Laminar y Caída Libre")

# Altura del suelo de la simulación (para la caída libre)
y_suelo_px = alto_pantalla - 20 # 20px desde abajo


# === PARÁMETROS DEL TUBO (BASADOS EN LA ESTRUCTURA DE EMI) ===
x_tubo = 50                 # Inicio del primer segmento horizontal
ancho_tubo_segmento1 = 150  # Longitud del primer segmento
y_centro_tubo_base = 300    # Altura central de referencia para el primer segmento (en px)

x_diagonal = x_tubo + ancho_tubo_segmento1 # Inicio del segmento diagonal (donde termina el 1ro)
ancho_diagonal = 300        # Longitud del segmento diagonal

x_tubo_salida = x_diagonal + ancho_diagonal # Inicio del segmento de salida (donde termina la diagonal)
ancho_tubo_salida = 150     # Longitud del segmento de salida


fuente = pygame.font.SysFont("Arial", 18)
fuente_ecuacion = pygame.font.SysFont("Arial", 22, bold=True) # Fuente para la ecuación
fuente_ecuacion_valores = pygame.font.SysFont("Arial", 16) # Fuente para la ecuación con valores


# === COLORES ===
BLANCO = (255, 255, 255)
AZUL = (50, 50, 255)
NEGRO = (0, 0, 0)
GRIS = (200, 200, 200) # Color para los botones
VERDE_ENCENDIDO = (0, 200, 0)
ROJO_APAGADO = (200, 0, 0)

# === FUNCIONES DE UTILIDAD ===
# Mueve la definición de dibujar_texto aquí, fuera del bucle principal
def dibujar_texto(texto, x, y, color=NEGRO, fuente_obj=fuente):
    superficie = fuente_obj.render(texto, True, color)
    pantalla.blit(superficie, (x, y))

# === BOTONES DE LA INTERFAZ ===
botones = {
    "radio_entrada_mas": pygame.Rect(950, 35, 30, 30),
    "radio_entrada_menos": pygame.Rect(910, 35, 30, 30),
    "radio_salida_mas": pygame.Rect(950, 65, 30, 30),
    "radio_salida_menos": pygame.Rect(910, 65, 30, 30),
    "velocidad_entrada_mas": pygame.Rect(1000, 140, 30, 30),
    "velocidad_entrada_menos": pygame.Rect(960, 140, 30, 30),
    "toggle_friccion": pygame.Rect(910, 225, 120, 25), 
    "altura_mas": pygame.Rect(950, 290, 30, 30), 
    "altura_menos": pygame.Rect(910, 290, 30, 30), 
    "toggle_caida_libre": pygame.Rect(910, 400, 150, 25), 
}


# === CLASE DE PARTÍCULAS ===
class Particula:
    def __init__(self, desplazamiento_y_normalizado):
        self.x = x_tubo 
        self.desplazamiento_y = desplazamiento_y_normalizado 
        self.y = 0 
        self.velocidad_x = 0 
        self.velocidad_y = 0 
        self.radio_particula = 4
        self.radio_local_actual = radio_entrada_px 
        self.presion_local_kpa = 0.0 
        self.estado = "EN_TUBO" 
        self.tiempo_caida_libre = 0 

    def obtener_propiedades_segmento(self, x_pos):
        if x_tubo <= x_pos < x_diagonal:
            return radio_entrada_px, y_centro_tubo_base
        elif x_diagonal <= x_pos < x_tubo_salida:
            longitud_segmento = ancho_diagonal
            if longitud_segmento == 0: progreso_en_segmento = 0 
            else: progreso_en_segmento = (x_pos - x_diagonal) / longitud_segmento
            
            r_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso_en_segmento
            y_c_local = y_centro_tubo_base - (Altura_px * progreso_en_segmento)
            
            return r_local, y_c_local
        elif x_tubo_salida <= x_pos < x_tubo_salida + ancho_tubo_salida:
            return radio_salida_px, y_centro_tubo_base - Altura_px
        else:
            return radio_entrada_px, y_centro_tubo_base

    def actualizar_posicion_y(self):
        if self.estado == "EN_TUBO":
            self.radio_local_actual, y_centro_local_px = self.obtener_propiedades_segmento(self.x)
            self.y = y_centro_local_px + self.desplazamiento_y * self.radio_local_actual
            self.h_local_cm = y_centro_local_px / cm_a_px # Altura local del centro del tubo en cm
        # No actualizamos Y en caída libre aquí, se hace en mover() con velocidad_y

    def actualizar_velocidad(self):
        if self.estado == "EN_TUBO":
            radio_local_px = self.radio_local_actual
            if radio_local_px < 1: radio_local_px = 1
            
            area_local_cm2 = math.pi * (radio_local_px / cm_a_px)**2
            
            V_continuidad_local_cm_s = 0
            if area_local_cm2 > 0.001: 
                V_continuidad_local_cm_s = caudal_cm3_s / area_local_cm2
            
            velocidad_base_cm_s = V_continuidad_local_cm_s
            if friccion: 
                perfil_exponente = 2
                minimo_relativo = 0.2
                factor = 1 - abs(self.desplazamiento_y) ** perfil_exponente
                factor = max(factor, minimo_relativo)
                velocidad_base_cm_s = V_continuidad_local_cm_s * factor
            
            if velocidad_base_cm_s > 1000: velocidad_base_cm_s = 1000

            self.velocidad_x = ((velocidad_base_cm_s / cm_a_px) / fps) * factor_visual
            self.velocidad_y = 0 
            
            # === Calcular la PRESION LOCAL de la partícula usando BERNOULLI ===
            try:
                P_local_dinas_cm2 = energia_total_bernoulli - \
                                    0.5 * DENSIDAD_AGUA_GCMS * (velocidad_base_cm_s ** 2) - \
                                    DENSIDAD_AGUA_GCMS * GRAVEDAD_CMS2 * self.h_local_cm 
                                    
                self.presion_local_kpa = P_local_dinas_cm2 / 10000
                if self.presion_local_kpa < 0: self.presion_local_kpa = 0
                    
            except Exception as e:
                self.presion_local_kpa = 0
        
        elif self.estado == "CAIDA_LIBRE":
            self.velocidad_y += (GRAVEDAD_CMS2 / cm_a_px / fps) 
            self.presion_local_kpa = 0 


    def mover(self):
        if self.estado == "EN_TUBO":
            self.x += self.velocidad_x
            # Transición a caída libre al salir del tubo
            if self.x > x_tubo_salida + ancho_tubo_salida:
                if caida_libre_activa: # Solo entra en caída libre si está activa
                    self.estado = "CAIDA_LIBRE"
                    # Usar la velocidad horizontal que tenía al salir del tubo
                    self.velocidad_y = 0 # Inicia caída vertical desde 0
                    self.tiempo_caida_libre = 0
                else: # Si caída libre no activa, reinicia en la entrada
                    self.x = x_tubo
                    # Asegura que la posición Y al reiniciar sea correcta para el estado "EN_TUBO"
                    self.y = y_centro_tubo_base + self.desplazamiento_y * radio_entrada_px 
                    self.velocidad_x = 0
                    self.velocidad_y = 0
                    self.tiempo_caida_libre = 0
        
        elif self.estado == "CAIDA_LIBRE":
            self.x += self.velocidad_x
            self.y += self.velocidad_y
            self.tiempo_caida_libre += (1 / fps) 
            
            # Si la partícula toca el "suelo", reiniciarla
            if self.y > y_suelo_px:
                self.x = x_tubo 
                # Asegura que la posición Y al reiniciar sea correcta para el estado "EN_TUBO"
                self.y = y_centro_tubo_base + self.desplazamiento_y * radio_entrada_px 
                self.velocidad_x = 0
                self.velocidad_y = 0
                self.estado = "EN_TUBO"
                self.tiempo_caida_libre = 0


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

# === FUNCIÓN PARA RECALCULAR PARÁMETROS ===
# Variables para los valores en vivo de la ecuación de Bernoulli
P1_eq_live_kpa = 0.0
V1_eq_live_cms = 0.0
H1_eq_live_cm = 0.0
P2_eq_live_kpa = 0.0
V2_eq_live_cms = 0.0
H2_eq_live_cm = 0.0

# Variable para la distancia de caída libre (hecha global para acceso directo desde el display)
distancia_horizontal_caida_libre_cm = 0.0


def recalcular_parametros():
    global radio_entrada_cm, radio_salida_cm, velocidad_entrada_cm_s, Altura_cm
    global radio_entrada_px, radio_salida_px, Altura_px
    global area_entrada_cm2, area_salida_cm2
    global caudal_cm3_s, caudal_lps, velocidad_entrada_px, velocidad_salida_cm_s
    global particulas, energia_total_bernoulli 
    global DENSIDAD_AGUA_GCMS, GRAVEDAD_CMS2, PRESION_ENTRADA_KPA 

    # Para los valores en vivo de la ecuación (Bernoulli)
    global P1_eq_live_kpa, V1_eq_live_cms, H1_eq_live_cm
    global P2_eq_live_kpa, V2_eq_live_cms, H2_eq_live_cm
    
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
    
    # === Cálculo de Caída Libre para el display (teórico) ===
    global distancia_horizontal_caida_libre_cm # Hacerla global para el texto
    distancia_horizontal_caida_libre_cm = 0.0 # Reiniciar
    
    # Solo calculamos la distancia de caída libre si la función está activa
    if caida_libre_activa:
        # Altura desde el centro del tubo de salida hasta el suelo
        h_caida_cm = (y_suelo_px - (y_centro_tubo_base - Altura_px)) / cm_a_px
        
        if h_caida_cm > 0:
            tiempo_caida_seg = math.sqrt(2 * h_caida_cm / GRAVEDAD_CMS2)
            distancia_horizontal_caida_libre_cm = velocidad_salida_cm_s * tiempo_caida_seg
    
    # === Actualizar Valores para la Ecuación de Bernoulli en vivo ===
    P1_eq_live_kpa = PRESION_ENTRADA_KPA
    V1_eq_live_cms = velocidad_entrada_cm_s
    H1_eq_live_cm = h_entrada_cm_ref

    # Para el punto 2, usaremos las condiciones teóricas de salida del tubo
    # (P2_eq_live_kpa y V2_eq_live_cms se actualizarán en el bucle principal a partir de una partícula)
    H2_eq_live_cm = (y_centro_tubo_base - Altura_px) / cm_a_px # Altura del centro del tubo de salida en cm


    # Después de recalcular los parámetros que definen el tubo, reiniciar las partículas
    particulas = crear_particulas()
    for p in particulas: # Asegurarse que todas inician EN_TUBO y en la posición correcta
        p.estado = "EN_TUBO"
        p.x = x_tubo
        p.actualizar_posicion_y() # Para que se posicionen correctamente al inicio
        p.velocidad_x = 0 
        p.velocidad_y = 0
        p.tiempo_caida_libre = 0


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
            
            # Lógica para el botón de Fricción
            elif botones["toggle_friccion"].collidepoint(evento.pos):
                friccion = not friccion
                recalcular_parametros()
            
            # Lógica para el botón de Caída Libre
            elif botones["toggle_caida_libre"].collidepoint(evento.pos):
                caida_libre_activa = not caida_libre_activa 
                recalcular_parametros() 


    pantalla.fill(BLANCO)

    # === DIBUJAR LOS BORDES DEL TUBO ===
    puntos_superiores, puntos_inferiores = [], []

    # Segmento 1: Horizontal de Entrada
    for dx in range(x_tubo, x_diagonal + 1): 
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

    # Dibujar el "suelo" solo si caída libre está activa
    if caida_libre_activa:
        pygame.draw.line(pantalla, NEGRO, (x_tubo_salida, y_suelo_px), (ancho_pantalla - 50, y_suelo_px), 2)


    # === ACTUALIZAR Y DIBUJAR PARTÍCULAS ===
    presion_salida_mostrada_kpa_temp = 0.0 # Variable temporal para acumular presión de salida
    V2_eq_live_cms_temp = 0.0 # Variable temporal para velocidad de salida en vivo
    particula_encontrada_salida = False # Flag para saber si encontramos una partícula representativa

    for p in particulas:
        p.actualizar_posicion_y() 
        p.actualizar_velocidad()  
        p.mover() 
        p.dibujar(pantalla)

        # Buscar una partícula representativa para la presión y velocidad de salida en vivo
        # Solo si está en el estado EN_TUBO y al final del último segmento
        if p.estado == "EN_TUBO" and p.x > (x_tubo_salida + ancho_tubo_salida * 0.75) and abs(p.desplazamiento_y) < 0.1:
            presion_salida_mostrada_kpa_temp = p.presion_local_kpa
            # Convertir la velocidad de px/fotograma a cm/s
            V2_eq_live_cms_temp = p.velocidad_x / ((factor_visual / cm_a_px) / fps)
            particula_encontrada_salida = True
    
    # Asignar los valores temporales a las globales después del bucle de partículas
    if particula_encontrada_salida:
        P2_eq_live_kpa = presion_salida_mostrada_kpa_temp
        V2_eq_live_cms = V2_eq_live_cms_temp
    else: # Si no hay partículas en la salida aún, usar valores por defecto o cero
        P2_eq_live_kpa = 0.0
        V2_eq_live_cms = velocidad_salida_cm_s # usar la de continuidad si no hay partícula visible

    # === MOSTRAR TEXTO INFORMATIVO ===
    # Ajuste de posiciones Y para los textos del panel derecho
    y_inicio_panel = 40 # Mismo inicio
    line_height = 25 # Espacio entre líneas
    
    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 750, y_inicio_panel)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 750, y_inicio_panel + line_height)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 750, y_inicio_panel + line_height * 2)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 750, y_inicio_panel + line_height * 3)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 750, y_inicio_panel + line_height * 4 + 10) # +10 para separación
    dibujar_texto(f"Velocidad salida (Continuidad): {velocidad_salida_cm_s:.1f} cm/s", 750, y_inicio_panel + line_height * 5 + 10)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 750, y_inicio_panel + line_height * 6 + 10)
    
    dibujar_texto(f"Fricción:", 750, y_inicio_panel + line_height * 7 + 10) 
    dibujar_texto(f"Altura: {Altura_cm:.1f} cm", 750, y_inicio_panel + line_height * 8 + 30) # +30 para más espacio
    
    dibujar_texto(f"Presión entrada: {PRESION_ENTRADA_KPA:.1f} kPa", 750, y_inicio_panel + line_height * 9 + 40)
    dibujar_texto(f"Presión salida (teórica): {P2_eq_live_kpa:.1f} kPa", 750, y_inicio_panel + line_height * 10 + 40)
    dibujar_texto(f"Energía Bernoulli (E_ref): {energia_total_bernoulli:.0f} dinas/cm²", 750, y_inicio_panel + line_height * 11 + 40)
    
    # Ajuste de posición para el texto de caída libre
    caida_libre_text_y = y_inicio_panel + line_height * 12 + 50
    if caida_libre_activa:
        dibujar_texto(f"Distancia horizontal caída libre: {distancia_horizontal_caida_libre_cm:.1f} cm", 750, caida_libre_text_y)
    else:
        dibujar_texto(f"Caída Libre: Desactivada", 750, caida_libre_text_y) 


    # === Ecuaciones de Bernoulli ===
    # Ajuste de posiciones para las ecuaciones en la parte inferior izquierda
    eq_x = 50
    eq_y_start = 450 # Posición Y de inicio para las ecuaciones
    
    # 1. Ecuación estática (simbólica)
    dibujar_texto("Ecuación de Bernoulli:", eq_x, eq_y_start, fuente_obj=fuente_ecuacion)
    dibujar_texto(r"$P_1 + \frac{1}{2}\rho v_1^2 + \rho g h_1 = P_2 + \frac{1}{2}\rho v_2^2 + \rho g h_2$", eq_x, eq_y_start + 25, fuente_obj=fuente_ecuacion)

    # 2. Ecuación con valores en vivo
    dibujar_texto("Con valores en vivo (Puntos 1 y 2):", eq_x, eq_y_start + 65, fuente_obj=fuente_ecuacion_valores)
    
    # Formatear la ecuación con los valores actuales
    # Reducimos la precisión de los decimales para que quepa bien
    # GRAVEDAD_CMS2 en .0f para no mostrar decimales en 981
    eq_live_str_pt1 = f"{P1_eq_live_kpa:.1f} + 0.5({DENSIDAD_AGUA_GCMS:.1f})({V1_eq_live_cms:.1f})^2 + ({DENSIDAD_AGUA_GCMS:.1f})({GRAVEDAD_CMS2:.0f})({H1_eq_live_cm:.1f})"
    eq_live_str_pt2 = f"{P2_eq_live_kpa:.1f} + 0.5({DENSIDAD_AGUA_GCMS:.1f})({V2_eq_live_cms:.1f})^2 + ({DENSIDAD_AGUA_GCMS:.1f})({GRAVEDAD_CMS2:.0f})({H2_eq_live_cm:.1f})"
    
    dibujar_texto(eq_live_str_pt1, eq_x, eq_y_start + 90, fuente_obj=fuente_ecuacion_valores)
    dibujar_texto("=", eq_x + fuente_ecuacion_valores.render(eq_live_str_pt1, True, NEGRO).get_width() / 2, eq_y_start + 105, fuente_obj=fuente_ecuacion_valores)
    dibujar_texto(eq_live_str_pt2, eq_x, eq_y_start + 125, fuente_obj=fuente_ecuacion_valores)


    # === DIBUJAR LOS BOTONES ===
    # Ajuste de posición para los botones en el panel derecho (se coordinan con los textos)
    botones["radio_entrada_mas"].y = y_inicio_panel -5
    botones["radio_entrada_menos"].y = y_inicio_panel -5
    
    botones["radio_salida_mas"].y = y_inicio_panel + line_height -5
    botones["radio_salida_menos"].y = y_inicio_panel + line_height -5

    botones["velocidad_entrada_mas"].y = y_inicio_panel + line_height * 4 + 10 -5
    botones["velocidad_entrada_menos"].y = y_inicio_panel + line_height * 4 + 10 -5

    botones["toggle_friccion"].y = y_inicio_panel + line_height * 7 + 10 -2 # Un poco más arriba para centrar con el texto "Fricción"
    
    botones["altura_mas"].y = y_inicio_panel + line_height * 8 + 30 -5
    botones["altura_menos"].y = y_inicio_panel + line_height * 8 + 30 -5
    
    botones["toggle_caida_libre"].y = caida_libre_text_y - 2 # Ajustar al texto de caída libre


    for nombre, rect in botones.items():
        if "toggle_friccion" in nombre: 
            color_friccion_btn = VERDE_ENCENDIDO if friccion else ROJO_APAGADO
            pygame.draw.rect(pantalla, color_friccion_btn, rect)
            texto_friccion = "Sí" if friccion else "No"
            texto_surf = fuente.render(texto_friccion, True, BLANCO)
            pantalla.blit(texto_surf, (rect.x + (rect.width - texto_surf.get_width()) / 2, rect.y + (rect.height - texto_surf.get_height()) / 2))
        elif "toggle_caida_libre" in nombre: 
            color_caida_libre_btn = VERDE_ENCENDIDO if caida_libre_activa else ROJO_APAGADO
            pygame.draw.rect(pantalla, color_caida_libre_btn, rect)
            texto_caida_libre = "Caída Libre: Sí" if caida_libre_activa else "Caída Libre: No"
            texto_surf = fuente.render(texto_caida_libre, True, BLANCO)
            pantalla.blit(texto_surf, (rect.x + (rect.width - texto_surf.get_width()) / 2, rect.y + (rect.height - texto_surf.get_height()) / 2))
        else: # El resto de botones (radios, velocidad, altura)
            pygame.draw.rect(pantalla, GRIS, rect)
            if "mas" in nombre:
                dibujar_texto("+", rect.x + 7, rect.y + 2)
            elif "menos" in nombre:
                dibujar_texto("-", rect.x + 9, rect.y + 2)


    pygame.display.flip()
    reloj.tick(fps)

pygame.quit()