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

from .tools import str2float
from datetime import datetime, timedelta

def extraer_datos_pronostico(data, subset, columna):
    """
    Esta función extrae los datos para realizar los pronósticos y los acumula en listas por hora, para las próximas
    12 horas.
    ------------------------------
    Recibe tres parámetros:
    * data: pd.DataFrame, el subset de datos original con la totalidad de la data
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

def extraer_subset_valor(columna, valor, delta, data, subset):
    """
    Esta función extrae un subset de acuerdo a un rango de valores máximo y mínimo.
    ----------------------------
    Recibe cinco parámetros:
    * columna: string, nombre de la columna correspondiente al rango de valores que quiere comparar.
    * valor: int o float, valor para la comparación.
    * delta: int o float, valor para generar el rango de la comparación.
    * data: pd.DataFrame, el subset de datos original con la totalidad de la data
    * subset: pd.DataFrame, el subset correspondiente a las coincidencias de la condición incicial por fecha.
    ----------------------------
    Retorna el subset extraído.
    """
    sub_subset = subset[(subset[columna] >= (valor-delta)) & (subset[columna] <= (valor+delta))]
    listas_por_hora = extraer_datos_pronostico(data, sub_subset, columna)
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

def pronostico(variable, valor, delta, data, subset):
    """
    Esta función lleva a cabo el pronóstico para la variable especificada.
    ----------------------------
    Recibe cinco parámetros:
    * variable: string, la variable que se quiere pronosticar.
    * valor: int o float, el valor inicial de la variable.
    * delta: int o float, el valor para generar el rango de búsqueda para las coincidencias.
    * data: pd.DataFrame, el subset de datos original con la totalidad de la data
    * subset: pd.DataFrame, el subset correspondiente a las coincidencias de la condición incicial por fecha.
    ----------------------------
    Retorna los valores pronosticados para las próximas 12 horas como una lista.
    """
    if valor == 'VRB':
        valor = 180.
    elif valor.isdigit():
        valor = str2float(valor)
    elif valor == '':
        return ['///'] * 13
    if variable == "QNH":
        valor = valor / 100
    pronos = extraer_subset_valor(variable, valor, delta, data, subset)
    if variable == "RAF":
        print("Pronóstico de Ráfagas: {}".format(pronos))
    if variable == "DIR":
        return pronostico_redondeado(pronos)
    if variable == "VIS":
        return pronostico_redondeado_visibilidad(pronos)
    return pronos

def horas_pronosticadas(fecha):
    """
    Esta función genera una lista con las horas de pronóstico.
    ----------------------------
    Recibe un parámetro:
    * fecha: datetime.datetime, la fecha del METAR más reciente.
    ----------------------------
    Retorna las horas de pronóstico como una lista.
    """
    lista = []
    for i in range(1, 14):
        nueva_fecha = fecha + timedelta(hours=i)
        lista.append(nueva_fecha.hour)
    return lista

def verificar_pronostico_rafagas(pronos_RAF, pronos_MAG):
    """
    Esta función verifica que cada entrada en la lista pronostico_RAF
    sea al menos mayor a 5 unidades de la misma entrada en pronostico_MAG.
    ----------------------------
    No recibe ningún parámetro.
    ----------------------------
    No retorna ningún resultado.
    """
    for i in range(len(pronos_RAF)):
        if pronos_RAF[i] < (pronos_MAG[i] + 5.):
            pronos_RAF[i] = 0