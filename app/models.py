from django.db import models
from datetime import datetime
from .choices import codigos_telefonicos_paises
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.core.validators import MinLengthValidator    
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class Categoria(models.Model):
    categoria = models.CharField(max_length=50, verbose_name="Categoría", unique=True)
    estado = models.BooleanField(default=True, verbose_name="Estado")

    def __str__(self):
        return f"{self.categoria}"

    class Meta:
        verbose_name= "categoria"
        verbose_name_plural ='categorias'
        db_table ='Categoria'
        
########################################################################################################################################

class Presentacion(models.Model):
    presentacion = models.CharField(max_length=50, verbose_name="Presentación")
    estado = models.BooleanField(default=True, verbose_name="Estado")

    def __str__(self):
        return f"{self.presentacion}"

    class Meta:
        verbose_name = "presentacion"
        verbose_name_plural = "presentaciones"
        db_table = "Presentacion"

        
########################################################################################################################################

class Producto(models.Model):
    producto = models.CharField(max_length=50, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(verbose_name="Cantidad")
    valor = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Costo")
    porcentaje_ganancia = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Porcentaje de ganancia", default=0)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de venta", null=True, blank=True)
    NumVerificador = models.BigIntegerField(verbose_name="NumVerificador", unique=True)
    estado = models.BooleanField(default=True, verbose_name="Estado")
    id_categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, verbose_name="Categoría")
    id_presentacion = models.ForeignKey(Presentacion, on_delete=models.PROTECT, verbose_name="Presentación")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")

    def save(self, *args, **kwargs):
        # Calcular el precio de venta basado en el valor y porcentaje de ganancia
        if self.valor is not None and self.porcentaje_ganancia is not None:
            # Calcula el precio de venta: valor + (valor * porcentaje / 100)
            self.precio_venta = self.valor + (self.valor * self.porcentaje_ganancia / 100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.producto}-{self.id_presentacion.presentacion}({self.id_presentacion})"

    class Meta:
        verbose_name = "producto"
        verbose_name_plural = "productos"
        db_table = "Producto"

########################################################################################################################################

class Administrador(models.Model):
    class TipoDocumento(models.TextChoices):
        CC = 'CC', 'Cédula de Ciudadanía'
        CE = 'CE', 'Cédula de Extranjería'
        PSP = 'PSP', 'Pasaporte'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='administrador')
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    tipo_documento = models.CharField(max_length=3, choices=TipoDocumento.choices, default=TipoDocumento.CC, verbose_name="Tipo de documento")
    numero_documento = models.PositiveIntegerField(verbose_name="Número de documento")
    telefono = models.PositiveIntegerField(verbose_name="Teléfono")
    contrasena = models.CharField(max_length=128, validators=[MinLengthValidator(8)], verbose_name="Contraseña")
    conf_contrasena = models.CharField(max_length=128, verbose_name="Confirmación de contraseña", default="")

    def clean(self):
        super().clean()
        if self.contrasena != self.conf_contrasena:
            raise ValidationError({"conf_contrasena": "Las contraseñas no coinciden"})

    def save(self, *args, **kwargs):
        if not self.pk or 'user' not in kwargs:
            user, created = User.objects.get_or_create(username=self.user.username)
        else:
            user = self.user

        if self.contrasena:
            user.set_password(self.contrasena)

        user.is_superuser = True
        user.is_staff = True
        user.save()

        self.user = user
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Administrador"
        verbose_name_plural = "Administradores"
        db_table = 'Administrador'

@receiver(post_delete, sender=Administrador)
def eliminar_usuario_relacionado(sender, instance, **kwargs):
    user = instance.user
    if user:
        user.delete()

########################################################################################################################################

class Operador(models.Model):
    class TipoDocumento(models.TextChoices):
        CC = 'CC', 'Cédula de Ciudadanía'
        TI = 'TI', 'Tarjeta de Identidad'
        CE = 'CE', 'Cédula de Extranjería'
        PSP = 'PSP', 'Pasaporte'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='operador')
    nombre = models.CharField(max_length=50, verbose_name="Nombre")
    tipo_documento = models.CharField(max_length=3, choices=TipoDocumento.choices, default=TipoDocumento.CC, verbose_name="Tipo de documento")
    numero_documento = models.PositiveIntegerField(verbose_name="Número de documento", unique=True)
    telefono = models.PositiveIntegerField(verbose_name="Teléfono")
    contrasena = models.CharField(max_length=128, validators=[MinLengthValidator(8)], verbose_name="Contraseña")
    conf_contrasena = models.CharField(max_length=128, verbose_name="Confirmación de contraseña", default="")

    def clean(self):
        super().clean()
        if self.contrasena != self.conf_contrasena:
            raise ValidationError({"conf_contrasena": "Las contraseñas no coinciden"})

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Operador"
        verbose_name_plural = "Operadores"
        db_table = 'Operador'

