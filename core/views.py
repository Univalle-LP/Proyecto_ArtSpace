from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import ObraArte, Taller, InscripcionTaller, AuditoriaLog
from .forms import RegistroForm, LoginForm
from django.contrib.auth.models import User
from django.utils import timezone
from .forms import ObraForm, TallerForm

# ---------- FUNCIÓN PARA REGISTRAR AUDITORÍA ----------
def registrar_auditoria(usuario, accion, tabla=None, registro_id=None, descripcion=None, ip=None):
    AuditoriaLog.objects.create(
        usuario=usuario,
        accion=accion,
        tabla_afectada=tabla,
        registro_id=registro_id,
        descripcion=descripcion,
        ip=ip
    )

# ---------- VISTA DE REGISTRO ----------
def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            registrar_auditoria(user, 'LOGIN', ip=request.META.get('REMOTE_ADDR'))
            messages.success(request, '¡Registro exitoso!')
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, 'core/registro.html', {'form': form})

# ---------- VISTA DE LOGIN ----------
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                registrar_auditoria(user, 'LOGIN', ip=request.META.get('REMOTE_ADDR'))
                messages.success(request, f'¡Bienvenido {user.username}!')
                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

# ---------- VISTA DE LOGOUT ----------
def logout_view(request):
    if request.user.is_authenticated:
        registrar_auditoria(request.user, 'LOGOUT', ip=request.META.get('REMOTE_ADDR'))
    logout(request)
    return redirect('login')

# ---------- HOME ----------
@login_required
def home_view(request):
    obras = ObraArte.objects.all().order_by('-fecha_creacion')[:6]
    talleres = Taller.objects.filter(fecha__gte=timezone.now()).order_by('fecha')[:6]
    return render(request, 'core/home.html', {'obras': obras, 'talleres': talleres})

# ---------- CRUD OBRAS ----------
@login_required
def lista_obras_view(request):
    obras = ObraArte.objects.all().order_by('-fecha_creacion')
    return render(request, 'core/lista_obras.html', {'obras': obras})

@login_required
def crear_obra_view(request):
    if request.method == 'POST':
        form = ObraForm(request.POST, request.FILES)
        if form.is_valid():
            obra = form.save(commit=False)
            obra.artista = request.user
            obra.save()
            registrar_auditoria(request.user, 'CREATE', 'ObraArte', obra.id, 
                               f'Creó obra: {obra.titulo}', request.META.get('REMOTE_ADDR'))
            messages.success(request, '¡Obra creada exitosamente!')
            return redirect('lista_obras')
    else:
        form = ObraForm()
    return render(request, 'core/crear_obra.html', {'form': form})

@login_required
def editar_obra_view(request, obra_id):
    obra = get_object_or_404(ObraArte, id=obra_id)
    if request.user != obra.artista and not request.user.is_superuser:
        messages.error(request, 'Sin permiso.')
        return redirect('lista_obras')
    if request.method == 'POST':
        # Guardar datos ANTES de la modificación
        datos_antes = f"Título: {obra.titulo}, Precio: {obra.precio}, Técnica: {obra.tecnica}"
        form = ObraForm(request.POST, request.FILES, instance=obra)
        if form.is_valid():
            form.save()
            # Guardar datos DESPUÉS de la modificación
            datos_despues = f"Título: {obra.titulo}, Precio: {obra.precio}, Técnica: {obra.tecnica}"
            registrar_auditoria(request.user, 'UPDATE', 'ObraArte', obra.id, 
                               f'Editó obra: {obra.titulo}. ANTES: {datos_antes} | DESPUÉS: {datos_despues}', 
                               request.META.get('REMOTE_ADDR'))
            messages.success(request, '¡Obra actualizada!')
            return redirect('lista_obras')
    else:
        form = ObraForm(instance=obra)
    return render(request, 'core/editar_obra.html', {'form': form, 'obra': obra})

@login_required
def eliminar_obra_view(request, obra_id):
    obra = get_object_or_404(ObraArte, id=obra_id)
    if request.user != obra.artista and not request.user.is_superuser:
        messages.error(request, 'Sin permiso.')
        return redirect('lista_obras')
    if request.method == 'POST':
        titulo = obra.titulo
        obra.delete()
        registrar_auditoria(request.user, 'DELETE', 'ObraArte', obra_id, f'Eliminó obra: {titulo}', request.META.get('REMOTE_ADDR'))
        messages.success(request, '¡Obra eliminada!')
        return redirect('lista_obras')
    return render(request, 'core/eliminar_obra.html', {'obra': obra})

