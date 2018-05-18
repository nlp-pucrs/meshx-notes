from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
import os
import pandas as pd 
import logging
class VinculaPageView(TemplateView):
    template_name = 'vincula.html'
    logger = logging.getLogger(__name__)

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
            vincula.loc[id_ea] = [id_ea, id_evol, None, None, None, None]
            teste = "if"
        else:
            vincula.loc[id_ea] = [-1, -1, None, None, None, None]

        vincula.to_csv(caminho_vincula, index=None)

        context['debbuging'] = teste
        return context




    