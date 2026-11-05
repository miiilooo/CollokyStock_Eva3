from django.shortcuts import redirect
from django.contrib import messages

def requerir_grupos(grupos_permitidos=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            if request.user.groups.filter(name__in=grupos_permitidos).exists():
                return view_func(request, *args, **kwargs)
            messages.error(request, "No tienes permisos suficientes para acceder a esta sección.")
            return redirect('dashboard')
        return _wrapped_view
    return decorator
