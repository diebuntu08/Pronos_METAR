#!/usr/bin/python3
#-*-coding: utf-8-*-

__author__ = "Diego Antonio Garro Molina"
__copyright__ = "Copyright 2019, Diego Garro e Instituto Meteorológico Nacional"
__credits__ = "Diego Garro, Instituto Meteorologico Nacional"
__license__ = "None"
__version__ = "1.0.2"
__maintaier__ = "Diego Garro Molina"
__email__ = "dgarro@imn.ac.cr"
__status__ = "Developer"

import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta

import utils.date_tools as datetools
import utils.scrap_tools as scraptools
import utils.tools as tools
from utils.classes.metar_class import METAR

log = open('log.txt', 'w')

def copiar_corrida_anterior():
    """
    Esta función lleva a cabo la copia de la corrida anterior para el registro y
    control de calidad de la aplicación.
    """
    pass

# Se lleva a cabo la copia de la corrida anterior.
try:
    copiar_corrida_anterior()
    mensaje = "{}... Copia de la corrida anterior realizada satisfactoriamente."
    datetools.registro_de_actividad(log, mensaje=mensaje)
except:
    mensaje = "{}... La copia de la corrida anterior ha fallado!!"
    datetools.registro_de_actividad(log, mensaje=mensaje)

# Se lee el archivo metar_data.csv para generar el dataframe de pandas
try:
    data = pd.read_csv('files/metar_data.csv')
    #print(data.head(10))
    #print(data.shape)
    mensaje = "{}... Archivo 'metar_data.csv' leido correctamente."
    datetools.registro_de_actividad(log, mensaje=mensaje)
except:
    mensaje = "{}... La lectura del archivo 'metar_data.csv' ha fallado inesperadamente."
    datetools.registro_de_actividad(log, mensaje=mensaje)
    exit()

# Lista con año, mes, dia, hora y minuto en formato UTC para scrapear el metar más actual
hoy = datetools.fecha_para_metar()

# URL de Ogimet.com para scrapear el metal más reciente
URL_BASE = 'https://www.ogimet.com/display_metars2.php?lugar=mroc&tipo=SA&ord=REV&nil=SI&fmt=txt&ano={}&mes={}&day={}&hora={}&anof={}&mesf={}&dayf={}&horaf={}&minf=05&enviar=Ver'
url = URL_BASE.format(hoy[0], str(hoy[1]).zfill(2), str(hoy[2]).zfill(2), str(hoy[3]).zfill(2), hoy[0], str(hoy[1]).zfill(2), str(hoy[2]).zfill(2), str(hoy[3]).zfill(2))

# Se scrapea el metar más actual desde la página de Ogimet.com
metar = scraptools.scraping_metar(log, url)
if metar != '':
    print(metar)
else:
    mensaje = "{}... No se pudo acceder al METAR."
    datetools.registro_de_actividad(log, mensaje=mensaje)
    exit()


# Se crea el objeto METAR para poder extraer todos los datos necesarios
metar_obj = METAR(metar)
mensaje = "{}... Se crea el objeto METAR, el cual servirá de condición inicial."
datetools.registro_de_actividad(log, mensaje=mensaje)

# Se extraen todos los datos con los métodos públicos del objeto METAR

# Se extrae la fecha
fecha = metar_obj.extraer_fecha()

# Se extraen los datos del viento
dirc, vel, raf = metar_obj.extraer_viento()
print("Los datos del viento: {}, {}, {}".format(dirc, vel, raf))

# Se extraen las temperaturas
T, Tr = metar_obj.extraer_temperaturas()

# Se extrae la presión
presion = metar_obj.extraer_presion()

# Se extrae la visibilidad
vis = metar_obj.extraer_visibilidad()

# Se extrae la nubosidad
nubes = metar_obj.extraer_tiempo()

# Se extrae el tiempo presente
t_presente = metar_obj.extraer_tiempo(tiempo='t_presente')

print("Visibilidad del METAR: {}".format(vis))
print("Nubes del METAR: {}".format(nubes))
print("Tiempo presente del METAR: {}".format(t_presente))

mensaje = "{}... Se extraen los datos del objeto metar usando sus métodos públicos correctamente."
datetools.registro_de_actividad(log, mensaje=mensaje)
#print("Fecha: {}".format(fecha))
#print("Direccion: {}\nVelocidad: {}\nRafagas: {}".format(dirc, vel, raf))
#print("Temperatura: {}\nTemperatura rocío: {}".format(T, Tr))
#print("Presion: {}".format(presion))

# Se crea un nuevo objeto de tipo datetime.date con la fecha actual extraida del METAR
fecha = datetime.strptime(fecha, '%Y%m%d%H%M')

# Se crea el subset usando como criterio la fecha actual, este subset contiene todos los datos de la misma fecha
# de cada año +- 7 días, es decir, contiene datos de 15 días de cada año
subset = datetools.extraer_subset_fechas(data, fecha)
#print("Shape del subset: {}".format(subset.shape))
#print(subset.head(25))
#print(subset.tail(25))

