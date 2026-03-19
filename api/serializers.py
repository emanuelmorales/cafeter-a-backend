
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, Table, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    role      = serializers.SerializerMethodField()
    firstName = serializers.CharField(source='first_name')
    lastName  = serializers.CharField(source='last_name')
    isActive  = serializers.BooleanField(source='is_active')

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'firstName', 'lastName', 'role', 'isActive']

    def get_role(self, obj):
        if obj.is_superuser or obj.groups.filter(name='Administradores').exists():
            return 'admin'
        if obj.groups.filter(name='Cajeros').exists():
            return 'cashier'
        return 'waiter'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ['id', 'name', 'icon', 'color']


class ProductSerializer(serializers.ModelSerializer):
    categoryId   = serializers.SerializerMethodField()
    categoryName = serializers.SerializerMethodField()
    category_id  = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model  = Product
        fields = [
            'id', 'name', 'description', 'price',
            'image', 'available',
            'categoryId', 'categoryName', 'category_id',
            'created_at', 'updated_at'
        ]

    def get_categoryId(self, obj):
        return obj.category_id

    def get_categoryName(self, obj):
        return obj.category.name if obj.category else ''

    def create(self, validated_data):
        cat_id  = validated_data.pop('category_id', None)
        product = Product(**validated_data)
        if cat_id:
            product.category_id = cat_id
        product.save()
        return product

    def update(self, instance, validated_data):
        cat_id = validated_data.pop('category_id', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if cat_id is not None:
            instance.category_id = cat_id
        instance.save()
        return instance


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Table
        fields = ['id', 'number', 'seats', 'status']


class OrderItemReadSerializer(serializers.ModelSerializer):
    productId    = serializers.SerializerMethodField()
    productName  = serializers.SerializerMethodField()
    productImage = serializers.SerializerMethodField()
    unitPrice    = serializers.SerializerMethodField()
    subtotal     = serializers.SerializerMethodField()

    class Meta:
        model  = OrderItem
        fields = ['id', 'productId', 'productName', 'productImage',
                  'quantity', 'unitPrice', 'subtotal', 'price', 'notes']

    def get_productId(self, obj):
        return obj.product.id if obj.product else None

    def get_productName(self, obj):
        return obj.product.name if obj.product else ''

    def get_productImage(self, obj):
        return obj.product.image if obj.product else ''

    def get_unitPrice(self, obj):
        if obj.product:
            return float(obj.product.price)
        return float(obj.price) / obj.quantity if obj.quantity else 0

    def get_subtotal(self, obj):
        if obj.product:
            return round(float(obj.product.price) * obj.quantity, 2)
        return float(obj.price)


class OrderItemWriteSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=False, allow_null=True)
    product    = serializers.IntegerField(required=False, allow_null=True)
    quantity   = serializers.IntegerField(default=1)
    notes      = serializers.CharField(default='', allow_blank=True)

    def validate(self, data):
        pid = data.get('product_id') or data.get('product')
        if not pid:
            raise serializers.ValidationError('Se requiere product_id o product')
        data['resolved_product_id'] = pid
        return data


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemReadSerializer(many=True, read_only=True)

    class Meta:
        model  = Order
        fields = [
            'id', 'items', 'table_number', 'customer_name',
            'status', 'type', 'total', 'payment_method',
            'notes', 'created_at', 'updated_at'
        ]


class OrderCreateSerializer(serializers.Serializer):
    items         = OrderItemWriteSerializer(many=True)
    table_number  = serializers.IntegerField(required=False, allow_null=True)
    customer_name = serializers.CharField(default='', allow_blank=True)
    type          = serializers.CharField(default='dine-in')
    notes         = serializers.CharField(default='', allow_blank=True)

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order      = Order.objects.create(**validated_data)
        total      = 0
        for item_data in items_data:
            pid = item_data['resolved_product_id']
            qty = item_data.get('quantity', 1)
            try:
                product = Product.objects.get(id=pid)
                price   = float(product.price) * qty
                total  += price
                OrderItem.objects.create(
                    order=order, product=product,
                    quantity=qty, price=price,
                    notes=item_data.get('notes', '')
                )
            except Product.DoesNotExist:
                pass
        order.total = round(total, 2)
        order.save()
        return order
