from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import EmpresaForm
from .models import Empresa


def empresa_list(request):
    empresas = Empresa.objects.all()
    return render(request, 'empresas/empresa_list.html', {'empresas': empresas})


def empresa_create(request):
    form = EmpresaForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        empresa = form.save()
        messages.success(request, f'Empresa {empresa.razon_social} registrada correctamente.')
        return redirect('empresa_list')
    return render(request, 'empresas/empresa_form.html', {'form': form})
