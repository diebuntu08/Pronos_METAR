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

import requests
import re
from bs4 import BeautifulSoup

from .date_tools import registro_de_actividad

def scraping_metar(log, url):
    """
    Esta función scrapea la página de Ogimet.com para obtener el último METAR emitido
    por MROC.
    -----------------------
    Recibe dos parámetros.
    log: file, el archivo log para ir documentando los procesos con fecha y hora.
    url: string, la dirección de Ogimet.com de donde se extraerá el METAR más reciente.
    -----------------------
    Retorna el METAR más actual como una cadena de texto si logra conectar a la url,
    si no, retorna una cadena vacía
    """
    f = open("texto_web.txt", 'w')
    req = requests.get(url)
    statusCode = req.status_code
    if statusCode == 200:
        mensaje = "{}... Se accede correctamente a la página de Ogimet.com."
        registro_de_actividad(log, mensaje=mensaje)
        html = BeautifulSoup(req.text, "html.parser")
        entrada = html.find('pre')
        f.write(str(entrada))
        mensaje = "{}... Se escribe correctamente el METAR más reciente en el archivo 'texto_web.txt'."
        registro_de_actividad(log, mensaje=mensaje)
    else:
        mensaje = "{}... No se pudo acceder a la pádina de Ogimet.com."
        registro_de_actividad(log, mensaje=mensaje)
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
                registro_de_actividad(log, mensaje=mensaje)
                return " ".join(lista)
    return ''