import time

import numpy as np

from gensim.models import KeyedVectors
import unicodedata

from unicodedata import normalize

import gzip
import xml.etree.ElementTree as ET

from Similaridade import Similaridade

import pylab

class dicionarios_graficos():
	"""docstring for ClassName"""
	indiceReverso = {}
	dictMesh = {}
	terms = []
	scope = ""
	similar = Similaridade()
	headingParams = []
	xmlMesh = ""
	wordEmbedding = ""
	qualifiersParams = []
	printTime = ""
	adicionaTermoPadrao = ""
	tree = ""
	wordModel = ""
	contador = 0

	px = []
	py = []
    
        
	def __init__(self, xmlMesh, wordEmbedding, headingParams = [1.0, 1.0, 5], qualifiersParams = [0.9, 0.89, 0.89, 0.89, 0.89], printTime=True, adicionaTermoPadrao=False):
		self.xmlMesh = xmlMesh
		self.wordEmbedding = wordEmbedding
		self.headingParams = headingParams
		self.qualifiersParams = qualifiersParams
		self.printTime = printTime
		self.adicionaTermoPadrao = adicionaTermoPadrao
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
			if i > 10:
				break

			self.contador += 1

			ID = d.find('.DescriptorUI').text
		    
			start = time.time()

			qualifier = self.verificaQualifier(d)

			end = time.time()
			time_qualifer.append(end - start)
		    
			heading = d.find('.DescriptorName/String').text

		    #Adicionando o heading inteiro no Mesh

			start = time.time()

			self.add_IndiceReverso(heading, ID, self.headingParams[0], self.headingParams[1], self.headingParams[2])

			end = time.time()
			time_add_IndiceReverso.append(end - start)

			start = time.time()

			self.seleciona_TermosMesh(d, qualifier, ID, heading)

			end = time.time()
			time_seleciona_TermosMesh.append(end - start)

			start = time.time()

			self.add_Mesh(heading, ID, qualifier )

			end = time.time()
			time_add_Mesh.append(end - start)

		    #self.indiceReverso['term']
			if(self.adicionaTermoPadrao):
				start = time.time()
				indiceReverso = self.adiciona_termosPadrao_IndiceReverso()
				end = time.time()
				time_adiciona_termosPadrao_IndiceReverso += round(end - start,3)

			self.contador += self.similar.tempo()
			self.px.append(i)
			self.py.append(self.contador)


		
		pylab.figure(2)
		pylab.plot(self.px,self.py)
		pylab.show()
		#self.salva_Dicionario('dictMesh', 'dictMesh')
		#self.salva_Dicionario('indiceReverso', 'indiceReverso')

		if(self.printTime):
			return round(np.mean(time_qualifer), 5), round(np.mean(time_add_IndiceReverso), 5), round(np.mean(time_seleciona_TermosMesh), 5), round(np.mean(time_add_Mesh), 5)

	def verificaQualifier(self, descriptor):
		qualifier = '#'

		for aql in descriptor.findall('.AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName'):
			teste_qualifier = aql.find('./String').text
			if(teste_qualifier == 'anatomy & histology' or teste_qualifier == 'pharmacology' or teste_qualifier == 'methods' or teste_qualifier == 'diagnosis'):
				qualifier = teste_qualifier
				break
			self.contador += 1

		return qualifier

	def add_IndiceReverso(self, heading, ID, porc_similar, porc_medio, flag):
		
		self.indiceReverso[heading.lower()+" _i"] = {
			'ID': ID,
			'porc_similar': porc_similar,
			'porc_medio': porc_medio,
			'flag': flag

		}

	def add_Mesh(self, heading, ID, qualifier):
		self.dictMesh[ID] = {
			'ID': ID,
			'name': heading,
			'scope': self.scope,
			'terms': sorted(set(self.terms), reverse=True),
			'qualifier': qualifier
		}

	def seleciona_TermosMesh(self, descriptor, qualifier, ID, heading):        
		for c in descriptor.findall('.ConceptList/'):
			self.contador += 1
			termos_similares = []
			porc_lista = []
			porc_medio = 0

			if c.find('./ScopeNote') != None:
				self.scope = c.find('./ScopeNote').text.replace('\n','').strip()
			cont = 0
			for t in c.findall('./TermList/'):            
				self.terms.append(t.find('./String').text)
				## INICIO VERIFICANDO

				self.contador += 1
				palavraa = t.find('./String').text.lower()

				palavraa = palavraa.replace('(','')
				palavraa = palavraa.replace(')','')
				palavraa = palavraa.replace('[','')
				palavraa = palavraa.replace(']','')

				novo = palavraa.split(' ')

				palavra_similar = []  

				#Pega os termos similares e armazena eles e a sua porcentagem em duas listas, uma para cada um
				termos_similares, porc_lista = self.similar.verifica_similaridade( self.wordModel, novo, qualifier, termos_similares, porc_lista, self.qualifiersParams[0], self.qualifiersParams[1], self.qualifiersParams[2], self.qualifiersParams[3], self.qualifiersParams[4])


			#Verifica se realmente e similar, termo por termo que foi armazenado acima
			termos_similares, self.terms, porc_maior, flag = self.similar.verifica_valor(self.terms, termos_similares, self.indiceReverso, porc_lista, self.dictMesh, descriptor.find('.DescriptorUI').text)
			for i in range(0, len(termos_similares)-1):
				self.add_IndiceReverso( termos_similares[i], ID, porc_maior[i], 0, flag)
				self.contador += 1
			self.dictMesh, indiceReverso, self.terms = self.similar.verifica_similaridade_media(self.wordModel, termos_similares, c.findall('./TermList/'), self.indiceReverso, self.dictMesh,ID, self.terms)

			palavraa = heading.replace('(','')
			palavraa = palavraa.replace(')','')

			novo = palavraa.split(' ')

			termos_similares = []
			porc_lista = []
			porc_medio = 0

			termos_similares, porc_lista = self.similar.verifica_similaridade( self.wordModel, novo, qualifier, termos_similares, porc_lista, self.qualifiersParams[0], self.qualifiersParams[1], self.qualifiersParams[2], self.qualifiersParams[3], self.qualifiersParams[4])
			termos_similares, self.terms, porc_maior,  flag= self.similar.verifica_valor(self.terms, termos_similares, indiceReverso, porc_lista, self.dictMesh, descriptor.find('.DescriptorUI').text)
			
			for i in range(0, len(termos_similares)-1):
				self.contador += 1
				self.add_IndiceReverso( termos_similares[i], ID, porc_maior[i], 0, flag)
			self.dictMesh, self.indiceReverso, self.terms = self.similar.verifica_similaridade_media(self.wordModel, termos_similares, c.findall('./TermList/'), self.indiceReverso, self.dictMesh,ID, self.terms)

            #Adicionando no dicionario MeSH

			self.terms.append(" <input type='hidden' name='ID' value='"+ID+"'/> ")

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


	def adiciona_termosPadrao_IndiceReverso(self):
		for dui in list(self.dictMesh):
			self.contador += 1
			d = self.dictMesh[str(dui)]
			for t in d['terms']:
				self.contador += 1
				if not('<i>' in t):
					if(t.find('(') == -1):
						novo = t.replace(' ', '_')
						novo = t.split('[')
					elif(t[-1] == ')'):
						novo = t.replace(' ', '_')
						novo = t.split('(')
					indice = novo[0]
					indice = indice.replace('_', ' ')
					if(indice != '' and indice[-1] == ' '):
						indice = indice[0:-1]
		            ## antes de adicionar o termo, remover o que esta entre parenteses -(blabla)-
		            #if(indice.lower() in self.indiceReverso):
		            
					if(indice.lower()+" _i" in self.indiceReverso and self.indiceReverso[indice.lower()+" _i"]['flag'] == 4):
		                
						termos_similares = []
						termos_similares, porc_lista = self.similar.verifica_similaridade( self.wordModel, indice, 'qualifier', termos_similares, [], 0.9, 0.89, 0.89, 0.89, 0.89)

						#gera_Lista
						self.indiceReverso = self.similar.verifica_similaridade_media_repetido(self.wordModel, indice.lower(), self.indiceReverso[indice.lower()+" _i"]['ID'], termos_similares, self.indiceReverso, self.dictMesh, dui)          
					else:
						self.add_IndiceReverso(indice, d['ID'], 0.99, 0.99, 4)
				