def extraer_datos_pronostico(subset, columna):
    """
    Esta función extrae los datos para realizar los pronósticos y los acumula en listas por hora, para las próximas
    12 horas.
    ------------------------------
    Recibe dos parámetros:
    * subset: pd.DataFrame, el subset correspondiente a las coincidencias de la condición incicial por fecha.
    * columna: string, la columna de o variable que se quiere pronosticar.
    ------------------------------
    Retorna una lista con listas de valores acomodados por hora para realizar los pronósticos.
    """
    filas = subset.index.tolist()
    listas_por_hora = []
    for f in filas:
        lista = []
        for h in range(1, 14):
            try:
                lista.append(data[columna][f+h])
            except:
                continue
        listas_por_hora.append(lista)
    return listas_por_hora

def promedios(listas):
    """
    Esta función calcula los promedios para cada hora.
    -----------------------------
    Recibe un parámetro:
    * listas: list, la lista que retorna la función extraer_datos_pronostico(subset, column).
    -----------------------------
    Retorna otra lista con los promedios calculados para cada hora.
    """
    lista = []
    for i in range(len(listas[0])):
        suma = 0
        contador = 0
        for l in listas:
            try:
                valor = l[i]
            except:
                continue
            if str(valor) == 'nan' or valor == 999.0:
                contador += 1
                continue
            suma += valor
        lista.append(suma / (len(listas) - contador))
    return lista

def extraer_subset_valor(columna, valor, delta):
    """
    Esta función extrae un subset de acuerdo a un rango de valores máximo y mínimo.
    ----------------------------
    Recibe tres parámetros:
    * columna: string, nombre de la columna correspondiente al rango de valores que quiere comparar.
    * valor: int o float, valor para la comparación.
    * delta: int o float, valor para generar el rango de la comparación.
    ----------------------------
    Retorna el subset extraído.
    """
    sub_subset = subset[(subset[columna] >= (valor-delta)) & (subset[columna] <= (valor+delta))]
    listas_por_hora = extraer_datos_pronostico(sub_subset, columna)
    #print(listas_por_hora)
    if len(listas_por_hora) > 0:
        return promedios(listas_por_hora)
    else:
        return([0] * 13)

def redondear_entero(valor):
    """
    Esta función redondea un número a la decena más cercana.
    ----------------------------
    Recibe un parámetro:
    * valor: int o float, valor a ser redondeado.
    ----------------------------
    Retorna el valor redondeado.
    """
    valor = round(valor, 0)
    residuo = float(str(valor).zfill(5)[-3:])
    if residuo >= 5:
        valor += 10 - residuo
    else:
        valor -= residuo
    return valor

def pronostico_redondeado(pronos):
    """
    Esta función redondea los valores de una lista y los almacena en otra la cual retornará
    al final del proceso.
    ----------------------------
    Recibe un parámetro:
    * pronos: list, la lista con los valores pronosticados que se desean redondear.
    ----------------------------
    Retorna una lista con los valores redondeados.
    """
    pronos_redondeado = []
    for valor in pronos:
        pronos_redondeado.append(redondear_entero(valor))
    return pronos_redondeado

def redondear_a_9999(valor):
    """
    Esta función cambia el valor de 10000 por 9999 par la visibilidad reinante.
    ----------------------------
    Recibe un parámetro:
    * valor: int o float, el valor a ser cambiado.
    ----------------------------
    Retorna el valor correspondiente de acuerdo con la condición.
    """
    if valor == 10000:
        return 9999
    return valor

def pronostico_redondeado_visibilidad(pronos):
    """
    Esta función redondea los valores pronosticados de la visibilidad reinante en una lista
    al millar más próximo.
    -----------------------------
    Recibe un parámetro:
    * pronos: list, la lista con los valores que se desean redondear.
    -----------------------------
    Retorna una lista con los valores redondeados al millar más próximo.
    """
    pronostico_redondeado = []
    for valor in pronos:
        if valor >= 1000:
            divisor = 1000
        else:
            divisor = 100
        valor = valor / divisor
        pronostico_redondeado.append(redondear_a_9999(round(valor, 0) * divisor))
    return pronostico_redondeado        

def pronostico(variable, valor, delta):
    """
    Esta función lleva a cabo el pronóstico para la variable especificada.
    ----------------------------
    Recibe tres parámetros:
    * variable: string, la variable que se quiere pronosticar.
    * valor: int o float, el valor inicial de la variable.
    * delta: int o float, el valor para generar el rango de búsqueda para las coincidencias.
    ----------------------------
    Retorna los valores pronosticados para las próximas 12 horas como una lista.
    """
    if valor == 'VRB':
        valor = 180.
    elif valor.isdigit():
        valor = tools.str2float(valor)
    elif valor == '':
        return ['///'] * 13
    if variable == "QNH":
        valor = valor / 100
    pronos = extraer_subset_valor(variable, valor, delta)
    if variable == "RAF":
        print("Pronóstico de Ráfagas: {}".format(pronos))
    if variable == "DIR":
        return pronostico_redondeado(pronos)
    if variable == "VIS":
        return pronostico_redondeado_visibilidad(pronos)
    return pronos

