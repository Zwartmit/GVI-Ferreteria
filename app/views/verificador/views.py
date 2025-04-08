from django.shortcuts import render
from app.models import Producto

def verificador(request):
    resultado = None
    error = None

    if request.method == 'POST':
        codigo = request.POST.get('codigo', '').strip()

        if codigo:  # <-- Agregamos esta validación
            try:
                producto = Producto.objects.get(NumVerificador=codigo)
                resultado = {
                    'nombre': producto.producto,
                    'valor': float(producto.valor),
                }
            except Producto.DoesNotExist:
                error = 'Código no encontrado'
        else:
            error = 'Por favor ingresa un código'

    return render(request, 'verificador/verificador.html', {
        'resultado': resultado,
        'error': error
    })
