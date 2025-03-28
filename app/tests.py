from django.test import TestCase
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))
from asuan.wsgi import *
from app.models import *

# LISTAR
# consulta = Cliente.objects.all()
# print(consulta)

# -----------------------------------------
# # INSERTAR
# categoria = Categoria(
#     categoria="Almuerzos"
# )
# categoria.save()
# consulta = Categoria.objects.all()
# print(consulta)

# -----------------------------------------

# EDITAR
# cliente = Cliente.objects.get(id=1)
# print(cliente.nombre)
# cliente.nombre='Juan'
# cliente.tipo_documento='TI'
# cliente.numero_documento= 2131412
# cliente.email='juanisimo@gmail.com'
# cliente.telefono=23124122
# cliente.save()
# print(cliente.nombre)

# -----------------------------------------

# ELIMINAR
# cliente = Cliente.objects.get(id=2)
# cliente.delete()
# consulta = Cliente.objects.all()
# print(consulta)

# -----------------------------------------