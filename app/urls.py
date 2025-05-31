from django.urls import path, include
from app.views.proveedor.ajax import marcar_cancelada, abonar_deuda_total
from app.views import *
from app.views.categoria.views import *
from app.views.presentacion.views import *
from app.views.producto.views import *
from app.views.administrador.views import *
from app.views.operador.views import *
from app.views.proveedor.views import *
from app.views.venta.views import *
from app.views.detalle_venta.views import *
from app.views.reportes.viewsExcel import *
from app.views.reportes.views import *
from app.views.verificador.views import *
from app.views.factura.views import *
from backups.views import BackupDatabaseView, RestoreDatabaseView, DeleteBackupView, BackupListView

app_name = 'app'
urlpatterns = [
    path('proveedor/marcar_cancelada/', marcar_cancelada, name='proveedor_marcar_cancelada'),
    path('proveedor/abonar_deuda_total/', abonar_deuda_total, name='proveedor_abonar_deuda_total'),
    ### CRUD CATEGORÍA ###
    path('categoria/listar/', CategoriaListView.as_view(), name='categoria_lista'),
    path('categoria/crear/', CategoriaCreateView.as_view(), name='categoria_crear'),
    path('categoria/editar/<int:pk>/', CategoriaUpdateView.as_view(), name='categoria_editar'),
    path('categoria/eliminar/<int:pk>/', CategoriaDeleteView.as_view(), name='categoria_eliminar'),

    ### CRUD PRESENTACIÓN ###
    path('presentacion/listar/', PresentacionListView.as_view(), name='presentacion_lista'),
    path('presentacion/crear/', PresentacionCreateView.as_view(), name='presentacion_crear'),
    path('presentacion/editar/<int:pk>/', PresentacionUpdateView.as_view(), name='presentacion_editar'),
    path('presentacion/eliminar/<int:pk>/', PresentacionDeleteView.as_view(), name='presentacion_eliminar'),

    ### CRUD PRODUCTO ###
    path('producto/listar/', ProductoListView.as_view(), name='producto_lista'),
    path('producto/crear/', ProductoCreateView.as_view(), name='producto_crear'),
    path('producto/editar/<int:pk>/', ProductoUpdateView.as_view(), name='producto_editar'),
    path('producto/eliminar/<int:pk>/', ProductoDeleteView.as_view(), name='producto_eliminar'),
    path('producto/importar/', importar_factura_view, name='producto_importar'),

    ### CRUD ADMINISTRADOR ###
    path('administrador/listar/', AdministradorListView.as_view(), name='administrador_lista'),
    path('administrador/crear/', AdministradorCreateView.as_view(), name='administrador_crear'),
    path('administrador/editar/<int:pk>/', AdministradorUpdateView.as_view(), name='administrador_editar'),
    path('administrador/eliminar/<int:pk>/', AdministradorDeleteView.as_view(), name='administrador_eliminar'),

    ### CRUD OPERADOR ###
    path('operador/listar/', OperadorListView.as_view(), name='operador_lista'),
    path('operador/crear/', OperadorCreateView.as_view(), name='operador_crear'),
    path('operador/editar/<int:pk>/', OperadorUpdateView.as_view(), name='operador_editar'),
    path('operador/eliminar/<int:pk>/', OperadorDeleteView.as_view(), name='operador_eliminar'),
    
    ### CRUD PROVEEDOR ###
    path('proveedor/listar/', ProveedorListView.as_view(), name='proveedor_lista'),
    path('proveedor/crear/', ProveedorCreateView.as_view(), name='proveedor_crear'),
    path('proveedor/editar/<int:pk>/', ProveedorUpdateView.as_view(), name='proveedor_editar'),
    path('proveedor/eliminar/<int:pk>/', ProveedorDeleteView.as_view(), name='proveedor_eliminar'),

    ### CRUD FACTURA ###
    path('facturas/crear/', FacturaCreateView.as_view(), name='factura_crear'),

    ### CRUD VENTA ###
    path('venta/listar/', VentaListView.as_view(), name='venta_lista'),
    path('venta/crear/', VentaCreateView.as_view(), name='venta_crear'),
    path('venta/editar/<int:pk>/', VentaUpdateView.as_view(), name='venta_editar'),
    path('venta/eliminar/<int:pk>/', VentaDeleteView.as_view(), name='venta_eliminar'),
    path('venta/opciones/', ventas_view, name='venta_opciones'),
    path('venta/factura/<int:pk>/', factura_venta_view, name='venta_factura'),

    ### DETALLE VENTA ###
    path('detalle_venta/listar/', DetalleVentaListView.as_view(), name='detalle_venta_lista'),
    path('detalleventa/eliminar/<int:pk>/', DetalleVentaDeleteView.as_view(), name='detalle_venta_eliminar'),

    ### COPIA DE SEGURIDAD DE BASE DE DATOS ###
    path('gestionar_backups/', BackupDatabaseView.as_view(), name='gestionar_backups'),
    path('restaurar_backup/', RestoreDatabaseView.as_view(), name='restaurar_backup'),
    path('eliminar-backup/', DeleteBackupView.as_view(), name='eliminar_backup'),
    path('backup_list/', BackupListView.as_view(), name='backup_list'),

    ### REPORTES ###
    path('gestion_reportes/', reporte_selector, name='gestion_reportes'),
    path('reportes/productos/excel/', export_productos_excel, name='export_productos_excel'),
    path('reportes/administradores/excel/', export_administradores_excel, name='export_administradores_excel'),
    path('reportes/operadores/excel/', export_operadores_excel, name='export_operadores_excel'),

    ### API´S ###
    path('venta/productos_api/', productos_api, name='productos_api'),
    path('verificador/', verificador, name='verificador'),
   
]
