#!/usr/bin/python
#-*-coding: utf-8-*-

from datetime import datetime
import re

hoy = datetime.utcnow()
anios = [x for x in range(2019, 2020)]

#formato = r'\sCABOK\s|\sCVAOK\s|\sCAOK\s|\sCAVK\s|\sCVOK\s|\sCAVUK\s|\sCAOVK\s|\s9999\sNSC\s|\s9999NSC\s|\sCAVIK\s|\sCAV0K\s'
#formato = r'CAVOK21'
#formato = r'\s99999\s|\s999\s'
#formato = r'(CAVOK)(\d{2})'
#formato = r'\s\d{6}\s|\s\d{4}Z\s|\s\d{5}Z\s'
#formato = r'KT\sNSC\s'
#formato = r'NOSI|NOSG|N0SIG|NSOIG|NOISG|NO\sSIG|N\sOSIG|NOSI\sG|NOS\sIG|NOSI\sG0'
formato = r'NOSIGG'
#formato = r'TEMP|TEPO|TEMP0|TMEPO|TEMOP|TEPMO|TEMP\sO|TEM\sPO|TE\sMPO|T\sEMPO'
#formato = r'BCMG|BECGM|BEMCG|BGECM|BECM\sG|BEC\sMG|BE\sCMG|B\sECMG|BECMGG|BECMGO'

for anio in anios:
	f = open('files/' + str(anio) + '.txt', 'r')
	f2 = open('nuevos/' + str(anio) + '.txt', 'w')
	for linea in f:
		#print(linea)
		linea = re.sub(formato, 'NOSIG', linea)
		f2.write(linea)
	f.close()
	f2.close()
