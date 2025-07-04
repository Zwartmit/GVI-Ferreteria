import django
import os
import re
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.db.models import ProtectedError
from app.models import Proveedor, Producto
from app.forms import ProveedorForm
from django.db.models import Sum

@method_decorator(login_required, name='dispatch')
class ProveedorListView(ListView):
    model = Proveedor
    template_name = 'proveedor/listar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de proveedores'
        context['entidad'] = 'Listado de proveedores'
        context['listar_url'] = reverse_lazy('app:proveedor_lista')
        context['crear_url'] = reverse_lazy('app:proveedor_crear')
        context['has_permission'] = self.request.user.has_perm('app.view_proveedor')
        proveedores = context['object_list']

        for proveedor in proveedores:
            proveedor.facturas_list = proveedor.facturas.all()
            if proveedor.cancelada:
                proveedor.deuda_total = 0.00
            else:
                proveedor.deuda_total = sum([
                    f.valor_total - f.valor_abonado for f in proveedor.facturas.all()
                    if f.valor_abonado < f.valor_total
                ])
            proveedor.tiene_factura_archivo = any(f.archivo for f in proveedor.facturas_list)

        if self.request.user.groups.filter(name='Operador').exists():
            context['can_add'] = False
        else:
            context['can_add'] = self.request.user.has_perm('app.add_proveedor')

        return context

@method_decorator(login_required, name='dispatch')
class ProveedorCreateView(CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor/crear.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar proveedor'
        context['listar_url'] = reverse_lazy('app:proveedor_lista')
        return context

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'success': True, 'message': 'Proveedor registrado correctamente.'})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})

@method_decorator(login_required, name='dispatch')
class ProveedorUpdateView(UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = 'proveedor/crear.html'
    success_url = reverse_lazy('app:proveedor_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar proveedor'
        context['entidad'] = 'Editar proveedor'
        context['listar_url'] = reverse_lazy('app:proveedor_lista')
        return context

    def form_valid(self, form):
        try:
            form.save()
            return JsonResponse({'success': True, 'message': 'Proveedor editado exitosamente.'})
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'errors': errors})


@method_decorator(login_required, name='dispatch')
class ProveedorDeleteView(DeleteView):
    model = Proveedor
    template_name = 'proveedor/eliminar.html'
    success_url = reverse_lazy('app:proveedor_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar proveedor'
        context['entidad'] = 'Eliminar proveedor'
        context['listar_url'] = reverse_lazy('app:proveedor_lista')
        context['has_permission'] = not self.request.user.groups.filter(name='Operador').exists() and self.request.user.has_perm('app.delete_proveedor')
        return context

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.has_perm('app.delete_proveedor') or self.request.user.groups.filter(name='Operador').exists():
            list_context = ProveedorListView.as_view()(request, *args, **kwargs).context_data
            return render(request, 'proveedor/listar.html', list_context)
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Proveedor eliminado con éxito.'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar el proveedor.'})

@method_decorator(login_required, name='dispatch')
class ProveedorProductosView(ListView):
    model = Proveedor
    template_name = 'proveedor/productos.html'
    context_object_name = 'proveedores'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Proveedores y sus Productos'
        context['entidad'] = 'Proveedores y Productos'
        context['listar_url'] = reverse_lazy('app:proveedor_lista')
        context['has_permission'] = self.request.user.has_perm('app.view_proveedor')
        
        # Obtener el proveedor seleccionado si existe
        proveedor_id = self.request.GET.get('proveedor_id')
        if proveedor_id:
            try:
                proveedor_seleccionado = Proveedor.objects.get(id=proveedor_id)
                productos = Producto.objects.filter(proveedor=proveedor_seleccionado)
                context['proveedor_seleccionado'] = proveedor_seleccionado
                context['productos'] = productos
            except Proveedor.DoesNotExist:
                context['proveedor_seleccionado'] = None
                context['productos'] = []
        else:
            context['proveedor_seleccionado'] = None
            context['productos'] = []
            
        return context
