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
from django.db.models import Q
from django.urls import reverse
from django.contrib import messages
from app.models import Venta, Producto, Detalle_venta, Cliente, Cuenta, Plato, Mesero
from app.forms import VentaForm, ClienteForm, DetalleVentaForm, CuentaForm, MeseroForm
import json

@method_decorator(never_cache, name='dispatch')
def lista_venta(request):
    nombre = {
        'titulo': 'Listado de ventas',
        'ventaas': Venta.objects.all()
    }
    return render(request, 'venta/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class VentaListView(ListView):
    model = Venta
    template_name = 'venta/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        ventas = Venta.objects.all()
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de ventas'
        context['entidad'] = 'Listado de ventas'
        context['listar_url'] = reverse_lazy('app:venta_lista')
        context['crear_url'] = reverse_lazy('app:venta_crear')
        context['ventas_con_detalles'] = [
            {'venta': venta, 
            'cuentas': Cuenta.objects.filter(id_venta=venta),
            'detalles_venta': Detalle_venta.objects.filter(id_venta=venta)
            }
            for venta in ventas
        ]
        
        return context
    
###### API'S ######
    
def productos_api(request):
    term = request.GET.get('term', '') 
    productos = Producto.objects.filter(Q(producto__icontains=term) & Q(estado=True)
    ).values('id', 'producto', 'valor', 'cantidad','id_presentacion__presentacion','id_presentacion__unidad_medida')
    return JsonResponse(list(productos), safe=False)

def platos_api(request):
    term = request.GET.get('term', '')
    platos = Plato.objects.filter(
        Q(plato__icontains=term) & Q(estado=True) 
    ).values('id', 'plato', 'valor')
    
    return JsonResponse(list(platos), safe=False)

def clientes_api(request):  
    term = request.GET.get('term', '')
    clientes = Cliente.objects.filter(
        Q(nombre__icontains=term) | Q(numero_documento__icontains=term),
        estado=True
    ).values(
        'id', 'nombre', 'tipo_documento', 'numero_documento', 'email', 'pais_telefono', 'telefono'
    )
    return JsonResponse(list(clientes), safe=False)

def meseros_api(request):
    term = request.GET.get('term', '') 
    meseros = Mesero.objects.filter(Q(nombre__icontains=term) & Q(estado=True)
    ).values('id', 'nombre', 'tipo_documento', 'numero_documento', 'email', 'pais_telefono', 'telefono')
    return JsonResponse(list(meseros), safe=False)

###### GUARDAR CLIENTE ######

def crear_cliente_ajax(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            return JsonResponse({
                'success': True,
                'cliente_id': cliente.id,
                'cliente_nombre': cliente.nombre,
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    return JsonResponse({'success': False}, status=400)

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class VentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/crear.html'
    success_url = reverse_lazy('app:venta_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar venta'
        context['entidad'] = 'Registrar venta'
        context['error'] = 'Esta venta ya existe'
        context['listar_url'] = reverse_lazy('app:venta_lista')
        context['detalleventa_form'] = DetalleVentaForm()
        return context
    
    def form_valid(self, form):
        try:
            venta = form.save(commit=False)
            venta.tipo_venta = Venta.TipoVenta.Caja
            detalles_venta_json = self.request.POST.get('detalles_venta')
            dinero_recibido = float(self.request.POST.get('money_received', 0))

            if detalles_venta_json:
                try:
                    detalles_venta = json.loads(detalles_venta_json)
                except json.JSONDecodeError:
                    detalles_venta = []
            else:
                detalles_venta = []

            venta.total_venta = sum(float(d['subtotal_venta']) for d in detalles_venta)
            venta.dinero_recibido = dinero_recibido
            venta.cambio = dinero_recibido - venta.total_venta
            venta.save()

            for detalle in detalles_venta:
                id_producto = detalle.get('id_producto')
                cantidad_producto = detalle.get('cantidad_producto')
                subtotal_venta = detalle.get('subtotal_venta')

                try:
                    producto_instance = Producto.objects.get(pk=id_producto)
                except Producto.DoesNotExist:
                    continue

                producto_instance.cantidad -= int(cantidad_producto)
                producto_instance.save()

                Detalle_venta.objects.create(
                    id_venta=venta,
                    id_producto=producto_instance, 
                    cantidad_producto=cantidad_producto,
                    subtotal_venta=subtotal_venta
                )
                
            return JsonResponse({'success': True, 'message': 'Venta generada exitosamente'})
        except Exception as e:
            print(f"Error al guardar la venta: {e}")
            return JsonResponse({'success': False, 'message': 'Error al generar la venta'})
        
###### EDITAR ######

@method_decorator(never_cache, name='dispatch')
class VentaUpdateView(UpdateView):
    model = Venta
    form_class = VentaForm
    template_name = 'venta/crear.html'
    success_url = reverse_lazy('app:venta_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar venta'
        context['entidad'] = 'Editar venta'
        context['error'] = 'Esta venta ya existe'
        context['listar_url'] = reverse_lazy('app:venta_lista')
        return context
    
###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class VentaDeleteView(DeleteView):
    model = Venta
    template_name = 'venta/eliminar.html'
    success_url = reverse_lazy('app:venta_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar venta'
        context['entidad'] = 'Eliminar venta'
        context['listar_url'] = reverse_lazy('app:venta_lista')
        return context 
    
def ventas_view(request):
    return render(request, 'venta/ventas.html')