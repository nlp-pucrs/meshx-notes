from django.shortcuts import render
from django.http import HttpResponse

def ea(request):
    return render(request, 'home.html')
