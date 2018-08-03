import time

import numpy as np

from gensim.models import KeyedVectors
import unicodedata

from unicodedata import normalize

import gzip
import xml.etree.ElementTree as ET

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
        
	def __init__(self, xmlMesh, wordEmbedding, idioma="por", porcent_methods=9, porcent_diagnosis=9, porcent_anatomy= 9, porcent_other=9, porcent_pharmacology=9.3, _topn=10, printTime=True):
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

			start = time.time()

			#self.add_IndiceReverso(self.remover_acentos(d.find('.DescriptorUI').text), heading)
			#self.terms.append(self.remover_acentos(d.find('.DescriptorUI').text))

			end = time.time()

			time_add_IndiceReverso.append(end - start)

			start = time.time()

			self.seleciona_TermosMesh(qualifier, ID, heading, d)

			end = time.time()

			time_seleciona_TermosMesh.append(end - start)

			self.seleciona_heading_primeiraParte(d)

			start = time.time()

			self.add_Mesh(d.find('.DescriptorName/String').text.lower(), ID, qualifier )

			end = time.time()
			time_add_Mesh.append(end - start)

		if(self.printTime):
			return round(np.mean(time_qualifer), 5), round(np.mean(time_add_IndiceReverso), 5), round(np.mean(time_seleciona_TermosMesh), 5), round(np.mean(time_add_Mesh), 5)

	def verificaQualifier(self, d):
		qualifier = '#'
	
		for aql in d.findall('.AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName'):
			teste_qualifier = aql.find('./String').text
			if(teste_qualifier == 'anatomy & histology' or teste_qualifier == 'pharmacology' or teste_qualifier == 'methods' or teste_qualifier == 'diagnosis'):
				qualifier = teste_qualifier
				break

		return qualifier

	def add_IndiceReverso(self, ID, termo):
		self.indiceReverso[termo] = {
			'ID': ID
		} 

	def add_Mesh(self, heading, ID, qualifier):
		self.dictMesh[ID] = {
			'ID': ID,
			'name': heading,
			'scope': self.scope,
			'terms': sorted(set(self.terms), reverse=True),
			'qualifier': qualifier
		}

	def seleciona_TermosMesh(self, qualifier, ID, heading, descriptor):        
		for c in descriptor.findall('.ConceptList/'):

			if c.find('./ScopeNote') != None:
				self.scope = c.find('./ScopeNote').text.replace('\n','').strip()
			for t in c.findall('./TermList/'):
				if not(self.idioma in t.find('./TermUI').text) and self.idioma != "en":
					continue
				self.terms.append(t.find('./String').text)

				self.add_IndiceReverso(self.remover_acentos(descriptor.find('.DescriptorUI').text), (t.find('./String').text.lower()))
				
				palavra_similar = []


				if t.find('./String').text.lower() in self.wordModel.vocab:
					sem_assento = self.remover_acentos(t.find('./String').text.lower())
					#self.terms.append(sem_assento)


					palavra_similar = self.wordModel.most_similar_cosmul(sem_assento.lower(),topn= self._topn)
					for palavra_similar, porcentagem in palavra_similar:

						sem_assento = self.remover_acentos(palavra_similar)

						if(porcentagem > self.porcent_anatomy and qualifier == 'anatomy & histology'):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, sem_assento+" _i")

						elif(porcentagem > self.porcent_pharmacology and qualifier == 'pharmacology'):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, sem_assento+" _i")

						elif(porcentagem > self.porcent_methods and qualifier == 'methods'):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, sem_assento+" _i")

						elif(porcentagem > self.porcent_diagnosis and qualifier == 'diagnosis'):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, sem_assento+" _i")

						elif(porcentagem > self.porcent_other):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, sem_assento+" _i")

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
		self.add_IndiceReverso(d.find('.DescriptorUI').text, self.remover_acentos(indice.lower()+" _i"))
		#self.terms.append("<i>"+indice+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+indice+"' value='1'/> Certo <input class='radio' type='radio' name='"+indice+"'' value='0'/> Errado</span>")

		#terms.append(indice)

		self.terms.append(" <input type='hidden' name='ID' value='"+d.find('.DescriptorUI').text+"'/> ")   

	def salvaIndiceReverso(self, nome):
		import gzip, pickle

		with gzip.open(nome,'wb') as fp:
			pickle.dump(self.indiceReverso,fp)
			fp.close()

	def salvaDictMesh(self, nome):
		import gzip, pickle

		with gzip.open(nome,'wb') as fp:
			pickle.dump(self.dictMesh,fp)
			fp.close()

	def carrega_Dicionario(self, nome):
		import gzip, pickle

		with gzip.open(nome, 'rb') as fp:
			self.dictMesh = pickle.load(fp)
			fp.close()

	def carrega_IndiceReverso(self, nome):
		import gzip, pickle

		with gzip.open(nome, 'rb') as fp:
			self.indiceReverso = pickle.load(fp)
			fp.close()

	def remover_acentos(self, txt):
		return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')