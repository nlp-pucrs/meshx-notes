from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import os
import pandas as pd 

class EventoAdversoPageView(TemplateView):

    template_name = 'header.html'

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

        if self.request.GET.get('id_ea') == None or (0 > indice_ea) or (indice_ea >= (len(ea.loc[::]))):
            indice_ea = 0
        else:
            indice_ea = int(self.request.GET.get('id_ea'))

        if self.request.GET.get('id_evol') == None or (0 > indice_evolucao) or (indice_evolucao >= (len(evolucao.loc[::]))):
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
        

        l = vincula.loc[indice_ea]
        m = evolucao.loc[indice_evolucao]
        n = ea.loc[indice_ea]
    
        # Context da Evolução
        context['data_evolucao'] = m['DATA EVOL'] 
        context['registro_evol'] = m['REG. PACIENTE']
        context['evolucao'] = m['DADOS DA EVOLUÇÃO']
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
        context['evol_vinculada'] = l['id_evol']
        
        return context

    