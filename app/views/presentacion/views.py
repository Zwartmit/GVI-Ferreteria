from django.contrib import messages
import django
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import os
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.db.models import ProtectedError
from app.models import Presentacion
from app.forms import PresentacionForm

@method_decorator(never_cache, name='dispatch')
def lista_presentacion(request):
    nombre = {
        'titulo': 'Listado de presentaciones',
        'presentaciones': Presentacion.objects.all()
    }
    return render(request, 'presentacion/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class PresentacionListView(ListView):
    model = Presentacion
    template_name = 'presentacion/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de presentaciones'
        context['entidad'] = 'Listado de presentaciones'
        context['listar_url'] = reverse_lazy('app:presentacion_lista')
        context['crear_url'] = reverse_lazy('app:presentacion_crear')
        return context

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class PresentacionCreateView(CreateView):
    model = Presentacion
    form_class = PresentacionForm
    template_name = 'presentacion/crear.html'
    success_url = reverse_lazy('app:presentacion_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar presentación'
        context['entidad'] = 'Registrar presentación'
        context['error'] = 'Esta presentación ya existe'
        context['listar_url'] = reverse_lazy('app:presentacion_lista')
        context['created'] = self.request.session.pop('created', False) 
        return context
    
    def form_valid(self, form):
        presentacion = form.cleaned_data.get('presentacion').lower()
        unidad_medida = form.cleaned_data.get('unidad_medida')

        # Verifica si ya existe una combinación de presentación y unidad de medida
        if Presentacion.objects.filter(presentacion__iexact=presentacion, unidad_medida=unidad_medida).exists():
            form.add_error('presentacion', 'Ya existe una presentación registrada con ese nombre y unidad de medida.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        success_url = reverse('app:presentacion_crear') + '?created=True'
        return redirect(success_url)
        
###### EDITAR ######

@method_decorator(never_cache, name='dispatch')
class PresentacionUpdateView(UpdateView):
    model = Presentacion
    form_class = PresentacionForm
    template_name = 'presentacion/crear.html'
    success_url = reverse_lazy('app:presentacion_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar presentación'
        context['entidad'] = 'Editar presentación'
        context['error'] = 'Esta presentación ya existe'
        context['listar_url'] = reverse_lazy('app:presentacion_lista')
        return context
    
    def form_valid(self, form):
        presentacion = form.cleaned_data.get('presentacion').lower()
        response = super().form_valid(form)
        success_url = reverse('app:presentacion_crear') + '?updated=True'
        return redirect(success_url)

###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class PresentacionDeleteView(DeleteView):
    model = Presentacion
    template_name = 'presentacion/eliminar.html'
    success_url = reverse_lazy('app:presentacion_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar presentación'
        context['entidad'] = 'Eliminar presentación'
        context['listar_url'] = reverse_lazy('app:presentacion_lista')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Presentación eliminada con éxito.'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar la presentación porque está asociada a un producto.'})