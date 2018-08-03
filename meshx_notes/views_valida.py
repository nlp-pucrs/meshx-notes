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

class ValidaPageView(TemplateView):
	template_name = 'valida.html'

	def zera_validaEN(self):
		dictValida = {}

		import gzip, pickle

		with gzip.open('dictValidaEN.dict.gz','wb') as fp:
			pickle.dump(dictValida,fp)
			fp.close()

	def zera_validaPT(self):
		dictValida = {}

		import gzip, pickle

		with gzip.open('./meshx_notes/data/dictValidaPT.dict.gz','wb') as fp:
			pickle.dump(dictValida,fp)
			fp.close()


	def get_context_data(self, **kwargs):
		context = super(ValidaPageView, self).get_context_data(**kwargs)



		context['eu'] = ""



		current_path = os.path.dirname(os.path.realpath(__file__))

		idioma  = self.request.GET.get('l')

		if idioma == "pt":
			caminho_dicionario = './data/dictMesh_.dict.gz'
			caminho_indice = './data/indiceReversoPT.dict.gz'
			caminho_valida = './data/dictValidaPT.dict.gz'
		else:
			caminho_dicionario = './data/dictMesh.dict_eng_.gz'
			caminho_indice = './data/indiceReversoEN.dict.gz'
			caminho_valida = './data/dictValidaEN.dict.gz'
				
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

		serial = self.request.GET.get('serial')

		posicoes = serial.split('-');

		ID = self.request.GET.get('ID')

		if ID != None:
			if ID in dictMesh:
				#for t in dictMesh[ID]:
				#Poe a escolha do usuario aqui

				val_valida = 2

				termos = ' '.join(dictMesh[ID]['terms'])

				for indice in indiceReverso:
					if indice == "tinham":
						context['eu'] = "tinham"
						break
					if '_i' in indice:
						val_valida = 2

						new_indice = indice.replace(' _i', '')
						#######3
						new_indice = new_indice.replace('_', ' ')

						if new_indice != '':
							if new_indice in serial:
								#if(new_indice == "tinham"):
								#context['eu'] = new_indice
								for palavra in posicoes:
									if new_indice ==  palavra[:-2]:
										val_valida =  palavra[-1:]
										context['eu'] = palavra[:-2]


									
						#Poe no dicionario
						if  val_valida != 2:
							dictValida[new_indice] = {
								'ID': ID,
								'target': val_valida
							}

								
							

			#Salva o dicionario
				with gzip.open(caminho_valida,'wb') as fp:
					pickle.dump(dictValida,fp)
					fp.close()
		#self.zera_validaPT()


		#Outro para teste
		
		return context
