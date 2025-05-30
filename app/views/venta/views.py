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
from app.models import Venta, Producto, Detalle_venta
from app.forms import VentaForm, DetalleVentaForm
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
    ).values('id', 'producto', 'valor', 'precio_venta', 'cantidad', 'id_presentacion__presentacion')
        
    # Modificar los datos para asegurarnos que el campo valor se actualice con precio_venta
    productos_list = list(productos)
    for producto in productos_list:
        # Si tiene precio_venta, copiar ese valor al campo valor para la interfaz de ventas
        if producto.get('precio_venta') is not None:
            producto['valor'] = producto['precio_venta']
            
    return JsonResponse(productos_list, safe=False)

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
            # Obtener el producto una sola vez por su ID
            producto_instance = Producto.objects.get(pk=detalle['id_producto'])
            # Actualizar la cantidad de producto
            producto_instance.cantidad -= int(detalle['cantidad_producto'])
            producto_instance.save()
            
            # Obtener el nombre del producto que viene del frontend
            nombre_producto = detalle.get('nombre_producto', '')
            
            # Si no hay nombre del producto desde el frontend, usar el de la base de datos
            if not nombre_producto:
                nombre_producto = producto_instance.producto
                
            # Crear el detalle de venta con el nombre correcto del producto y el precio de venta
            # Si el producto tiene precio_venta usarlo, sino usar el valor original
            precio_a_usar = producto_instance.precio_venta if producto_instance.precio_venta is not None else producto_instance.valor
            
            Detalle_venta.objects.create(
                id_venta=venta,
                id_producto=producto_instance,
                nombre_producto=nombre_producto,  # Priorizar el nombre enviado desde el frontend
                valor_unitario=precio_a_usar,    # Usar precio_venta en lugar de valor
                cantidad_producto=detalle['cantidad_producto'],
                subtotal_venta=detalle['subtotal_venta']
            )

        # Verificar si es una solicitud AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': 'Venta generada exitosamente',
                'id_venta': venta.id,
                'total': float(venta.total_venta),
                'cambio': float(venta.cambio)
            })
        
        # Si no es AJAX, redirigir normalmente con un mensaje
        messages.success(self.request, 'Venta generada exitosamente')
        return super().form_valid(form)

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


def productos_api(request):
    term = request.GET.get('term', '')
    productos = Producto.objects.filter(
        (Q(producto__icontains=term) | Q(NumVerificador__icontains=term)) & Q(estado=True)
    ).values('id', 'producto', 'valor', 'precio_venta', 'cantidad', 'id_presentacion__presentacion')
    
    # Modificar los datos para asegurarnos que el campo valor se actualice con precio_venta
    productos_list = list(productos)
    for producto in productos_list:
        # Si tiene precio_venta, copiar ese valor al campo valor para la interfaz de ventas
        if producto.get('precio_venta') is not None:
            producto['valor'] = producto['precio_venta']
    
    return JsonResponse(productos_list, safe=False)