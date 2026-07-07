from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import MovimientoForm
from .models import Billetera, Movimiento


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect('index')
    else:
        form = AuthenticationForm()

    return render(request, 'core/login.html', {'form': form})


@login_required(login_url='login')
def index(request):
    billetera, _ = Billetera.objects.get_or_create(usuario=request.user)
    movimientos = Movimiento.objects.filter(billetera=billetera)
    saldo = billetera.consultarSaldo()

    if request.method == 'POST':
        form = MovimientoForm(request.POST)
        if form.is_valid():
            monto = form.cleaned_data['monto']
            tipo = request.POST.get('tipo')

            if tipo == Movimiento.RETIRO and monto > saldo:
                messages.error(request, 'No tienes saldo suficiente para retirar esa cantidad.')
            elif tipo == Movimiento.DEPOSITO:
                billetera.depositar(monto)
                messages.success(request, 'Movimiento guardado correctamente.')
            elif tipo == Movimiento.RETIRO:
                billetera.retirar(monto)
                messages.success(request, 'Movimiento guardado correctamente.')
            return redirect('index')
    else:
        form = MovimientoForm()

    return render(request, 'core/index.html', {
        'form': form,
        'saldo': saldo,
        'billetera': billetera,
        'movimientos': movimientos[:5],
    })


@login_required(login_url='login')
def eliminar_billetera(request):
    if request.method == 'POST':
        Billetera.objects.filter(usuario=request.user).delete()
        Billetera.objects.create(usuario=request.user)
        messages.success(request, 'Billetera eliminada. Se creo una billetera nueva para continuar las pruebas.')

    return redirect('index')
