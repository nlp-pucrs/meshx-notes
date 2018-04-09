
####
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.contrib import messages

###

from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
#importing loading from django template 
from django.template import loader

import pandas as pd


class PacientePageView(TemplateView):
	template_name = 'index.html'


	def get_context_data(self, **kwargs):
		context = super(PacientePageView, self).get_context_data(**kwargs)

        #dirspot = os.path.abspath(os.path.dirname(__file__))

		prescription = pd.read_csv('./excel_evol.csv.gz', compression='gzip', nrows=50000)

        #tag = self.request.GET.get('tag')
        #reg = tag

        #data = self.request.GET.get('data')

        #idList = prescription[(prescription['REG. PACIENTE'] == int(reg)) & (prescription['DATA PRESC'] == data)].index

		p = []
		c = []
		for idx in prescription.index:
			m = prescription.loc[idx] #valor que ha' aqui
            #p.append([ prescription.columns[0], m['DATA'], prescription.columns[1], m['TIPO'], prescription.columns[2], m['RESUMO DO EVENTO'], prescription.columns[3], m['REGISTRO'],  prescription.columns[4], int(m['EVENTO']), prescription.columns[5], m['SEXO'], prescription.columns[6],  int(m['ID']), prescription.columns[7],  m['GRAVIDADE'] ])
            #p.append([m['DATA'], m['TIPO'], m['RESUMO DO EVENTO'], m['REGISTRO'],  int(m['EVENTO']), m['SEXO'], int(m['ID']), m['GRAVIDADE'] ])
            #c.append(prescription.columns[0], prescription.columns[1], prescription.columns[2], prescription.columns[3], prescription.columns[4], prescription.columns[5], prescription.columns[6], prescription.columns[7])

			tamanho = prescription.shape[1]
			i=0
			for i in range(tamanho):
				p.append([prescription.columns[i].title()+": ", m[i] ])
				i+=1
			p.append([".fim." ])

            #p.append([m['DATA'], m['TIPO'], m['RESUMO DO EVENTO'], m['REGISTRO'],  int(m['EVENTO']), m['SEXO'], int(m['ID']), m['GRAVIDADE'] ])
            #c.append(prescription.columns[0], prescription.columns[1], prescription.columns[2], prescription.columns[3], prescription.columns[4], prescription.columns[5], prescription.columns[6], prescription.columns[7])

            #j1 = sorted(p, key=lambda m: m[8], reverse=True)
            #j2 = sorted(c, key=lambda c: m[8], reverse=True)
            #junto = zip(c, p)

        #tag = int(reg/10)
        #context['tag'] = self.request.GET.get('tag')
        #context['data'] = data
		context['prescription'] = p

		return context