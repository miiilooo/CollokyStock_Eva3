from django.db.models import Q
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from .models import Producto, Bodega, Movimiento

@login_required
def dashboard(request):
    return render(request, 'stock/dashboard.html')

@login_required
def lista_productos(request):
    from stock.models import Producto
    query = request.GET.get('q', '')
    if query:
        productos = Producto.objects.filter(nombre__icontains=query) | Producto.objects.filter(sku__icontains=query)
    else:
        productos = Producto.objects.all().order_by('-id')
    return render(request, 'stock/lista_productos.html', {'productos': productos, 'query': query})
def crear_producto(request):
    from stock.models import Bodega, Producto
    bodegas = Bodega.objects.all()
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        talla = request.POST.get('talla', '').strip()
        sku = request.POST.get('sku', '').strip()
        stock_str = request.POST.get('stock', '').strip()
        precio = request.POST.get('precio', '').strip()
        bodega_id = request.POST.get('bodega', '').strip()
        
        try:
            cantidad = int(stock_str)
            producto = Producto.objects.create(
                nombre=nombre,
                talla=talla,
                sku=sku,
                stock=cantidad,
                precio=float(precio)
            )
            
            # Asignar la bodega seleccionada si existe
            if bodega_id:
                bodega_obj = Bodega.objects.get(pk=bodega_id)
                producto.bodegas.add(bodega_obj)
            
            messages.success(request, "¡Producto creado y asignado a la bodega con éxito!")
            return redirect('lista_productos')
        except Exception as e:
            messages.error(request, f"Error al crear el producto: {e}")
            return render(request, 'stock/form_producto.html', {'bodegas': bodegas})
            
    return render(request, 'stock/form_producto.html', {'bodegas': bodegas})
def editar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'POST':
        producto.nombre = request.POST.get('nombre')
        producto.sku = request.POST.get('sku')
        producto.precio = request.POST.get('precio', 0)
        
        fields_names = [f.name for f in Producto._meta.get_fields()]
        if 'talla' in fields_names:
            producto.talla = request.POST.get('talla')
        if 'stock' in fields_names:
            producto.stock = request.POST.get('stock', 0)
            
        bodegas_ids = request.POST.getlist('bodegas')
        producto.save()

        if hasattr(producto, 'bodegas'):
            producto.bodegas.set(bodegas_ids)
        elif hasattr(producto, 'bodega') and bodegas_ids:
            producto.bodega_id = bodegas_ids[0]
            producto.save()

        return redirect('lista_productos')
    
    bodegas = Bodega.objects.all()
    return render(request, 'stock/form_producto.html', {'producto': producto, 'bodegas': bodegas})

