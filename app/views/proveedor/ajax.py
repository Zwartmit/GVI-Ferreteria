from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from app.models import Proveedor
from app.models import Factura
from django.db import models

@require_POST
@csrf_exempt  # Si usas CSRF en AJAX, puedes quitar esto y manejar el token en JS
def marcar_cancelada(request):
    id = request.POST.get('id')
    proveedor = Proveedor.objects.get(id=id)
    proveedor.cancelada = True
    proveedor.save()
    # Cancelar todas las facturas pendientes (valor_abonado < valor_total)
    proveedor.facturas.filter(valor_abonado__lt=models.F('valor_total')).update(valor_abonado=models.F('valor_total'))
    return JsonResponse({'success': True})

from decimal import Decimal

@require_POST
@csrf_exempt
def abonar_deuda_total(request):
    id = request.POST.get('id')
    monto = Decimal(request.POST.get('monto', '0'))
    proveedor = Proveedor.objects.get(id=id)
    facturas = proveedor.facturas.filter(valor_abonado__lt=models.F('valor_total')).order_by('fecha_registro', 'id')
    monto_original = monto
    for factura in facturas:
        pendiente = factura.valor_total - factura.valor_abonado
        if monto <= 0:
            break
        abono = min(pendiente, monto)
        factura.valor_abonado += abono
        factura.save()
        monto -= abono
    # Recalcular deuda total
    nueva_deuda = sum([
        f.valor_total - f.valor_abonado for f in proveedor.facturas.all()
        if f.valor_abonado < f.valor_total
    ])
    if nueva_deuda == 0:
        proveedor.cancelada = True
        proveedor.save()
    return JsonResponse({
        'success': True,
        'nueva_deuda': '{:.2f}'.format(nueva_deuda),
        'abonado': '{:.2f}'.format(float(monto_original - monto)),
    })