# En la lista 'datos' se almacenarán todos los pronósticos para el despliegue a pantalla y archivo
datos = []

def horas_pronosticadas():
    """
    Esta función genera una lista con las horas de pronóstico.
    ----------------------------
    No recibe ningún parámetro.
    ----------------------------
    Retorna las horas de pronóstico como una lista.
    """
    lista = []
    for i in range(1, 14):
        nueva_fecha = fecha + timedelta(hours=i)
        lista.append(nueva_fecha.hour)
    return lista

datos.append(horas_pronosticadas())

# Pronóstico para la variable QNH
pronostico_QNH = pronostico("QNH", presion, 0.02)
datos.append(pronostico_QNH)

# Pronóstico para la variable Temperatura
pronostico_TEMP = pronostico("TEMP", T, 1.)
datos.append(pronostico_TEMP)

# Pronóstico para la variable Dirección del viento
pronostico_DIR = pronostico("DIR", dirc, 20.)
datos.append(pronostico_DIR)

# Pronóstico para la variable Velocidad del viento
pronostico_MAG = pronostico("MAG", vel, 4.)
datos.append(pronostico_MAG)

# Pronóstico para la variable Ráfagas de viento
#print("RAFAGAS ACTUALES: {}\nTIPO: {}".format(raf, type(raf)))
if raf == '0':
    pronostico_RAF = pronostico("RAF", str(int(vel)+10), 4.)
else:
    pronostico_RAF = pronostico("RAF", raf, 4.)

def verificar_pronostico_rafagas():
    """
    Esta función verifica que cada entrada en la lista pronostico_RAF
    sea al menos mayor a 5 unidades de la misma entrada en pronostico_MAG.
    ----------------------------
    No recibe ningún parámetro.
    ----------------------------
    No retorna ningún resultado.
    """
    for i in range(len(pronostico_RAF)):
        if pronostico_RAF[i] < (pronostico_MAG[i] + 5.):
            pronostico_RAF[i] = 0

verificar_pronostico_rafagas()
datos.append(pronostico_RAF)

# Pronósticos para la variable Visibilidad
#pronostico_VIS = pronostico("VIS", vis, 1000.)
#datos.append(pronostico_VIS)

# Se crea el objeto de tipo file para escribir el pronóstico y se formatea el mismo para la salida
# del pronóstico.
salida = open("pronos.txt", "w")
fecha_salida = datetools.fecha_para_registro()
salida.write("ESTE MODELO CORRIÓ EL {}UTC.".format(fecha_salida).center(131, ' ') + '\n')
salida.write('PROMEDIO HORARIO PARA LAS PRÓXIMAS 12 HORAS DE LAS VARIABLES DE INTERÉS EN EL AEROPUERTO INT. JUAN SANTAMARÍA (MROC).'.center(131, ' ') + '\n')
salida.write('SALIDA DEL MODELO ESTADÍSTICO AEROData USANDO VALORES MEDIOS PARA EL QNH (inHg), TEMPERATURA (°C), DIRECCION Y VELOCIDAD DEL VIENTO.\n')
salida.write('INSTITUTO METEOROLÓGICO NACIONAL, DEPARTAMENTO DE METEOROLOGÍA SINÓPTICA Y AERONÁUTICA.'.center(131, ' ') + '\n')
salida.write('-' * 132 + '\n\n')
salida.write('-' * 132 + '\n\n')
tabla = """\
       +--------------------------------------------------------------------------------------------------------------------+
       | HORA UTC    QNH (inHg)    Temperatura (°C)    Direccion Viento (°)    Velocidad Viento (kt)    Ráfagas Viento (kt)  |
       |--------------------------------------------------------------------------------------------------------------------|
{}
       +--------------------------------------------------------------------------------------------------------------------+\
"""

def escribir_a_archivo():
    lista = []
    for i in range(13):
        HORA = str(datos[0][i]).zfill(2)
        QNH = round(datos[1][i], 2)
        TEMP = round(datos[2][i], 1)
        DIR = int(datos[3][i])
        MAG = int(round(datos[4][i], 0))
        RAF = int(round(datos[5][i], 0))
        #VIS = int(round(datos[6][i], 0))
        #print("{} {:3.2f} {:3.1f} {:3d} {:3d} {:3d} {:4d}".format(HORA, QNH, TEMP, DIR, MAG, RAF, VIS))
        print("{} {:3.2f} {:3.1f} {:3d} {:3d} {:3d}".format(HORA, QNH, TEMP, DIR, MAG, RAF))
        lista.append("       | {:>8} {:13.2f} {:19.1f} {:23d} {:24d} {:22d} |".format(HORA, QNH, TEMP, DIR, MAG, RAF))
    t = (tabla.format('\n'.join(fila for fila in lista)))
    salida.write(t)

escribir_a_archivo()

salida.close()
log.close()
