from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Tabla de Auditoría - registra TODAS las acciones importantes
class AuditoriaLog(models.Model):
    ACCIONES = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGOUT', 'Cierre de sesión'),
        ('CREATE', 'Creación'),
        ('UPDATE', 'Actualización'),
        ('DELETE', 'Eliminación'),
        ('VIEW', 'Consulta'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.CharField(max_length=20, choices=ACCIONES)
    tabla_afectada = models.CharField(max_length=100, blank=True, null=True)
    registro_id = models.IntegerField(blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(blank=True, null=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.accion} - {self.fecha_hora}"

# Modelo de Obra de Arte
class ObraArte(models.Model):
    TECNICAS = [
        ('OLEO', 'Óleo'),
        ('ACRILICO', 'Acrílico'),
        ('ACUARELA', 'Acuarela'),
        ('DIBUJO', 'Dibujo'),
        ('ESCULTURA', 'Escultura'),
        ('DIGITAL', 'Arte Digital'),
        ('OTRO', 'Otra'),
    ]

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    tecnica = models.CharField(max_length=20, choices=TECNICAS)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='obras/', blank=True, null=True)
    artista = models.ForeignKey(User, on_delete=models.CASCADE, related_name='obras')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titulo

# Modelo de Taller
class Taller(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    fecha = models.DateTimeField()
    duracion_horas = models.IntegerField()
    cupos = models.IntegerField()
    cupos_disponibles = models.IntegerField()
    instructor = models.CharField(max_length=200)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre

# Modelo de Inscripción a Taller
class InscripcionTaller(models.Model):
    taller = models.ForeignKey(Taller, on_delete=models.CASCADE, related_name='inscripciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)

    class Meta:
        unique_together = ['taller', 'usuario']

    def __str__(self):
        return f"{self.usuario.username} - {self.taller.nombre}"