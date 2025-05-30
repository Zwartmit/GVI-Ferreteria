from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from app.forms import ReporteForm
from app.views.reportes.viewsExcel_sin_imagenes import *
from app.views.reportes.viewsExcel_ganancias import *
from app.views.reportes.viewsExcel_productos_dia import *
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
        elif tipo_reporte == 'productos_dia':
            # Si se proporciona una fecha, la usamos; de lo contrario, usamos la fecha actual
            fecha_seleccionada = fecha_inicio if fecha_inicio else datetime.now().date()
            return export_productos_dia_excel(request, fecha_seleccionada)
        elif tipo_reporte == 'administrador':
            return export_administradores_excel(request)
        elif tipo_reporte == 'operador':
            return export_operadores_excel(request)
        elif tipo_reporte == 'venta':
            return export_ventas_excel(request, fecha_inicio, fecha_fin)
        elif tipo_reporte == 'ganancias_diarias':
            return export_ganancias_diarias_excel(request)
        elif tipo_reporte == 'ganancias_mensuales':
            return export_ganancias_mensuales_excel(request)
    else:
        form = ReporteForm()

    contexto = {
        'titulo': 'Generar reportes',
        'entidad': 'Generar reportes',
        'form': form
    }
    
    return render(request, 'reportes.html', contexto)