@login_required
def eliminar_producto(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    producto.delete()
    return redirect('lista_productos')

@login_required


def lista_bodegas(request):
    query = request.GET.get("q", "")
    if query:
        bodegas = Bodega.objects.filter(Q(nombre__icontains=query) | Q(ubicacion__icontains=query))
    else:
        bodegas = Bodega.objects.all()
    return render(request, 'stock/lista_bodegas.html', {'bodegas': bodegas, 'query': query})

def crear_bodega(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        ubicacion = request.POST.get('ubicacion')
        Bodega.objects.create(nombre=nombre, ubicacion=ubicacion)
        return redirect('lista_bodegas')
    return render(request, 'stock/form_bodega.html')

@login_required
def editar_bodega(request, pk):
    bodega = get_object_or_404(Bodega, pk=pk)
    if request.method == 'POST':
        bodega.nombre = request.POST.get('nombre')
        bodega.ubicacion = request.POST.get('ubicacion')
        bodega.save()
        return redirect('lista_bodegas')
    return render(request, 'stock/form_bodega.html', {'bodega': bodega})

@login_required
def eliminar_bodega(request, pk):
    bodega = get_object_or_404(Bodega, pk=pk)
    bodega.delete()
    return redirect('lista_bodegas')

@login_required
def lista_movimientos(request):
    transacciones = Movimiento.objects.all().order_by('-id')
    return render(request, 'stock/lista_movimientos.html', {'transacciones': transacciones})

@login_required
def detalle_movimiento(request, pk):
    movimiento = get_object_or_404(Movimiento, pk=pk)
    return render(request, 'stock/detalle_movimiento.html', {'movimiento': movimiento})

@login_required
def registrar_movimiento(request):
    from stock.models import Bodega, Producto, Movimiento
    productos = Producto.objects.all()
    bodegas = Bodega.objects.all()
    
    if request.method == 'POST':
        tipo_raw = request.POST.get('tipo', 'ENTRADA')
        tipo = tipo_raw.upper() if tipo_raw else 'ENTRADA'
        producto_id = request.POST.get('producto')
        bodega_origen_id = request.POST.get('bodega')
        bodega_destino_id = request.POST.get('bodega_destino')
        cantidad_str = request.POST.get('cantidad')
        
        try:
            cantidad = int(cantidad_str)
            producto = Producto.objects.get(pk=producto_id)
            bodega_origen = Bodega.objects.get(pk=bodega_origen_id)
            
            bodega_dest_obj = None
            if bodega_destino_id and bodega_destino_id.strip():
                bodega_dest_obj = Bodega.objects.get(pk=bodega_destino_id)
            
            if tipo == 'ENTRADA':
                producto.stock += cantidad
                producto.save()
                producto.bodegas.add(bodega_origen)
                
                Movimiento.objects.create(
                    tipo='ENTRADA',
                    producto=producto,
                    bodega=bodega_origen,
                    bodega_destino=bodega_dest_obj,
                    cantidad=cantidad
                )
            elif tipo == 'SALIDA' or tipo == 'TRASLADO':
                if producto.stock >= cantidad:
                    # Descontar del origen
                    producto.stock -= cantidad
                    producto.save()
                else:
                    messages.error(request, f"Stock insuficiente en la bodega de origen. Stock disponible: {producto.stock}")
                    return render(request, 'stock/form_movimiento.html', {'productos': productos, 'bodegas': bodegas})
                
                # Si hay bodega de destino, asociar y asegurar que quede reflejado en el destino
                if bodega_dest_obj:
                    producto.bodegas.add(bodega_dest_obj)
                    # Si el modelo tuviera stock independiente por bodega se sumaría ahí;
                    # al ser stock global, aseguramos que la bodega destino quede vinculada correctamente con las unidades trasladadas.
                
                Movimiento.objects.create(
                    tipo='SALIDA',
                    producto=producto,
                    bodega=bodega_origen,
                    bodega_destino=bodega_dest_obj,
                    cantidad=cantidad
                )
            
            messages.success(request, f"¡Movimiento de {cantidad} unidades realizado con éxito!")
            return redirect('lista_movimientos')
            
        except Exception as e:
            messages.error(request, f"Error al registrar el movimiento: {e}")
            return render(request, 'stock/form_movimiento.html', {'productos': productos, 'bodegas': bodegas})
            
    return render(request, 'stock/form_movimiento.html', {'productos': productos, 'bodegas': bodegas})
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'stock/lista_usuarios.html', {'usuarios': usuarios})

@login_required
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        cargo = request.POST.get('cargo', 'promotor')
        is_staff = (cargo == 'supervisor')
        if username and password:
            User.objects.create_user(username=username, email=email, password=password, is_staff=is_staff)
            return redirect('lista_usuarios')
    return render(request, 'stock/form_usuario.html')

@login_required
def editar_usuario(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        target_user.username = request.POST.get('username', target_user.username)
        target_user.email = request.POST.get('email', target_user.email)
        cargo = request.POST.get('cargo', 'promotor')
        target_user.is_staff = (cargo == 'supervisor')
        new_password = request.POST.get('password')
        if new_password:
            target_user.set_password(new_password)
        target_user.save()
        return redirect('lista_usuarios')
    return render(request, 'stock/form_usuario.html', {'target_user': target_user})

@login_required
def eliminar_usuario(request, pk):
    target_user = get_object_or_404(User, pk=pk)
    if target_user != request.user:
        target_user.delete()
    return redirect('lista_usuarios')

@login_required
def inventario_global(request):
    bodegas = Bodega.objects.all()
    productos = Producto.objects.all()
    return render(request, 'stock/inventario_global.html', {'bodegas': bodegas, 'productos': productos})

custom_login = LoginView.as_view(template_name='stock/login.html')

@login_required
def custom_logout(request):
    logout(request)
    return redirect('login')


def obtener_bodegas_producto(request, producto_id):
    from stock.models import Producto, Bodega
    from django.http import JsonResponse
    try:
        producto = Producto.objects.get(pk=producto_id)
        bodegas_origen = list(producto.bodegas.values('id', 'nombre', 'ubicacion'))
        todas_bodegas = list(Bodega.objects.values('id', 'nombre', 'ubicacion'))
        
        # Excluir las bodegas de origen para que el destino sean las demás
        origen_ids = [b['id'] for b in bodegas_origen]
        bodegas_destino = [b for b in todas_bodegas if b['id'] not in origen_ids]
        
        return JsonResponse({
            'origen': bodegas_origen,
            'destino': bodegas_destino
        })
    except Producto.DoesNotExist:
        return JsonResponse({'error': 'Producto no encontrado'}, status=404)
