#!/usr/bin/python3
#-*-coding: utf-8-*-

from datetime import datetime
import re

f = open('files/metar_data.csv', 'w')

#f.write("118485,8,,,,,,,\n")
f.write('ANIO,MES,DIA,HORA,MINUTO,DIR,MAG,RAF,VIS,TIEMPO1,TIEMPO2,TIEMPO3,NUBES1,NUBES2,NUBES3,NUBES4,CAVOK,TEMP,DPTEMP,QNH\n')

anios = [x for x in range(2005, 2019)]

formatos = {"fecha" : r'\d{12}', "viento" : r'VRB\d{2}KT|VRB\d{2}G\d{2}KT|\d{5}KT|\d{5}G\d{2}KT',
			"vis" : r'\d{4}|\d{4}(N|E|W|S|NW|NE|SW|SE)', "cavok" : r'CAVOK', "temp" : r'\d{2}/\d{2}',
			"qnh" : r'A\d{4}|A////', "nubes": r'(FEW|SCT|BKN|OVC)\d{3}(CB|TCU)*',
			"tiempo": r'(\+|-)*(RA|DZ|SHRA|TSRA|FG|BR|BCFG)'}

formatos_viento = [r'VRB\d{2}KT', r'VRB\d{2}G\d{2}KT', r'\d{5}KT', r'\d{5}G\d{2}KT']

class Metar:

	nan = 'NaN'
	
	def __init__(self, metar):
		self.metar = metar.split(" ")
		self.pat_viento = re.compile(formatos["viento"])
		self.pat_vis = re.compile(formatos["vis"])
		self.pat_cavok = re.compile(formatos["cavok"])
		self.pat_temp = re.compile(formatos["temp"])
		self.pat_qnh = re.compile(formatos["qnh"])
		self.pat_nubes = re.compile(formatos["nubes"])
		self.pat_tiempo = re.compile(formatos["tiempo"])
		self.viento = "99999KT"
		self.vis = "-9999"
		self.cavok = "0"
		self.temp = "99/99"
		self.qnh = "A9999"
		self.tiempo = ["0"] * 3
		self.nubes = ["0"] * 4
	
	def extraer_datos(self):
		self.fecha = self.metar[0]
		self.separar_fecha()
		if "NIL=\n" in self.metar:
			self.cavok = self.nan
		else:
			indice_nubes = 0
			indice_tiempo = 0
			for entrada in self.metar:
				ac_viento = self.pat_viento.match(entrada)
				ac_vis = self.pat_vis.match(entrada)
				ac_cavok = self.pat_cavok.match(entrada)
				ac_temp = self.pat_temp.match(entrada)
				ac_qnh = self.pat_qnh.match(entrada)
				ac_tiempo = self.pat_tiempo.match(entrada)
				ac_nubes = self.pat_nubes.match(entrada)
				if ac_viento:
					self.viento = entrada
				elif ac_vis:
					self.vis = entrada
				elif ac_tiempo:
					if indice_tiempo > 2:
						continue
					self.tiempo[indice_tiempo] = "1"
					indice_tiempo += 1
				elif ac_nubes:
					if indice_nubes > 3:
						continue
					self.nubes[indice_nubes] = "1"
					indice_nubes += 1
				elif ac_cavok:
					self.cavok = entrada
					self.vis = "9999"
				elif ac_temp:
					self.temp = entrada
				elif ac_qnh:
					self.qnh = entrada
					break
				else:
					continue
	
	def separar_fecha(self):
		self.anio = self.fecha[:4]
		self.mes = self.fecha[4:6]
		self.dia = self.fecha[6:8]
		self.hora = self.fecha[8:10]
		self.minuto = self.fecha[10:12]
	
	def viento_tipo_1(self):
		self.dir = self.viento[0:3]
		self.mag = self.viento[3:5]
		self.raf = "0"
	
	def viento_tipo_2(self):
		self.dir = self.viento[0:3]
		self.mag = self.viento[3:5]
		self.raf = self.viento[6:8]
	
	def extraer_datos_viento(self):
		for formato in formatos_viento:
			patron = re.compile(formato)
			acierto = patron.match(self.viento)
			if acierto:
				index = formatos_viento.index(formato)
				if index == 0 or index == 2:
					self.viento_tipo_1()
				else:
					self.viento_tipo_2()
		if self.dir == '999':
			self.dir = self.nan
		elif self.dir == 'VRB':
			self.dir = '999'
		if self.mag == "99":
			self.mag = self.nan
			self.raf = self.nan
	
	def extrae_visibilidad(self):
		formato_dir = r'N|E|W|S|NE|NW|SE|SW'
		self.vis = re.sub(formato_dir, '', self.vis)
		zeta = self.vis.count("Z")
		if self.vis == '-9999':
			self.vis = self.nan
		if zeta > 0:
			self.vis = self.nan
	
	def extrae_cavok(self):
		if self.cavok == "CAVOK":
			self.cavok = "1"
	
	def extrae_temperaturas(self):
		if self.temp != "99/99":
			self.T = self.temp[0:2]
			self.Tr = self.temp[3:5]
		else:
			self.T = self.nan
			self.Tr = self.nan
	
	def extrae_qnh(self):
		self.qnh = re.sub(r'A', '', self.qnh)
		self.qnh = re.sub(r'=\n', '', self.qnh)
		if self.qnh == "////" or self.qnh == "9999":
			self.qnh = self.nan
		else:
			self.qnh = float(self.qnh) / 100
			self.qnh = str(self.qnh)
	
	def return_data(self):
		self.extraer_datos()
		self.extraer_datos_viento()
		self.extrae_visibilidad()
		self.extrae_cavok()
		self.extrae_temperaturas()
		self.extrae_qnh()
		lista = [self.anio, self.mes, self.dia, self.hora, self.minuto, self.dir,
				 self.mag, self.raf, self.vis, self.tiempo[0], self.tiempo[1],
				 self.tiempo[2], self.nubes[0], self.nubes[1], self.nubes[2],
				 self.nubes[3], self.cavok, self.T, self.Tr, self.qnh]
		return lista

separador = ","
for anio in anios:
	f1 = open("files/" + str(anio) + '.txt', 'r')
	for linea in f1:
		if linea[10:12] != '00':
			continue
		metar = Metar(linea)
		datos = metar.return_data()
		#if not "-9999" in datos:
		#	if not "-99" in datos:
		#		if not "-999" in datos:
		f.write(separador.join(datos) + '\n')
	f1.close()
f.close()
