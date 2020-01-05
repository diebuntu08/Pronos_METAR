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

def copiar_corrida_anterior(f_in, f_out):
    """
    Esta función lleva a cabo la copia de la corrida anterior para el registro y
    control de calidad de la aplicación.
    ------------------------
    Recibe dos parámetros:
    * f_in: file, el archivo de pronos.txt de donde se lee la corrida anterior.
    * f_out: file, el archivo de salidas.txt para escribir y guardar el historial de los pronósticos.
    ------------------------
    No retorna ningún valor.
    """
    lines = f_in.readlines()

    f_out.write(lines[0])
    f_out.write(lines[9])

    for line in range(11, 24):
        f_out.write(lines[line])
    