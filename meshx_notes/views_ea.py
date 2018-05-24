from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from gensim.models import KeyedVectors
import unicodedata
import os
import re
import pandas as pd 

class EventoAdversoPageView(TemplateView):

    template_name = 'header.html'

    def remove_accents(self, input_str):
	    nfkd_form = unicodedata.normalize('NFKD', input_str)
	    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

    def get_context_data(self, **kwargs):
        context = super(EventoAdversoPageView, self).get_context_data(**kwargs)

        caminho_evolucao = './data/excel_evol.csv.gz'
        caminho_ea =      './data/excel_ea.csv.gz'
        caminho_vincula = './data/vincula.csv'

        current_path = os.path.dirname(os.path.realpath(__file__))
        caminho_evolucao = os.path.join(current_path, caminho_evolucao)
        caminho_ea  = os.path.join(current_path, caminho_ea)
        caminho_vincula = os.path.join(current_path, caminho_vincula)

        evolucao = pd.read_csv(caminho_evolucao, compression='gzip')
        ea = pd.read_csv(caminho_ea, compression='gzip')
        vincula = pd.read_csv(caminho_vincula)


        indice_ea = 0
        indice_evolucao = 0

        if any((self.request.GET.get('id_ea') == None, (0 > indice_ea), (indice_ea >= (len(ea.loc[::]))))):
            indice_ea = 0
        else:
            indice_ea = int(self.request.GET.get('id_ea'))

        if any((self.request.GET.get('id_evol') == None, (0 > indice_evolucao), (indice_evolucao >= (len(evolucao.loc[::]))))):
            if(indice_ea == 0):
                indice_evolucao = 0
                context['ultima_posicao_evol'] = 16
                context['primeira_posicao_evol'] = -1
            else:
                indice_evolucao = 16
                context['ultima_posicao_evol'] = len(evolucao.loc[::])
                context['primeira_posicao_evol'] = 15
        else:
            if(indice_ea == 0):
                indice_evolucao = int(self.request.GET.get('id_evol'))
                context['ultima_posicao_evol'] = 16
                context['primeira_posicao_evol'] = -1
            else:
                indice_evolucao = int(self.request.GET.get('id_evol'))
                context['ultima_posicao_evol'] = len(evolucao.loc[::])
                context['primeira_posicao_evol'] = 15

        m = evolucao.loc[indice_evolucao]
        n = ea.loc[indice_ea]
        if(indice_ea in vincula.id_ea.values):
            vinculado = True
            linha = vincula[(vincula['id_ea'] == indice_ea)]
            valor_linha = linha['id_evol'].values
            context['evol_vinculada'] = valor_linha.item(0)
        else: 
            context['evol_vinculada'] = None


        nfkd_form = unicodedata.normalize('NFKD', m['DADOS DA EVOLUÇÃO'])
        aux = u"".join([c for c in nfkd_form if not unicodedata.combining(c)])

        texto = re.sub('[^\w\s]','', aux)
        evolucao = texto.split(' ');
        evolucao_charespecial = m['DADOS DA EVOLUÇÃO'].split(' ');

        for i in range(len(evolucao_charespecial)):
            evolucao_charespecial[i] = re.sub(r'(\w)(\W)',r'\1 \2', evolucao_charespecial[i])
            evolucao_charespecial[i]  = re.sub(r'(\W)(\w)',r'\1 \2', evolucao_charespecial[i])

        for i in range(len(evolucao)):

            confere = False

            palavra = evolucao[i]
            if(palavra != ' ' and palavra != ''):
                evolucao[i] = '<span onclick="sublinhar(this.id)" class="word" id="'+str(i)+'">'+palavra+'</span>'
                if(palavra == evolucao_charespecial[i][0:-2] and palavra != evolucao_charespecial[i]):
                	evolucao[i] = evolucao[i]+' '+evolucao_charespecial[i][-1]
                if(palavra == evolucao_charespecial[i][2:] and palavra != evolucao_charespecial[i]):
                    evolucao[i] = evolucao[i]+' '+evolucao_charespecial[i][0:1]
            else:
                evolucao[i] = evolucao_charespecial[i]

		#Junta tudo novamente
        strr = ' '.join(evolucao)
    
        # Context da Evolução
        context['data_evolucao'] = m['DATA EVOL'] 
        context['registro_evol'] = m['REG. PACIENTE']
        context['evolucao'] = strr
        context['indice_avancar_evol'] = indice_evolucao + 1
        context['indice_evol'] = indice_evolucao
        context['indice_retornar_evol'] = indice_evolucao - 1   

        # Context do Evento Adverso
        context['data_ea'] = n['DATA']
        context['tipo'] = n['TIPO']
        context['resumo_evento'] = n['RESUMO DO EVENTO']
        context['registro_ea'] = n['REGISTRO']
        context['evento'] = n['EVENTO'] 
        context['sexo'] = n['SEXO']
        context['ID'] = n['ID']
        context['gravidade'] = n['GRAVIDADE']
        context['indice_avancar_ea'] = indice_ea + 1
        context['indice_ea'] = indice_ea
        context['indice_retornar_ea'] = indice_ea - 1
        context['ultima_posicao_ea'] = len(ea.loc[::])      
        
        return context

    