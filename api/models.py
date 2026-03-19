
from django.db import models


class Category(models.Model):
    name  = models.CharField(max_length=100, verbose_name='Nombre')
    icon  = models.CharField(max_length=10, default='', verbose_name='Icono')
    color = models.CharField(max_length=80, default='bg-amber-100 text-amber-800', verbose_name='Color')

    class Meta:
        verbose_name        = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    name        = models.CharField(max_length=200, verbose_name='Nombre')
    description = models.TextField(blank=True, default='', verbose_name='Descripcion')
    price       = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    image       = models.CharField(max_length=20, default='', blank=True, verbose_name='Emoji')
    category    = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='products', verbose_name='Categoria'
    )
    available   = models.BooleanField(default=True, verbose_name='Disponible')
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Producto'
        verbose_name_plural = 'Productos'
        ordering            = ['name']

    def __str__(self):
        return self.name


class Table(models.Model):
    STATUS_CHOICES = [
        ('available', 'Disponible'),
        ('occupied',  'Ocupada'),
        ('reserved',  'Reservada'),
        ('cleaning',  'Limpieza'),
    ]
    number = models.IntegerField(unique=True, verbose_name='Numero de Mesa')
    seats  = models.IntegerField(default=4, verbose_name='Asientos')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='available', verbose_name='Estado'
    )

    class Meta:
        verbose_name        = 'Mesa'
        verbose_name_plural = 'Mesas'
        ordering            = ['number']

    def __str__(self):
        return f'Mesa {self.number}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pendiente'),
        ('preparing', 'Preparando'),
        ('ready',     'Listo'),
        ('delivered', 'Entregado'),
        ('paid',      'Cobrado'),
        ('cancelled', 'Cancelado'),
    ]
    TYPE_CHOICES = [
        ('dine-in',  'En Mesa'),
        ('takeaway', 'Para Llevar'),
    ]
    PAYMENT_CHOICES = [
        ('cash',     'Efectivo'),
        ('transfer', 'Transferencia'),
        ('credit',   'Credito'),
        ('debit',    'Debito'),
        ('qr',       'QR'),
        ('other',    'Otro'),
    ]

    table_number    = models.IntegerField(null=True, blank=True, verbose_name='Numero de Mesa')
    customer_name   = models.CharField(max_length=200, blank=True, default='', verbose_name='Cliente')
    status          = models.CharField(
        max_length=20, choices=STATUS_CHOICES,
        default='pending', verbose_name='Estado'
    )
    type            = models.CharField(
        max_length=20, choices=TYPE_CHOICES,
        default='dine-in', verbose_name='Tipo'
    )
    total           = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Total')
    payment_method  = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES,
        blank=True, default='', verbose_name='Metodo de Pago'
    )
    notes           = models.TextField(blank=True, default='', verbose_name='Notas')
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering            = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.id} - {self.customer_name}'


class OrderItem(models.Model):
    order    = models.ForeignKey(
        Order, on_delete=models.CASCADE,
        related_name='items', verbose_name='Pedido'
    )
    product  = models.ForeignKey(
        Product, on_delete=models.SET_NULL,
        null=True, verbose_name='Producto'
    )
    quantity = models.IntegerField(default=1, verbose_name='Cantidad')
    price    = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='Precio unitario')
    notes    = models.TextField(blank=True, default='', verbose_name='Notas')

    class Meta:
        verbose_name        = 'Item de Pedido'
        verbose_name_plural = 'Items de Pedido'

    def __str__(self):
        return f'{self.quantity}x {self.product}'
