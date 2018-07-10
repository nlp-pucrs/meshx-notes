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
    
        
	def __init__(self, xmlMesh, wordEmbedding, printTime=True):
		self.xmlMesh = xmlMesh
		self.wordEmbedding = wordEmbedding
		self.printTime = printTime
		self.wordModel = KeyedVectors.load_word2vec_format(self.wordEmbedding, binary=True)

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

			self.add_IndiceReverso(d.find('.DescriptorUI').text, heading)

			end = time.time()

			time_add_IndiceReverso.append(end - start)

			start = time.time()

			self.seleciona_TermosMesh(qualifier, ID, heading, d)

			end = time.time()

			time_seleciona_TermosMesh.append(end - start)

			self.seleciona_heading_primeiraParte(d)

			start = time.time()



			self.add_Mesh(heading, ID, qualifier )

			end = time.time()
			time_add_Mesh.append(end - start)
		

		#self.salva_Dicionario('dictMesh', 'dictMesh')
		#self.salva_Dicionario('indiceReverso', 'indiceReverso')

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
				if not("por" in t.find('./TermUI').text):
					continue
				self.terms.append(t.find('./String').text)

				self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, (t.find('./String').text.lower()))
				
				palavra_similar = []

				if t.find('./String').text.lower() in self.wordModel.vocab:
					sem_assento = self.remover_acentos(t.find('./String').text)
					palavra_similar = self.wordModel.most_similar_cosmul(sem_assento.lower(),topn=10)
					for palavra_similar, porcentagem in palavra_similar:
						if(porcentagem > 0.9 and qualifier != 'pharmacology'):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, palavra_similar.lower()+" _i")
					        
						elif(porcentagem > 0.93 and qualifier == 'pharmacology'):
							self.terms.append("<i>"+palavra_similar+"</i>" + " <span class = 'valida'><input class='radio' type='radio' name='"+palavra_similar+"' value='1'/> Certo <input class='radio' type='radio' name='"+palavra_similar+"'' value='0'/> Errado</span>")
							self.add_IndiceReverso(descriptor.find('.DescriptorUI').text, palavra_similar.lower()+" _i")

	def seleciona_heading_primeiraParte(self, d):
		heading = d.find('.DescriptorName/String').text.lower()

		novo = heading.replace(' ', '_')
		novo = novo.replace('[', ' ')
		novo = novo.replace('(', ' ')
		novo = novo.split(' ')
		indice = novo[0]
		indice = indice.replace('_', ' ')

		if(indice != '' and indice[-1] == ' '):
			indice = indice[0:-1]

		indice = self.remover_acentos(indice)

		self.add_IndiceReverso(d.find('.DescriptorUI').text, indice.lower()+" _i")

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

		with gzip.open(nome+'.dict.gz','rb') as fp:
			if(nome == "dictMesh"):
				self.dictMesh = pickle.load(fp)
			else:
				self.indiceReverso = pickle.load(fp)
			fp.close()

	def remover_acentos(self, txt):
		return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')