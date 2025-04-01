from django.shortcuts import render

def verificador(request):
    return render(request, 'verificador/verificador.html')
