#main.py

# === LIBRERÍAS NECESARIAS ===
import pygame      # Para gráficos y animación
import math        # Para funciones matemáticas como pi

<<<<<<< Updated upstream
# === OPCIÓN PARA ACTIVAR O DESACTIVAR FRICCIÓN ===
friccion = True     # Si es False, las partículas se moverán todas con la misma velocidad (flujo ideal sin fricción)
=======
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

presion_entrada_atm_lista= [2, 3, 4] #lista de presiones permitidas
indice_presion_entrada= 0 #comienza en 1 atm

# Variables que se inicializan con los valores de las listas (se recalcularán en recalcular_parametros)
radio_entrada_cm = radios_entrada_cm_lista[indice_radio_entrada]
radio_salida_cm = radios_salida_cm_lista[indice_radio_salida]
velocidad_entrada_cm_s = velocidades_entrada_cm_s_lista[indice_velocidad_entrada]
Altura_cm = alturas_cm_lista[indice_altura]
presion_entrada= presion_entrada_atm_lista[indice_presion_entrada]

# === VALORES CONSTANTES DE BERNULLI ===
gravedad_cm_s2=980
densidad_Agua_g_cm_3 = 1
>>>>>>> Stashed changes

# === ENTRADA DE DATOS DEL USUARIO ===
try:
    radio_entrada_cm = float(input("Radio de entrada (en cm, ej. 5): "))
    radio_salida_cm = float(input("Radio de salida (en cm, ej. 3): "))
    velocidad_entrada_cm_s = float(input("Velocidad de entrada (en cm/s, ej. 20): "))
    Altura_cm = float(input("Diferencia de altura(ne cm, ej. 10): "))
except:
    print("Entrada inválida. Saliendo.")
    exit()

<<<<<<< Updated upstream
# === CONVERSIÓN DE UNIDADES FÍSICAS A GRÁFICAS ===
=======
atm_a_g_cms_2= 1.01325e6
>>>>>>> Stashed changes
cm_a_px = 10
fps = 60

radio_entrada_px = radio_entrada_cm * cm_a_px
radio_salida_px = radio_salida_cm * cm_a_px

area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
area_salida_cm2 = math.pi * radio_salida_cm ** 2

Altura_px= Altura_cm * cm_a_px

caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s
caudal_lps = caudal_cm3_s / 1000

factor_visual = 100
velocidad_entrada_px = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual

velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2

# === CONFIGURACIÓN DE LA VENTANA ===
pygame.init()
ancho_pantalla, alto_pantalla = 1100, 400
pantalla = pygame.display.set_mode((ancho_pantalla, alto_pantalla))
pygame.display.set_caption("Simulación de Flujo Laminar (Poiseuille)")

fuente = pygame.font.SysFont("Arial", 18)

# === COLORES ===
BLANCO = (255, 255, 255)
AZUL = (50, 50, 255)
NEGRO = (0, 0, 0)

<<<<<<< Updated upstream
# === PARÁMETROS DEL TUBO ===
ancho_total=600
=======
# === BOTONES DE LA INTERFAZ ===
botones = {
    "radio_entrada_mas": pygame.Rect(950, 35, 30, 30),
    "radio_entrada_menos": pygame.Rect(910, 35, 30, 30),
    "radio_salida_mas": pygame.Rect(950, 65, 30, 30),
    "radio_salida_menos": pygame.Rect(910, 65, 30, 30),
    "velocidad_entrada_mas": pygame.Rect(1000, 140, 30, 30),
    "velocidad_entrada_menos": pygame.Rect(960, 140, 30, 30),
    "altura_mas": pygame.Rect(950, 255, 30, 30), # Nuevos botones para altura
    "altura_menos": pygame.Rect(910, 255, 30, 30), # Nuevos botones para altura
    "presion_mas": pygame.Rect(960, 285, 30, 30),
    "presion_menos": pygame.Rect(920, 285, 30, 30)
}
>>>>>>> Stashed changes

x_tubo = 50
ancho_tubo = 150 
y_centro_tubo = 300

x_diagonal=200
ancho_diagonal=300
y_centro_diagonal=300

x_tubo_salida=500
ancho_tubo_salida=150
y_centro_tubo_salida=y_centro_tubo-Altura_px


inclinacion=0.5

