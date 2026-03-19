
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products',   views.ProductViewSet,  basename='product')
router.register(r'tables',     views.TableViewSet,    basename='table')
router.register(r'orders',     views.OrderViewSet,    basename='order')
router.register(r'users',      views.UserViewSet,     basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/check/', views.check_session_view, name='check_session'),
]
