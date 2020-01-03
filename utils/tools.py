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