from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AlumnoForm, InscripcionForm, MaestroForm, MateriaForm
from .models import Alumno, Inscripcion, Maestro, Materia


def index(request):
    context = {
        'total_alumnos': Alumno.objects.filter(activo=True).count(),
        'total_maestros': Maestro.objects.filter(activo=True).count(),
        'total_materias': Materia.objects.filter(activa=True).count(),
        'total_inscripciones': Inscripcion.objects.filter(activo=True).count(),
        'alumnos_recientes': Alumno.objects.filter(activo=True).order_by('-fecha_creacion')[:5],
    }
    return render(request, 'core/index.html', context)


def alumno_list(request):
    q = request.GET.get('q', '').strip()
    alumnos = Alumno.objects.all()
    if q:
        alumnos = alumnos.filter(
            Q(nombre__icontains=q)
            | Q(apellido_paterno__icontains=q)
            | Q(apellido_materno__icontains=q)
            | Q(correo__icontains=q)
            | Q(matricula__icontains=q)
        )
    return render(request, 'core/alumno_list.html', {'alumnos': alumnos, 'q': q})


def alumno_create(request):
    form = AlumnoForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        alumno = form.save()
        messages.success(request, f'Alumno {alumno.matricula} registrado correctamente.')
        return redirect('alumno_list')
    return render(request, 'core/alumno_form.html', {'form': form, 'titulo': 'Nuevo alumno'})


def alumno_update(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    form = AlumnoForm(request.POST or None, instance=alumno)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Alumno actualizado correctamente.')
        return redirect('alumno_list')
    return render(request, 'core/alumno_form.html', {'form': form, 'titulo': 'Editar alumno', 'alumno': alumno})


def alumno_deactivate(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)
    alumno.activo = False
    alumno.save(update_fields=['activo'])
    messages.success(request, 'Alumno desactivado correctamente.')
    return redirect('alumno_list')


def maestro_list(request):
    q = request.GET.get('q', '').strip()
    maestros = Maestro.objects.all()
    if q:
        maestros = maestros.filter(
            Q(nombre__icontains=q)
            | Q(apellido_paterno__icontains=q)
            | Q(apellido_materno__icontains=q)
            | Q(correo__icontains=q)
            | Q(numero_empleado__icontains=q)
        )
    return render(request, 'core/maestro_list.html', {'maestros': maestros, 'q': q})


def maestro_create(request):
    form = MaestroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        maestro = form.save()
        messages.success(request, f'Maestro {maestro.numero_empleado} registrado correctamente.')
        return redirect('maestro_list')
    return render(request, 'core/maestro_form.html', {'form': form, 'titulo': 'Nuevo maestro'})


def maestro_update(request, pk):
    maestro = get_object_or_404(Maestro, pk=pk)
    form = MaestroForm(request.POST or None, instance=maestro)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Maestro actualizado correctamente.')
        return redirect('maestro_list')
    return render(request, 'core/maestro_form.html', {'form': form, 'titulo': 'Editar maestro', 'maestro': maestro})


def maestro_deactivate(request, pk):
    maestro = get_object_or_404(Maestro, pk=pk)
    maestro.activo = False
    maestro.save(update_fields=['activo'])
    messages.success(request, 'Maestro desactivado correctamente.')
    return redirect('maestro_list')


def materia_list(request):
    q = request.GET.get('q', '').strip()
    materias = Materia.objects.select_related('maestro_responsable')
    if q:
        materias = materias.filter(
            Q(clave__icontains=q)
            | Q(nombre__icontains=q)
            | Q(carrera__icontains=q)
            | Q(maestro_responsable__nombre__icontains=q)
            | Q(maestro_responsable__apellido_paterno__icontains=q)
            | Q(maestro_responsable__apellido_materno__icontains=q)
        )
    return render(request, 'core/materia_list.html', {'materias': materias, 'q': q})


def materia_create(request):
    form = MateriaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Materia registrada correctamente.')
        return redirect('materia_list')
    return render(request, 'core/materia_form.html', {'form': form, 'titulo': 'Nueva materia'})


def materia_update(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    form = MateriaForm(request.POST or None, instance=materia)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Materia actualizada correctamente.')
        return redirect('materia_list')
    return render(request, 'core/materia_form.html', {'form': form, 'titulo': 'Editar materia', 'materia': materia})


def materia_deactivate(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    materia.activa = False
    materia.save(update_fields=['activa'])
    messages.success(request, 'Materia desactivada correctamente.')
    return redirect('materia_list')


def inscripcion_list(request):
    q = request.GET.get('q', '').strip()
    inscripciones = Inscripcion.objects.select_related('alumno', 'materia')
    if q:
        inscripciones = inscripciones.filter(
            Q(alumno__nombre__icontains=q)
            | Q(alumno__apellido_paterno__icontains=q)
            | Q(alumno__apellido_materno__icontains=q)
            | Q(alumno__matricula__icontains=q)
            | Q(materia__nombre__icontains=q)
            | Q(materia__clave__icontains=q)
            | Q(periodo_escolar__icontains=q)
        )
    return render(request, 'core/inscripcion_list.html', {'inscripciones': inscripciones, 'q': q})


def inscripcion_create(request):
    form = InscripcionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Inscripcion registrada correctamente.')
        return redirect('inscripcion_list')
    return render(request, 'core/inscripcion_form.html', {'form': form, 'titulo': 'Nueva inscripcion'})


def inscripcion_deactivate(request, pk):
    inscripcion = get_object_or_404(Inscripcion, pk=pk)
    inscripcion.activo = False
    inscripcion.save(update_fields=['activo'])
    messages.success(request, 'Inscripcion desactivada correctamente.')
    return redirect('inscripcion_list')
