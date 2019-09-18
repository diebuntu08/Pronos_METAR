#!/usr/bin/python
#-*-coding: utf-8-*-

"""Este es un modelo estadístico para el pronóstico de los valores de QNH para
las siguientes 12 horas en el Aeropuerto Internacional Juan Santamaría. El
funcionamiento de este programa consiste en una base de datos con todos los
reportes METAR desde el año 2005, de la cual se extraen todos los mensajes de la misma
fecha y hora, cuyo valor de QNH se acerque al valor de la condición inicial que es,
el METAR más reciente emitido. Se obtiene unpromedio para cada una de las horas
siguientes con los mensajes válidos que se encuentren en la base de datos.
La salida es un archivo que contiene dichos valores promedio.
"""

from datetime import datetime, timedelta
import re
import urllib.request
import time

__author__ = "Diego Antonio Garro Molina"
__copyright__ = "Copyright 2018, Diego Garro e Instituto Meteorológico Nacional"
__credits__ = "Diego Garro, Instituto Meteorologico Nacional"
__license__ = "None"
__version__ = "1.0.2"
__maintaier__ = "Diego Garro Molina"
__email__ = "dgarro@imn.ac.cr"
__status__ = "Developer"

log = open('log.txt', 'w')

def copiar_corrida_anterior():
	f = open('QNH12hrs_frcst_MROC.txt', 'r')
	f2 = open('base/salidas.txt', 'a')
	linea1 = f.readline()
	f2.write(linea1)
	for i in range(8):
		linea = f.readline()
	for linea in f:
		f2.write(linea)
	f.close()
	f2.close()
	print("Copia de corrida anterior completada.\n")
	log.write("Copia de corrida anterior completada.\n")

try:
	copiar_corrida_anterior(log)
except:
	print("Copia de corrida anterior fallida.\n")
	log.write("Copia de corrida anterior fallida.\n")
	pass

def definir_rango_fechas(fecha_actual):
	lista = []
	for delta in range(7, 0, -1):
		fecha = fecha_actual - timedelta(days=delta)
	lista.append(fecha_actual)
	for delta in range(1, 8):
		fecha = fecha_actual + timedelta(days=delta)
		lista.append(fecha)
	return lista

def definir_fecha():
	hoy = datetime.utcnow()
	anio = hoy.year
	mes = hoy.month
	dia = hoy.day
	hora = hoy.hour
	minute = hoy.minute
	rango = definir_rango_fechas(hoy)
	return(anio, mes, dia, hora, minute, rango)

def convertir_a_string(valor):
	if valor < 10:
		return('0' + str(valor))
	else:
		return str(valor)

def metar_reciente(anio, mes, dia, hora):
	mes = convertir_a_string(mes)
	dia = convertir_a_string(dia)
	hora = convertir_a_string(hora)
	direccion = 'https://www.ogimet.com/display_metars2.php?lugar=mroc&tipo=SA&ord=REV&nil=SI&fmt=txt&ano=%i&mes=%s&day=%s&hora=%s&anof=%i&mesf=%s&dayf=%s&horaf=%s&minf=05&enviar=Ver'
	url = direccion%(anio, mes, dia, hora, anio, mes, dia, hora)
	while True:
		try:
			r = urllib.request.urlopen(url)
			texto = r.read().decode('iso-8859-1')
			break
		except:
			time.sleep(30)
			continue
	f = open('metar.txt', 'w')
	f.write(texto)
	f.close()
	f2 = open('metar.txt', 'r')
	fecha = str(anio) + mes + dia + hora + '00'
	linea_ant = ''
	for linea in f2:
		igual = linea.count('=')
		if linea[0:12] == fecha:
			linea_ant += linea.replace('\n', '')
			if igual == 0:
				continue
			else:
				break
		elif linea[0:24] == '                        ' and igual > 0:
			linea = re.sub(r'\s+', ' ', linea)
			linea_ant += linea
			break
	f2.close()
	nil = linea_ant.count('NIL')
	if nil == 0:
		return(linea_ant, False)
	else:
		return(linea_ant, True)

def extrae_presion(metar):
	formato = r'A\d{4}'
	patron = re.compile(formato)
	lista = metar.split(' ')
	for entrada in lista:
		acierto = patron.match(entrada)
		if acierto:
			presion = format(float(entrada.replace('A', '')) / 100, '.2f')
			return float(presion)

