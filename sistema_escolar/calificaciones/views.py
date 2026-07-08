import io
import random
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.db.models import Avg
from django.utils import timezone

# Librerías de ReportLab para el PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

from .models import Curso, AlumnoCurso

@login_required
def dashboard(request):
    es_docente = request.user.groups.filter(name='Docentes').exists()
    
    if es_docente:
        cursos = Curso.objects.filter(docente=request.user)
        context = {
            'cursos': cursos,
            'es_docente': True,
            'actas_pendientes': cursos.filter(acta_firmada=False).count()
        }
    else:
        # Si es alumno, ve los cursos en los que está inscrito
        inscripciones = AlumnoCurso.objects.filter(alumno=request.user)
        context = {
            'inscripciones': inscripciones,
            'es_docente': False
        }
    return render(request, 'calificaciones/dashboard.html', context)


@login_required
def grade_entry(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.docente != request.user:
        return HttpResponseForbidden("No tienes permiso para editar este curso.")
        
    alumnos_curso = curso.inscripciones.all()
    
    if request.method == 'POST':
        if curso.acta_firmada:
            return HttpResponseForbidden("El acta ya está firmada.")
            
        for ac in alumnos_curso:
            cal_key = f"cal_{ac.id}"
            obs_key = f"obs_{ac.id}"
            if cal_key in request.POST:
                ac.calificacion_final = request.POST.get(cal_key) or None
                ac.observaciones = request.POST.get(obs_key) or ""
                ac.save()
        return redirect('grade_entry', curso_id=curso.id)

    promedio_seccion = alumnos_curso.aggregate(Avg('calificacion_final'))['calificacion_final__avg'] or 0.0
    return render(request, 'calificaciones/grade_entry.html', {
        'curso': curso,
        'alumnos_curso': alumnos_curso,
        'promedio_seccion': round(promedio_seccion, 1)
    })


@login_required
def iniciar_firma(request, curso_id):
    """Paso 1 de la Doble Validación: Genera un código y simula enviarlo"""
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.docente != request.user:
        return HttpResponseForbidden()
        
    # Doble validación: Generamos un código de 6 dígitos aleatorio y lo guardamos en la sesión
    codigo_verificacion = str(random.randint(100000, 999999))
    request.session['codigo_firma'] = codigo_verificacion
    
    # Simulación de envío por consola
    print(f"DEBUG: Código de doble validación enviado: {codigo_verificacion}") 
    
    return redirect('digital_signature', curso_id=curso.id)


@login_required
def digital_signature(request, curso_id):
    """Paso 2 de la Doble Validación: Verificar código e ingresar contraseña/PIN"""
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.docente != request.user:
        return HttpResponseForbidden()
        
    codigo_correcto = request.session.get('codigo_firma')
    error = None

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo_sms')
        pin_ingresado = request.POST.get('pin') # Firma o contraseña
        
        # CORREGIDO: Eliminado el guion bajo erróneo de 'codigo_correct_'
        if codigo_ingresado == codigo_correcto and pin_ingresado:
            curso.acta_firmada = True
            curso.fecha_firma = timezone.now()
            curso.save()
            
            # Limpiar código de la sesión
            if 'codigo_firma' in request.session:
                del request.session['codigo_firma']
            return redirect('calificaciones_dashboard')
        else:
            error = "El código de doble validación o la firma son incorrectos."

    return render(request, 'calificaciones/digital_signature.html', {
        'curso': curso, 
        'error': error,
        'codigo_simulado': codigo_correcto 
    })


@login_required
def generar_pdf(request, curso_id):
    """Generación de PDF Académico. Permitido para profesores del curso y alumnos inscritos."""
    curso = get_object_or_404(Curso, id=curso_id)
    es_docente = curso.docente == request.user
    es_alumno = curso.inscripciones.filter(alumno=request.user).exists()
    
    if not (es_docente or es_alumno):
        return HttpResponseForbidden("No tienes autorización para generar el reporte de este curso.")
        
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, leading=22, textColor=colors.HexColor('#002045'), alignment=1)
    meta_style = ParagraphStyle('MetaStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor('#475569'))
    
    story.append(Paragraph("<b>EDUGESTIÓN PRO - REPORTE OFICIAL DE CALIFICACIONES</b>", title_style))
    story.append(Spacer(1, 20))
    
    meta_text = f"""
    <b>Curso:</b> {curso.nombre} <br/>
    <b>Sección:</b> {curso.seccion} | <b>Periodo:</b> {curso.periodo} <br/>
    <b>Profesor:</b> {curso.docente.get_full_name()} <br/>
    <b>Estado del Acta:</b> {'Firmada Digitalmente' if curso.acta_firmada else 'Borrador / Pendiente'} <br/>
    <b>Fecha de Emisión:</b> {timezone.now().strftime('%d/%m/%Y %H:%M')}
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(Spacer(1, 20))
    
    tabla_datos = [['Matrícula', 'Nombre del Alumno', 'Asistencia', 'Calificación', 'Observaciones']]
    
    inscripciones = curso.inscripciones.all() if es_docente else curso.inscripciones.filter(alumno=request.user)
    
    for ins in inscripciones:
        calif = str(ins.calificacion_final) if ins.calificacion_final is not None else "N/A"
        tabla_datos.append([
            ins.alumno.username,
            ins.alumno.get_full_name(),
            f"{ins.asistencia_porcentaje}%",
            calif,
            ins.observaciones or ""
        ])
        
    t = Table(tabla_datos, colWidths=[70, 180, 60, 70, 150])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#002045')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    
    doc.build(story)
    buffer.seek(0)
    return HttpResponse(buffer, content_type='application/pdf')