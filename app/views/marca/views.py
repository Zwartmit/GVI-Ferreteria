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
from app.models import Marca
from app.forms import MarcaForm

@method_decorator(never_cache, name='dispatch')
def lista_marca(request):
    nombre = {
        'titulo': 'Listado de marcas',
        'marcas': Marca.objects.all()
    }
    return render(request, 'marca/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class MarcaListView(ListView):
    model = Marca
    template_name = 'marca/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de marcas'
        context['entidad'] = 'Listado de marcas'
        context['listar_url'] = reverse_lazy('app:marca_lista')
        context['crear_url'] = reverse_lazy('app:marca_crear')
        return context

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class MarcaCreateView(CreateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'marca/crear.html'
    success_url = reverse_lazy('app:marca_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar marca'
        context['entidad'] = 'Registrar marca'
        context['error'] = 'Esta marca ya existe'
        context['listar_url'] = reverse_lazy('app:marca_lista')
        context['created'] = self.request.session.pop('created', False) 
        return context
    
    def form_valid(self, form):
        marca = form.cleaned_data.get('marca').lower()
        
        if Marca.objects.filter(marca__iexact=marca).exists():
            form.add_error('marca', 'Ya existe una marca registrada con ese nombre.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        success_url = reverse('app:marca_crear') + '?created=True'
        return redirect(success_url)
    
###### EDITAR ######

@method_decorator(never_cache, name='dispatch')
class MarcaUpdateView(UpdateView):
    model = Marca
    form_class = MarcaForm
    template_name = 'marca/crear.html'
    success_url = reverse_lazy('app:marca_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar marca'
        context['entidad'] = 'Editar marca'
        context['error'] = 'Esta marca ya existe'
        context['listar_url'] = reverse_lazy('app:marca_lista')
        return context
    
    def form_valid(self, form):
        marca = form.cleaned_data.get('marca').lower()
        response = super().form_valid(form)
        success_url = reverse('app:marca_crear') + '?updated=True'
        return redirect(success_url)

###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class MarcaDeleteView(DeleteView):
    model = Marca
    template_name = 'marca/eliminar.html'
    success_url = reverse_lazy('app:marca_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar marca'
        context['entidad'] = 'Eliminar marca'
        context['listar_url'] = reverse_lazy('app:marca_lista')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Marca eliminada con éxito.'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar la marca porque está asociada a un producto.'})