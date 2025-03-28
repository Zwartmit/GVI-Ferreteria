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
from app.models import Categoria
from app.forms import CategoriaForm

@method_decorator(never_cache, name='dispatch')
def lista_categoria(request):
    nombre = {
        'titulo': 'Listado de categorias',
        'categorias': Categoria.objects.all()
    }
    return render(request, 'categoria/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class CategoriaListView(ListView):
    model = Categoria
    template_name = 'categoria/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de categorías'
        context['entidad'] = 'Listado de categorías'
        context['listar_url'] = reverse_lazy('app:categoria_lista')
        context['crear_url'] = reverse_lazy('app:categoria_crear')
        return context

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class CategoriaCreateView(CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/crear.html'
    success_url = reverse_lazy('app:categoria_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar categoría'
        context['entidad'] = 'Registrar categoría'
        context['error'] = 'Esta categoría ya existe'
        context['listar_url'] = reverse_lazy('app:categoria_lista')
        context['created'] = self.request.session.pop('created', False) 
        return context
        
    def form_valid(self, form):
        categoria = form.cleaned_data.get('categoria').lower()

        if Categoria.objects.filter(categoria__iexact=categoria).exists():
            form.add_error('categoria', 'Ya existe una categoría registrada con este nombre.')
            return self.form_invalid(form)

        response = super().form_valid(form)
        success_url = reverse('app:categoria_crear') + '?created=True'
        return redirect(success_url)

###### EDITAR ######

@method_decorator(never_cache, name='dispatch')
class CategoriaUpdateView(UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/crear.html'
    success_url = reverse_lazy('app:categoria_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar categoría'
        context['entidad'] = 'Editar categoría'
        context['error'] = 'Esta categoría ya existe'
        context['listar_url'] = reverse_lazy('app:categoria_lista')
        return context

    def form_valid(self, form):
        categoria = form.cleaned_data.get('categoria').lower()
        response = super().form_valid(form)
        success_url = reverse('app:categoria_crear') + '?updated=True'
        return redirect(success_url)

###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class CategoriaDeleteView(DeleteView):
    model = Categoria
    template_name = 'categoria/eliminar.html'
    success_url = reverse_lazy('app:categoria_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar categoría'
        context['entidad'] = 'Eliminar categoría'
        context['listar_url'] = reverse_lazy('app:categoria_lista')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Categoría eliminada con éxito.'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar la categoría porque está asociada a un producto.'})
