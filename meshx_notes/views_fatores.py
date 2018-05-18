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

import re


#from .forms import valida


class FatoresPageView(TemplateView):
	template_name = 'fatores.html'

	def remove_accents(self, input_str):
		nfkd_form = unicodedata.normalize('NFKD', input_str)
		return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

	def get_context_data(self, **kwargs):
		context = super(FatoresPageView, self).get_context_data(**kwargs)

		#Verifica se ha idioma

		caminho_evolucao = './data/excel_evol.csv.gz'

		current_path = os.path.dirname(os.path.realpath(__file__))
		caminho_evolucao = os.path.join(current_path, caminho_evolucao)

		prescription = pd.read_csv(caminho_evolucao, compression='gzip', nrows=50000)


		#Verifica se ha o ID

		if self.request.GET.get('id') == None:
			indice = 0
		else:
			indice = int(self.request.GET.get('id'))

		if (0 > indice) or (indice >= ( len(prescription.loc[::]) ) ):
			indice = 0

		#valor que ha' aqui

		m = prescription.loc[indice] 

		#texto = re.sub(r'\W','',m['DADOS DA EVOLUÇÃO'])

		nfkd_form = unicodedata.normalize('NFKD', m['DADOS DA EVOLUÇÃO'])
		aux = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

		texto = re.sub('[^\w\s]','', aux)
		evolucao = texto.split(' ');
		evolucao_charespecial = m['DADOS DA EVOLUÇÃO'].split(' ');
		#texto = evolucao
		for i in range(len(evolucao_charespecial)):
			evolucao_charespecial[i] = re.sub(r'(\w)', r'([^\w\s])',r'\1 \2', evolucao_charespecial[i])
			evolucao_charespecial[i]  = re.sub(r'([^\w\s])', r'(\w)',r'\1 \2', evolucao_charespecial[i])

		#Verifica a lista para ver se a palavra esta no dicionario
		for i in range(len(evolucao)):

			palavra = evolucao[i]
			if(palavra != ' ' and palavra != ''):
				evolucao[i] = '<span onclick="sublinhar(this.id)" class="word" id="'+str(i)+'">'+palavra+'</span>'
			else:
				evolucao[i] = evolucao_charespecial[i]
		#Junta tudo novamente

		strr = ' '.join(evolucao)

		#Retorna pro template
		
		context['data'] =  m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		context['indice_avancar'] = indice+1
		context['indice'] = indice
		context['indice_retornar'] = indice-1
		context['ultima_posicao'] = len(prescription.loc[::])
		return context
