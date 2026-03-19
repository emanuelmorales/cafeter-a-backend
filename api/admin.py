
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Category, Product, Table, Order, OrderItem


class CustomUserAdmin(UserAdmin):
    list_display  = ['username', 'first_name', 'last_name', 'email', 'get_role', 'is_active']
    list_filter   = ['is_active', 'groups', 'is_staff']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering      = ['username']

    def get_role(self, obj):
        if obj.is_superuser:
            return 'Superusuario'
        groups = obj.groups.values_list('name', flat=True)
        if 'Administradores' in groups: return 'Administrador'
        if 'Cajeros'         in groups: return 'Cajero'
        if 'Meseros'         in groups: return 'Mesero'
        return 'Sin rol'
    get_role.short_description = 'Rol'


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ['id', 'icon', 'name']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display  = ['id', 'image', 'name', 'category', 'price', 'available']
    list_filter   = ['category', 'available']
    list_editable = ['price', 'available']
    search_fields = ['name', 'description']


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display  = ['id', 'number', 'seats', 'status']
    list_editable = ['status']
    list_filter   = ['status']
    ordering      = ['number']


class OrderItemInline(admin.TabularInline):
    model           = OrderItem
    extra           = 0
    readonly_fields = ['price']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display    = ['id', 'customer_name', 'table_number', 'status', 'type', 'total', 'created_at']
    list_filter     = ['status', 'type', 'created_at']
    search_fields   = ['customer_name']
    inlines         = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']
    ordering        = ['-created_at']
