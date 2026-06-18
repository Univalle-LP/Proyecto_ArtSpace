from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import ObraArte, Taller

class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

class ObraForm(forms.ModelForm):
    class Meta:
        model = ObraArte
        fields = ['titulo', 'descripcion', 'tecnica', 'precio', 'imagen']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'precio': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor a 0.')
        return precio

    def clean_titulo(self):
        titulo = self.cleaned_data.get('titulo')
        if len(titulo) < 3:
            raise forms.ValidationError('El título debe tener al menos 3 caracteres.')
        return titulo

class TallerForm(forms.ModelForm):
    class Meta:
        model = Taller
        fields = ['nombre', 'descripcion', 'fecha', 'duracion_horas', 'cupos', 'instructor', 'precio']
        widgets = {
            'fecha': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descripcion': forms.Textarea(attrs={'rows': 4}),
            'precio': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'cupos': forms.NumberInput(attrs={'min': 1}),
        }

    def clean_cupos(self):
        cupos = self.cleaned_data.get('cupos')
        if cupos <= 0:
            raise forms.ValidationError('Los cupos deben ser al menos 1.')
        return cupos

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio < 0:
            raise forms.ValidationError('El precio no puede ser negativo.')
        return precio

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        from django.utils import timezone
        if fecha < timezone.now():
            raise forms.ValidationError('La fecha debe ser futura.')
        return fecha