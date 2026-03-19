import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeteria_backend.settings')
django.setup()
from api.models import Category, Product, Table
from django.contrib.auth.models import Group

print('Limpiando datos anteriores...')
Product.objects.all().delete()
Category.objects.all().delete()
Table.objects.all().delete()

print('Creando categorias...')
cats_data = [
    ('Cafe',           'bg-amber-100 text-amber-800'),
    ('Te e Infusiones','bg-green-100 text-green-800'),
    ('Bebidas Frias',  'bg-blue-100 text-blue-800'),
    ('Postres',        'bg-pink-100 text-pink-800'),
    ('Sandwiches',     'bg-yellow-100 text-yellow-800'),
    ('Desayunos',      'bg-orange-100 text-orange-800'),
]
cat_objs = {}
for name, color in cats_data:
    obj = Category.objects.create(name=name, color=color)
    cat_objs[name] = obj

print('Creando productos...')
products = [
    ('Espresso',             'Cafe espresso clasico puro',            2.50, 'Cafe'),
    ('Americano',            'Espresso con agua caliente',            3.00, 'Cafe'),
    ('Cappuccino',           'Espresso con leche espumada',           3.50, 'Cafe'),
    ('Latte',                'Cafe con leche vaporizada',             4.00, 'Cafe'),
    ('Mocaccino',            'Espresso con chocolate',                4.50, 'Cafe'),
    ('Macchiato',            'Espresso con toque de leche',           3.00, 'Cafe'),
    ('Te Verde',             'Te verde natural antioxidante',         2.50, 'Te e Infusiones'),
    ('Te Negro',             'Te negro clasico energizante',          2.50, 'Te e Infusiones'),
    ('Manzanilla',           'Infusion relajante de manzanilla',      2.00, 'Te e Infusiones'),
    ('Jugo de Naranja',      'Jugo natural de naranja fresco',        3.00, 'Bebidas Frias'),
    ('Limonada',             'Limonada natural refrescante',          3.00, 'Bebidas Frias'),
    ('Smoothie de Fresa',    'Smoothie de fresa y yogur',             4.50, 'Bebidas Frias'),
    ('Agua Mineral',         'Agua mineral con o sin gas',            1.50, 'Bebidas Frias'),
    ('Frappe de Cafe',       'Cafe frio cremoso con chantilly',       5.00, 'Bebidas Frias'),
    ('Cheesecake',           'Cheesecake de fresa con base galleta',  4.00, 'Postres'),
    ('Brownie',              'Brownie de chocolate caliente',         3.50, 'Postres'),
    ('Croissant',            'Croissant de mantequilla hojaldrado',   2.50, 'Postres'),
    ('Muffin de Arandanos',  'Muffin artesanal de arandanos',         2.50, 'Postres'),
    ('Dona Glaseada',        'Dona clasica con glaseado de colores',  2.00, 'Postres'),
    ('Sandwich de Pollo',    'Sandwich de pollo a la plancha',        5.50, 'Sandwiches'),
    ('Sandwich Vegetariano', 'Sandwich con vegetales frescos',        4.50, 'Sandwiches'),
    ('Club Sandwich',        'Club sandwich clasico triple',          6.00, 'Sandwiches'),
    ('Wrap de Pollo',        'Wrap con pollo y verduras',             5.00, 'Sandwiches'),
    ('Desayuno Completo',    'Huevos revueltos, pan tostado y jugo',  8.00, 'Desayunos'),
    ('Tostadas Mantequilla', 'Pan tostado con mantequilla y mermelada', 3.00, 'Desayunos'),
    ('Granola con Yogur',    'Granola artesanal con yogur y miel',    4.50, 'Desayunos'),
    ('Tostadas de Aguacate', 'Pan tostado con aguacate y huevo',      5.50, 'Desayunos'),
    ('Panqueques',           'Panqueques con miel de maple',          5.00, 'Desayunos'),
]
for name, desc, price, cat_name in products:
    cat = cat_objs.get(cat_name)
    if cat:
        Product.objects.create(name=name, description=desc, price=price, category=cat, available=True)

print('Creando mesas...')
for i in range(1, 13):
    seats = 2 if i <= 3 else (6 if i >= 11 else 4)
    Table.objects.create(number=i, seats=seats, status='available')

print('Creando grupos de usuarios...')
for g in ['Administradores', 'Cajeros', 'Meseros']:
    Group.objects.get_or_create(name=g)

nc = str(Category.objects.count())
np = str(Product.objects.count())
nt = str(Table.objects.count())
print('')
print('Datos cargados correctamente:')
print('  ' + nc + ' categorias')
print('  ' + np + ' productos')
print('  ' + nt + ' mesas')
print('  3 grupos: Administradores, Cajeros, Meseros')
print('Listo!')
