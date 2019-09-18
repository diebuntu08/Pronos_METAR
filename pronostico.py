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
import numpy as numpy
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime

log = open('log.txt', 'w')

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
    return( datetime.strftime(hoy, '%Y/%m/%d %H:%M:%S'))

def registro_de_actividad(mensaje):
    """
    Esta función registra la actividad realizada justo antes de ser ejecutada y
    la almacena en el archivo log.txt.
    -----------------------
    Recibe un único parámetro, el mensaje a ser impreso en pantalla y escrito en
    el archivo 'log.txt'.
    -----------------------
    No retorna ningún valor.
    """
    fecha = fecha_para_registro()
    print(mensaje.format(fecha))
    log.write(mensaje + '\n')

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
    registro_de_actividad(mensaje)
except:
    mensaje = "{}... La copia de la corrida anterior ha fallado!!"
    registro_de_actividad(mensaje)

# Se lee el archivo metar_data.csv para generar el dataframe de pandas
try:
    data = pd.read_csv('files/metar_data.csv')
    #print(data.head(10))
    #print(data.shape)
    mensaje = "{}... Archivo 'metar_data.csv' leido correctamente."
    registro_de_actividad(mensaje)
except:
    mensaje = "{}... La lectura del archivo 'metar_data.csv' ha fallado inesperadamente."
    registro_de_actividad(mensaje)
    exit()

# Lista con año, mes, dia, hora y minuto en formato UTC para scrapear el metar más actual
hoy = fecha_para_metar()

# URL de Ogimet.com para scrapear el metal más reciente
URL_BASE = 'https://www.ogimet.com/display_metars2.php?lugar=mroc&tipo=SA&ord=REV&nil=SI&fmt=txt&ano={}&mes={}&day={}&hora={}&anof={}&mesf={}&dayf={}&horaf={}&minf=05&enviar=Ver'
url = URL_BASE.format(hoy[0], str(hoy[1]).zfill(2), str(hoy[2]).zfill(2), str(hoy[3]).zfill(2), hoy[0], str(hoy[1]).zfill(2), str(hoy[2]).zfill(2), str(hoy[3]).zfill(2))

def scraping_metar():
    """
    Esta función scrapea la página de Ogimet.com para obtener el último METAR emitido
    por MROC.
    -----------------------
    No recibe parámetros
    -----------------------
    Retorna el METAR más actual como una cadena de texto si logra conectar a la url,
    si no, retorna una cadena vacía
    """
    f = open("texto_web.txt", 'w')
    req = requests.get(url)
    statusCode = req.status_code
    if statusCode == 200:
        mensaje = "{}... Se accede correctamente a la página de Ogimet.com."
        registro_de_actividad(mensaje)
        html = BeautifulSoup(req.text, "html.parser")
        entrada = html.find('pre')
        f.write(str(entrada))
        mensaje = "{}... Se escribe correctamente el METAR más reciente en el archivo 'texto_web.txt'."
        registro_de_actividad(mensaje)
    else:
        mensaje = "{}... No se pudo acceder a la pádina de Ogimet.com."
        registro_de_actividad(mensaje)
        return ''
    f.close()

    # Se abre de nuevo el archivo texto_web.txt para extraer el METAR
    formato = r'\d{12}'
    with open("texto_web.txt") as f:
        lista = []
        for linea in f:
            match = re.match(formato, linea)
            if match:
                lista.append(linea.replace('\n', ''))
                for linea in f:
                    if linea.count("</pre>") > 0:
                        break
                    lista.append(re.sub(r'\s{2,}', '', linea.replace('\n', '')))
                mensaje = "{}... Se lee correctamente el METAR más reciente desde el archivo 'texto_web.txt'."
                registro_de_actividad(mensaje)
                return " ".join(lista)
    return ''

metar = scraping_metar()
if metar != '':
    print(metar)
else:
    mensaje = "{}... No se pudo acceder al METAR"
    registro_de_actividad(mensaje + '\n')

class METAR(object):
    """
    Esta clase evalúa cada entrada del METAR y extrae los datos de interés para
    generar los cálculos del pronóstico.
    """

    def __init__(self, metar):
        """
        Constructor.
        ------------------------
        Recibe un único parámetro, el METAR como un string.
        ------------------------
        No retorna valores.
        """
        self.metar = metar.split(" ")
    
    def extraer_fecha(self):
        """
        Método: Extrae la fecha del METAR.
        ------------------------
        No recibe ningún parámetro.
        ------------------------
        Retorna la fecha del METAR.
        """
        return self.metar[0]
    
    def extraer_viento(self):
        """
        Método: Extrae el viento del METAR.
        ------------------------
        No recibe ningún parámetro.
        ------------------------
        Retorna el viento del METAR.
        """
        formato = r'\d{5}KT|\d{5}G\d{2}KT|VRB\d{2}KT|VRB\d{2}G\d{2}KT'
        for entrada in self.metar:
            acierto = re.match(formato, entrada)
            if acierto:
                dirc = entrada[0:3]
                vel = entrada[3:5]
                if 'G' in entrada:
                    raf = entrada[7:9]
                else:
                    raf = '0'
                return(dirc, vel, raf)
        return('', '', '')
    
    def extraer_temperaturas(self):
        """
        Método: Extrae las temperaturas del METAR.
        ------------------------
        No recibe ningún parámetro.
        ------------------------
        Retorna las temperaturas del METAR.
        """
        formato = r'\d{2}/\d{2}|\d{2}///|///\d{2}|/////'
        for entrada in self.metar:
            acierto = re.match(formato, entrada)
            if acierto:
                if entrada == '/////':
                    return('', '')
                T = entrada[0:2]
                Tr = entrada[3:]
                return(T, Tr)
        return('', '')
    
    def extraer_presion(self):
        """
        Método: Extrae la presión del METAR.
        ------------------------
        No recibe ningún parámetro.
        ------------------------
        Retorna la presión del METAR.
        """
        formato = r'A\d{4}|A////'
        for entrada in self.metar:
            acierto = re.match(formato, entrada)
            if acierto:
                return(entrada.replace('a', '').replace('A', ''))
        return ''

# Se crea el objeto METAR para poder extraer todos los datos necesarios
metar_obj = METAR(metar)
mensaje = "{}... Se crea el objeto METAR, el cual servirá de condición inicial."
registro_de_actividad(mensaje)

# Se extraen todos los datos con los métodos públicos del objeto METAR
fecha = metar_obj.extraer_fecha()
dirc, vel, raf = metar_obj.extraer_viento()
T, Tr = metar_obj.extraer_temperaturas()
presion = metar_obj.extraer_presion()
print("Fecha: {}".format(fecha))
print("Direccion: {}\nVelocidad: {}\nRafagas: {}".format(dirc, vel, raf))
print("Temperatura: {}\nTemperatura rocío: {}".format(T, Tr))
print("Presion: {}".format(presion))

def str2date():
    """
    Esta función crea un objeto datetime usando la fecha del METAR.
    ------------------------
    No recibe ningún parámetro.
    ------------------------
    Retorna el objeto datetime.
    """
    date = datetime.strptime(fecha, '%Y%m%d%H%M')
    return date

def str2float(valor):
    """
    Esta función cambia el tipo de un valor de string a float.
    ------------------------
    Recibe el valor a cambiar su tipo.
    ------------------------
    Retorna el valor como un float si es un dígito, de lo contrario retorna
    el mismo valor como string.
    """
    if valor.isdigit():
        return float(valor)
    return valor

fecha = str2date()
print(fecha.year, type(fecha.year))   
dirc = str2float(dirc)
print(dirc, type(dirc))     


log.close()