# === CLASE DE PARTÍCULAS ===
class Particula:
    def __init__(self, desplazamiento_y_normalizado):
        self.x = x_tubo
        self.desplazamiento_y = desplazamiento_y_normalizado
        self.y = 0
        self.velocidad = 0
        self.radio_particula = 4

    def actualizar_posicion_y(self, radio_local, altura_local):
        self.y = (y_centro_tubo + self.desplazamiento_y * radio_local) - altura_local


    
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
        if self.x > x_tubo + ancho_total:
            self.x = x_tubo
<<<<<<< Updated upstream
            self.y= 1000
=======
            self.y = 1000 #el primer frame spawneamos las particulas fuera del frame para evitar parpadeo
>>>>>>> Stashed changes

    def dibujar(self, pantalla):
        pygame.draw.circle(pantalla, AZUL, (int(self.x), int(self.y)), self.radio_particula)

# === CREACIÓN DE PARTÍCULAS ===
<<<<<<< Updated upstream
particulas = []
paso = 0.02
margen = 0.9
pos = -margen
while pos <= margen:
    particulas.append(Particula(pos))
    pos += paso
=======
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
    global presion_entrada_g_cms_2, presion_salida_g_cms_2
    global particulas # Necesitamos reiniciar las partículas

    # Actualizar valores CM de las listas
    radio_entrada_cm = radios_entrada_cm_lista[indice_radio_entrada]
    radio_salida_cm = radios_salida_cm_lista[indice_radio_salida]
    velocidad_entrada_cm_s = velocidades_entrada_cm_s_lista[indice_velocidad_entrada]
    Altura_cm = alturas_cm_lista[indice_altura] 
    presion_entrada= presion_entrada_atm_lista[indice_presion_entrada]

    # Convertir a Píxeles
    radio_entrada_px = radio_entrada_cm * cm_a_px
    radio_salida_px = radio_salida_cm * cm_a_px
    Altura_px = Altura_cm * cm_a_px 

    #convertir de atm a g\cm2
    presion_entrada_g_cms_2=presion_entrada * atm_a_g_cms_2

    # Recalcular áreas y caudales
    area_entrada_cm2 = math.pi * radio_entrada_cm ** 2
    area_salida_cm2 = math.pi * radio_salida_cm ** 2
    caudal_cm3_s = area_entrada_cm2 * velocidad_entrada_cm_s
    caudal_lps = caudal_cm3_s / 1000
    
    # Recalcular velocidades visuales y de salida
    velocidad_entrada_px = ((velocidad_entrada_cm_s / cm_a_px) / fps) * factor_visual
    velocidad_salida_cm_s = velocidad_entrada_cm_s * (radio_entrada_cm / radio_salida_cm) ** 2
    
    # Después de recalcular los parámetros que definen el tubo, reiniciar las partículas
    particulas = crear_particulas()

# Realizar el cálculo inicial al arrancar el programa
recalcular_parametros()

>>>>>>> Stashed changes

# === BUCLE PRINCIPAL DE LA SIMULACIÓN ===
reloj = pygame.time.Clock()
ejecutando = True

