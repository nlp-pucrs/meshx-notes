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

from gensim.models import KeyedVectors
import unicodedata


class PacientePageView(TemplateView):
	template_name = 'index.html'
		
	def remove_accents(self, input_str):
		nfkd_form = unicodedata.normalize('NFKD', input_str)
		return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])
	


	def get_context_data(self, **kwargs):

		context = super(PacientePageView, self).get_context_data(**kwargs)

		prescription = pd.read_csv('./excel_evol.csv.gz', compression='gzip', nrows=50000)
		wordModel = KeyedVectors.load_word2vec_format('health_w2v_unigram_50.bin', binary=True)

		m = prescription.loc[15] #valor que ha' aqui

		evolucao = m['DADOS DA EVOLUÇÃO'].split(' ');
		#Passando pelo xml
		
		with gzip.open('dictMesh.dict.gz','rb') as fp:
			dictMesh = pickle.load(fp)
			fp.close()

		

		valida = False

		#Verifica a lista para ver se a palavra esta no dicionario
		cont = 0
		for palavra in evolucao:
			for dui in dictMesh:
				d = dictMesh[dui]
				for t in d['terms']:
					if t.lower() == palavra.lower():
						teste = dictMesh[dui]['terms']
						termos = '<br/>- '.join(teste)
						evolucao[cont] = '<a href="#" data-name="<h3>'+d['name']+'</h3><br/>"  data-terms="<b>Termos semelhantes:</b><br/>- '+termos+'" data-scope="<b>Definicao:</b> '+d['scope']+'">'+palavra+'</a>'
						cont +=1
						valida = True
						break
			if valida == False:
				evolucao[cont] = palavra
				cont +=1
				sem_assento = self.remove_accents(palavra)
				if palavra in wordModel.vocab:
					palavra_similar = wordModel.most_similar_cosmul(sem_assento,topn=20)
					for p in palavra_similar:
						if sem_assento == p[0]:
							for t in d['terms']:
								if t.lower() == p[0].lower():
									teste = dictMesh[dui]['terms']
									termos = '<br/>- '.join(teste)
									evolucao[cont] = '<a href="#" data-name="<h3>'+d['name']+'</h3><br/>"  data-terms="<b>Termos semelhantes:</b><br/>- '+termos+'" data-scope="<b>Definicao:</b> '+d['scope']+'">'+palavra+'</a>'
									cont +=1
									break


			valida = False
					
			
		strr = ' '.join(evolucao)
		
		context['data'] = m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		return context

