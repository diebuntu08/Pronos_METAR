#!/usr/bin/python3
#-*-coding: utf-8-*-

import pandas as pd
import numpy as np

data = pd.read_csv('metar_data.csv')
print(data.head(10))
print(data.shape)

fechas = [8, 9, 10, 11, 12, 13, 14, 15]
subset = data[(data['DIA'] >= fechas[0]) & (data['DIA'] <= fechas[-1])]
print(subset.head())
print(subset.shape)
subset = subset[subset['MES'] == 1]
print(subset.head())
print(subset.shape)
qnhs = [29.99, 30.05]
subset = subset[(subset['QNH'] >= qnhs[0]) & (subset['QNH'] <= qnhs[-1])]
print(subset)
print(subset.shape)
subset = subset[subset['HORA'] == 11]
print(subset)
print(subset.shape)
print('El promedio del QNH es: {:.2f}'.format(subset['QNH'].mean()))
rows = subset.index.tolist()
mega_lista = []
for i in rows:
	lista = []
	for h in range(1, 13):
		lista.append(data['QNH'][i+h])
	mega_lista.append(lista)
print('La longitud de la lista es {}'.format(len(mega_lista)))
print('El promedio de la lista es: {:.2f}'.format(np.array(mega_lista).mean()))
print(mega_lista)
for i in range(len(mega_lista[0])):
	suma = 0
	for l in mega_lista:
		suma += l[i]
	print('El promedio de las posiciones {} en mega_lista es: {:.2f}'.format(i, suma / len(mega_lista)))
