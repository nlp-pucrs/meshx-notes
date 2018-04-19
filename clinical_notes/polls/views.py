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

		indice = int(self.request.GET.get('id'))

		if  (0 > indice) or (indice >= ( len(prescription.loc[::]) ) ) or indice == None:
			indice = 0

		m = prescription.loc[indice] #valor que ha' aqui

		evolucao = m['DADOS DA EVOLUÇÃO'].split(' ');
		#Passando pelo xml
		
		with gzip.open('dictMesh.dict.gz','rb') as fp:
			dictMesh = pickle.load(fp)
			fp.close()

		

		valida = False

		#Verifica a lista para ver se a palavra esta no dicionario
		cont = 0
		for palavra in evolucao:

			evolucao[cont] = palavra

			## Busca palavra no Mesh
			for dui in dictMesh:
				d = dictMesh[dui]
				for t in d['terms']:
					new_t = t.replace('<i>', '')
					new_t = new_t.replace('</i>', '')
					if new_t.lower() == palavra.lower():
						teste = dictMesh[dui]['terms']
						termos = '<br/>- '.join(teste)
						

						if(d['qualifier'] == 'anatomy & histology'):
							start_underline = '<span class = "anatomy">'
							end_underline = '</span>'
						elif(d['qualifier'] == 'methods'):
							start_underline = '<span class = "procedure">'
							end_underline = "</span>"
						elif(d['qualifier'] == 'diagnosis'):
							start_underline = '<span class = "diagnosis">'
							end_underline = '</span>'
						elif(d['qualifier'] == 'pharmacology'):
							start_underline = '<span class = "medication">'
							end_underline = '</span>'
						else:
							start_underline = ''
							end_underline = ''



						d['name'] = d['name'].replace('[', ' [')
						evolucao[cont] = start_underline+'<a style="color:inherit; text-decoration:none" href="#" data-id="<strong>ID: </strong>'+d['ID']+'<br/><br/>" data-name="<h3><a target= \'_blank\' href=\'https://meshb.nlm.nih.gov/record/ui?ui='+dui+'\'>'+d['name']+'<a></h3><br/>"  data-terms="<strong>Termos semelhantes:</strong><br/>- '+termos+'" data-scope="<strong>Definicao:</strong> '+d['scope']+'">'+palavra+'</a>'+end_underline
						break

					

			
			cont +=1
					
			
		strr = ' '.join(evolucao)
		
		context['data'] = m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		context['indice_avancar'] = int(indice+1)
		context['indice_retornar'] = indice-1
		context['ultima_posicao'] = len(m) - 1
		return context

###################################################


class PacientePageViewEng(TemplateView):
	template_name = 'index.html'
	
	def remove_accents(self, input_str):
		nfkd_form = unicodedata.normalize('NFKD', input_str)
		return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

	def get_context_data(self, **kwargs):
		context = super(PacientePageViewEng, self).get_context_data(**kwargs)

		prescription = pd.read_csv('./excel_evol_eng.csv.gz', compression='gzip', nrows=50000)

		indice = int(self.request.GET.get('id'))

		if  (0 > indice) or (indice >= ( len(prescription.loc[::]) ) ) or indice == None:
			indice = 0
		m = prescription.loc[indice]

		evolucao = m['DADOS DA EVOLUÇÃO'].split(' ');
		#Passando pelo xml
		
		with gzip.open('dictMesh.dict_eng.gz','rb') as fp:
			dictMesh = pickle.load(fp)
			fp.close()

		valida = False

		#Verifica a lista para ver se a palavra esta no dicionario
		cont = 0
		for palavra in evolucao:

			evolucao[cont] = palavra

			## Busca palavra no Mesh
			for dui in dictMesh:
				d = dictMesh[dui]
				for t in d['terms']:
					new_t = t.replace('<i>', '')
					new_t = new_t.replace('</i>', '')
					if new_t.lower() == palavra.lower():
						teste = dictMesh[dui]['terms']
						termos = '<br/>- '.join(teste)
						

						if(d['qualifier'] == 'anatomy & histology'):
							start_underline = '<span class = "anatomy">'
							end_underline = '</span>'
						elif(d['qualifier'] == 'methods'):
							start_underline = '<span class = "procedure">'
							end_underline = "</span>"
						elif(d['qualifier'] == 'diagnosis'):
							start_underline = '<span class = "diagnosis">'
							end_underline = '</span>'
						elif(d['qualifier'] == 'pharmacology'):
							start_underline = '<span class = "medication">'
							end_underline = '</span>'
						else:
							start_underline = ''
							end_underline = ''

						d['name'] = d['name'].replace('[', ' [')
						evolucao[cont] = start_underline+'<a style="color:inherit; text-decoration:none" href="#" data-id="<strong>ID: </strong>'+d['ID']+'<br/><br/>" data-name="<h3><a target= \'_blank\' href=\'https://meshb.nlm.nih.gov/record/ui?ui='+dui+'\'>'+d['name']+'<a></h3><br/>"  data-terms="<strong>Termos semelhantes:</strong><br/>- '+termos+'" data-scope="<strong>Definicao:</strong> '+d['scope']+'">'+palavra+'</a>'+end_underline
						break

					

			
			cont +=1

		strr = ' '.join(evolucao)
		
		context['data'] = m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		context['indice_avancar'] = indice+1
		context['indice_retornar'] = indice-1
		context['ultima_posicao'] = len(m) - 1
		return context