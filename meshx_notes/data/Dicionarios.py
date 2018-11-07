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

	def __init__(self, xmlMesh, wordEmbedding, maisSimilar, similaridadeDefinicao, idioma="por", porcent_methods=9, porcent_diagnosis=9, porcent_anatomy= 9, porcent_other=9, porcent_pharmacology=9.3, _topn=10, printTime=True):
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

			ID =  	d.find('.DescriptorUI').text
		    
			start = time.time()

			qualifier = self.verificaQualifier(d)

			end = time.time()
			time_qualifer.append(end - start)
		    
			heading = d.find('.DescriptorName/String').text.lower()+" _i"

		    #Adicionando o heading inteiro no Mesh

			start = time.time()

			end = time.time()

			time_add_IndiceReverso.append(end - start)

			start = time.time()

			#definicao no idioma selecionado

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

		for i in range(20):
			#Adicionando as porcentagens que variam de 0.01 em 0.01

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

			padrao_ouro = pd.read_csv(caminho_padrao_ouro, nrows=50000)

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

			acuracia_diagnosis = certo[DIAGNOSIS]/total[DIAGNOSIS]
			acuracia_methods = certo[METHODS]/total[METHODS]
			acuracia_anatomy = certo[ANATOMY]/total[ANATOMY]
			acuracia_other = certo[OTHER]/total[OTHER]
			acuracia_pharmacology = certo[PHARMACOLOGY]/total[PHARMACOLOGY]

			lista_porcentagens[PORCENTAGEM]={
				'acuracia diagnosis': acuracia_diagnosis,
				'acuracia methods': acuracia_methods,
				'acuracia anatomy': acuracia_anatomy,
				'acuracia other': acuracia_other,
				'acuracia pharmacology': acuracia_pharmacology,
				'Total diagnosis': total[DIAGNOSIS],
				'Total methods': total[METHODS],
				'Total anatomy': total[ANATOMY],
				'Total other': total[OTHER],
				'Certo pharmacology': total[PHARMACOLOGY],
				'Certo diagnosis': certo[DIAGNOSIS],
				'Certo methods': certo[METHODS],
				'Certo anatomy': certo[ANATOMY],
				'Certo other': certo[OTHER],
				'Certo pharmacology': certo[PHARMACOLOGY]
			}
		return(lista_porcentagens)

	def retira_especiaisHeading(self, termo):
		INICIO = 0
		FIM = termo.find('[')

		return(termo[INICIO:FIM])

	#No lugar da definição do MeSH será adicionada a que está no XML do termo no idioma desejado
	def muda_definicao(self, idioma, heading, ID):
		if(idioma == "por" and self.similaridadeDefinicao):
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
					anotacao = d.find('.record/indexing_annotation').text
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

	def add_IndiceReverso(self, ID, termo, similaridade, termo_adicionado):
		compara_mais_similar = self.comparaSimilaridade(similaridade, termo, termo_adicionado) or self.maisSimilar == False
		compara_definicao = self.similaridadeMedia_definicao(termo, similaridade) or self.similaridadeDefinicao == False

		if(compara_mais_similar or compara_definicao):
			self.indiceReverso[termo] = {
				'ID': ID,
				'similaridade': similaridade
			} 

	def similaridadeMedia_definicao(self, termo, similaridade_termo):
		if(self.similaridadeDefinicao and termo in self.indiceReverso):
			definicao_nova = self.remover_pontuacao(self.remover_acentos(self.scope)).split(' ')
			similaridade_nova =  self.media_definicoes(definicao_nova, termo)

			if(termo+' _i' in self.indiceReverso):
				ID = self.indiceReverso[termo+' _i']
			elif(termo in self.indiceReverso):
				ID = self.indiceReverso[termo]
			else:
				return False

			definicao_atual = self.remover_pontuacao(self.remover_acentos(self.scope)).split(' ')
			similaridade_atual =  self.media_definicoes(definicao_atual, termo)

			if(similaridade_nova > similaridade_atual):
				return True
		elif not(termo in self.indiceReverso):
			return True

		return False
		

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
					if(similar == termo_definicao and porcentagem > porcentagem_termo):
						porcentagem_termo = porcentagem
			return porcentagem_termo



	#Compara a similaidade de dois headings do dicionário (o atual e o que já estava, caso o mesmo termo já tenha sido processado)
	#E retorna True se o atual for mais similar com o termo informado, False caso o que já estava for mais similar
	def comparaSimilaridade(self, similaridade, termo, termo_adicionado):
		termo = termo+" _i"

		if (self.maisSimilar) and (termo in self.indiceReverso) and (self.indiceReverso[termo]['similaridade'] < similaridade) and (self.indiceReverso[termo]['ID'] in self.dictMesh) and (termo_adicionado in self.dictMesh[self.indiceReverso[termo]['ID']]['terms']) or not(termo in self.indiceReverso):
			if termo in self.indiceReverso:
				id_ = self.indiceReverso[termo]['ID']
				self.dictMesh[id_]['terms'].remove(termo_adicionado)
				print("Estou aqui!")
			return True
		else:
			return False

	def add_Mesh(self, heading, ID, qualifier):
		self.dictMesh[ID] = {
			'ID': ID,
			'name': heading,
			'scope': self.scope,
			'terms': sorted(set(self.terms), reverse=True),
			'qualifier': qualifier
		}

	#Seleciona os termos do MeSH e salva os mesmos no dicionário, aqui também ocorre a chamada das funçõs de similaridade
	def seleciona_TermosMesh(self, qualifier, ID, heading, descriptor):
		for c in descriptor.findall('.ConceptList/'):

			if not(self.muda_definicao(self.idioma, heading, ID)):
				if c.find('./ScopeNote') != None:
					self.scope = c.find('./ScopeNote').text.replace('\n','').strip()
			for t in c.findall('./TermList/'):
				if not(self.idioma in t.find('./TermUI').text) and self.idioma != "en":
					continue

				termo_adicionado = t.find('./String').text
				self.terms.append(termo_adicionado.lower())

				self.add_IndiceReverso(self.remover_acentos(descriptor.find('.DescriptorUI').text), (t.find('./String').text.lower()), self.MAIS_SIMILAR, termo_adicionado)

				##add função AQUI

	
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