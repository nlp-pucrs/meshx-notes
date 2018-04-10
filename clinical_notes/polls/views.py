from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import FormView
from django.contrib import messages

###

from django.http import HttpResponse
from django.views.generic.base import TemplateView
 
#importing loading from django template 
from django.template import loader

import pandas as pd

import gzip
import xml.etree.ElementTree as ET
import string


class PacientePageView(TemplateView):
	template_name = 'index.html'


	def get_context_data(self, **kwargs):
		context = super(PacientePageView, self).get_context_data(**kwargs)

		prescription = pd.read_csv('./excel_evol.csv.gz', compression='gzip', nrows=50000)

		m= prescription.loc[0] #valor que ha' aqui

		#evolucao = m['DADOS DA EVOLUÇÃO'].split(' ');
		#Passando pelo xml

		evolucao = 	['Medicina do Vício', 'Medicina do Adolescente', 'Medicina', 'Acinetobacter', 'Febre']

		with gzip.open('./pordesc2018-small.xml.gz') as pordesc2018:
			tree = ET.parse(pordesc2018)

		cont = 0
		for palavra in evolucao:
				elem = tree.find("./DescriptorRecord/*/*/*/*/[String='"+palavra.title()+"']/../../../../")
				if elem is not None:
					DUI = elem.text
					descriptor = tree.find("./DescriptorRecord/[DescriptorUI='"+DUI+"']")
					name = descriptor.find('.DescriptorName/String').text
					scope = descriptor.find('.ConceptList/Concept/ScopeNote').text
					evolucao[cont] = '<a href="#" data-ui="'+DUI+'" data-scope="'+scope+'">'+palavra+'</a>'
					cont +=1
					continue
				cont +=1
		strr = ' '.join(evolucao)

		
		context['data'] = m['REG. PACIENTE']
		context['registro'] = '1234'
		context['evolucao'] = strr
		return context