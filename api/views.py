
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from .models import Category, Product, Table, Order
from .serializers import (
    CategorySerializer, ProductSerializer, TableSerializer,
    OrderSerializer, OrderCreateSerializer, UserSerializer,
)


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo no permitido'}, status=405)
    try:
        body = json.loads(request.body)
    except Exception:
        return JsonResponse({'error': 'JSON invalido'}, status=400)

    username = body.get('username', '').strip()
    password = body.get('password', '').strip()

    if not username or not password:
        return JsonResponse({'error': 'Usuario y contrasena son requeridos'}, status=400)

    user = authenticate(request, username=username, password=password)
    if not user:
        return JsonResponse({'error': 'Usuario o contrasena incorrectos'}, status=401)
    if not user.is_active:
        return JsonResponse({'error': 'Esta cuenta esta desactivada'}, status=403)

    # Crear sesión de Django
    login(request, user)

    if user.is_superuser or user.groups.filter(name='Administradores').exists():
        role = 'admin'
    elif user.groups.filter(name='Cajeros').exists():
        role = 'cashier'
    else:
        role = 'waiter'

    full_name = f'{user.first_name} {user.last_name}'.strip() or user.username

    # Crear respuesta JSON con la cookie de sesión
    response_data = {
        'id':        user.id,
        'username':  user.username,
        'firstName': user.first_name,
        'lastName':  user.last_name,
        'fullName':  full_name,
        'email':     user.email,
        'role':      role,
        'isStaff':   user.is_staff,
        'sessionId': request.session.session_key,
    }
    
    # Crear respuesta con cookies
    response = JsonResponse(response_data)
    
    # Forzar el guardado de la sesión y establecer la cookie
    request.session.save()
    response.set_cookie(
        'sessionid',
        request.session.session_key,
        max_age=86400,  # 24 horas
        httponly=False,
        samesite='Lax',
        path='/',
    )
    
    return response


@csrf_exempt
def logout_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Metodo no permitido'}, status=405)
    
    logout(request)
    
    response = JsonResponse({'success': True})
    response.delete_cookie('sessionid', path='/')
    
    return response