# ---------- CRUD TALLERES (SOLO ADMIN) ----------
@login_required
def lista_talleres_view(request):
    talleres = Taller.objects.all().order_by('fecha')
    return render(request, 'core/lista_talleres.html', {'talleres': talleres})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def crear_taller_view(request):
    if request.method == 'POST':
        taller = Taller.objects.create(
            nombre=request.POST.get('nombre'),
            descripcion=request.POST.get('descripcion'),
            fecha=request.POST.get('fecha'),
            duracion_horas=request.POST.get('duracion_horas'),
            cupos=request.POST.get('cupos'),
            cupos_disponibles=request.POST.get('cupos'),
            instructor=request.POST.get('instructor'),
            precio=request.POST.get('precio')
        )
        registrar_auditoria(request.user, 'CREATE', 'Taller', taller.id, f'Creó taller: {taller.nombre}', request.META.get('REMOTE_ADDR'))
        messages.success(request, '¡Taller creado!')
        return redirect('lista_talleres')
    return render(request, 'core/crear_taller.html')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def editar_taller_view(request, taller_id):
    taller = get_object_or_404(Taller, id=taller_id)
    if request.method == 'POST':
        taller.nombre = request.POST.get('nombre', taller.nombre)
        taller.descripcion = request.POST.get('descripcion', taller.descripcion)
        taller.fecha = request.POST.get('fecha', taller.fecha)
        taller.duracion_horas = request.POST.get('duracion_horas', taller.duracion_horas)
        taller.cupos = request.POST.get('cupos', taller.cupos)
        taller.cupos_disponibles = request.POST.get('cupos_disponibles', taller.cupos_disponibles)
        taller.instructor = request.POST.get('instructor', taller.instructor)
        taller.precio = request.POST.get('precio', taller.precio)
        taller.save()
        registrar_auditoria(request.user, 'UPDATE', 'Taller', taller.id, f'Editó taller: {taller.nombre}', request.META.get('REMOTE_ADDR'))
        messages.success(request, '¡Taller actualizado!')
        return redirect('lista_talleres')
    return render(request, 'core/editar_taller.html', {'taller': taller})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_taller_view(request, taller_id):
    taller = get_object_or_404(Taller, id=taller_id)
    if request.method == 'POST':
        nombre = taller.nombre
        taller.delete()
        registrar_auditoria(request.user, 'DELETE', 'Taller', taller_id, f'Eliminó taller: {nombre}', request.META.get('REMOTE_ADDR'))
        messages.success(request, '¡Taller eliminado!')
        return redirect('lista_talleres')
    return render(request, 'core/eliminar_taller.html', {'taller': taller})

# ---------- INSCRIPCIONES ----------
@login_required
def inscribirse_taller_view(request, taller_id):
    taller = get_object_or_404(Taller, id=taller_id)
    if taller.cupos_disponibles <= 0:
        messages.error(request, 'Sin cupos.')
        return redirect('lista_talleres')
    inscripcion, created = InscripcionTaller.objects.get_or_create(taller=taller, usuario=request.user)
    if created:
        taller.cupos_disponibles -= 1
        taller.save()
        registrar_auditoria(request.user, 'CREATE', 'InscripcionTaller', inscripcion.id, f'Inscrito en taller: {taller.nombre}', request.META.get('REMOTE_ADDR'))
        messages.success(request, f'¡Inscrito en {taller.nombre}!')
    else:
        messages.info(request, 'Ya inscrito.')
    return redirect('lista_talleres')

@login_required
def mis_inscripciones_view(request):
    inscripciones = InscripcionTaller.objects.filter(usuario=request.user).select_related('taller')
    return render(request, 'core/mis_inscripciones.html', {'inscripciones': inscripciones})

# ---------- AUDITORÍA (SOLO ADMIN) ----------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def auditoria_view(request):
    logs = AuditoriaLog.objects.all().order_by('-fecha_hora')
    return render(request, 'core/auditoria.html', {'logs': logs})