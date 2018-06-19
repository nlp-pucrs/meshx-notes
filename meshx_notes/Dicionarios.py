from Similaridade import Similaridade

class Dicionarios():
	"""docstring for ClassName"""
	indiceReverso = {}
	dictMesh = {}
	terms = []
	scope = ""
	similar = Similaridade()
	headingParams = []
    
        
	def __init__(self, wordModel, headingParams = [1.0, 1.0, 5]):
		self.wordModel = wordModel
		self.headingParams = headingParams

	def verificaQualifier(self, descriptor):
		qualifier = '#'

		for aql in descriptor.findall('.AllowableQualifiersList/AllowableQualifier/QualifierReferredTo/QualifierName'):
			teste_qualifier = aql.find('./String').text
			if(teste_qualifier == 'anatomy & histology' or teste_qualifier == 'pharmacology' or teste_qualifier == 'methods' or teste_qualifier == 'diagnosis'):
				qualifier = teste_qualifier
				break

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
        
			termos_similares = []
			porc_lista = []
			porc_medio = 0

			if c.find('./ScopeNote') != None:
				self.scope = c.find('./ScopeNote').text.replace('\n','').strip()
			cont = 0
			for t in c.findall('./TermList/'):            
				self.terms.append(t.find('./String').text)
				## INICIO VERIFICANDO


				palavraa = t.find('./String').text.lower()

				palavraa = palavraa.replace('(','')
				palavraa = palavraa.replace(')','')
				palavraa = palavraa.replace('[','')
				palavraa = palavraa.replace(']','')

				novo = palavraa.split(' ')

				palavra_similar = []  

				#Pega os termos similares e armazena eles e a sua porcentagem em duas listas, uma para cada um
				termos_similares, porc_lista = self.similar.verifica_similaridade( self.wordModel, novo, qualifier, termos_similares, porc_lista, 0.9, 0.89, 0.89, 0.89, 0.89)


			#Verifica se realmente e similar, termo por termo que foi armazenado acima
			termos_similares, self.terms, porc_maior, flag = self.similar.verifica_valor(self.terms, termos_similares, self.indiceReverso, porc_lista, self.dictMesh, descriptor.find('.DescriptorUI').text)
			for i in range(0, len(termos_similares)-1):
				self.add_IndiceReverso( termos_similares[i], ID, porc_maior[i], 0, flag)
			self.dictMesh, indiceReverso, self.terms = self.similar.verifica_similaridade_media(self.wordModel, termos_similares, c.findall('./TermList/'), self.indiceReverso, self.dictMesh,ID, self.terms)

			palavraa = heading.replace('(','')
			palavraa = palavraa.replace(')','')

			novo = palavraa.split(' ')

			termos_similares = []
			porc_lista = []
			porc_medio = 0

			termos_similares, porc_lista = self.similar.verifica_similaridade( self.wordModel, novo, qualifier, termos_similares, porc_lista, 0.9, 0.89, 0.89, 0.89, 0.89)
			termos_similares, self.terms, porc_maior,  flag= self.similar.verifica_valor(self.terms, termos_similares, indiceReverso, porc_lista, self.dictMesh, descriptor.find('.DescriptorUI').text)
			
			for i in range(0, len(termos_similares)-1):
				self.add_IndiceReverso( termos_similares[i], ID, porc_maior[i], 0, flag)
			self.dictMesh, self.indiceReverso, self.terms = self.similar.verifica_similaridade_media(self.wordModel, termos_similares, c.findall('./TermList/'), self.indiceReverso, self.dictMesh,ID, self.terms)

            #Adicionando no dicionario MeSH

			self.terms.append(" <input type='hidden' name='ID' value='"+ID+"'/> ")

	def salva_Dicionario(self, nome, dicionario):
		import gzip, pickle

		with gzip.open(nome+'.dict.gz','wb') as fp:
			if(dicionario == "dictMesh"):
				pickle.dump(self.dictMesh,fp)
			else:
				pickle.dump(self.indiceReverso,fp)
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
			d = self.dictMesh[str(dui)]
			for t in d['terms']:
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
				