@receiver(post_delete, sender=Operador)
def eliminar_usuario_relacionado(sender, instance, **kwargs):
    user = instance.user
    if user:
        user.delete()

########################################################################################################################################        

class Proveedor(models.Model):
    nombre = models.CharField(max_length=50, verbose_name="Nombre", unique=True)
    telefono = models.PositiveIntegerField(null=True, blank=True, verbose_name="Teléfono")
    cancelada = models.BooleanField(default=False, verbose_name="Cancelada")

    @property
    def plazo_minimo(self):
        facturas = self.facturas.filter(fecha_vencimiento__isnull=False)
        plazos = [f.dias_restantes for f in facturas if f.dias_restantes is not None and f.dias_restantes >= 0 and f.estado != 'Cancelada']
        return min(plazos) if plazos else None

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        db_table = 'Proveedor'

######################################################################################################################################## 

class Factura(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, related_name='facturas')
    archivo = models.FileField( upload_to='facturas_pdfs/', null=True, blank=True, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    valor_total = models.DecimalField(max_digits=10, decimal_places=2)
    valor_abonado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_registro = models.DateField(auto_now_add=True)
    fecha_vencimiento = models.DateField(verbose_name="Fecha de vencimiento", null=True, blank=True)

    @property
    def estado(self):
        if self.valor_abonado >= self.valor_total:
            return "Cancelada"
        elif self.valor_abonado > 0:
            return "Abonada parcialmente"
        return "Pendiente"
        
    @property
    def dias_restantes(self):
        from datetime import date
        today = date.today()
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento - today
            return delta.days
        return None

    def save(self, *args, **kwargs):
        # Si es una factura nueva o el proveedor está marcado como cancelado
        if not self.id or (hasattr(self, 'proveedor') and self.proveedor.cancelada):
            self.proveedor.cancelada = False
            self.proveedor.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.proveedor.nombre} - {self.estado}"

    class Meta:
        verbose_name = "Factura"
        verbose_name_plural = "Facturas"
        db_table = 'Factura'

########################################################################################################################################

class Venta(models.Model):
    class MedotoPago(models.TextChoices):
        EF = 'EF', 'Efectivo'
        TF = 'TF', 'Transferencia'
    
    class TipoVenta(models.TextChoices):
        Caja = 'Caja', 'Venta en Caja'

    fecha_venta = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de la venta")
    total_venta = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total de la venta", null=True, blank=True)
    dinero_recibido = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Dinero recibido", null=True, blank=True)
    cambio = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cambio", null=True, blank=True)
    metodo_pago = models.CharField(max_length=3, choices=MedotoPago.choices, default=MedotoPago.EF, verbose_name="Metodo de Pago")
    tipo_venta = models.CharField(max_length=6, choices=TipoVenta.choices, default=TipoVenta.Caja, verbose_name="Tipo de Venta")

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name= "venta"
        verbose_name_plural ='ventas'
        db_table ='Venta' 

########################################################################################################################################

class Detalle_venta(models.Model):
    id_venta = models.ForeignKey(Venta, on_delete=models.PROTECT)
    id_producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, null=True, blank=True)
    
    nombre_producto = models.CharField(max_length=100)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)  # Este campo usará el precio_venta cuando se seleccione un producto
    
    cantidad_producto = models.PositiveIntegerField(verbose_name="Cantidad de productos")
    subtotal_venta = models.DecimalField(max_digits=11, decimal_places=2, verbose_name="Subtotal", default="0")
    fecha_detalle = models.DateTimeField(auto_now_add=True, verbose_name="Fecha detalle")

    def __str__(self):
        return str(self.id_producto)

    class Meta:
        verbose_name= "detalle_de_venta"
        verbose_name_plural ='detalles_de_ventas'
        db_table ='Detalle_venta' 

########################################################################################################################################

class Compra(models.Model):
    proveedor = models.CharField(max_length=100, verbose_name="Proveedor")
    fecha_compra = models.DateTimeField(default=datetime.now, verbose_name="Fecha de la compra")
    estado = models.BooleanField(default=True, verbose_name="Estado")

    def __str__(self):
        return f"Compra #{self.id} - {self.proveedor}"

    class Meta:
        verbose_name = "compra"
        verbose_name_plural = "compras"
        db_table = "Compra"

########################################################################################################################################

class Detalle_compra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE)
    producto = models.ForeignKey('Producto', on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    class Meta:
        verbose_name = "detalle_compra"
        verbose_name_plural = "detalles_compras"
        db_table = "Detalle_compra"

########################################################################################################################################

class Verificador(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre