import django
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import os
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from app.models import Detalle_venta

@method_decorator(never_cache, name='dispatch')
def lista_productos(request):
    nombre = {
        'titulo': 'Listado de productos',
        'productos': Detalle_venta.objects.all()
    }
    return render(request, 'producto/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class DetalleVentaListView(ListView):
    model = Detalle_venta
    template_name = 'detalle_venta/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registro de ventas por caja'
        context['entidad'] = 'Registro de ventas por cajas'
        context['listar_url'] = reverse_lazy('app:detalle_venta_lista')
        context['crear_url'] = reverse_lazy('app:producto_crear')
        return context
    
    ###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class DetalleVentaDeleteView(DeleteView):
    model = Detalle_venta
    template_name = 'detalle_venta/eliminar.html'
    success_url = reverse_lazy('app:venta_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar venta'
        context['entidad'] = 'Eliminar venta'
        context['listar_url'] = reverse_lazy('app:detalle_venta_lista')
        return context 
    
def ventas_view(request):
    return render(request, 'venta/ventas.html')
