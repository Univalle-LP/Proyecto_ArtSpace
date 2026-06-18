from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('obras/', views.lista_obras_view, name='lista_obras'),
    path('obras/crear/', views.crear_obra_view, name='crear_obra'),
    path('obras/editar/<int:obra_id>/', views.editar_obra_view, name='editar_obra'),
    path('obras/eliminar/<int:obra_id>/', views.eliminar_obra_view, name='eliminar_obra'),
    path('talleres/', views.lista_talleres_view, name='lista_talleres'),
    path('talleres/crear/', views.crear_taller_view, name='crear_taller'),
    path('talleres/editar/<int:taller_id>/', views.editar_taller_view, name='editar_taller'),
    path('talleres/eliminar/<int:taller_id>/', views.eliminar_taller_view, name='eliminar_taller'),
    path('talleres/inscribirse/<int:taller_id>/', views.inscribirse_taller_view, name='inscribirse_taller'),
    path('mis-inscripciones/', views.mis_inscripciones_view, name='mis_inscripciones'),
    path('auditoria/', views.auditoria_view, name='auditoria'),
    path('', views.home_view, name='home'),  # ¡DEBE ESTAR AL FINAL!
]