from django.contrib import messages
import django
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import os
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.db.models import ProtectedError
from app.models import Factura

@method_decorator(never_cache, name='dispatch')
def lista_factura(request):
    nombre = {
        'titulo': 'Gestión de facturas',
        'facturas': Factura.objects.all()
    }
    return render(request, 'factura/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class FacturaListView(ListView):
    model = Factura
    template_name = 'factura/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Gestión de facturas'
        context['entidad'] = 'Gestión de facturas'
        context['listar_url'] = reverse_lazy('app:factura_lista')
        return context
