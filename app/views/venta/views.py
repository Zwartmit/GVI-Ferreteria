from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from app.models import Venta, Producto, Detalle_venta, Cliente
from app.forms import VentaForm, ClienteForm, DetalleVentaForm
import json

@never_cache
def lista_venta(request):
    context = {
        'titulo': 'Listado de ventas',
        'ventaas': Venta.objects.all()
    }
    return render(request, 'venta/listar.html', context)

###### LISTAR ######

@method_decorator([login_required, never_cache], name='dispatch')
class VentaListView(ListView):
    model = Venta
    template_name = 'venta/listar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ventas = Venta.objects.all()
        context.update({
            'titulo': 'Listado de ventas',
            'entidad': 'Listado de ventas',
            'listar_url': reverse_lazy('app:venta_lista'),
            'crear_url': reverse_lazy('app:venta_crear'),
            'ventas_con_detalles': [
                {
                    'venta': venta,
                    'detalles_venta': Detalle_venta.objects.filter(id_venta=venta)
                }
                for venta in ventas
            ]
        })
        return context

###### API'S ######

def productos_api(request):
    term = request.GET.get('term', '')
    productos = Producto.objects.filter(
        Q(producto__icontains=term) & Q(estado=True)
    ).values('id', 'producto', 'valor', 'cantidad', 'id_presentacion__presentacion')
    return JsonResponse(list(productos), safe=False)

def clientes_api(request):
    term = request.GET.get('term', '')
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=term) | Q(numero_documento__icontains=term), estado=True
    ).values('id', 'nombre', 'tipo_documento', 'numero_documento', 'email', 'pais_telefono', 'telefono')
    return JsonResponse(list(clientes), safe=False)

###### CREAR ######

@method_decorator([login_required, never_cache], name='dispatch')
class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/crear.html'
    success_url = reverse_lazy('app:venta_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Registrar venta',
            'entidad': 'Registrar venta',
            'listar_url': reverse_lazy('app:venta_lista'),
            'detalleventa_form': DetalleVentaForm()
        })
        return context

    def form_valid(self, form):
        venta = form.save(commit=False)
        detalles_venta_json = self.request.POST.get('detalles_venta')
        dinero_recibido = float(self.request.POST.get('money_received', 0))

        detalles_venta = json.loads(detalles_venta_json) if detalles_venta_json else []
        venta.total_venta = sum(float(d['subtotal_venta']) for d in detalles_venta)
        venta.dinero_recibido = dinero_recibido
        venta.cambio = dinero_recibido - venta.total_venta
        venta.save()

        for detalle in detalles_venta:
            producto_instance = Producto.objects.get(pk=detalle['id_producto'])
            producto_instance.cantidad -= int(detalle['cantidad_producto'])
            producto_instance.save()
            Detalle_venta.objects.create(
                id_venta=venta,
                id_producto=producto_instance,
                cantidad_producto=detalle['cantidad_producto'],
                subtotal_venta=detalle['subtotal_venta']
            )
        
        return JsonResponse({'success': True, 'message': 'Venta generada exitosamente'})

###### EDITAR ######

@method_decorator([login_required, never_cache], name='dispatch')
class VentaUpdateView(UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/crear.html'
    success_url = reverse_lazy('app:venta_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Editar venta',
            'entidad': 'Editar venta',
            'listar_url': reverse_lazy('app:venta_lista')
        })
        return context

###### ELIMINAR ######

@method_decorator([login_required, never_cache], name='dispatch')
class VentaDeleteView(DeleteView):
    model = Venta
    template_name = 'venta/eliminar.html'
    success_url = reverse_lazy('app:venta_lista')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'titulo': 'Eliminar venta',
            'entidad': 'Eliminar venta',
            'listar_url': reverse_lazy('app:venta_lista')
        })
        return context

def ventas_view(request):
    return render(request, 'venta/ventas.html')
