from django.contrib import messages
import pandas as pd
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
from app.models import Producto, Categoria, Marca, Presentacion, Compra, Detalle_compra
from app.forms import ProductoForm

@method_decorator(never_cache, name='dispatch')
def lista_productos(request):
    nombre = {
        'titulo': 'Listado de productos',
        'productos': Producto.objects.all()
    }
    return render(request, 'producto/listar.html', nombre)

###### LISTAR ######

@method_decorator(never_cache, name='dispatch')
class ProductoListView(ListView):
    model = Producto
    template_name = 'producto/listar.html'
    
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        nombre = {'nombre': 'Juan'}
        return JsonResponse(nombre)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Listado de productos'
        context['entidad'] = 'Listado de productos'
        context['listar_url'] = reverse_lazy('app:producto_lista')
        context['crear_url'] = reverse_lazy('app:producto_crear')
        return context

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class ProductoCreateView(CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto/crear.html'
    success_url = reverse_lazy('app:producto_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Registrar producto'
        context['entidad'] = 'Registrar producto'
        context['error'] = 'Este producto ya existe'
        context['listar_url'] = reverse_lazy('app:producto_lista')
        return context
    
    def form_valid(self, form):
        producto = form.cleaned_data.get('producto').lower()
        
        if Producto.objects.filter(producto__iexact=producto).exists():
            form.add_error('producto', 'Ya existe un producto registrado con ese nombre.')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        success_url = reverse('app:producto_crear') + '?created=True'
        return redirect(success_url)
    
###### EDITAR ######

@method_decorator(never_cache, name='dispatch')
class ProductoUpdateView(UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'producto/crear.html'
    success_url = reverse_lazy('app:producto_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar producto'
        context['entidad'] = 'Editar producto'
        context['error'] = 'Este producto ya existe'
        context['listar_url'] = reverse_lazy('app:producto_lista')
        return context
    
    def form_valid(self, form):
        producto = form.cleaned_data.get('producto').lower()
        response = super().form_valid(form)
        success_url = reverse('app:producto_crear') + '?updated=True'
        return redirect(success_url)

###### ELIMINAR ######

@method_decorator(never_cache, name='dispatch')
class ProductoDeleteView(DeleteView):
    model = Producto
    template_name = 'producto/eliminar.html'
    success_url = reverse_lazy('app:producto_lista')

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Eliminar producto'
        context['entidad'] = 'Eliminar producto'
        context['listar_url'] = reverse_lazy('app:producto_lista')
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({'success': True, 'message': 'Producto eliminado con éxito.'})
        except ProtectedError:
            return JsonResponse({'success': False, 'message': 'No se puede eliminar el producto.'})

###### IMPORTAR ######

def importar_factura_view(request):
    if request.method == 'POST' and request.FILES.get('archivo'):
        archivo = request.FILES['archivo']
        try:
            df = pd.read_excel(archivo)

            required_columns = ['Producto', 'Cantidad', 'Valor', 'NumVerificador', 'Categoría', 'Marca', 'Presentación']

            if not all(col in df.columns for col in required_columns):
                messages.error(request, "El archivo no contiene todas las columnas requeridas: " + ", ".join(required_columns))
                return redirect('app:producto_lista')
            
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                messages.error(
                    request,
                    f"El archivo no contiene las siguientes columnas requeridas: {', '.join(missing_columns)}"
                )
                return redirect('app:producto_lista')
            
            compra = Compra.objects.create(proveedor="Proveedor Desconocido", estado=True)

            for _, row in df.iterrows():
                categoria, _ = Categoria.objects.get_or_create(categoria=row['Categoría'])
                marca, _ = Marca.objects.get_or_create(marca=row['Marca'])
                presentacion, _ = Presentacion.objects.get_or_create(presentacion=row['Presentación'])

                producto, created = Producto.objects.get_or_create(
                    producto=row['Producto'],
                    NumVerificador=row['NumVerificador'],
                    defaults={
                        'cantidad': row['Cantidad'],
                        'valor': row['Valor'],
                        'estado': True,
                        'id_categoria': categoria,
                        'id_marca': marca,
                        'id_presentacion': presentacion,
                    }
                )

                if not created:
                    producto.cantidad += row['Cantidad']
                    producto.valor = row['Valor']
                    producto.save()

                Detalle_compra.objects.create(
                    compra=compra,
                    producto=producto,
                    cantidad=row['Cantidad'],
                    valor_unitario=row['Valor'],
                    subtotal=row['Cantidad'] * row['Valor']
                )

            messages.success(request, "Datos importados correctamente desde la factura.")
        except Exception as e:
            messages.error(request, f"Error al procesar el archivo: {e}")
        return redirect('app:producto_lista')
    else:
        messages.error(request, "No se seleccionó un archivo.")
        return redirect('app:producto_lista')
