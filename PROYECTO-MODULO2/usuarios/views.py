# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required

from .forms import RegistroUsuarioForm, PerfilUsuarioForm
from .models import PerfilUsuario


def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)

        if form.is_valid():
            usuario = form.save()

            PerfilUsuario.objects.create(
                usuario=usuario,
                telefono=form.cleaned_data.get('telefono'),
                direccion=form.cleaned_data.get('direccion'),
                rol='USUARIO',
                estado='ACTIVO'
            )

            login(request, usuario)

            return redirect('lista_libros')
    else:
        form = RegistroUsuarioForm()

    return render(request, 'usuarios/registro.html', {
        'form': form
    })


def iniciar_sesion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            usuario = authenticate(username=username, password=password)

            if usuario is not None:
                login(request, usuario)
                return redirect('lista_libros')
    else:
        form = AuthenticationForm()

    return render(request, 'usuarios/login.html', {
        'form': form
    })


def cerrar_sesion(request):
    logout(request)
    return redirect('login')


@login_required
def perfil_usuario(request):
    perfil, creado = PerfilUsuario.objects.get_or_create(
        usuario=request.user,
        defaults={
            'rol': 'USUARIO',
            'estado': 'ACTIVO'
        }
    )

    return render(request, 'usuarios/perfil.html', {
        'perfil': perfil
    })