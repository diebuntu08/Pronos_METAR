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

import re

# Clase para crear objetos que describen las características del METAR
class METAR(object):
    """
    Esta clase crea un objeto METAR, evalúa cada entrada y extrae los datos de interés para
    generar los cálculos del pronóstico.
    """

    pronostico_tendencia = ['NOSIG', 'NSIG', 'NSOIG', 'NOSGI', 'NOSG', 'NOSI',
                            'BECMG', 'BCMG', 'BCEMG', 'BECGM', 'BECM', 'BECG',
                            'TEMPO', 'TMPO', 'TMEPO', 'TEMOP', 'TEMP', 'TEMO']

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
                    raf = entrada[6:8]
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
    
    def extraer_visibilidad(self):
        """
        Método: Extrae la visibilidad reinante del METAR.
        ------------------------
        No recibe ningún parámetro.
        ------------------------
        Retorna la visibilidad del METAR.
        """
        formato = r'\d{4}'
        formato_viento = r'\d{5}KT|\d{5}G\d{2}KT|VRB\d{2}KT|VRB\d{2}G\d{2}KT'
        for entrada in self.metar[4:]:
            acierto_viento = re.match(formato_viento, entrada)
            if acierto_viento:
                continue
            if entrada in self.pronostico_tendencia:
                break
            acierto = re.match(formato, entrada)
            if acierto:
                return(entrada)
        return '9999'
    
    def extraer_tiempo(self, tiempo='nubes'):
        """
        Método: Extrae las capas de nubes del METAR.
        ------------------------
        No recibe ningún parámetro:
        * tiempo: string, el tiempo a extraer, puede ser 'nubes' o 't_presente'.
        ------------------------
        Retorna una lista con las capas de nubes extraidas del METAR.
        """
        if tiempo == 'nubes':
            formato = r'(FEW|SCT|BKN|OVC)\d{3}(CB|TCU)*'
        elif tiempo == 't_presente':
            formato = r'(\+|-)*(RA|DZ|SHRA|TSRA|FG|BR|BCFG)'
        else:
            raise ValueError("Incorrect parameter! '{}' is not recognized".format(tiempo))
        TIEMPO = ''
        for entrada in self.metar[5:]:
            if entrada in self.pronostico_tendencia:
                break
            acierto = re.match(formato, entrada)
            if acierto:
                TIEMPO += entrada + ' '
        return TIEMPO.split(' ')[:-1]