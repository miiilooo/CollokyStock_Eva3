from django import forms
from .models import Movimiento, Bodega, Producto

class MovimientoForm(forms.ModelForm):
    class Meta:
        model = Movimiento
        fields = ['tipo', 'producto', 'bodega', 'cantidad']
        widgets = {
            'tipo': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'}),
            'producto': forms.Select(attrs={'class': 'form-select'}),
            'bodega': forms.Select(attrs={'class': 'form-select', 'id': 'id_bodega'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bodega'].queryset = Bodega.objects.all()
