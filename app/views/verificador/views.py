from django.shortcuts import render

def verificador(request):
    contexto = {
        'titulo': 'Verificador de precios',
        'entidad': 'Verificador de precios'
    }
    return render(request, 'verificador/verificador.html', contexto)
