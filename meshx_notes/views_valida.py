from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.contrib import messages

###

from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
#importing loading from django template 
from django.template import loader

import pandas as pd
import os

import gzip, pickle
import string

from gensim.models import KeyedVectors
import unicodedata

from django.views.generic import TemplateView

import gzip, pickle

class ValidaClass():

	def salva_formulario(serial):
		current_path = os.path.dirname(os.path.realpath(__file__))
		caminho_dicionario = './data/dictMesh.dict.gz'
		caminho_indice = './data/indiceReversoPT.dict.gz'
		caminho_valida = './data/dictValida.dict.gz'
		caminho_dicionario = os.path.join(current_path, caminho_dicionario)
		caminho_indice = os.path.join(current_path, caminho_indice)
		caminho_valida = os.path.join(current_path, caminho_valida)

		with gzip.open(caminho_indice,'rb') as fd:
			indiceReverso = pickle.load(fd)
			fd.close()

		with gzip.open(caminho_dicionario,'rb') as fd:
			dictMesh = pickle.load(fd)
			fd.close()

		with gzip.open(caminho_valida,'rb') as fd:
			dictValida = pickle.load(fd)
			fd.close()

		dictValidaa = {}

		posicoes = serial.split('-');

		ID = posicoes[-1]

		if ID != None:
			if ID in dictMesh:
				#for t in dictMesh[ID]:
				#Poe a escolha do usuario aqui

				val_valida = 2

				termos = ' '.join(dictMesh[ID]['terms'])
				for indice in indiceReverso:
					if '<i>' in indice:
						indice_list = indice.split(' ');
						new_indice = indice_list[0]

						if new_indice in ' '.join(dictMesh[ID]['terms']):
							new_indice = new_indice.replace('</i>', '')
							new_indice = new_indice.replace('<i>', '')
							if new_indice in serial:
								for palavra in posicoes:
									if new_indice in  palavra:
										val_valida =  palavra[-1]
							
							#Poe no dicionario
							if  val_valida != None:
								dictValidaa[new_indice] = {
									'ID': ID,
									'target': val_valida
								}
							elif val_valida == None:
								try:
									dictValidaa[new_indice] = {
										'ID': dictValida[new_indice]['ID'],
										'target': dictValida[new_indice]['target']
									}
								except KeyError:
									pass
								

			#Salva o dicionario
				with gzip.open(caminho_valida,'wb') as fp:
					pickle.dump(dictValidaa,fp)
					fp.close()