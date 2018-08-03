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


#from .forms import valida


class PacientePageView(TemplateView):
	template_name = 'index.html'

	def remove_accents(self, input_str):
		nfkd_form = unicodedata.normalize('NFKD', input_str)
		return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

	def get_context_data(self, **kwargs):
		context = super(PacientePageView, self).get_context_data(**kwargs)

		#Verifica se ha idioma

		formulario = "teste"

		lingua = self.request.GET.get('l')

		if lingua == None or (lingua != 'pt' and lingua != 'en'):
			lingua = 'pt'

		val = self.request.GET.get('val')

		if val == None or val == '0':
			val = '0'
		else:
			val = '1'

		if(lingua == 'pt'):
			caminho_evolucao = './data/excel_evol.csv.gz'
			caminho_dicionario = './data/dictMesh_.dict.gz'
			caminho_indice = './data/indiceReversoPT.dict.gz'
			caminho_valida = './data/dictValidaPT.dict.gz'
			definicao = 'Definicao'
			enviar = "Enviar"
			html_semelhantes_inicio = '<br/><br/><strong>Termos Semelhantes</strong><br/>- '
			html_mesh_inicio = '<br/><br/><strong>Termos Mesh</strong><br>- '
		elif(lingua == 'en'):
			caminho_evolucao = './data/excel_evol_eng.csv.gz'
			caminho_dicionario = './data/dictMesh.dict_eng_.gz'
			caminho_indice = './data/indiceReversoEN.dict.gz'
			caminho_valida = './data/dictValidaEN.dict.gz'
			definicao = 'Definition'
			enviar = "Send"
			html_semelhantes_inicio = '<br/><br/><strong>Similar Terms</strong><br/>- '
			html_mesh_inicio = '<br/><br/><strong>Mesh Terms</strong>'


		current_path = os.path.dirname(os.path.realpath(__file__))
		caminho_evolucao = os.path.join(current_path, caminho_evolucao)
		caminho_dicionario = os.path.join(current_path, caminho_dicionario)
		caminho_indice = os.path.join(current_path, caminho_indice)
		caminho_valida = os.path.join(current_path, caminho_valida)

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

		evolucao = m['DADOS DA EVOLUÇÃO'].split(' ')

		#Abrindo o dicionario

		with gzip.open(caminho_indice,'rb') as fd:
			indiceReverso = pickle.load(fd)
			fd.close()

		with gzip.open(caminho_dicionario,'rb') as fd:
			dictMesh = pickle.load(fd)
			fd.close()

		with gzip.open(caminho_valida,'rb') as fd:
			dictValida = pickle.load(fd)
			fd.close()

		#Lista com os termos ja verificados dos semelhantes
		verificados = []

		for IDD in dictValida:
			# cria a linha i
			linha = [] # lista vazia
			linha.append(IDD)
			linha.append(dictValida[IDD]['target'])

			# coloque linha na matriz
			verificados.append(linha)

		#Verifica a lista para ver se a palavra esta no dicionario
		valida = 0
		for i in range(len(evolucao)):

			palavra = evolucao[i].lower()
			palavra_i = palavra +' _i'

			if (i+2 < (len(evolucao))):
				palavra_tri = palavra.lower()+" "+evolucao[i+1].lower()+" "+evolucao[i+2].lower()
				palavra_tri_i = palavra.lower()+" "+evolucao[i+1].lower()+" "+evolucao[i+2].lower() + ' _i'

			if (i+1 < (len(evolucao))):
				palavra_bi = palavra.lower()+" "+evolucao[i+1].lower()
				palavra_bi_i = palavra.lower()+" "+evolucao[i+1].lower() + ' _i'

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
					new_t = indice_termos.replace(' _i', '')
					#new_t = indice_termos.replace('<i>', '')


					
				else:
					new_t = indice_termos
					new_t = indice_termos

				if(indiceReverso[indice_termos]):
					ID = indiceReverso[indice_termos]['ID']	
				elif(indiceReverso[indice_termos+" _i"]):
					ID = indiceReverso[indice_termos+" _i"]['ID']	
				verifica_mesh = 0
				verifica_similar = 0 

				html_similar = []
				html_mesh = []
				hidden = ""

				if(ID in dictMesh):
					term = dictMesh[ID]['terms']
					html_mesh = []
					html_similar = []

					for t in term:
						#if("hidden" in t):
							#continue

						if not("hidden" in t):
							if not("<i>" in t):
								html_mesh.append(t)
							else:
								html_similar.append(t)

						if("hidden" in t):
							hidden = t


				if(len(html_similar)!=0):
					html_termos = html_semelhantes_inicio
					html_termos += '<br/>- '.join(html_similar)+"</i>"
					html_termos +=  hidden
				else:
					html_termos = ""
				
				html_termos += html_mesh_inicio
				html_termos += '<br/>- '.join(html_mesh)
				
				termos = html_termos

				if "</i>" in termos and val == '0':
					termos = termos+"<br/><br/><button onclick='cbx3()'>Enviar</button>"

				#Verifica o qualifier, se ha, entao salva, senao bota vazio
				#Adiciona a o nome do qualifier com a cor dele

				if(dictMesh[ID]['qualifier'] == 'anatomy & histology'):
					start_underline = '<span class = "anatomy">'
					end_underline = '</span>'

					if(lingua == 'pt'):
						qualifier_texto = "<span class=\'anatomy_word\'>Anatomia</span>"
					elif(lingua == 'en'):
						qualifier_texto = "<span class=\'anatomy_word\'>Anatomy</span>"

				elif(dictMesh[ID]['qualifier'] == 'methods'):
					start_underline = '<span class = "procedure">'
					end_underline = "</span>"

					if(lingua == 'pt'):
						qualifier_texto = "<span class=\'procedure_word\'>Procedimento</span>"
					elif(lingua == 'en'):
						qualifier_texto = "<span class=\'procedure_word\'>Procedure</span>"

				elif(dictMesh[ID]['qualifier'] == 'diagnosis'):
					start_underline = '<span class = "diagnosis">'
					end_underline = '</span>'

					if(lingua == 'pt'):
						qualifier_texto = "<span class=\'diagnosis_word\'>Diagnóstico</span>"
					elif(lingua == 'en'):
						qualifier_texto = "<span class=\'diagnosis_word\'>Diagnosis</span>"

				elif(dictMesh[ID]['qualifier'] == 'pharmacology'):
					start_underline = '<span class = "medication">'
					end_underline = '</span>'

					if(lingua == 'pt'):
						qualifier_texto = "<span class=\'medication_word\'>Medicação</span>"
					elif(lingua == 'en'):
						qualifier_texto = "<span class=\'medication_word\'>Medication</span>"

				elif(dictMesh[ID]['qualifier'] == '#'):
					start_underline = '<span class = "other">'
					end_underline = '</span>'

					if(lingua == 'pt'):
						qualifier_texto = "<span class=\'other_word\'>Outro</span>"
					elif(lingua == 'en'):
						qualifier_texto = "<span class=\'other_word\'>Other</span>"

				else:
					start_underline = ''
					end_underline = ''

				#Sobrescreve a que tinha e bota com uma nova com o link etc.

				nome = dictMesh[ID]['name'].replace('[', ' [')
				evolucao[i] = start_underline+'<span class = "word" style="color:inherit; text-decoration:none" href="#" data-id="<strong>ID: </strong>'+ID+'<br/><br/>" data-qualifier="'+qualifier_texto+'<br/><br/>" data-name="<h3><a target= \'_blank\' href=\'https://meshb.nlm.nih.gov/record/ui?ui='+ID+'\'>'+dictMesh[ID]['name']+'<a></h3><br/>"  data-terms="'+termos+'" data-scope="<strong>'+definicao+':</strong> '+dictMesh[ID]['scope']+'" data-valida="'+val+'">'+new_t+'</span>'+end_underline
				
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
		context['lingua'] = lingua
		context['verificados'] = verificados
		context['val'] = val
		return context