@csrf_exempt
def check_session_view(request):
    """Verifica si la sesión está activa y devuelve el usuario"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Metodo no permitido'}, status=405)
    
    # Debug: imprimir información de la sesión
    print(f"Session key: {request.session.session_key}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"Cookies: {request.COOKIES}")
    
    if request.user.is_authenticated:
        user = request.user
        if user.is_superuser or user.groups.filter(name='Administradores').exists():
            role = 'admin'
        elif user.groups.filter(name='Cajeros').exists():
            role = 'cashier'
        else:
            role = 'waiter'
        
        full_name = f'{user.first_name} {user.last_name}'.strip() or user.username
        
        return JsonResponse({
            'authenticated': True,
            'id':        user.id,
            'username':  user.username,
            'firstName': user.first_name,
            'lastName':  user.last_name,
            'fullName':  full_name,
            'email':     user.email,
            'role':      role,
            'isStaff':   user.is_staff,
        })
    
    return JsonResponse({'authenticated': False})


class UserViewSet(viewsets.ViewSet):

    def list(self, request):
        users = User.objects.all().order_by('username')
        data  = []
        for u in users:
            if u.is_superuser or u.groups.filter(name='Administradores').exists():
                role = 'admin'
            elif u.groups.filter(name='Cajeros').exists():
                role = 'cashier'
            else:
                role = 'waiter'
            data.append({
                'id':        u.id,
                'username':  u.username,
                'email':     u.email,
                'firstName': u.first_name,
                'lastName':  u.last_name,
                'role':      role,
                'isActive':  u.is_active,
            })
        return Response(data)

    def create(self, request):
        d        = request.data
        username = d.get('username', '').strip()
        password = d.get('password', '').strip()
        if not username or not password:
            return Response({'error': 'username y password son requeridos'}, status=400)
        if User.objects.filter(username=username).exists():
            return Response({'error': 'El usuario ya existe'}, status=400)

        u = User.objects.create_user(
            username   = username,
            password   = password,
            email      = d.get('email', ''),
            first_name = d.get('firstName', ''),
            last_name  = d.get('lastName',  ''),
        )
        role = d.get('role', 'waiter')
        if role == 'admin':
            u.is_staff = True
            u.save()
        group_map  = {'admin': 'Administradores', 'cashier': 'Cajeros', 'waiter': 'Meseros'}
        group_name = group_map.get(role)
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            u.groups.set([group])

        return Response(UserSerializer(u).data, status=201)

    def update(self, request, pk=None):
        try:
            u = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)

        d            = request.data
        u.email      = d.get('email',     u.email)
        u.first_name = d.get('firstName', u.first_name)
        u.last_name  = d.get('lastName',  u.last_name)
        u.is_active  = d.get('isActive',  u.is_active)

        new_username = d.get('username', u.username)
        if new_username != u.username:
            if User.objects.filter(username=new_username).exists():
                return Response({'error': 'El nombre de usuario ya existe'}, status=400)
            u.username = new_username

        if d.get('password') and len(d['password']) >= 6:
            u.set_password(d['password'])

        role = d.get('role')
        if role:
            group_map  = {'admin': 'Administradores', 'cashier': 'Cajeros', 'waiter': 'Meseros'}
            group_name = group_map.get(role)
            u.is_staff = (role == 'admin')
            if group_name:
                group, _ = Group.objects.get_or_create(name=group_name)
                u.groups.set([group])

        u.save()
        return Response(UserSerializer(u).data)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        try:
            u = User.objects.get(pk=pk)
            if u.is_superuser:
                return Response({'error': 'No se puede eliminar al superusuario'}, status=400)
            u.delete()
            return Response(status=204)
        except User.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=404)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset         = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset         = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        qs        = super().get_queryset()
        category  = self.request.query_params.get('category')
        available = self.request.query_params.get('available')
        if category:
            qs = qs.filter(category_id=category)
        if available is not None:
            qs = qs.filter(available=available.lower() == 'true')
        return qs

    def _normalize_data(self, data):
        d = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'category' in d and 'category_id' not in d:
            d['category_id'] = d['category']
        if 'categoryId' in d and 'category_id' not in d:
            d['category_id'] = d['categoryId']
        return d

    def create(self, request, *args, **kwargs):
        data       = self._normalize_data(request.data)
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        data       = self._normalize_data(request.data)
        partial    = kwargs.pop('partial', False)
        instance   = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['post', 'patch'])
    def toggle_availability(self, request, pk=None):
        product           = self.get_object()
        product.available = not product.available
        product.save()
        return Response(ProductSerializer(product).data)


class TableViewSet(viewsets.ModelViewSet):
    queryset         = Table.objects.all()
    serializer_class = TableSerializer

    @action(detail=True, methods=['post', 'patch'])
    def update_status(self, request, pk=None):
        table      = self.get_object()
        new_status = request.data.get('status')
        valid      = [s[0] for s in Table.STATUS_CHOICES]
        if new_status not in valid:
            return Response({'error': f'Estado invalido. Opciones: {valid}'}, status=400)
        table.status = new_status
        table.save()
        return Response(TableSerializer(table).data)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product').all()

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)

        # Normalizar tipo de pedido
        t        = data.get('type') or data.get('order_type') or 'dine-in'
        type_map = {
            'dine_in':     'dine-in',
            'dinein':      'dine-in',
            'en_mesa':     'dine-in',
            'en-mesa':     'dine-in',
            'takeout':     'takeaway',
            'take_away':   'takeaway',
            'take-away':   'takeaway',
            'para_llevar': 'takeaway',
        }
        data['type'] = type_map.get(t, t)

        # Normalizar table_number
        tn = data.get('table_number') or data.get('table') or data.get('tableNumber')
        try:
            data['table_number'] = int(tn) if tn else None
        except (ValueError, TypeError):
            data['table_number'] = None

        # Normalizar customer_name
        data['customer_name'] = (
            data.get('customer_name') or
            data.get('customerName') or ''
        )

        # Normalizar items
        items = data.get('items', [])
        normalized_items = []
        for item in items:
            pid = (
                item.get('product_id') or
                item.get('productId') or
                item.get('product')
            )
            normalized_items.append({
                'product_id': pid,
                'quantity':   item.get('quantity', 1),
                'notes':      item.get('notes', ''),
            })
        data['items'] = normalized_items

        serializer = OrderCreateSerializer(data=data)
        if serializer.is_valid():
            order = serializer.save()

            # Actualizar estado de la mesa automaticamente a 'occupied'
            if order.type == 'dine-in' and order.table_number:
                try:
                    table        = Table.objects.get(number=order.table_number)
                    table.status = 'occupied'
                    table.save()
                except Table.DoesNotExist:
                    pass

            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post', 'patch'])
    def update_status(self, request, pk=None):
        order      = self.get_object()
        new_status = request.data.get('status')
        valid      = [s[0] for s in Order.STATUS_CHOICES]

        if new_status not in valid:
            return Response({'error': f'Estado invalido. Opciones: {valid}'}, status=400)

        old_status          = order.status
        order.status        = new_status
        payment_method      = request.data.get('payment_method', '')
        if payment_method:
            order.payment_method = payment_method
        order.save()

        # Logica de mesas segun el nuevo estado
        if order.type == 'dine-in' and order.table_number:
            try:
                table = Table.objects.get(number=order.table_number)

                if new_status == 'paid':
                    # Al cobrar -> mesa pasa a Limpieza
                    table.status = 'cleaning'
                    table.save()

                elif new_status == 'cancelled' and old_status not in ('paid', 'cancelled'):
                    # Al cancelar -> verificar si hay otros pedidos activos en la mesa
                    other_active = Order.objects.filter(
                        table_number=order.table_number,
                        type='dine-in'
                    ).exclude(id=order.id).exclude(
                        status__in=['delivered', 'paid', 'cancelled']
                    ).exists()
                    if not other_active:
                        table.status = 'available'
                        table.save()

            except Table.DoesNotExist:
                pass

        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        today        = timezone.now().date()
        today_orders = Order.objects.filter(created_at__date=today)
        paid_orders  = today_orders.filter(status__in=['paid', 'delivered'])
        total_sales  = sum(float(o.total) for o in paid_orders)
        avg_ticket   = total_sales / paid_orders.count() if paid_orders.count() > 0 else 0
        return Response({
            'today_orders': today_orders.count(),
            'today_sales':  round(total_sales, 2),
            'avg_ticket':   round(avg_ticket, 2),
            'pending':      today_orders.filter(status='pending').count(),
            'preparing':    today_orders.filter(status='preparing').count(),
            'ready':        today_orders.filter(status='ready').count(),
            'delivered':    today_orders.filter(status='delivered').count(),
            'paid':         today_orders.filter(status='paid').count(),
            'cancelled':    today_orders.filter(status='cancelled').count(),
        })
