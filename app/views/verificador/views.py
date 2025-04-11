from django.shortcuts import render
from app.models import Producto
from django.core.exceptions import MultipleObjectsReturned

def verificador(request):
    resultado = None
    error = None

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()

        if codigo:
            try:
                producto = Producto.objects.get(NumVerificador=codigo)
                resultado = {
                    'nombre': producto.producto,
                    'valor': float(producto.valor),
                }
            except Producto.DoesNotExist:
                error = 'Código no encontrado'
            except MultipleObjectsReturned:
                error = 'Error: hay múltiples productos con ese código'
        else:
            error = 'Por favor ingresa un código'

    return render(request, 'verificador/verificador.html', {
        'resultado': resultado,
        'error': error
    })