def extrae_temperatura(metar):
	formato = r'\d{2}/\d{2}|\d{2}///'
	patron = re.compile(formato)
	lista = metar.split(' ')
	for entrada in lista:
		acierto = patron.match(entrada)
		if acierto:
			temp = float(re.sub(r'/\d{2}', '', entrada.replace('///', '')))
			return temp

def extrae_direccion_viento(metar):
	formato = r'\d{5}KT|\d{5}G\d{2}KT'
	formato_VRB = r'VRB\d{2}KT|VRB\d{2}G\d{2}KT'
	patron = re.compile(formato)
	patron_VRB = re.compile(formato_VRB)
	lista = metar.split(' ')
	for entrada in lista:
		acierto = patron.match(entrada)
		acierto_VRB = patron_VRB.match(entrada)
		if acierto:
			dirc = float(re.sub(r'\d{2}KT|\d{2}G\d{2}KT', '', entrada))
			return dirc
		elif acierto_VRB:
			return 'VRB'

def extrae_velocidad_viento(metar):
	formato = r'VRB\d{2}KT|\d{5}KT|VRB\d{2}G\d{2}KT|\d{5}G\d{2}KT'
	patron = re.compile(formato)
	lista = metar.split(' ')
	for entrada in lista:
		acierto = patron.match(entrada)
		if acierto:
			vel = float(entrada[3:5])
			return vel

def extrae_rafagas_viento(metar):
	formato = r'\d{5}G\d{2}KT'
	patron = re.compile(formato)
	lista = metar.split(' ')
	for entrada in lista:
		acierto = patron.match(entrada)
		if acierto:
			raf = float(entrada[6:8])
			return raf
	return None

def compara_presiones(metar_actual, metar_pasado):
	presion_actual = extrae_presion(metar_actual)
	presion_pasado = extrae_presion(metar_pasado)
	if presion_actual == presion_pasado:
		return True
	else:
		return False

def promedio(lista):
	suma = 0.0
	for valor in lista:
		suma += valor
	if suma == 0.0:
		return len(lista)
	else:
		return(suma / len(lista))

def promedio_direccion(lista):
	suma = 0.0
	vrb = 0
	for valor in lista:
		if valor == 'VRB':
			vrb += 1
		else:
			suma += valor
	if len(lista) == 0:
		return(0, 0)
	else:
		return(suma / (len(lista) - vrb), vrb / len(lista))

def promedio_rafagas(lista):
	suma = 0.0
	for valor in lista:
		suma += valor
	if len(lista) == 0:
		return 0
	else:
		return(suma / len(lista))

def extraer_data_1var(y, d, variables, listado, func=''):
	try:
		f = open('files/' + str(y) + '.txt', 'r')
		fecha = datetime(y, d.month, d.day, d.hour, 0, 0)
		formato = datetime.strftime(fecha, r'%Y%m%d%H%M')
		patron = re.compile(formato)
		for linea in f:
			acierto = patron.match(linea)
			if acierto:
				nil = linea.count('NIL')
				if nil == 0:
					var = globals()[func](linea)
					f.close()
					if var in variables:
						for x in range(1, 13):
							nueva_fecha = fecha + timedelta(hours=x)
							formato_nuevo = datetime.strftime(nueva_fecha, r'%Y%m%d%H%M')
							patron_nuevo = re.compile(formato_nuevo)
							f2 = open('files/' + str(nueva_fecha.year) + '.txt', 'r')
							for linea in f2:
								acierto_nuevo = patron_nuevo.match(linea)
								if acierto_nuevo:
									nil = linea.count('NIL')
									if nil == 0:
										var_nuevo = globals()[func](linea)
										if isinstance(var_nuevo, float):
											listado[x-1].append(var_nuevo)
									break
							f2.close()
	except:
		pass
	return listado

def extraer_data_2var(y, d, variables1, variables2, listado1, listado2, func1='', func2=''):
	try:
		f = open('files/' + str(y) + '.txt', 'r')
		fecha = datetime(y, d.month, d.day, d.hour, 0, 0)
		formato = datetime.strftime(fecha, r'%Y%m%d%H%M')
		patron = re.compile(formato)
		for linea in f:
			acierto = patron.match(linea)
			if acierto:
				nil = linea.count('NIL')
				if nil == 0:
					var1 = globals()[func1](linea)
					f.close()
					if var1 in variables1:
						for x in range(1, 13):
							nueva_fecha = fecha + timedelta(hours=x)
							formato_nuevo = datetime.strftime(nueva_fecha, r'%Y%m%d%H%M')
							patron_nuevo = re.compile(formato_nuevo)
							f2 = open('files/' + str(nueva_fecha.year) + '.txt', 'r')
							for linea in f2:
								acierto_nuevo = patron_nuevo.match(linea)
								if acierto_nuevo:
									nil = linea.count('NIL')
									if nil == 0:
										var1_nuevo = globals()[func1](linea)
										if isinstance(var1_nuevo, float):
											listado1[x-1].append(var1_nuevo)
										var2_nuevo = globals()[func2](linea)
										if isinstance(var2_nuevo, float):
											listado2[x-1].append(var2_nuevo)
									break
							f2.close()
	except:
		pass
	return(listado1, listado2)

