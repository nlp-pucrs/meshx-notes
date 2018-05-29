from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import os
import pandas as pd 
import logging
class VinculaPageView(TemplateView):
    template_name = 'vincula.html'

    def get_context_data(self, **kwargs):
        context = super(VinculaPageView, self).get_context_data(**kwargs)

        caminho_vincula = './data/vincula.csv'

        current_path = os.path.dirname(os.path.realpath(__file__))
        caminho_vincula = os.path.join(current_path, caminho_vincula)

        vincula = pd.read_csv(caminho_vincula)

        id_ea = int(self.request.GET.get('id_ea'))
        id_evol = int(self.request.GET.get('id_evol'))
        vincular = self.request.GET.get('vincular')

        if(vincular == 'True'):
            if(id_ea in vincula.id_ea.values):
                linha = vincula[(vincula['id_ea'] == id_ea)]
                valor_linha = linha['id_evol'].values
                context['evol_vinculada'] = valor_linha.item(0)
                context['tempo'] = 5
            else:
                vincula.loc[id_evol, 'id_ea'] = id_ea
                vincula.loc[id_evol, 'id_evol'] = id_evol
                context['tempo'] = 0
        else:
            vincula.loc[id_evol, 'id_ea'] = -1
            context['tempo'] = 0

        vincula.to_csv(caminho_vincula, index=None)

        context['id_ea'] = id_ea
        context['id_evol'] = id_evol
        return context




    