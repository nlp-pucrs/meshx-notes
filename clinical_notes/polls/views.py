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

		#Verifica se ha idioma

		lingua = self.request.GET.get('l')

		if lingua == None or (lingua != 'pt' and lingua != 'eng'):
			lingua = 'pt'

		if(lingua == 'pt'):
			caminho_evolucao = './excel_evol.csv.gz'
			caminho_dicionario = 'dictMesh.dict.gz'
			definicao = 'Definicao'
			termos_semelhantes = 'Termos semelhantes'
		elif(lingua == 'eng'):
			caminho_evolucao = './excel_evol_eng.csv.gz'
			caminho_dicionario = 'dictMesh.dict_eng.gz'
			definicao = 'Definition'
			termos_semelhantes = 'Similar terms'


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

		evolucao = m['DADOS DA EVOLUÇÃO'].split(' ');

		#Abrindo o dicionario
		
		with gzip.open(caminho_dicionario,'rb') as fp:
			dictMesh = pickle.load(fp)
			fp.close()

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
						
						#Verifica o qualifier, se ha, entao salva, senao bota vazio

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

						#Sobrescreve a que tinha e bota com uma nova com o link etc.

						d['name'] = d['name'].replace('[', ' [')
						evolucao[cont] = start_underline+'<a style="color:inherit; text-decoration:none" href="#" data-id="<strong>ID: </strong>'+d['ID']+'<br/><br/>" data-name="<h3><a target= \'_blank\' href=\'https://meshb.nlm.nih.gov/record/ui?ui='+dui+'\'>'+d['name']+'<a></h3><br/>"  data-terms="<strong>'+termos_semelhantes+':</strong><br/>- '+termos+'" data-scope="<strong>'+definicao+':</strong> '+d['scope']+'">'+palavra+'</a>'+end_underline
						break

			cont +=1
					
		#Junta tudo novamente

		strr = ' '.join(evolucao)

		#Retorna pro template
		
		context['data'] = m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		context['indice_avancar'] = indice+1
		context['indice_retornar'] = indice-1
		context['ultima_posicao'] = len(prescription.loc[::])
		context['lingua'] = lingua
		return context