from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

from .models import PerfilUsuario


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        # Si es superusuario o staff de Django, lo dejamos pasar directo
        if request.user.is_superuser or request.user.is_staff:
            return view_func(request, *args, **kwargs)

        # Si no es superusuario/staff, revisamos su PerfilUsuario
        try:
            perfil = request.user.perfilusuario
        except PerfilUsuario.DoesNotExist:
            messages.error(request, 'Tu usuario no tiene perfil asignado.')
            return redirect('lista_libros')

        if perfil.rol != 'ADMIN' and perfil.rol != 'Administrador':
            messages.error(request, 'No tienes permiso para acceder a esta sección.')
            return redirect('lista_libros')

        return view_func(request, *args, **kwargs)

    return wrapper