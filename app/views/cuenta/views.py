import json
import django
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import os
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView, DeleteView, CreateView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect

from app.models import Cuenta, Venta, Detalle_venta, Producto, Plato
from app.forms import CuentaForm, VentaForm, ClienteForm, DetalleVentaForm, CuentaForm, MeseroForm

@method_decorator(never_cache, name='dispatch')
def lista_cuenta(request):
    nombre = {
        'titulo': 'Listado de cuentas',
        'cuentas': Cuenta.objects.all()
    }
    return render(request, 'cuenta/listar.html',nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class CuentaListView(ListView): 
    model = Cuenta
    template_name = 'cuenta/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de cuentas'
        context['entidad'] = 'Listado de cuentas'
        context['listar_url'] = reverse_lazy('app:cuenta_lista')
        context['crear_url'] = reverse_lazy('app:cuenta')
        return context

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class CuentaCreateView(CreateView):
    model = Venta
    form_class = VentaForm
    template_name = 'cuenta/crear.html'
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
        context['cliente_form'] = ClienteForm()
        context['detalleventa_form'] = DetalleVentaForm()
        context['cuenta_form'] = CuentaForm()
        return context

    def form_valid(self, form):
        try:
            venta = form.save(commit=False)
            venta.tipo_venta = Venta.TipoVenta.Cuenta
            detalles_venta_json = self.request.POST.get('detalles_venta')
            cuentas_json = self.request.POST.get('cuentas')
            dinero_recibido = float(self.request.POST.get('dinero_recibido', 0))
            
            if detalles_venta_json:
                try:
                    detalles_venta = json.loads(detalles_venta_json)
                except json.JSONDecodeError:
                    detalles_venta = []
            else:
                detalles_venta = []

            if cuentas_json:
                try:
                    cuentas_data = json.loads(cuentas_json)
                except json.JSONDecodeError:
                    cuentas_data = []
            else:
                cuentas_data = [] 

            total_productos = sum(float(d['subtotal_venta']) for d in detalles_venta)
            total_platos = sum(float(c['subtotal_plato']) for c in cuentas_data)
            venta.total_venta = total_productos + total_platos
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

            for cuenta in cuentas_data:
                id_plato = cuenta.get('id_plato')
                cantidad_plato = cuenta.get('cantidad_plato')
                subtotal_plato = cuenta.get('subtotal_plato')
                id_cliente = cuenta.get('id_cliente')
                id_mesero = cuenta.get('id_mesero')

                try:
                    plato_instance = Plato.objects.get(pk=id_plato) 
                except Plato.DoesNotExist:
                    continue

                Cuenta.objects.create(
                    id_venta=venta,
                    id_plato=plato_instance, 
                    cantidad_plato=cantidad_plato,
                    subtotal_plato=subtotal_plato,
                    id_cliente_id=id_cliente,  
                    id_mesero_id=id_mesero
                )

            return JsonResponse({'success': True, 'message': 'Venta generada exitosamente'})
        except Exception as e:
            print(f"Error al guardar la venta: {e}")
            return JsonResponse({'success': False, 'message': 'Error al generar la venta'})
    
###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class CuentaDeleteView(DeleteView):
    model = Cuenta
    template_name = 'cuenta/eliminar.html'
    success_url = reverse_lazy('app:cuenta_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar cuenta'
        context['entidad'] = 'Eliminar cuenta'
        context['listar_url'] = reverse_lazy('app:cuenta_lista')
        return context
