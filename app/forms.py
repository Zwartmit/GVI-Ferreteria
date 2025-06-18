from dataclasses import fields
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django_select2.forms import Select2Widget
from django import forms
from django.forms import *
from app.models import *
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm, TextInput, Select, NumberInput, EmailInput, PasswordInput
from app.models import Administrador
from app.models import Operador

class CategoriaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categoria"].widget.attrs["autofocus"] = True

    class Meta:
        model = Categoria
        fields = "__all__"
        widgets = {
            "categoria": TextInput(
                attrs={
                    "placeholder": "Categoría",
                }
            ),
            "estado": Select(
                choices=[(True, "Activo"), (False, "Inactivo")],
                attrs={
                    "placeholder": "Estado de la categoría",
                }
            )
        }

class PresentacionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["presentacion"].widget.attrs["autofocus"] = True

    class Meta:
        model = Presentacion
        fields = "__all__"
        widgets = {
            "presentacion": TextInput(
                attrs={
                    "placeholder": "Presentación",
                }
            ),
            "estado": Select(
                choices=[(True, "Activo"), (False, "Inactivo")],
                attrs={
                    "placeholder": "Estado de la presentación",
                }
            )
        }

class ProductoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["id_categoria"].queryset = Categoria.objects.filter(estado=True)
        self.fields["id_presentacion"].queryset = Presentacion.objects.filter(estado=True)
        
        # Configuramos el campo de precio_venta como de solo lectura ya que se calcula automáticamente
        if 'precio_venta' in self.fields:
            self.fields['precio_venta'].widget.attrs['readonly'] = True

    class Meta:
        model = Producto
        fields = ["producto", "cantidad", "stock_minimo", "valor", "porcentaje_ganancia", "precio_venta", "NumVerificador", "estado", "id_categoria", "id_presentacion", "proveedor"]
        widgets = {
            "producto": TextInput(
                attrs={
                    "placeholder": "Nombre del producto",
                }
            ),
            "cantidad": NumberInput(
                attrs={
                    "placeholder": "Cantidad a registrar",
                }
            ),
            "stock_minimo": NumberInput(
                attrs={
                    "placeholder": "Stock mínimo para reabastecimiento",
                    "min": "1"
                }
            ),
            "valor": NumberInput(
                attrs={
                    "placeholder": "Valor del producto",
                    "class": "form-control valor-producto",
                    "onchange": "calcularPrecioVenta()"
                }
            ),
            "porcentaje_ganancia": NumberInput(
                attrs={
                    "placeholder": "Porcentaje de ganancia",
                    "class": "form-control porcentaje-ganancia",
                    "onchange": "calcularPrecioVenta()",
                    "min": "0",
                    "step": "0.01"
                }
            ),
            "precio_venta": NumberInput(
                attrs={
                    "placeholder": "Precio de venta (calculado)",
                    "class": "form-control precio-venta",
                    "readonly": "readonly"
                }
            ),
            'NumVerificador': NumberInput(
                attrs={
                    'placeholder': 'Número para el verificador',
                    'class': 'form-control',  
                }
            ),
            "estado": Select(
                choices=[(True, "Activo"), (False, "Inactivo")],
                attrs={
                    "placeholder": "Estado del producto",
                }
            ),
            "proveedor": Select(
                attrs={
                    "placeholder": "Seleccionar proveedor (opcional)",
                    "class": "form-control"
                }
            )
        }

class AdministradorForm(ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        widget=TextInput(attrs={"placeholder": "Nombre de usuario"})
    )
    email = forms.EmailField(
        label="Email",
        max_length=150,
        widget=EmailInput(attrs={"placeholder": "Correo electrónico"})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=PasswordInput(attrs={"placeholder": "Contraseña"}),
        required=False  
    )
    conf_password = forms.CharField(
        label="Confirmar contraseña",
        widget=PasswordInput(attrs={"placeholder": "Confirmar contraseña"}),
        required=False 
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email
        self.fields["username"].widget.attrs["autofocus"] = True

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("conf_password")
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        numero_documento = cleaned_data.get('numero_documento')
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("conf_password")

        if not password1 or not password2:
            raise ValidationError('La contraseña es obligatoria.')

        if password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')

        if len(password1) < 6 or not any(char.isupper() for char in password1) or not any(char.isdigit() for char in password1):
            raise ValidationError('La contraseña debe tener al menos 6 caracteres, incluir una letra mayúscula y un número.')
        
        if User.objects.filter(username=username).exclude(pk=self.instance.user.pk if self.instance and self.instance.pk else None).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk if self.instance and self.instance.pk else None).exists():
            raise ValidationError("Este correo electrónico ya está en uso.")
        
        if Administrador.objects.filter(numero_documento=numero_documento).exclude(pk=self.instance.pk if self.instance and self.instance.pk else None).exists():
            raise ValidationError("Este número de documento ya está registrado.")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if self.instance.pk:
            user = self.instance.user
            if username and user.username != username:
                user.username = username
            if email and user.email != email:
                user.email = email
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
        
        administrador = super().save(commit=False)
        administrador.user = user
        if commit:
            administrador.save()
        return administrador

    class Meta:
        model = Administrador
        fields = ["username", "email", "nombre", "tipo_documento", "numero_documento", "telefono", "password", "conf_password"]
        widgets = {
            "nombre": TextInput(attrs={"placeholder": "Nombre del administrador"}),
            "tipo_documento": Select(attrs={"placeholder": "Tipo de documento"}),
            "numero_documento": NumberInput(attrs={"min": 8, "placeholder": "Número de documento"}),
            "telefono": NumberInput(attrs={"min": 1, "placeholder": "Teléfono"}),
            "password": PasswordInput(attrs={"min": 1, "placeholder": "Contraseña"}),
            "conf_password": PasswordInput(attrs={"min": 1, "placeholder": "Confirme su contraseña"})
        }

