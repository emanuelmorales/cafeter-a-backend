import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cafeteria_backend.settings')
django.setup()
from django.contrib.auth.models import User, Group
if not User.objects.filter(username='admin').exists():
    u = User.objects.create_superuser('admin', 'admin@cafeteria.com', 'admin1234')
    g, _ = Group.objects.get_or_create(name='Administradores')
    u.groups.set([g])
    print('Superusuario creado: admin / admin1234')
else:
    print('El usuario admin ya existe')