def extraer_data_direccion(y, d, variables, listado, func=''):
	try:
		f = open('files/' + str(y) + '.txt', 'r')
		fecha = datetime(y, d.month, d.day, d.hour, 0, 0)
		formato = datetime.strftime(fecha, r'%Y%m%d%H%M')
		patron = re.compile(formato)
		for linea in f:
			acierto = patron.match(linea)
			if acierto:
				nil = linea.count('NIL')
				if nil == 0:
					var = globals()[func](linea)
					f.close()
					if var in variables:
						for x in range(1, 13):
							nueva_fecha = fecha + timedelta(hours=x)
							formato_nuevo = datetime.strftime(nueva_fecha, r'%Y%m%d%H%M')
							patron_nuevo = re.compile(formato_nuevo)
							f2 = open('files/' + str(nueva_fecha.year) + '.txt', 'r')
							for linea in f2:
								acierto_nuevo = patron_nuevo.match(linea)
								if acierto_nuevo:
									nil = linea.count('NIL')
									if nil == 0:
										var_nuevo = globals()[func](linea)
										if isinstance(var_nuevo, float) or var_nuevo == 'VRB':
											listado[x-1].append(var_nuevo)
									break
							f2.close()
	except:
		pass
	return listado

anio, mes, dia, hora, minuto, rango_fechas = definir_fecha()
metar, nil = metar_reciente(anio, mes, dia, hora)
metar = re.sub(r'\d{7}KT', 'VRB02KT', metar)
if nil == True:
	log.write('El metar más reciente aparece como "NIL". Espere la siguiente corrida\n')
	log.write('o ejecute de nuevo el programa manualmente cuando se arregle el problema.\n\n')
	exit(0)
presion_actual = extrae_presion(metar)
temp_actual = extrae_temperatura(metar)
dirc_actual = extrae_direccion_viento(metar)
vel_actual = extrae_velocidad_viento(metar)
raf_actual = extrae_rafagas_viento(metar)
presiones = [presion_actual+p for p in [-.02, -.01, .00, .01, .02]]
temperaturas = [temp_actual+t for t in [-1., 0., 1.]]
if dirc_actual != 'VRB':
	direcciones = [dirc_actual+dirc for dirc in [-20., -10., 0., 10., 20.]]
else:
	direcciones = [x for x in range(110, 250, 10)]
	direcciones.append('VRB')
velocidades = [vel_actual+vel for vel in [-3, -2, -1, 0, 1, 2, 3]]
if raf_actual == None:
	vels = [vel_actual+v for v in [-4., -3., -2., -1., 0., 1., 2., 3., 4.]]
	rafagas = [v+10 for v in vels]
else:
	rafagas = [raf_actual+r for r in [-4., -3., -2., -1., 0., 1., 2., 3., 4.]]
print(rafagas)
print('Se toman como condiciones iniciales:',presion_actual,temp_actual,dirc_actual,vel_actual,raf_actual,'. Estas se tomaron del METAR:\n')
print(metar)

anios = [x for x in range(2005, anio)]
listado_p = [[], [], [], [], [], [], [], [], [], [], [], []]
listado_T = [[], [], [], [], [], [], [], [], [], [], [], []]
listado_dir = [[], [], [], [], [], [], [], [], [], [], [], []]
listado_v = [[], [], [], [], [], [], [], [], [], [], [], []]
listado_raf = [[], [], [], [], [], [], [], [], [], [], [], []]
for y in anios:
	for d in rango_fechas:
		listado_p = extraer_data_1var(y, d, presiones, listado_p, func='extrae_presion')
		listado_T = extraer_data_1var(y, d, temperaturas, listado_T, func='extrae_temperatura')
		listado_dir = extraer_data_direccion(y, d, direcciones, listado_dir, func='extrae_direccion_viento')
		listado_v, listado_raf = extraer_data_2var(y, d, velocidades, rafagas, listado_v, listado_raf, func1='extrae_velocidad_viento', func2='extrae_rafagas_viento')
		#listado_v = extraer_data_1var(y, d, velocidades, listado_v, func='extrae_velocidad_viento')
		#listado_raf = extraer_data_1var(y, d, rafagas, listado_raf, func='extrae_rafagas_viento')

