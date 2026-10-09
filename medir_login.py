import time
from django.db import connection
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

USUARIO = 'victor'          # un usuario que exista en la base de Supabase
CLAVE = '123456'      # su contraseña real

def medir(nombre, f):
    t = time.perf_counter()
    resultado = f()
    print(f'{nombre}: {time.perf_counter() - t:.3f} s')
    return resultado

def consulta():
    with connection.cursor() as c:
        c.execute('SELECT 1')

medir('1) SELECT 1 (abre la conexión)', consulta)
medir('2) SELECT 1 (reutiliza)', consulta)
medir('3) SELECT 1 (reutiliza)', consulta)

u = medir('4) buscar usuario', lambda: User.objects.get(username=USUARIO))
medir('5) check_password', lambda: u.check_password(CLAVE))
medir('6) authenticate completo', lambda: authenticate(username=USUARIO, password=CLAVE))

connection.close()