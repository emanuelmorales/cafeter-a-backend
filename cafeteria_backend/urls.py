
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def api_root(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Cafeteria API funcionando correctamente',
        'endpoints': {
            'categories': '/api/categories/',
            'products':   '/api/products/',
            'tables':     '/api/tables/',
            'orders':     '/api/orders/',
            'users':      '/api/users/',
            'login':      '/api/auth/login/',
            'admin':      '/admin/',
        }
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', api_root),
]
