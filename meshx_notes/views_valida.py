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

	def get_context_data(self, **kwargs):
		context = super(ValidaPageView, self).get_context_data(**kwargs)
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
					if '_i' in indice:
						context['eu'] = "estou aqui!"
						val_valida = 2

						new_indice = indice.replace(' _i', '')

						if new_indice in ' '.join(dictMesh[ID]['terms']):
							if new_indice in serial:
								for palavra in posicoes:
									if new_indice in  palavra:
										val_valida =  palavra[-1]
										
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

		#Outro para teste
		
		return context