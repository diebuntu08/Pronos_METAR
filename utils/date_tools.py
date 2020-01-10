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
from datetime import datetime, timedelta

def fecha_salida():
    """
    Esta función retorna la fecha a la cual es ejecutada y devuelve esa fecha en tiempo UTC.
    -----------------------
    No recibe parámetros
    -----------------------
    Retorna una fecha con formato %Y/%m/%d %H:%M:%S.
    Por ejemplo: 2019/08/01 22:45:25
    """
    hoy = datetime.utcnow()
    return( datetime.strftime(hoy, '%Y/%m/%d %H:%M:%S') )

def fecha_para_registro():
    """
    Esta función retorna la fecha a la cual es ejecutada y devuelve esa fecha.
    -----------------------
    No recibe parámetros
    -----------------------
    Retorna una fecha con formato %Y/%m/%d %H:%M:%S.
    Por ejemplo: 2019/08/01 22:45:25
    """
    hoy = datetime.today()
    return( datetime.strftime(hoy, '%Y/%m/%d %H:%M:%S') )

def registro_de_actividad(log, mensaje="{}... "):
    """
    Esta función registra la actividad realizada justo antes de ser ejecutada y
    la almacena en el archivo log.txt.
    -----------------------
    Puede recibir hasta 2 parámetros.
    log: file, el archivo log para ir documentando los procesos con fecha y hora.
    mensaje: string, el mensaje a escribir en el archivo log.
    -----------------------
    No retorna ningún valor.
    """
    fecha = fecha_para_registro()
    print(mensaje.format(fecha))
    log.write(mensaje.format(fecha) + '\n')

def fecha_para_metar():
    """
    Esta función retorna la fecha en una lista para la extracción del metar
    más reciente desde la web.
    -----------------------
    No recibe parámetros
    -----------------------
    Retorna una lista con año, mes, dia, hora y minuto actuales
    """
    lista = []
    hoy = datetime.utcnow()
    lista.append(hoy.year)
    lista.append(hoy.month)
    lista.append(hoy.day)
    lista.append(hoy.hour)
    lista.append(hoy.minute)
    return lista

def definir_rango_fechas(fecha):
    """
    Esta función define el rango de fechas para buscar dentro de la data de los METAR.
    ------------------------
    Recibe un parámetro.
    fecha: datetime.datetime, la fecha para generar el rango de búsqueda dentro del dataframe.
    ------------------------
    Retorna una lista con objetos de tipo fecha.
    """
    lista = []
    for d in range(-7, 8):
        if d < 0:
            lista.append(fecha - timedelta(days=abs(d)))
        else:
            lista.append(fecha + timedelta(days=d))
    return lista

def extraer_subset_fechas(data, fecha):
    """
    Esta función extrae un subset por rango de fechas.
    -------------------------
    Recibe dos parámetros.
    data: pd.DataFrame, el data frame para extraer los datos necesarios.
    fecha: datetime.datetime, la fecha para generar el rango de búsqueda dentro del dataframe.
    -------------------------
    Retorna el subset de acuerdo al rango de fechas deseado.
    """
    fechas = definir_rango_fechas(fecha)
    subset = data[(data['MES'] == fechas[0].month) | (data['MES'] == fechas[-1].month)]
    subset1 = subset[(subset['MES'] == fechas[0].month) & (subset['DIA'] == fechas[0].day)]
    for d in fechas[1:]:
        subset1 = pd.concat([subset1, subset[(subset['MES'] == d.month) & (subset['DIA'] == d.day)]], axis=0)
    subset1 = subset1[subset1['HORA'] == fecha.hour]
    return subset1
