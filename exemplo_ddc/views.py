# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.files.storage import default_storage

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.fields.files import FieldFile
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.contrib import messages

from forms import ContactForm, FilesForm, ContactFormSet

import os
import pandas as pd
import datetime


# http://yuji.wordpress.com/2013/01/30/django-form-field-in-initial-data-requires-a-fieldfile-instance/
class FakeField(object):
    storage = default_storage


fieldfile = FieldFile(None, FakeField, 'dummy.txt')

class IndexPageView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPageView, self).get_context_data(**kwargs)
        #dirspot = os.path.abspath(os.path.dirname(__file__))
        prescription = pd.read_csv('./prescription_score_cooc.csv.gz', compression='gzip', nrows=50000)
        prescription_filter = prescription

        dt = self.request.GET.get('dt','')
        if dt != '':
            dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
            dt = dt.strftime('%d/%m/%y')
            prescription_filter = prescription_filter[prescription_filter['DATA PRESC']==dt]

        m = self.request.GET.get('m','')
        if m != '':
            prescription_filter = prescription_filter[prescription_filter['MEDICAMENTO'].str.lower().str.contains(m)]


        s = self.request.GET.get('s','')
        if s == '':
            s = 1
        else:
            s = int(s)

        presc_Index = prescription_filter[['MEDICAMENTO','REG. PACIENTE', 'DATA PRESC']].groupby(['REG. PACIENTE', 'DATA PRESC']).agg(['count'])
        presc_Index = presc_Index['MEDICAMENTO']
        prescriptions = []
        for i, (reg, data) in enumerate(presc_Index.index):
            idList = prescription[(prescription['REG. PACIENTE'] == reg) & (prescription['DATA PRESC'] == data)].index
            score = int(prescription.loc[idList]['general_score'].sum())
            if score >= s:
                tag = reg
                prescriptions.append([tag,reg,data,score])
            if len(prescriptions) > 20:
                break

        context['dt'] = self.request.GET.get('dt','')
        context['s'] = self.request.GET.get('s','')
        context['m'] = self.request.GET.get('m','')

        context['prescriptions'] = sorted(prescriptions, key=lambda p: p[3], reverse=True)
        return context


class PrescriptionPageView(TemplateView):
    template_name = 'prescription.html'

    def get_context_data(self, **kwargs):
        context = super(PrescriptionPageView, self).get_context_data(**kwargs)
        dirspot = os.path.abspath(os.path.dirname(__file__))
        prescription = pd.read_csv(dirspot + '/prescription_score_cooc.csv.gz', compression='gzip', nrows=50000)
        tag = self.request.GET.get('tag')
        reg = tag
        data = self.request.GET.get('data')
        idList = prescription[(prescription['REG. PACIENTE'] == int(reg)) & (prescription['DATA PRESC'] == data)].index
        p = []
        for idx in idList:
            m = prescription.loc[idx]
            p.append([ m['MEDICAMENTO'], m['DOSE'], m['VIA'], m['FREQUÊNCIA'], m['COMPLEMENTO'], int(m['dose_score']), int(m['via_score']), int(m['obs_score']), int(m['dup_score']), int(m['cooc_score']), int(m['general_score']) ])

        #tag = int(reg/10)
        context['tag'] = self.request.GET.get('tag')
        context['data'] = data
        context['prescription'] = sorted(p, key=lambda m: m[10], reverse=True)

        return context

class MedicationPageView(TemplateView):
    template_name = 'medication.html'


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        messages.info(self.request, 'hello localhost')
        return context


class DefaultFormsetView(FormView):
    template_name = 'formset.html'
    form_class = ContactFormSet


class DefaultFormView(FormView):
    template_name = 'form.html'
    form_class = ContactForm


class DefaultFormByFieldView(FormView):
    template_name = 'form_by_field.html'
    form_class = ContactForm


class FormHorizontalView(FormView):
    template_name = 'form_horizontal.html'
    form_class = ContactForm


class FormInlineView(FormView):
    template_name = 'form_inline.html'
    form_class = ContactForm


class FormWithFilesView(FormView):
    template_name = 'form_with_files.html'
    form_class = FilesForm

    def get_context_data(self, **kwargs):
        context = super(FormWithFilesView, self).get_context_data(**kwargs)
        context['layout'] = self.request.GET.get('layout', 'vertical')
        return context

    def get_initial(self):
        return {
            'file4': fieldfile,
        }


class PaginationView(TemplateView):
    template_name = 'pagination.html'

    def get_context_data(self, **kwargs):
        context = super(PaginationView, self).get_context_data(**kwargs)
        lines = []
        for i in range(200):
            lines.append('Line %s' % (i + 1))
        paginator = Paginator(lines, 10)
        page = self.request.GET.get('page')
        try:
            show_lines = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            show_lines = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            show_lines = paginator.page(paginator.num_pages)
        context['lines'] = show_lines
        return context


class MiscView(TemplateView):
    template_name = 'misc.html'