while ejecutando:
<<<<<<< Updated upstream
    pantalla.fill(BLANCO)

        # === DIBUJAR LOS BORDES DEL TUBO ===
    puntos_superiores, puntos_inferiores = [], []

    #parte 1 para la primera area

    for dx in range(ancho_tubo + 1):
        x = x_tubo + dx
        #radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso //guardado para la diagonal
        radio_local = radio_entrada_px
        y_superior = y_centro_tubo - radio_local
        y_inferior = y_centro_tubo + radio_local
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    dy_parts=Altura_px/ancho_diagonal
    dy=0
    for dx in range(ancho_diagonal):
        x=x_diagonal+dx
        progreso = dx / ancho_diagonal
        radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
        y_superior = (y_centro_tubo - radio_local)-dy
        y_inferior = (y_centro_tubo + radio_local)-dy
        dy=dy+dy_parts
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    for dx in range (ancho_tubo_salida+1):
        x = x_tubo_salida + dx
        #radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso //guardado para la diagonal
        radio_local = radio_salida_px 
        y_superior = y_centro_tubo_salida - radio_local
        y_inferior = y_centro_tubo_salida + radio_local
        puntos_superiores.append((x, y_superior))
        puntos_inferiores.append((x, y_inferior))

    pygame.draw.lines(pantalla, NEGRO, False, puntos_superiores, 2)
    pygame.draw.lines(pantalla, NEGRO, False, puntos_inferiores, 2)
    # print(puntos_superiores)
    # print(puntos_inferiores)

    #     #prueba comienzo del tubo Area 1 
    # pygame.draw.line(pantalla, NEGRO, (x_tubo,y_centro_tubo-radio_entrada_px), (x_tubo+ancho_tubo,y_centro_tubo-radio_entrada_px))
    # pygame.draw.line(pantalla, NEGRO, (x_tubo,y_centro_tubo+radio_entrada_px), (x_tubo+ancho_tubo,y_centro_tubo+radio_entrada_px))

    #      #prueba area diagonal
    # pygame.draw.line(pantalla, NEGRO, (x_diagonal,y_centro_tubo-radio_entrada_px), (x_diagonal+ancho_diagonal,(y_centro_tubo-radio_salida_px)-Altura_px))
    # pygame.draw.line(pantalla, NEGRO, (x_diagonal,y_centro_tubo+radio_entrada_px), (x_diagonal+ancho_diagonal,(y_centro_tubo+radio_salida_px)-Altura_px))

    #     #prueba final del tubo Area 2
    # pygame.draw.line(pantalla, NEGRO, (x_tubo_salida,y_centro_tubo_salida-radio_salida_px), (x_tubo_salida+ancho_tubo_salida,y_centro_tubo_salida-radio_salida_px))
    # pygame.draw.line(pantalla, NEGRO, (x_tubo_salida,y_centro_tubo_salida+radio_salida_px), (x_tubo_salida+ancho_tubo_salida,y_centro_tubo_salida+radio_salida_px))
=======
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
            
            # Lógica de botones para Altura (¡NUEVO!)
            elif botones["altura_mas"].collidepoint(evento.pos):
                if indice_altura < len(alturas_cm_lista) - 1:
                    indice_altura += 1
                    recalcular_parametros()
            elif botones["altura_menos"].collidepoint(evento.pos):
                if indice_altura > 0:
                    indice_altura -= 1
                    recalcular_parametros()
            elif botones["presion_mas"].collidepoint(evento.pos):
                if indice_presion_entrada < len(presion_entrada_atm_lista) - 1:
                    indice_presion_entrada += 1
                    recalcular_parametros()
            elif botones["presion_menos"].collidepoint(evento.pos):
                if indice_presion_entrada > 0:
                    indice_presion_entrada -= 1
                    recalcular_parametros()


    pantalla.fill(BLANCO)

    # # === DIBUJAR LOS BORDES DEL TUBO (LÓGICA DE EMI) ===
    # puntos_superiores, puntos_inferiores = [], []

    # # Segmento 1: Horizontal de Entrada
    # for dx in range(ancho_tubo_segmento1 + 1):
    #     x = x_tubo + dx
    #     radio_local = radio_entrada_px # Radio constante en este segmento
    #     y_superior = y_centro_tubo_base - radio_local
    #     y_inferior = y_centro_tubo_base + radio_local
    #     puntos_superiores.append((x, y_superior))
    #     puntos_inferiores.append((x, y_inferior))

    # # Segmento 2: Diagonal (Cambio de radio y altura)
    # # NOTA: Los puntos deben "engancharse" al final del segmento anterior y principio del siguiente
    # # Para asegurar continuidad, los rangos de dx y la interpolación deben ser precisos.
    # # Se genera una pequeña superposición de 1px al final del segmento anterior y al inicio del actual
    # # para asegurar que las líneas se unan correctamente.
    # for dx in range(ancho_diagonal + 1):
    #     x = x_diagonal + dx
    #     # Progreso dentro de este segmento específico (0 a 1)
    #     progreso = dx / ancho_diagonal
        
    #     # Interpolar el radio de entrada a salida a lo largo de la diagonal
    #     radio_local = radio_entrada_px - (radio_entrada_px - radio_salida_px) * progreso
        
    #     # Interpolar la altura central desde y_centro_tubo_base hasta (y_centro_tubo_base - Altura_px)
    #     y_centro_actual = y_centro_tubo_base - (Altura_px * progreso)
        
    #     y_superior = y_centro_actual - radio_local
    #     y_inferior = y_centro_actual + radio_local
    #     puntos_superiores.append((x, y_superior))
    #     puntos_inferiores.append((x, y_inferior))

    # # Segmento 3: Horizontal de Salida (Elevado)
    # for dx in range (ancho_tubo_salida + 1):
    #     x = x_tubo_salida + dx
    #     radio_local = radio_salida_px # Radio constante en este segmento
    #     y_superior = (y_centro_tubo_base - Altura_px) - radio_local # Usar la altura final del segmento diagonal
    #     y_inferior = (y_centro_tubo_base - Altura_px) + radio_local
    #     puntos_superiores.append((x, y_superior))
    #     puntos_inferiores.append((x, y_inferior))

    # pygame.draw.lines(pantalla, NEGRO, False, puntos_superiores, 2)
    # pygame.draw.lines(pantalla, NEGRO, False, puntos_inferiores, 2)

            #prueba comienzo del tubo Area 1 
    pygame.draw.line(pantalla, NEGRO, (x_tubo,y_centro_tubo_base-radio_entrada_px), (x_diagonal,y_centro_tubo_base-radio_entrada_px))
    pygame.draw.line(pantalla, NEGRO, (x_tubo,y_centro_tubo_base+radio_entrada_px), (x_diagonal,y_centro_tubo_base+radio_entrada_px))

         #prueba area diagonal
    pygame.draw.line(pantalla, NEGRO, (x_diagonal,y_centro_tubo_base-radio_entrada_px), (x_tubo_salida,(y_centro_tubo_base-radio_salida_px)-Altura_px))
    pygame.draw.line(pantalla, NEGRO, (x_diagonal,y_centro_tubo_base+radio_entrada_px), (x_tubo_salida,(y_centro_tubo_base+radio_salida_px)-Altura_px))

        #prueba final del tubo Area 2
    pygame.draw.line(pantalla, NEGRO, (x_tubo_salida,(y_centro_tubo_base-radio_salida_px)-Altura_px), (x_tubo_salida+ancho_tubo_salida,(y_centro_tubo_base-radio_salida_px)-Altura_px))
    pygame.draw.line(pantalla, NEGRO, (x_tubo_salida,(y_centro_tubo_base+radio_salida_px)-Altura_px), (x_tubo_salida+ancho_tubo_salida,(y_centro_tubo_base+radio_salida_px)-Altura_px))