print('\n\nEstos son los datos que se promediarán por hora:')
horarios = []
time = hora
for lista in listado_p:
	time += 1
	if time == 24:
		time = 0
	hour = convertir_a_string(time)
	horarios.append(hour + 'Z')
	print(hour + 'Z:',lista,'\n',)
log.close()

def salida_datos(listado, decimales):
	promedios = []
	for lista in listado:
		prom = promedio(lista)
		promedios.append(float(round(prom, decimales)))
	return promedios

def salida_datos_direccion(listado, decimales):
	promedios = []
	porcentajes_vrb = []
	for lista in listado:
		prom, porc_vrb = promedio_direccion(lista)
		promedios.append(float(round(prom, decimales)))
		porcentajes_vrb.append(float(round(porc_vrb, decimales)))
	return(promedios, porcentajes_vrb)

def salida_datos_rafagas(listado, decimales):
	promedios = []
	for lista in listado:
		prom = promedio_rafagas(lista)
		promedios.append(float(round(prom, decimales)))
	return promedios

def convertir_a_string_viento(valor):
	if valor < 10:
		return('00' + str(int(round(valor, 0))))
	elif valor < 100:
		return('0' + str(int(round(valor, 0))))
	else:
		return(str(int(round(valor, 0))))

#SACA EL PROMEDIO DE CADA LISTA EN listado_p
promedios_p = salida_datos(listado_p, 2)

#SACA EL PROMEDIO EN CADA LISTA EN listado_T
promedios_T = salida_datos(listado_T, 1)

#SACA EL PROMEDIO DE CADA LISTA EN listado_dir
promedios_dir, porcentajes_vrb = salida_datos_direccion(listado_dir, 0)

#SACA EL PROMEDIO DE CADA LISTA EN listado_v
promedios_v = salida_datos(listado_v, 0)

#SACA EL PROMEDIO DE CADA LISTA EN listado_raf
promedios_raf = salida_datos_rafagas(listado_raf, 0)

print('\n\nLos valores pronosticados para las siguientes 12 horas son:\n')
#print(promedios_noround)
#print(horarios)
#print(promedios)

minuto = convertir_a_string(minuto)
hora = convertir_a_string(hora)
mes = convertir_a_string(mes)
dia = convertir_a_string(dia)
salida = open('QNH12hrs_frcst_MROC.txt', 'w')
salida.write('                                  ESTE MODELO CORRIÓ EL %s/%s/%i a las %s:%sUTC.\n'%(dia, mes, anio, hora, minuto))
salida.write('      PROMEDIO HORARIO PARA LAS PRÓXIMAS 12 HORAS DE LAS VARIABLES DE INTERÉS EN EL AEROPUERTO INT. JUAN SANTAMARÍA (MROC).\n')
salida.write('SALIDA DEL MODELO ESTADÍSTICO AEROData USANDO VALORES MEDIOS PARA EL QNH (inHg), TEMPERATURA (°C), DIRECCION Y VELOCIDAD DEL VIENTO.\n')
salida.write('                     INSTITUTO METEOROLÓGICO NACIONAL, DEPARTAMENTO DE METEOROLOGÍA SINÓPTICA Y AERONÁUTICA.\n\n')
salida.write('####################################################################################################################################\n\n')
salida.write('####################################################################################################################################\n\n')
salida.write('HORA UTC    QNH (inHg)    Temperatura (°C)    Direccion Viento (°)    Velocidad Viento (kt)    Ráfagas Viento (kt)\n')
for i in range(len(promedios_p)):
	dirc = convertir_a_string_viento(promedios_dir[i])
	v = convertir_a_string_viento(promedios_v[i])
	raf = convertir_a_string_viento(promedios_raf[i])
	time, qnh, T, vrb = horarios[i], promedios_p[i], promedios_T[i], int(porcentajes_vrb[1])
	print('%3s%6s%5s%5s%5s%5s\n'%(time.replace('Z', ''), format(qnh, '.2f'), format(T, '.1f'), dirc, v, raf))
	salida.write('%8s%14s%20s%24s%25s%23s\n'%(time.replace('Z', ''), format(qnh, '.2f'), format(T, '.1f'), dirc, v, raf))
salida.close()

