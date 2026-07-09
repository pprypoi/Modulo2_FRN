from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from .models import SolicitudPrestamo, Prestamo
from .forms import SolicitudPrestamoForm, PrestamoForm
from libros.models import Ejemplar

from django.contrib.auth.decorators import login_required
from usuarios.decorators import admin_required

## Vista para solicitar prestamo
@login_required(login_url='login')
def solicitar_prestamo(request):
    if request.method == 'POST':
        form = SolicitudPrestamoForm(request.POST)

        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.estado = 'PENDIENTE'
            solicitud.save()

            return redirect('lista_solicitudes')
    else:
        form = SolicitudPrestamoForm()

    return render(request, 'prestamos/formulario_solicitud.html', {
        'form': form,
        'titulo': 'Solicitar préstamo'
    })

## para que el admin vea las solicitudes de prestamo y pueda aprobarlas o rechazarlas
@admin_required
def lista_solicitudes(request):
    solicitudes = SolicitudPrestamo.objects.all().order_by('-fecha_solicitud')

    return render(request, 'prestamos/lista_solicitudes.html', {
        'solicitudes': solicitudes
    })

### Para que el admin apruebe la solicitud 
@admin_required
def aprobar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudPrestamo, id=solicitud_id)

    ejemplar = Ejemplar.objects.filter(
        libro=solicitud.libro,
        estado='DISPONIBLE'
    ).first()

    if ejemplar is None:
        solicitud.observaciones = 'No hay ejemplares disponibles en este momento.'
        solicitud.save()
        return redirect('lista_solicitudes')

    prestamo = Prestamo.objects.create(
        usuario=solicitud.usuario,
        ejemplar=ejemplar,
        solicitud=solicitud,
        fecha_limite=timezone.now() + timedelta(days=7),
        estado='ACTIVO'
    )

    ejemplar.estado = 'PRESTADO'
    ejemplar.save()

    solicitud.estado = 'APROBADA'
    solicitud.save()

    return redirect('prestamos_activos')

##Para rechazarla
@admin_required
def rechazar_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudPrestamo, id=solicitud_id)

    solicitud.estado = 'RECHAZADA'
    solicitud.save()

    return redirect('lista_solicitudes')

##Para registrar el prestamo sin necesidad de una solicitud previa
@admin_required
def registrar_prestamo(request):
    if request.method == 'POST':
        form = PrestamoForm(request.POST)

        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.estado = 'ACTIVO'
            prestamo.save()

            ejemplar = prestamo.ejemplar
            ejemplar.estado = 'PRESTADO'
            ejemplar.save()

            if prestamo.solicitud:
                prestamo.solicitud.estado = 'APROBADA'
                prestamo.solicitud.save()

            return redirect('prestamos_activos')
    else:
        form = PrestamoForm()

    return render(request, 'prestamos/formulario_prestamo.html', {
        'form': form,
        'titulo': 'Registrar préstamo'
    })

##Prestamos activos
@admin_required
def prestamos_activos(request):
    prestamos = Prestamo.objects.filter(estado='ACTIVO').order_by('-fecha_prestamo')

    return render(request, 'prestamos/prestamos_activos.html', {
        'prestamos': prestamos
    })

##Registrar devolucion
@admin_required
def registrar_devolucion(request, prestamo_id):
    prestamo = get_object_or_404(Prestamo, id=prestamo_id)

    prestamo.estado = 'DEVUELTO'
    prestamo.fecha_devolucion = timezone.now()
    prestamo.save()

    ejemplar = prestamo.ejemplar
    ejemplar.estado = 'DISPONIBLE'
    ejemplar.save()

    return redirect('prestamos_activos')