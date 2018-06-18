from Dicionarios import Dicionarios

cont = 0

geraDict = Dicionarios(KeyedVectors.load_word2vec_format('health_w2v_unigram_50.bin', binary=True))

for d in tree.findall("./DescriptorRecord"):

	ID = d.find('.DescriptorUI').text

	qualifier = geraDict.verificaQualifier(d)

	heading = d.find('.DescriptorName/String').text

	#Adicionando o heading inteiro no Mesh
	geraDict.add_IndiceReverso(heading, ID, 1.0, 1.0, 5)

	geraDict.seleciona_TermosMesh(d, qualifier, ID, heading)

	geraDict.add_Mesh(heading, ID, qualifier )

	#geraDict.indiceReverso['term']

indiceReverso = geraDict.adiciona_termosPadrao_IndiceReverso()

geraDict.salva_Dicionario()