from django import forms
from .models import Horario


class HorarioForm(forms.ModelForm):

    class Meta:
        model = Horario
        fields = [
            'dia',
            'hora_inicio',
            'hora_fin',
            'estado'
        ]

        widgets = {

            'dia': forms.Select(
                attrs={
                    'class': 'form-select'
                }
            ),

            'hora_inicio': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),

            'hora_fin': forms.TimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'time'
                }
            ),

            'estado': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            )

        }

        labels = {

            'dia': 'Día',

            'hora_inicio': 'Hora de inicio',

            'hora_fin': 'Hora de finalización',

            'estado': 'Horario activo'

        }

        help_texts = {

            'dia': '',

            'hora_inicio': '',

            'hora_fin': '',

            'estado': ''

        }