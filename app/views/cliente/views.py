from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.shortcuts import render
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from app.models import Cliente
from app.forms import ClienteForm
from django.db.models import ProtectedError

@method_decorator(login_required, name='dispatch')
class ClienteListView(ListView):
    model = Cliente
    template_name = 'cliente/listar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de clientes'
        context['entidad'] = 'Listado de clientes'
        context['listar_url'] = reverse_lazy('app:cliente_lista')
        context['crear_url'] = reverse_lazy('app:cliente_crear')
        context['has_permission'] = self.request.user.has_perm('app.view_cliente')

        if self.request.user.groups.filter(name='Cliente').exists():
            context['can_add'] = False
        else:
            context['can_add'] = self.request.user.has_perm('app.add_cliente')

        return context

@method_decorator(login_required, name='dispatch')
class ClienteCreateView(CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/crear.html'
    success_url = reverse_lazy('app:cliente_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar cliente'
        context['entidad'] = 'Registrar cliente'
        context['listar_url'] = reverse_lazy('app:cliente_lista')
        context['has_permission'] = not self.request.user.groups.filter(name='Cliente').exists() and self.request.user.has_perm('app.add_cliente')
        return context

    def form_valid(self, form):
        try:
            form.save()
            return JsonResponse({'success': True, 'message': 'Cliente creado exitosamente.'})
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'errors': errors})

@method_decorator(login_required, name='dispatch')
class ClienteUpdateView(UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'cliente/crear.html'
    success_url = reverse_lazy('app:cliente_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar cliente'
        context['entidad'] = 'Editar cliente'
        context['listar_url'] = reverse_lazy('app:cliente_lista')
        context['has_permission'] = not self.request.user.groups.filter(name='Cliente').exists() and self.request.user.has_perm('app.change_cliente')
        return context

    def form_valid(self, form):
        try:
            form.save()
            return JsonResponse({'success': True, 'message': 'Cliente editado exitosamente.'})
        except ValidationError as e:
            form.add_error(None, e)
            return self.form_invalid(form)

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({'success': False, 'errors': errors})

@method_decorator(login_required, name='dispatch')
class ClienteDeleteView(DeleteView):
    model = Cliente
    template_name = 'cliente/eliminar.html'
    success_url = reverse_lazy('app:cliente_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar cliente'
        context['entidad'] = 'Eliminar cliente'
        context['listar_url'] = reverse_lazy('app:cliente_lista')
        context['has_permission'] = not self.request.user.groups.filter(name='Cliente').exists() and self.request.user.has_perm('app.delete_cliente')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Cliente eliminado con éxito.'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar el cliente.'})
