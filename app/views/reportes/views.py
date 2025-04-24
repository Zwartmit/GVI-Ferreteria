from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app.forms import ReporteForm
from app.views.reportes.viewsExcel import *
from django.utils.dateparse import parse_date

@login_required
@never_cache
def reporte_selector(request):
    if request.method == 'POST':
        tipo_reporte = request.POST.get('tipo_reporte')
        
        fecha_inicio = request.POST.get('fecha_inicio')
        fecha_fin = request.POST.get('fecha_fin')
        
        fecha_inicio = parse_date(fecha_inicio) if fecha_inicio else None
        fecha_fin = parse_date(fecha_fin) if fecha_fin else None

        print("Fecha de inicio:", fecha_inicio)
        print("Fecha de fin:", fecha_fin)
        
        if tipo_reporte == 'producto':
            return export_productos_excel(request, fecha_inicio, fecha_fin)
        elif tipo_reporte == 'administrador':
            return export_administradores_excel(request)
        elif tipo_reporte == 'operador':
            return export_operadores_excel(request)
        elif tipo_reporte == 'venta':
            return export_ventas_excel(request, fecha_inicio, fecha_fin)
    else:
        form = ReporteForm()

    contexto = {
        'titulo': 'Generar reportes',
        'entidad': 'Generar reportes',
        'form': form
    }
    
    return render(request, 'reportes.html', contexto)
