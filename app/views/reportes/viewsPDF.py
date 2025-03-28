import io
from io import BytesIO
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image, Spacer
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
from app.models import *

def generate_pdf_report(title_text, headers, data_rows, filename):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A3))
    elements = []

    styles = getSampleStyleSheet()
    style_title = styles['Title']
    style_normal = styles['Normal']

    centered_style = ParagraphStyle(
        name='CenteredStyle',
        parent=styles['Normal'],
        alignment=1 
    )

    image_path = 'app/views/reportes/logo_asuan.png'
    image = Image(image_path)
    image_width = 3 * inch  
    image_height = 1 * inch
    image.drawHeight = image_height
    image.drawWidth = image_width
    image.hAlign = 'CENTER'

    elements.append(image)
    elements.append(Spacer(1, 12))

    title = Paragraph(title_text, style_title)
    elements.append(title)

    fecha = datetime.now().strftime("%d/%m/%Y")
    date_paragraph = Paragraph(f"Fecha: {fecha}", centered_style)
    elements.append(date_paragraph)
    elements.append(Spacer(1, 12))

    data = [headers] + data_rows

    col_widths = [2 * inch, 2 * inch, 2 * inch, 2 * inch, 2 * inch, 2 * inch]
    table = Table(data, colWidths=col_widths)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#04644B")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={filename}.pdf'
    return response

################################################## Categorias ##################################################
@login_required
@never_cache
def export_categorias_pdf(request):
    headers = ['ID', 'Categoría', 'Estado']
    data_rows = [
        [categoria.id, categoria.categoria, 'Activo' if categoria.estado else 'Inactivo']
        for categoria in Categoria.objects.all()
    ]
    return generate_pdf_report("Reporte de Categorías", headers, data_rows, "Reporte de categorias")

################################################## Marcas ##################################################
@login_required
@never_cache
def export_marcas_pdf(request):
    headers = ['ID', 'Marca', 'Estado']
    data_rows = [
        [marca.id, marca.marca, 'Activo' if marca.estado else 'Inactivo']
        for marca in Marca.objects.all()
    ]
    return generate_pdf_report("Reporte de Marcas", headers, data_rows, "Reporte de marcas")

################################################## Presentaciones ##################################################
@login_required
@never_cache
def export_presentaciones_pdf(request):
    headers = ['ID', 'Presentación', 'Estado']
    data_rows = [
        [presentacion.id, presentacion.presentacion, 'Activo' if presentacion.estado else 'Inactivo']
        for presentacion in Presentacion.objects.all()
    ]
    return generate_pdf_report("Reporte de Presentaciones", headers, data_rows, "Reporte de presentaciones")

################################################## Productos ##################################################
@login_required
@never_cache
def export_productos_pdf(request):
    headers = ['ID', 'Producto', 'Cantidad', 'Valor', 'Categoría', 'Marca', 'Presentación', 'Estado']
    data_rows = [
        [
            producto.id, producto.producto, producto.cantidad, producto.valor,
            producto.id_categoria.categoria, producto.id_marca.marca, 
            producto.id_presentacion.presentacion,
            'Activo' if producto.estado else 'Inactivo'
        ]
        for producto in Producto.objects.all()
    ]
    return generate_pdf_report("Reporte de Productos", headers, data_rows, "Reporte de productos")

################################################## Platos ##################################################
@login_required
@never_cache
def export_platos_pdf(request):
    headers = ['ID', 'Nombre', 'Descripción', 'Valor', 'Estado']
    
    platos = Plato.objects.all()
    data_rows = []
    
    centered_paragraph_style = ParagraphStyle(
        name="CenteredParagraph",
        parent=getSampleStyleSheet()['Normal'],
        alignment=1,  
        spaceBefore=0,
        spaceAfter=0,
    )
    
    for plato in platos:
        description_paragraph = Paragraph(plato.descripcion, centered_paragraph_style)
        row = [
            plato.id,
            plato.plato,
            description_paragraph,  
            f"${plato.valor:.2f}",
            'Activo' if plato.estado else 'Inactivo'
        ]
        data_rows.append(row)
    
    return generate_pdf_report("Reporte de Platos", headers, data_rows, "Reporte de platos")