class OperadorForm(ModelForm):
    username = forms.CharField(
        label="Nombre de usuario",
        max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Nombre de usuario"})
    )
    email = forms.EmailField(
        label="Email",
        max_length=150,
        widget=forms.EmailInput(attrs={"placeholder": "Correo electrónico"})
    )
    password = forms.CharField(
        label="Contraseña",
        widget=PasswordInput(attrs={"placeholder": "Contraseña"}),
        required=False
    )
    conf_password = forms.CharField(
        label="Confirmar contraseña",
        widget=PasswordInput(attrs={"placeholder": "Confirmar contraseña"}),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs["autofocus"] = True
        
        if self.instance and self.instance.pk and hasattr(self.instance, 'user'):
            self.fields['username'].initial = self.instance.user.username
            self.fields['email'].initial = self.instance.user.email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("conf_password")
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        numero_documento = cleaned_data.get('numero_documento')
        password1 = cleaned_data.get("password")
        password2 = cleaned_data.get("conf_password")

        if not password1 or not password2:
            raise ValidationError('La contraseña es obligatoria.')

        if password1 != password2:
            raise ValidationError('Las contraseñas no coinciden.')

        if len(password1) < 6 or not any(char.isupper() for char in password1) or not any(char.isdigit() for char in password1):
            raise ValidationError('La contraseña debe tener al menos 6 caracteres, incluir una letra mayúscula y un número.')
        
        if User.objects.filter(username=username).exclude(pk=self.instance.user.pk if self.instance and self.instance.pk else None).exists():
            raise ValidationError("Este nombre de usuario ya está en uso.")
        
        if User.objects.filter(email=email).exclude(pk=self.instance.user.pk if self.instance and self.instance.pk else None).exists():
            raise ValidationError("Este correo electrónico ya está en uso.")
        
        if Administrador.objects.filter(numero_documento=numero_documento).exclude(pk=self.instance.pk if self.instance and self.instance.pk else None).exists():
            raise ValidationError("Este número de documento ya está registrado.")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden")
        
        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if self.instance.pk and hasattr(self.instance, 'user'):
            user = self.instance.user
            user.username = username
            user.email = email
            if password:
                user.set_password(password)
            user.save()
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password or None  
            )
            self.instance.user = user 

        operador = super().save(commit=False)
        operador.contrasena = password if password else operador.contrasena
        operador.conf_contrasena = cleaned_data.get('conf_password') if password else operador.conf_contrasena
        if commit:
            operador.save()
        return operador

    class Meta:
        model = Operador
        fields = ["username", "email", "nombre", "tipo_documento", "numero_documento", "telefono", "password", "conf_password"]
        widgets = {
            "nombre": TextInput(attrs={"placeholder": "Nombre del operador"}),
            "tipo_documento": Select(attrs={"placeholder": "Tipo de documento"}),
            "numero_documento": NumberInput(attrs={"min": 8, "placeholder": "Número de documento"}),
            "telefono": NumberInput(attrs={"min": 1, "placeholder": "Teléfono"}),
            "password": PasswordInput(attrs={"min": 1, "placeholder": "Contraseña"}),
            "conf_password": PasswordInput(attrs={"min": 1, "placeholder": "Confirme su contraseña"})
        }

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ('nombre', 'telefono')

    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        if Proveedor.objects.filter(nombre__iexact=nombre).exists():
            raise forms.ValidationError('Ya existe un proveedor con este nombre.')
        return nombre

class FacturaForm(ModelForm):
    def clean_fecha_vencimiento(self):
        fecha = self.cleaned_data.get('fecha_vencimiento')
        from datetime import date
        if fecha and fecha <= date.today():
            raise forms.ValidationError('La fecha de vencimiento no puede ser anterior a la fecha actual.')
        return fecha

    class Meta:
        model = Factura
        fields = "__all__"
        widgets = {
            "fecha_vencimiento": DateInput(attrs={"type": "date"}),
        }

class VentaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Venta
        fields = "__all__"
        exclude = ['fecha_venta', 'tipo_venta']
        widgets = { 
            "metodo_pago": Select(
                attrs={
                    "placeholder": "Metodo de pago",
                }
            ),
        }

class DetalleVentaForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cantidad_producto"].widget.attrs["autofocus"] = True
        self.fields['id_producto'].queryset = Producto.objects.all()

    class Meta:
        model = Detalle_venta
        fields = "__all__"
        # exclude = ['fecha_detalle']
        widgets = {
            "cantidad_producto": NumberInput(
                attrs={
                    "placeholder": "Cantidad"
                }
            ),
            "id_producto": Select2Widget(
                attrs={
                    "class": "product-select"
                }
            ),
        }
        
class ReporteForm(forms.Form):
    FORMATO_CHOICES = [
        ('excel', 'Excel'),
        ('pdf', 'PDF'),
    ]
    formato = forms.ChoiceField(choices=FORMATO_CHOICES, label='Formato del Reporte')
    
    TIPO_REPORTE_CHOICES = [
        ('producto', 'Reporte de Productos'),
        ('administrador', 'Reporte de Administradores'),
        ('operador', 'Reporte de Operadores'),
        ('venta', 'Reporte de Ventas del Día'),
        ('ganancias_diarias', 'Reporte de Ganancias Diarias'),
        ('ganancias_mensuales', 'Reporte de Ganancias Mensuales'),
    ]
    tipo_reporte = forms.ChoiceField(choices=TIPO_REPORTE_CHOICES, label='Tipo de Reporte')
    
    fecha_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de Inicio')
    fecha_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label='Fecha de Fin')