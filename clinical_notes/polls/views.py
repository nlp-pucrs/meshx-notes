
####

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.fields.files import FieldFile
from django.views.generic import FormView
from django.contrib import messages

###

from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
#importing loading from django template 
from django.template import loader

import pandas as pd
#from polls.models import Paciente

"""
 
#our view which is a function named index

def index(request):
    
    #getting our template 
    template = loader.get_template('index.html')
    context = super(index, self).index(**kwargs)

    #Pegando os dados da tabela
	ea = pd.read_csv('excel_ea.csv.gz', compression='gzip')

	paciente = Paciente()

	for idx in ea.index:
		paciente.data_paciente =  ea.loc[idx,'DATA']
		paciente.tipo =  ea.loc[idx,'TIPO']
		paciente.resumo_evento =  ea.loc[idx,'RESUMO DO EVENTO']
		paciente.registro =  ea.loc[idx,'REGISTRO']
		paciente.evento =  ea.loc[idx,'EVENTO']
		paciente.sexo =  ea.loc[idx,'SEXO']
		paciente.id_paciente =  ea.loc[idx,'ID']
		paciente.gravidade =  ea.loc[idx,'GRAVIDADE']
    
    #rendering the template in HttpResponse
    return HttpResponse(template.render())
"""

class PacientePageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(PacientePageView, self).get_context_data(**kwargs)

        #dirspot = os.path.abspath(os.path.dirname(__file__))

        prescription = pd.read_csv('./excel_ea.csv.gz', compression='gzip', nrows=50000)

        #tag = self.request.GET.get('tag')
        #reg = tag

        #data = self.request.GET.get('data')

        #idList = prescription[(prescription['REG. PACIENTE'] == int(reg)) & (prescription['DATA PRESC'] == data)].index

        p = []
        for idx in prescription.index:
            m = prescription.loc[idx] #valor que ha' aqui
            p.append([ m['DATA'], m['TIPO'], m['RESUMO DO EVENTO'], m['REGISTRO'], int(m['EVENTO']), m['SEXO'], int(m['ID']), m['GRAVIDADE'] ])

        #tag = int(reg/10)
        #context['tag'] = self.request.GET.get('tag')
        #context['data'] = data
        context['prescription'] = sorted(p, key=lambda m: m[7], reverse=True)
        context['teste'] = "Estou aqui testando e deu tudo certo!"

        return context