################################################## Meseros ##################################################
@login_required
@never_cache
def export_meseros_pdf(request):
    headers = ['ID', 'Mesero', 'Tipo de documento', '# de documento', 'Email', 'Prefijo', 'Teléfono']
    data_rows = [
        [mesero.id, mesero.nombre, mesero.tipo_documento, mesero.numero_documento, mesero.email, mesero.pais_telefono, mesero.telefono]
        for mesero in Mesero.objects.all()
    ]
    return generate_pdf_report("Reporte de Meseros", headers, data_rows, "Reporte de meseros")

################################################## Clientes ##################################################
@login_required
@never_cache
def export_clientes_pdf(request):
    headers = ['ID', 'Cliente', 'Tipo de documento', '# de documento', 'Email', 'Prefijo', 'Teléfono']
    data_rows = [
        [cliente.id, cliente.nombre, cliente.tipo_documento, cliente.numero_documento, cliente.email, cliente.pais_telefono, cliente.telefono]
        for cliente in Cliente.objects.all()
    ]
    return generate_pdf_report("Reporte de Clientes", headers, data_rows, "Reporte de clientes")

################################################## Administradores ##################################################
@login_required
@never_cache
def export_administradores_pdf(request):
    headers = ['ID', 'Nombre', 'Tipo de documento', '# de documento', 'Email', 'Teléfono']
    data_rows = [
        [admin.id, admin.nombre, admin.tipo_documento, admin.numero_documento, admin.user.email, admin.telefono]
        for admin in Administrador.objects.all()
    ]
    return generate_pdf_report("Reporte de Administradores", headers, data_rows, "Reporte de administradores")

################################################## Operadores ##################################################
@login_required
@never_cache
def export_operadores_pdf(request):
    headers = ['ID', 'Nombre', 'Tipo de documento', '# de documento', 'Email', 'Teléfono']
    data_rows = [
        [operador.id, operador.nombre, operador.tipo_documento, operador.numero_documento, operador.user.email, operador.telefono]
        for operador in Operador.objects.all()
    ]
    return generate_pdf_report("Reporte de Operadores", headers, data_rows, "Reporte de operadores")

################################################## Ventas ##################################################
@login_required
@never_cache
def export_ventas_pdf(request, fecha_inicio=None, fecha_fin=None):
    if fecha_inicio and fecha_fin:
        ventas = ventas.filter(fecha_venta__range=[fecha_inicio, fecha_fin])
        headers = ['ID', 'Fecha Venta', 'Total Venta', 'Dinero Recibido', 'Cambio', 'Metodo de pago']
        data_rows = [
            [venta.id, venta.fecha_venta.strftime("%Y-%m-%d %H:%M:%S"), venta.total_venta, venta.dinero_recibido, venta.cambio, venta.metodo_pago]
            for venta in Venta.objects.all()
        ]
        return generate_pdf_report("Reporte de Ventas", headers, data_rows, "Reporte de ventas")

# ################################################## Detalles ##################################################
# @login_required
# @never_cache
# def export_detalle_ventas_pdf(request):
#     headers = ['ID', 'ID Venta', 'Fecha Venta', 'Producto', 'Cantidad', 'Subtotal Venta']
#     data_rows = [
#         [detalle.id, detalle.id_venta, detalle.id_venta.fecha_venta.strftime("%Y-%m-%d %H:%M:%S"), 
#          f"{detalle.id_producto.producto}-{detalle.id_producto.id_presentacion.presentacion}({detalle.id_producto.id_presentacion.unidad_medida})", 
#          detalle.cantidad_producto, detalle.subtotal_venta]
#         for detalle in Detalle_venta.objects.all()
#     ]
#     return generate_pdf_report("Reporte de Detalles de Ventas", headers, data_rows, "Reporte de detalles de ventas")

# ################################################## Cuentas ##################################################
# @login_required
# @never_cache
# def export_cuentas_pdf(request):
#     headers = ['ID', 'ID Venta', 'Fecha Venta', 'Plato', 'Cantidad', 'Subtotal Venta', 'Cliente', 'Mesero']
#     data_rows = [
#         [cuenta.id, cuenta.id_venta, cuenta.id_venta.fecha_venta.strftime("%Y-%m-%d %H:%M:%S"), cuenta.id_plato.plato, cuenta.cantidad_plato, cuenta.subtotal_plato, cuenta.id_cliente.numero_documento, cuenta.id_mesero.nombre]
#         for cuenta in Cuenta.objects.all()
#     ]
#     return generate_pdf_report("Reporte de Cuentas", headers, data_rows, "Reporte de cuentas")