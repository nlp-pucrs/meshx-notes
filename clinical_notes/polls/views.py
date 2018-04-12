from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.contrib import messages

###

from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
#importing loading from django template 
from django.template import loader

import pandas as pd

import gzip, pickle
import string


class PacientePageView(TemplateView):
	template_name = 'index.html'


	def get_context_data(self, **kwargs):
		context = super(PacientePageView, self).get_context_data(**kwargs)

		prescription = pd.read_csv('./excel_evol.csv.gz', compression='gzip', nrows=50000)

		m = prescription.loc[8] #valor que ha' aqui

		evolucao = m['DADOS DA EVOLUÇÃO'].split(' ');
		#Passando pelo xml
		
		with gzip.open('dictMesh.dict.gz','rb') as fp:
			dictMesh = pickle.load(fp)
			fp.close()


		#Verifica a lista para ver se a palavra esta no dicionario
		cont = 0
		for palavra in evolucao:
			for dui in dictMesh:
				d = dictMesh[dui]
				for t in d['terms']:
					if t.lower() == palavra.lower():
						teste = dictMesh[dui]['terms']
						termos = '<br/>- '.join(teste)
						evolucao[cont] = '<a href="#" data-ui="das" data-terms="Termos semelhantes:<br/>- '+termos+'" data-scope="Definicao: '+d['scope']+'">'+palavra+'</a>'
						cont +=1

				
		strr = ' '.join(evolucao)
		
		context['data'] = m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		return context

