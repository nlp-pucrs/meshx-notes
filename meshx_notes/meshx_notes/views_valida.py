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

	def valida(self, **kwargs):
		context = super(ValidaPageView, self).valida(**kwargs)
		caminho_dicionario = '../data/dictMesh.dict.gz'

		with gzip.open(caminho_dicionario,'rb') as fd:
			dictMesh = pickle.load(fd)
			fd.close()

		ID = self.request.GET.get('ID')

		if ID != None:
			if ID in dictMesh:
				for t in dictMesh[ID]:
					#Poe a escolha do usuario aqui
					val_valida = self.request.GET.get(t[terms])

					#Caso ele nao tenha escolhido, entao sera nula
					if val_valida != 0 or val_valida != 1:
						val_valida = None

					#Poe no dicionario
					dictValida[t[terms]] = {
						'ID': ID,
						'target': val_valida
					}

			#Salva o dicionario
				with gzip.open('dictValida.dict.gz','wb') as fp:
					pickle.dump(dictValida,fp)
					fp.close()
			#Somente de teste
			else:
				dictValida['eu'] = {
					'ID': '21',
					'target': '45'
				}
				with gzip.open('dictValida.dict.gz','wb') as fp:
					pickle.dump(dictValida,fp)
					fp.close()

		#Outro para teste
		context['eu'] = "estou aqui funcionando!"
		return context