>>>>>>> Stashed changes


    # === ACTUALIZAR Y DIBUJAR PARTÍCULAS ===
    for p in particulas:
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

    dibujar_texto(f"Radio entrada: {radio_entrada_cm:.1f} cm", 750, 40)
    dibujar_texto(f"Radio salida: {radio_salida_cm:.1f} cm", 750, 65)
    dibujar_texto(f"Área entrada: {area_entrada_cm2:.1f} cm²", 750, 90)
    dibujar_texto(f"Área salida: {area_salida_cm2:.1f} cm²", 750, 115)
    dibujar_texto(f"Velocidad entrada: {velocidad_entrada_cm_s:.1f} cm/s", 750, 145)
    dibujar_texto(f"Velocidad salida (centro): {velocidad_salida_cm_s:.1f} cm/s", 750, 170)
    dibujar_texto(f"Caudal estimado: {caudal_lps:.3f} L/s", 750, 200)
    dibujar_texto(f"Fricción: {'Sí' if friccion else 'No'}", 750, 230)
<<<<<<< Updated upstream
    dibujar_texto(f"Altura: {Altura_cm:.1f} cm", 750, 260)
=======
    dibujar_texto(f"Altura: {Altura_cm:.1f} cm", 750, 260) # Muestra la altura
    dibujar_texto(f"Presion de entrada: {presion_entrada} atm", 750, 290) # Muestra la presion de entrada
    dibujar_texto(f"Presion de salida: 1atm", 750, 320) # Muestra la presion de entrada

    # === DIBUJAR LOS BOTONES ===
    for nombre, rect in botones.items():
        pygame.draw.rect(pantalla, GRIS, rect)
        if "mas" in nombre:
            dibujar_texto("+", rect.x + 7, rect.y + 2)
        elif "menos" in nombre:
            dibujar_texto("-", rect.x + 9, rect.y + 2)
>>>>>>> Stashed changes

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False

    pygame.display.flip()
    reloj.tick(fps)

pygame.quit()

