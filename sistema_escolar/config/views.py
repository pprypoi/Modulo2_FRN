from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def home(request):
    modulos = [
        {
            'nombre': 'Alumnos y Maestros',
            'descripcion': 'Altas, bajas y edición de alumnos, maestros, materias e inscripciones.',
            'url': 'dashboard',
        },
        {
            'nombre': 'Calificaciones',
            'descripcion': 'Captura de calificaciones, firma digital de actas y reporte en PDF.',
            'url': 'calificaciones_dashboard',
        },
        {
            'nombre': 'Horarios',
            'descripcion': 'Registro y edición de horarios de clase.',
            'url': 'horarios_index',
        },
        {
            'nombre': 'Empresas',
            'descripcion': 'Registro de empresas vinculadas a la escuela.',
            'url': 'empresa_list',
        },
        {
            'nombre': 'Billetera',
            'descripcion': 'Movimientos de ingresos y egresos con saldo acumulado.',
            'url': 'billetera_list',
        },
    ]
    return render(request, 'home.html', {'modulos': modulos})
