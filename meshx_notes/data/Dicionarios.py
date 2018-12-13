import time

import numpy as np

from gensim.models import KeyedVectors
import unicodedata

from unicodedata import normalize

import gzip, pickle
import xml.etree.ElementTree as ET

import pandas as pd
import os

import re

from Similaridade import Similaridade

class Dicionarios():
	"""docstring for ClassName"""
	cont = 0
	dictMesh = {}	
	indiceReverso = {}
	wordModel = ""
	scope = ""
	terms = []
	porcent_methods = 0
	porcent_diagnosis = 0
	porcent_anatomy = 0
	porcent_other = 0
	porcent_pharmacology = 0
	_topn = 0
	idioma=""
	maisSimilar = True
	MAIS_SIMILAR = 1
	similaridadeDefinicao = False

	def __init__(self, xmlMesh, wordEmbedding, idioma="por", porcent_methods=0.9, porcent_diagnosis=0.9,  porcent_pharmacology=0.93, porcent_anatomy= 0.9, porcent_other=0.9, _topn=10, printTime=True, maisSimilar=False, similaridadeDefinicao=False):
		self.xmlMesh = xmlMesh
		self.wordEmbedding = wordEmbedding
		self.printTime = printTime
		self.wordModel = KeyedVectors.load_word2vec_format(self.wordEmbedding, binary=True)
		self.porcent_methods = porcent_methods
		self.porcent_diagnosis = porcent_diagnosis
		self.porcent_anatomy = porcent_anatomy
		self.porcent_other = porcent_other
		self.porcent_pharmacology = porcent_pharmacology
		self._topn = _topn
		self.idioma = idioma
		self.maisSimilar = maisSimilar
		self.similaridadeDefinicao = similaridadeDefinicao

		with gzip.open(self.xmlMesh) as pordesc2018:
			self.tree = ET.parse(pordesc2018)


	def run(self):

		time_qualifer = []
		time_add_IndiceReverso = []
		time_seleciona_TermosMesh = []
		time_add_Mesh = []
		time_adiciona_termosPadrao_IndiceReverso = []

		cont = 0

		for i, d in enumerate(self.tree.findall("./DescriptorRecord")):
			#if i > 100:
			#	break

			self.terms = []

			ID = d.find('.DescriptorUI').text
		    
			start = time.time()

			qualifier = self.verificaQualifier(d)

			end = time.time()
			time_qualifer.append(end - start)
		    
			heading = d.find('.DescriptorName/String').text.lower()+" _i"

		    #Adicionando o heading inteiro no Mesh
			'''
			start = time.time()

			end = time.time()

			time_add_IndiceReverso.append(end - start)
			'''

			#definicao no idioma selecionado

			start = time.time()

			self.seleciona_TermosMesh(qualifier, ID, heading, d)

			end = time.time()

			time_seleciona_TermosMesh.append(end - start)

			#print('seleciona_heading_primeiraParte')
			self.seleciona_heading_primeiraParte(d)

			self.adiciona_termos_WE(qualifier, d)

			start = time.time()

			#print("add_Mesh")
			self.add_Mesh(d.find('.DescriptorName/String').text.lower(), ID, qualifier)


			end = time.time()
			time_add_Mesh.append(end - start)

			#print("fim")

		if(self.printTime):
			return round(np.mean(time_qualifer), 5), round(np.mean(time_add_IndiceReverso), 5), round(np.mean(time_seleciona_TermosMesh), 5), round(np.mean(time_add_Mesh), 5)

	def testaThresh(self):

		current_path = os.path.dirname(os.path.realpath(__file__))
		#caminho_padrao_ouro = './data/padrao_ouro.csv'
		caminho_padrao_ouro = './padrao_ouro.csv'
		caminho_padrao_ouro = os.path.join(current_path, caminho_padrao_ouro)

		lista_porcentagens = {}

		padrao_ouro = pd.read_csv(caminho_padrao_ouro, nrows=50000)

		for i in range(20):
			#Adicionando as porcentagens que variam de 0.01 em 0.01

			self.indiceReverso = {}
			self.dictMesh = {}

			DIAGNOSIS = 0
			METHODS = 1
			ANATOMY = 2
			OTHER = 3
			PHARMACOLOGY = 4

			PORCENTAGEM = 0.80+(i*0.01)

			self.porcent_methods = PORCENTAGEM
			self.porcent_diagnosis = PORCENTAGEM
			self.porcent_anatomy = PORCENTAGEM
			self.porcent_other = PORCENTAGEM
			self.porcent_pharmacology = PORCENTAGEM

			certo = [0]*5
			total =[0]*5

			self.run()

			pharmacology_total, anatomy_total, methods_total, diagnosis_total, other_total, total_termos_padraoOuro = self.conta_padrao_ouro_qualifiers()

			#CONFERIR

			for indice in self.indiceReverso:
				try :
					indice_teste = indice
					if(' _i' in indice):
						indice_teste = indice.replace(' _i', '')

					ids_termos = padrao_ouro[padrao_ouro['Termos'] == indice_teste].index
					termo = padrao_ouro.loc[ids_termos[0]]

					if(self.dictMesh[self.indiceReverso[indice]['ID']]['qualifier'] == 'pharmacology'):
						atual = PHARMACOLOGY
					elif(self.dictMesh[self.indiceReverso[indice]['ID']]['qualifier'] == 'anatomy & histology'):
						atual = ANATOMY
					elif(self.dictMesh[self.indiceReverso[indice]['ID']]['qualifier'] == 'methods'):
						atual = METHODS
					elif(self.dictMesh[self.indiceReverso[indice]['ID']]['qualifier'] == 'diagnosis'):
						atual = DIAGNOSIS
					elif(self.dictMesh[self.indiceReverso[indice]['ID']]['qualifier'] == '#'):
						atual = OTHER

					if(self.indiceReverso[indice]['ID'] == str(termo['ID']) or self.indiceReverso[indice]['ID'] == str(termo['ID_2']) or self.indiceReverso[indice]['ID'] == str(termo['ID_3']) or self.indiceReverso[indice]['ID'] == str(termo['ID_4']) or  self.indiceReverso[indice]['ID'] == str(termo['ID_5'])):
						certo[atual] +=1

					total[atual] +=1
				except IndexError:
					continue
			for i in range(5):
				if(total[i] == 0):
					total[i] = 1

			presicion_diagnosis = certo[DIAGNOSIS]/total[DIAGNOSIS]
			presicion_methods = certo[METHODS]/total[METHODS]
			presicion_anatomy = certo[ANATOMY]/total[ANATOMY]
			presicion_other = certo[OTHER]/total[OTHER]
			presicion_pharmacology = certo[PHARMACOLOGY]/total[PHARMACOLOGY]

			recall_diagnosis = certo[DIAGNOSIS]/diagnosis_total
			recall_methods = certo[METHODS]/methods_total
			recall_anatomy = certo[ANATOMY]/anatomy_total
			recall_other = certo[OTHER]/other_total
			recall_pharmacology = certo[PHARMACOLOGY]/pharmacology_total

			total_certo = certo[DIAGNOSIS] + certo[METHODS] + certo[ANATOMY] + certo[OTHER] + certo[PHARMACOLOGY]

			acuracia = total_certo/total_termos_padraoOuro

			f1measure_diagnosis = 2*((presicion_diagnosis*recall_diagnosis)/(presicion_diagnosis+recall_diagnosis))
			f1measure_methods = 2*((presicion_methods*recall_methods)/(presicion_methods+recall_methods))
			f1measure_anatomy = 2*((presicion_anatomy*recall_anatomy)/(presicion_anatomy+recall_anatomy))
			f1measure_other = 2*((presicion_other*recall_other)/(presicion_other+recall_other))
			f1measure_pharmacology = 2*((presicion_pharmacology*recall_pharmacology)/(presicion_pharmacology+recall_pharmacology))


			lista_porcentagens[PORCENTAGEM]={
				'0 Acurácia': acuracia,

				'1.0 Precision diagnosis': presicion_diagnosis,
				'1.1 Reccal diagnosis': recall_diagnosis,
				'1.2 F1 score diagnosis': f1measure_diagnosis,
				'1.3 Total diagnosis': total[DIAGNOSIS],
				'1.4 Certo diagnosis': certo[DIAGNOSIS],

				'2.0 Precision methods': presicion_methods,
				'2.1 Recall methods': recall_methods,
				'2.2 F1 score methods': f1measure_methods,
				'2.3 Total methods': total[METHODS],
				'2.4 Certo methods': certo[METHODS],

				'3.0 Precision anatomy': presicion_anatomy,
				'3.1 Recall anatomy': recall_anatomy,
				'3.2 F1 score anatomy': f1measure_anatomy,
				'3.3 Total anatomy': total[ANATOMY],
				'3.4 Certo anatomy': certo[ANATOMY],

				'4.0 Precision other': presicion_other,
				'4.1 Recall other': recall_other,
				'4.2 F1 score other': f1measure_other,
				'4.3 Total other': total[OTHER],
				'4.4 Certo other': certo[OTHER],

				'5.0 Precision pharmacology': presicion_pharmacology,
				'5.1 Recall pharmacology': recall_pharmacology,
				'5.2 F1 score pharmacology': f1measure_pharmacology,
				'5.3 Total pharmacology': total[PHARMACOLOGY],
				'5.4 Certo pharmacology': certo[PHARMACOLOGY]
			}

		return(lista_porcentagens)

	def conta_padrao_ouro_qualifiers(self):

		pharmacology = 0
		anatomy = 0
		diagnosis = 0
		methods = 0
		other = 0
		total = 0
		i=0
		continua = True

		#Caminho
		caminho_padrao_ouro = './padrao_ouro.csv'

		#Pegando os dados
		padrao_ouro = pd.read_csv(caminho_padrao_ouro, nrows=50000)

		while(continua):
    
			try:
				termo = str(padrao_ouro["Termos"][i]).split('\n')
				termo = ''.join(termo)

				cont = 0

				for teste in padrao_ouro:
					if(cont==0):
						cont +=1
						continue

					linha = str(padrao_ouro[teste][i]).split('\n')

					ID = linha[0]

					if(ID != 'nan' and ID != "ambiguo"):
						if(self.dictMesh[ID]['qualifier'] == 'pharmacology'):
							pharmacology += 1
						elif(self.dictMesh[ID]['qualifier'] == 'anatomy & histology'):
							anatomy += 1
						elif(self.dictMesh[ID]['qualifier'] == 'methods'):
							methods += 1
						elif(self.dictMesh[ID]['qualifier'] == 'diagnosis'):
							diagnosis += 1
						elif(self.dictMesh[ID]['qualifier'] == '#'):
							other += 1

						total += 1

						break
						
				i +=1
			except KeyError:
				continua = False
			    


			'''indice_teste = indice
			if(' _i' in indice):
				indice_teste = indice.replace(' _i', '')

			ids_termos = padrao_ouro[padrao_ouro['Termos'] == indice_teste].index
			termo = padrao_ouro.loc[ids_termos[0]]

			total += 1

			if(str(termo['ID']) != "NULL"):
				ID = str(termo['ID'])
			elif(str(termo['ID_2']) != "NULL"):
				ID = str(termo['ID_2'])
			elif(str(termo['ID_3']) != "NULL"):
				ID = str(termo['ID_3'])
			elif(str(termo['ID_4']) != "NULL"):
				ID = str(termo['ID_4'])
			elif(str(termo['ID_5']) != "NULL"):
				ID = str(termo['ID_5'])
			else:
				continue

			if(self.dictMesh[ID]['qualifier'] == 'pharmacology'):
				pharmacology += 1
			elif(self.dictMesh[ID]['qualifier'] == 'anatomy & histology'):
				anatomy += 1
			elif(self.dictMesh[ID]['qualifier'] == 'methods'):
				methods += 1
			elif(self.dictMesh[ID]['qualifier'] == 'diagnosis'):
				diagnosis += 1
			elif(self.dictMesh[ID]['qualifier'] == '#'):
				other += 1'''

		if(pharmacology == 0):
			pharmacology = 1
		if(anatomy == 0):
			anatomy = 1
		if(methods == 0):
			methods = 1
		if(diagnosis == 0):
			diagnosis = 1
		if(other == 0):
			other = 1

		if(total == 0):
			total = 1


		return pharmacology, anatomy, methods, diagnosis, other, total


	def retira_especiaisHeading(self, termo):
		INICIO = 0
		FIM = termo.find('[')

		return(termo[INICIO:FIM])

	#No lugar da definição do MeSH será adicionada a que está no XML do termo no idioma desejado
	def muda_definicao(self, idioma, heading, ID):
		#if(idioma == "por" and self.similaridadeDefinicao):
		if(idioma == "por"):
				termo_xml = self.retira_especiaisHeading(heading.lower())
				xmlMesh = './DECS_XML/'+termo_xml+'.xml'
				#print(xmlMesh)

				definicao = self.pega_definicao_xml(xmlMesh, ID)
				#print("Definicao", definicao)
				#print("_______________")

				if(definicao):
					self.scope = definicao
					return(True)
				else:
					return(False)
		else:
			return(False)

	#Retorna a definição do ID informado, a qual está no XML
	def pega_definicao_xml(self, xmlMesh, id_mesh):
		try:
			with open(xmlMesh, 'rb') as pordesc2018:
				tree = ET.parse(pordesc2018)

			for i, d in enumerate(tree.findall("./decsws_response/record_list")):
				id_xml = d.find('.record/unique_identifier_nlm').text

				#Pega as informações do xml do ID desejado
				if(id_xml == id_mesh):
					#anotacao = d.find('.record/indexing_annotation').text
					definicao = d.find('.record/definition/occ').attrib.get('n')

					return(definicao)

		except:
			return("")

	#Retorna o qualifier do termo desejado
	def verificaQualifier(self, d):
		qualifier = '#'
	
		for aql in d.findall('.AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName'):
			teste_qualifier = aql.find('./String').text
			if(teste_qualifier == 'anatomy & histology' or teste_qualifier == 'pharmacology' or teste_qualifier == 'methods' or teste_qualifier == 'diagnosis'):
				qualifier = teste_qualifier
				break

		return qualifier

	def add_IndiceReverso(self, ID, termo, similaridade, termo_no_dicionario):
		#if(self.termo_original_ja_adicionado(termo)):
			#return False

		compara_mais_similar = self.comparaSimilaridade(similaridade, termo, termo_no_dicionario, False)
		compara_definicao, similaridade = self.similaridadeMedia_definicao(termo, similaridade, termo_no_dicionario)
		ultimo_encontrado =  self.maisSimilar == False and self.similaridadeDefinicao == False

		if(compara_mais_similar or compara_definicao or ultimo_encontrado):
			self.indiceReverso[termo] = {
				'ID': ID,
				'similaridade': similaridade
			} 
			return True
		return False

	def termo_original_ja_adicionado(self, termo):

		if(termo in self.indiceReverso):
			if(self.indiceReverso[termo]['similaridade'] == 1):
				return True
		return False

	def similaridadeMedia_definicao(self, termo, similaridade_termo, termo_no_dicionario):
		if(self.similaridadeDefinicao):

			if(similaridade_termo == 1):
				return True, similaridade_termo	

			definicao_nova = self.remover_pontuacao(self.remover_acentos(self.scope)).split(' ')
			similaridade_nova =  self.media_definicoes(definicao_nova, termo)

			if not(termo in self.indiceReverso):
				return True, similaridade_nova

			if(termo in self.indiceReverso):

				if(self.comparaSimilaridade(similaridade_nova, termo, termo_no_dicionario, True)):
					return True, similaridade_nova			

		return False, similaridade_termo
		

	def media_definicoes(self, definicao, termo):
		similaridade_definicao = 0
		for palavra_definicao in definicao:
			similaridade_definicao += self.comparaDoisTermos(palavra_definicao, termo)

		media = similaridade_definicao/len(definicao)

		return media


	def comparaDoisTermos(self, termo_definicao, termo_MeSH):
		if(termo_definicao == termo_MeSH):
			return 1
		else:
			porcentagem_termo = 0
			if(termo_MeSH in self.wordModel):
				palavra_similar = self.wordModel.most_similar_cosmul(termo_MeSH,topn=20)

				for similar, porcentagem in palavra_similar:
					if(similar == termo_definicao and porcentagem_termo < porcentagem):
						porcentagem_termo = porcentagem
			return porcentagem_termo



	#Compara a similaidade de dois headings do dicionário (o atual e o que já estava, caso o mesmo termo já tenha sido processado)
	#E retorna True se o atual for mais similar com o termo informado, False caso o que já estava for mais similar
	def comparaSimilaridade(self, similaridade, termo, termo_no_dicionario, aplicacao_auxiliar):
		if(self.maisSimilar or aplicacao_auxiliar):
			if(similaridade == 1):
				return True

			if not(termo in self.indiceReverso):
				return True

			if(self.indiceReverso[termo]['similaridade'] < similaridade):
				id_antigo = self.indiceReverso[termo]['ID']

				if(id_antigo in self.dictMesh and termo in self.dictMesh[id_antigo]['terms']):
					self.dictMesh[id_antigo]['terms'].remove(termo_no_dicionario)

				return True
		
		return False

	def add_Mesh(self, heading, ID, qualifier):
		self.dictMesh[ID] = {
			'ID': ID,
			'name': heading,
			'scope': self.scope.lower(),
			'terms': sorted(set(self.terms), reverse=True),
			'qualifier': qualifier
		}

	#Seleciona os termos do MeSH e salva os mesmos no dicionário, aqui também ocorre a chamada das funções de similaridade
	def seleciona_TermosMesh(self, qualifier, ID, heading, descriptor):
		for c in descriptor.findall('.ConceptList/'):

			if not(self.muda_definicao(self.idioma, heading, ID)):
				if c.find('./ScopeNote') != None:
					self.scope = c.find('./ScopeNote').text.replace('\n','').strip()
			for t in c.findall('./TermList/'):
				if not(self.idioma in t.find('./TermUI').text) and self.idioma != "en":
					continue

				termo_adicionado = t.find('./String').text

				adicionou = self.add_IndiceReverso(self.remover_acentos(descriptor.find('.DescriptorUI').text), (t.find('./String').text.lower()), self.MAIS_SIMILAR, termo_adicionado)

				if(adicionou):
					self.terms.append(termo_adicionado.lower())
	
	def adiciona_termos_WE(self, qualifier, descriptor):
		palavra_similar = []

		for termo in self.terms:
			if termo.lower() in self.wordModel.vocab:
				sem_assento = self.remover_acentos(termo.lower())
				#self.terms.append(sem_assento)

				palavra_similar = self.wordModel.most_similar_cosmul(sem_assento.lower(),topn= self._topn)
				for palavra_similar, porcentagem in palavra_similar:

					sem_assento = self.remover_acentos(palavra_similar)

					if not(sem_assento in self.indiceReverso and self.indiceReverso[sem_assento]['similaridade'] == self.MAIS_SIMILAR) and not(sem_assento+'_i' in self.indiceReverso and self.indiceReverso[sem_assento+'_i']['similaridade'] == self.MAIS_SIMILAR):

						teste_anatomy = porcentagem > self.porcent_anatomy and qualifier == 'anatomy & histology'
						teste_pharmacology = porcentagem > self.porcent_pharmacology and qualifier == 'pharmacology'
						teste_methods  = porcentagem > self.porcent_methods and qualifier == 'methods'
						teste_diagnosis = porcentagem > self.porcent_diagnosis and qualifier == 'diagnosis'
						teste_other = porcentagem > self.porcent_other


						if(teste_anatomy or teste_pharmacology or teste_methods or teste_diagnosis or teste_other):
							termo_adicionado = "<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>"
							self.terms.append(termo_adicionado.lower())
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, sem_assento+" _i", porcentagem, termo_adicionado)


	#Pega o heading sem parenteses e conchetes, só o termo na lingua desejada, uma vez que entre parenteses/conchetes está o mesmo em inglês
	def seleciona_heading_primeiraParte(self, d):
		heading = d.find('.DescriptorName/String').text.lower()

		novo = heading.replace(' ', '_')
		novo = novo.replace('[', ' ')
		novo = novo.replace('(', ' ')
		novo = novo.split(' ')
		indice = novo[0]
		indice = indice.replace('_', ' ')
		indice = self.remover_acentos(indice)

		if(indice != ' ' and indice != '' and indice[-1] == " "):
			indice = indice[:-1]

		indice = self.remover_acentos(indice)
		termo_adicionado = self.remover_acentos(indice.lower())

		self.add_IndiceReverso(d.find('.DescriptorUI').text, self.remover_acentos(indice.lower()+" _i"), self.MAIS_SIMILAR, termo_adicionado)
		#self.terms.append("<i>"+indice+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+indice+"' value='1'/> Certo <input class='radio' type='radio' name='"+indice+"'' value='0'/> Errado</span>")

		#terms.append(indice)

		self.terms.append(" <input type='hidden' name='ID' value='"+d.find('.DescriptorUI').text+"'/> ".lower())   

	def salvaIndiceReverso(self, nome):
		with gzip.open(nome,'wb') as fp:
			pickle.dump(self.indiceReverso,fp)
			fp.close()

	def salvaDictMesh(self, nome):
		with gzip.open(nome,'wb') as fp:
			pickle.dump(self.dictMesh,fp)
			fp.close()

	def carrega_Dicionario(self, nome):
		try:
			with gzip.open(nome, 'rb') as fp:
				self.dictMesh = pickle.load(fp)
				fp.close()

			return True
		except:
			return False


	def carrega_IndiceReverso(self, nome):
		try:
			with gzip.open(nome, 'rb') as fp:
				self.indiceReverso = pickle.load(fp)
				fp.close()
			return True
		except:
			return False

	def remover_acentos(self, txt):
		return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

	def remover_pontuacao(self, txt):
		return re.sub('[^\w\s]','', txt)