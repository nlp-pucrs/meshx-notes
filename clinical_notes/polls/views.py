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


class PacientePageView(TemplateView):
	template_name = 'index.html'

	def remove_accents(self, input_str):
		nfkd_form = unicodedata.normalize('NFKD', input_str)
		return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])



	def get_context_data(self, **kwargs):
		context = super(PacientePageView, self).get_context_data(**kwargs)

		#Verifica se ha idioma

		lingua = self.request.GET.get('l')

		if lingua == None or (lingua != 'pt' and lingua != 'en'):
			lingua = 'pt'

		if(lingua == 'pt'):
			caminho_evolucao = '../excel_evol.csv.gz'
			caminho_dicionario = '../dictMesh.dict.gz'
			caminho_indice = '../indiceReversoPT.dict.gz'
			definicao = 'Definicao'
			termos_semelhantes = 'Termos semelhantes'
		elif(lingua == 'en'):
			caminho_evolucao = '../excel_evol_eng.csv.gz'
			caminho_dicionario = '../dictMesh.dict_eng.gz'
			caminho_indice = '../indiceReversoEN.dict.gz'
			definicao = 'Definition'
			termos_semelhantes = 'Similar terms'


		current_path = os.path.dirname(os.path.realpath(__file__))
		caminho_evolucao = os.path.join(current_path, caminho_evolucao)
		caminho_dicionario = os.path.join(current_path, caminho_dicionario)
		caminho_indice = os.path.join(current_path, caminho_indice)

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

		with gzip.open(caminho_indice,'rb') as fd:
			indiceReverso = pickle.load(fd)
			fd.close()

		with gzip.open(caminho_dicionario,'rb') as fd:
			dictMesh = pickle.load(fd)
			fd.close()

		#Verifica a lista para ver se a palavra esta no dicionario
		valida = 0
		for i in range(len(evolucao)):

			palavra = evolucao[i].lower()
			palavra_i = '<i>' + palavra +'</i>'

			if (i+2 < (len(evolucao))):
				palavra_tri = palavra.lower()+" "+evolucao[i+1].lower()+" "+evolucao[i+2].lower()
				palavra_tri_i = '<i>' + palavra.lower()+" "+evolucao[i+1].lower()+" "+evolucao[i+2].lower() + '</i>'

			if (i+1 < (len(evolucao))):
				palavra_bi = palavra.lower()+" "+evolucao[i+1].lower()
				palavra_bi_i = '<i>' + palavra.lower()+" "+evolucao[i+1].lower() + '</i>'

			indice_termos = ''
			valida = 0

			### pesquisa trigramas
			if palavra_tri in indiceReverso:
				indice_termos = palavra_tri
				valida = 1	
				evolucao[i+1] = ''
				evolucao[i+2] = ''

			elif palavra_tri_i in indiceReverso:
				indice_termos = palavra_tri_i
				valida = 2
				evolucao[i+1] = ''
				evolucao[i+2] = ''
			### pesquisa bigrama
			elif palavra_bi in indiceReverso:
				indice_termos = palavra_bi
				valida = 1
				evolucao[i+1] = ''

			elif palavra_bi_i in indiceReverso:
				indice_termos = palavra_bi_i
				valida = 2
				evolucao[i+1] = ''
			### pesquisa unigrama
			elif palavra in indiceReverso:
				valida = 1
				indice_termos = palavra

			elif palavra_i in indiceReverso:
				indice_termos = palavra_i
				valida = 2

			if indice_termos != '':
				if(valida == 2):
					new_t = indice_termos.replace('</i>', '')
					new_t = indice_termos.replace('<i>', '')
					
				else:
					new_t = indice_termos
					new_t = indice_termos


				#if valida != 0:
				ID = indiceReverso[indice_termos]['ID']	
				teste = dictMesh[ID]['terms']
				termos = '<br/>- '.join(teste)
				
				#Verifica o qualifier, se ha, entao salva, senao bota vazio

				if(dictMesh[ID]['qualifier'] == 'anatomy & histology'):
					start_underline = '<span class = "anatomy">'
					end_underline = '</span>'
				elif(dictMesh[ID]['qualifier'] == 'methods'):
					start_underline = '<span class = "procedure">'
					end_underline = "</span>"
				elif(dictMesh[ID]['qualifier'] == 'diagnosis'):
					start_underline = '<span class = "diagnosis">'
					end_underline = '</span>'
				elif(dictMesh[ID]['qualifier'] == 'pharmacology'):
					start_underline = '<span class = "medication">'
					end_underline = '</span>'
				elif(dictMesh[ID]['qualifier'] == '#'):
					start_underline = '<span class = "other">'
					end_underline = '</span>'
				else:
					start_underline = ''
					end_underline = ''

				#Sobrescreve a que tinha e bota com uma nova com o link etc.

				nome = dictMesh[ID]['name'].replace('[', ' [')
				evolucao[i] = start_underline+'<a style="color:inherit; text-decoration:none" href="#" data-id="<strong>ID: </strong>'+ID+'<br/><br/>" data-name="<h3><a target= \'_blank\' href=\'https://meshb.nlm.nih.gov/record/ui?ui='+ID+'\'>'+dictMesh[ID]['name']+'<a></h3><br/>"  data-terms="<strong>'+termos_semelhantes+':</strong><br/>- '+termos+'" data-scope="<strong>'+definicao+':</strong> '+dictMesh[ID]['scope']+'">'+new_t+'</a>'+end_underline
				
		#Junta tudo novamente

		strr = ' '.join(evolucao)

		#Retorna pro template
		
		context['data'] = m['DATA EVOL']
		context['registro'] = m['REG. PACIENTE']
		context['evolucao'] = strr
		context['indice_avancar'] = indice+1
		context['indice'] = indice
		context['indice_retornar'] = indice-1
		context['ultima_posicao'] = len(prescription.loc[::])
		context['lingua'] = lingua
		return context