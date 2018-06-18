from gensim.models import KeyedVectors
import unicodedata

from unicodedata import normalize

import gzip
import xml.etree.ElementTree as ET

with gzip.open('pordesc2018.xml.gz') as pordesc2018:
    tree = ET.parse(pordesc2018)

class Similaridade():

	def remover_acentos(self, txt):
	    return normalize('NFKD', txt).encode('ASCII', 'ignore').decode('ASCII')

	def verifica_valor(self, terms, termos_similares, indiceReverso, porc_lista, dictMesh, id_Mesh):

	#Se ha termos, entao faz a media
   
		porc_maior = []
		flag = -1
		termos_certos = []

		if(len(termos_similares) > 0):
			for i in range(len(termos_similares)):
				flag = -1

				if not (termos_similares[i]+' _i' in indiceReverso):
					flag = 0
					porc_maior.append(porc_lista[i])
		        #Se a porcentagem do termo em uma definicao for maior que na qual ele ja esta
				else:
					if(len(porc_lista) != 0):
						if(termos_similares[i]+' _i' in indiceReverso and indiceReverso[termos_similares[i]+" _i"]['porc_similar'] < porc_lista[i]):
							flag = 1
							porc_maior.append(porc_lista[i])
		                #Se a porcentagem media do termo em uma definicao for maior que na qual ele ja esta

		            #Se for trocar, entao remove o lugar que ele estava antes

				if((flag != -1) and (termos_similares[i]+" _i" in indiceReverso) and len(porc_lista) != 0):
					ID = indiceReverso[termos_similares[i]+" _i"]['ID']
					if(ID in  dictMesh):
						for t in range(len(dictMesh[ID]['terms'])-1):
							if '<i> '+termos_similares[i]+' </i>' in dictMesh[ID]['terms'][t]:
								del dictMesh[ID]['terms'][t] 

		        #Se o termo foi reconhecido e esta sendo a primeira vez ou vai ser trocado,
		        #entao adiciona ele no indice reverso

				if(flag != -1):    
					#indiceReverso = dicionario.add_IndiceReverso(indiceReverso, termos_similares[i], id_Mesh, porc_maior, porc_medio, flag)
					terms.append("<i> "+termos_similares[i]+" </i>" + " <input class='radio' type='radio' name='"+termos_similares[i]+"' value='1'/> Certo <input class='radio' type='radio' name='"+termos_similares[i]+"' value='0'/> Errado")
					termos_certos.append(termos_similares[i])

		return termos_certos, terms, porc_maior, flag

	def verifica_similaridade(self, wordModel, novo, qualifier, termos_similares, porc_lista, porcent_pharmacology, porcent_anatomy, porcent_methods, porcent_diagnosis, porcent_others):
		palavra_similar = []
		for termo_novo in novo:           
			if termo_novo in wordModel.vocab: #Se o termo esta no word embeddings
				sem_assento = self.remover_acentos(termo_novo.lower())
				palavra_similar = wordModel.most_similar_cosmul(sem_assento,topn=10)
		       
		        #Verifica a similariedade

				for similar, porcentagem in palavra_similar:
					if(porcentagem > porcent_pharmacology and qualifier == 'pharmacology'):
						termos_similares.append(similar)
						porc_lista.append(porcentagem)
					elif (porcentagem > porcent_anatomy and qualifier == 'anatomy & histology'):
						termos_similares.append(similar)
						porc_lista.append(porcentagem)
					elif (porcentagem > porcent_methods and qualifier == 'methods'):
						termos_similares.append(similar)
						porc_lista.append(porcentagem)
					elif (porcentagem > porcent_diagnosis and qualifier == 'diagnosis'):
						termos_similares.append(similar)
						porc_lista.append(porcentagem)
					elif (porcentagem > porcent_others and qualifier == '#'):
						termos_similares.append(similar)
						porc_lista.append(porcentagem)

		return termos_similares, porc_lista

	def verifica_similaridade_media(self, wordModel, termos_similares, lista_termos, indiceReverso, dictMesh, id_Mesh, terms):
		palavra_similar = []
		if(id_Mesh in dictMesh):
			for termo_mesh in dictMesh[id_Mesh]: 
				if termo_mesh in wordModel.vocab: #Se o termo esta no word embeddings
					sem_assento = remover_acentos(termo_mesh.lower())
					palavra_similar = wordModel.most_similar_cosmul(sem_assento,topn=10)

		            #Verifica a similariedade

					cont = 0
					porc_medio = 0

					for similar, porcentagem in palavra_similar:
						for termo_similar in termos_similares: 
							if(similar == termo_similar):
								porc_medio += porcentagem
								cont  += 1

		            #Funca que ve a similaridade media
					if porc_medio != 0:
						porc_medio = porc_medio/cont

					flag = -1

					if(indiceReverso[similar]['porc_similar'] < porc_medio \
						and indiceReverso[similar]['porc_medio'] < porc_medio):   
							flag = 2
							porc_maior = porc_medio

					if((flag != -1) and (similar+" _i" in indiceReverso)):
						ID = indiceReverso[similar+" _i"]['ID']
						if(ID in dictMesh):
							for t in range(len(dictMesh[ID]['terms'])-1):
								if '<i> '+similar+' </i>' in dictMesh[ID]['terms'][t]:
									del dictMesh[ID]['terms'][t] 

					if(flag != -1):                       
						indiceReverso[termos_similares[i]+' _i'] = {
							'ID': id_Mesh,
							'porc_similar': porc_maior,
							'porc_medio': porc_medio,
							'flag': flag

						} 	
						terms.append("<i> "+termos_similares[i]+" </i>" + " <input class='radio' type='radio' name='"+termos_similares[i]+"' value='1'/> Certo <input class='radio' type='radio' name='"+termos_similares[i]+"' value='0'/> Errado")
		
		return dictMesh, indiceReverso, terms

	def verifica_similaridade_media_repetido(self, wordModel, termo, termo_id, termos_similares, indiceReverso, dictMesh, id_Mesh):
		palavra_similar = []
		porc_medio = []
		flag = -1
		if(id_Mesh in dictMesh):
			for termo_mesh in dictMesh[id_Mesh]: 
				if termo_mesh in wordModel.vocab: #Se o termo esta no word embeddings
					sem_assento = remover_acentos(termo_mesh.lower())
					palavra_similar = wordModel.most_similar_cosmul(sem_assento,topn=10)

		            #Verifica a similariedade

					cont = 0
					aux = 0

					for similar, porcentagem in palavra_similar:
						for termo_similar in termos_similares: 
							if(similar == termo_similar):
								aux += porcentagem
								cont  += 1
		            

		    #Funca que ve a similaridade media
			if aux != 0:
				aux = aux/cont

			porc_medio.append(aux)

		if(termo_id in dictMesh):
			for termo_mesh in dictMesh[termo_id]: 
				if termo_mesh in wordModel.vocab: #Se o termo esta no word embeddings
					sem_assento = remover_acentos(termo_mesh.lower())
					palavra_similar = wordModel.most_similar_cosmul(sem_assento,topn=10)

		            #Verifica a similariedade

					cont = 0
					aux = 0

					for similar, porcentagem in palavra_similar:
						for termo_similar in termos_similares: 
							if(similar == termo_similar):
								aux += porcentagem
								cont  += 1
		            

		    #Funca que ve a similaridade media
			if aux != 0:
				aux = aux/cont

			porc_medio.append(aux)

		if(porc_medio[0] < porc_medio[1]):   
			flag = 2
			porc_maior = porc_medio[1]

		if((flag != 2) and (termo+" _i" in indiceReverso)):
			id_Mesh = indiceReverso[termo+" _i"]['ID']

		if(flag != -1):                       
			indiceReverso[termo+' _i'] = {
				'ID': id_Mesh,
				'porc_similar': porc_maior,
				'porc_medio': porc_medio,
				'flag': 10

			}

		return indiceReverso