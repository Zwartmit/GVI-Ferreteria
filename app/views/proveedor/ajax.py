from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from app.models import Proveedor

@require_POST
@csrf_exempt  # Si usas CSRF en AJAX, puedes quitar esto y manejar el token en JS
def marcar_cancelada(request):
    id = request.POST.get('id')
    proveedor = Proveedor.objects.get(id=id)
    proveedor.cancelada = True
    proveedor.save()
    return JsonResponse({'success': True})
