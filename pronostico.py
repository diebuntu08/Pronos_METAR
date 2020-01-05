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
import utils.forecast_tools as forecastools
from utils.classes.metar_class import METAR

log = open('log.txt', 'w')


# Direcciones de los archivos para leer y guardar las corridas anteriores
f_in = open('pronos.txt', 'r')
f_out = open('base/salidas.txt', 'a')

# Se lleva a cabo la copia de la corrida anterior.
#tools.copiar_corrida_anterior(f_in, f_out)
try:
    tools.copiar_corrida_anterior2(f_in, f_out)
    mensaje = "{}... Copia de la corrida anterior realizada satisfactoriamente."
    datetools.registro_de_actividad(log, mensaje=mensaje)
except:
    mensaje = "{}... La copia de la corrida anterior ha fallado!!"
    datetools.registro_de_actividad(log, mensaje=mensaje)

# Se cierran los archivos una vez se ha realizado la copia de la corrida anterior
f_in.close()
f_out.close()

# Se lee el archivo metar_data.csv para generar el dataframe de pandas
data = pd.read_csv('files/metar_data.csv', dtype=float)
try:
    data = pd.read_csv('files/metar_data.csv', dtype=float)
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

#print("Visibilidad del METAR: {}".format(vis))
#print("Nubes del METAR: {}".format(nubes))
#print("Tiempo presente del METAR: {}".format(t_presente))

mensaje = "{}... Se extraen los datos del objeto metar usando sus métodos públicos correctamente."
datetools.registro_de_actividad(log, mensaje=mensaje)
#print("Fecha: {}".format(fecha))
#print("Direccion: {}\nVelocidad: {}\nRafagas: {}".format(dirc, vel, raf))
#print("Temperatura: {}\nTemperatura rocío: {}".format(T, Tr))
#print("Presion: {}".format(presion))

# Se crea un nuevo objeto de tipo datetime.date con la fecha actual extraida del METAR
fecha = datetime.strptime(fecha, '%Y%m%d%H%M')
mensaje = "{}... Se genera un objeto tipo datetime.datetime con la fecha del METAR."
datetools.registro_de_actividad(log, mensaje=mensaje)

# Se crea el subset usando como criterio la fecha actual, este subset contiene todos los datos de la misma fecha
# de cada año +- 7 días, es decir, contiene datos de 15 días de cada año
subset = datetools.extraer_subset_fechas(data, fecha)
mensaje = "{}... Se extraen las filas que coinciden con la fecha actual +- 15 días del archivo CSV."
datetools.registro_de_actividad(log, mensaje=mensaje)
#print("Shape del subset: {}".format(subset.shape))
#print(subset.head(25))
#print(subset.tail(25))

# En la lista 'datos' se almacenarán todos los pronósticos para el despliegue a pantalla y archivo
datos = []
datos.append(forecastools.horas_pronosticadas(fecha))
mensaje = "{}... Se genera la lista de horas de pronóstico."
datetools.registro_de_actividad(log, mensaje=mensaje)

# Pronóstico para la variable QNH
pronostico_QNH = forecastools.pronostico("QNH", presion, 0.02, data, subset)
datos.append(pronostico_QNH)

# Pronóstico para la variable Temperatura
pronostico_TEMP = forecastools.pronostico("TEMP", T, 1., data, subset)
datos.append(pronostico_TEMP)

# Pronóstico para la variable Dirección del viento
pronostico_DIR = forecastools.pronostico("DIR", dirc, 20., data, subset)
datos.append(pronostico_DIR)

# Pronóstico para la variable Velocidad del viento
pronostico_MAG = forecastools.pronostico("MAG", vel, 4., data, subset)
datos.append(pronostico_MAG)

# Pronóstico para la variable Ráfagas de viento
#print("RAFAGAS ACTUALES: {}\nTIPO: {}".format(raf, type(raf)))
if raf == '0':
    pronostico_RAF = forecastools.pronostico("RAF", str(int(vel)+10), 4., data, subset)
else:
    pronostico_RAF = forecastools.pronostico("RAF", raf, 4., data, subset)

forecastools.verificar_pronostico_rafagas(pronostico_RAF, pronostico_MAG)
datos.append(pronostico_RAF)

# Pronósticos para la variable Visibilidad
pronostico_VIS = forecastools.pronostico("VIS", vis, 1000., data, subset)
datos.append(pronostico_VIS)

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
       +--------------------------------------------------------------------------------------------------------------------+\n
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
        VIS = int(round(datos[6][i], 0))
        print("{} {:3.2f} {:3.1f} {:3d} {:3d} {:3d} {:4d}".format(HORA, QNH, TEMP, DIR, MAG, RAF, VIS))
        #print("{} {:3.2f} {:3.1f} {:3d} {:3d} {:3d}".format(HORA, QNH, TEMP, DIR, MAG, RAF))
        lista.append("       | {:>8} {:13.2f} {:19.1f} {:23d} {:24d} {:22d} |".format(HORA, QNH, TEMP, DIR, MAG, RAF))
    t = (tabla.format('\n'.join(fila for fila in lista)))
    salida.write(t)

escribir_a_archivo()

salida.close()
log.close()
