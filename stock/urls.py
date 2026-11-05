from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('productos/<int:producto_id>/bodegas-ajax/', views.obtener_bodegas_producto, name='obtener_bodegas_producto'),
    path('movimientos/<int:pk>/detalles/', views.detalle_movimiento, name='detalle_movimiento'),
    # Autenticación
    path('', views.custom_login, name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Recuperación de contraseña por correo
    path('reset_password/', auth_views.PasswordResetView.as_view(
        template_name="stock/password_reset.html",
        email_template_name="stock/password_reset_email.html",
        subject_template_name="stock/password_reset_subject.txt"
    ), name="reset_password"),
    path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(
        template_name="stock/password_reset_done.html"
    ), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name="stock/password_reset_confirm.html"
    ), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name="stock/password_reset_complete.html"
    ), name="password_reset_complete"),

    # Gestión Propia de Usuarios
    path('usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('usuarios/crear/', views.crear_usuario, name='crear_usuario'),

    # Bodegas
    path('bodegas/', views.lista_bodegas, name='lista_bodegas'),
    path('bodegas/crear/', views.crear_bodega, name='crear_bodega'),
    path('bodegas/editar/<int:pk>/', views.editar_bodega, name='editar_bodega'),
    path('bodegas/eliminar/<int:pk>/', views.eliminar_bodega, name='eliminar_bodega'),

    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/crear/', views.crear_producto, name='crear_producto'),
    path('productos/editar/<int:pk>/', views.editar_producto, name='editar_producto'),
    path('productos/eliminar/<int:pk>/', views.eliminar_producto, name='eliminar_producto'),

    # Movimientos
    path('movimientos/', views.lista_movimientos, name='lista_movimientos'),
    path('movimientos/registrar/', views.registrar_movimiento, name='registrar_movimiento'),
    path('usuarios/<int:pk>/editar/', views.editar_usuario, name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', views.eliminar_usuario, name='eliminar_usuario'),
    path('inventario-global/', views.inventario_global, name='inventario_global'),
]