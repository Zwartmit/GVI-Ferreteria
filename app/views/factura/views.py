from django.contrib import messages
import django
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
import os
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.http import JsonResponse
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.db.models import ProtectedError
from app.models import Factura
from app.forms import FacturaForm

@method_decorator(never_cache, name='dispatch')
def lista_factura(request):
    nombre = {
        'titulo': 'Gestión de facturas',
        'facturas': Factura.objects.all()
    }
    return render(request, 'factura/listar.html',nombre)

###### CREAR ######

@method_decorator(never_cache, name='dispatch')
class FacturaCreateView(CreateView):
    model = Factura
    form_class = FacturaForm
    template_name = 'factura/crear.html'

    def form_valid(self, form):
        factura = form.save()
        return JsonResponse({'success': True, 'message': 'Factura registrada correctamente.'})

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors})