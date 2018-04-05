import pandas as pd
from polls.models import Paciente

#Pegando os dados da tabela
ea = pd.read_csv('excel_ea.csv.gz', compression='gzip')

#paciente = Paciente(data_paciente, tipo, resumo_evento, registro, evento, sexo, id_paciente, gravidade)
paciente = Paciente('', '', '', '', '', '', '', '')

for idx in ea.index:
	paciente.data_paciente =  ea.loc[idx,'DATA']
	paciente.tipo =  ea.loc[idx,'tipo']
	paciente.resumo_evento =  ea.loc[idx,'RESUMO DO EVENTO']
	paciente.registro =  ea.loc[idx,'REGISTRO']
	paciente.evento =  ea.loc[idx,'EVENTO']
	paciente.sexo =  ea.loc[idx,'SEXO']
	paciente.id_paciente =  ea.loc[idx,'ID']
	paciente.gravidade =  ea.loc[idx,'GRAVIDADE']
	q.save()

