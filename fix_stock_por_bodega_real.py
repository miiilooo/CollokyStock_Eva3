import re

with open('stock/views.py', 'r', encoding='utf-8') as f:
    views_code = f.read()

# 1. Actualizar la vista de inventario global para calcular el stock real por bodega individualmente
nueva_inventario_global = '''@login_required
def inventario_global(request):
    from stock.models import Bodega, Producto, Movimiento
    from django.db.models import Sum

    bodegas = Bodega.objects.all()
    productos = Producto.objects.all()
    stock_por_bodega = {}

    for b in bodegas:
        stock_por_bodega[b.id] = {}
        for p in productos:
            # Si el producto pertenece a esta bodega o tiene movimientos en ella
            if b in p.bodegas.all() or Movimiento.objects.filter(producto=p, __Q(bodega=b) | __Q(bodega_destino=b)).exists():
                # Entradas iniciales (stock base asignado al crear o si no hay origen)
                # O si asumimos que el stock global es el inicial en la primera bodega asignada:
                
                # Movimientos donde esta bodega es ORIGEN (restan)
                salidas = Movimiento.objects.filter(
                    producto=p, bodega=b
                ).aggregate(total=Sum('cantidad'))['total'] or 0

                # Movimientos donde esta bodega es DESTINO (suman)
                entradas = Movimiento.objects.filter(
                    producto=p, bodega_destino=b
                ).aggregate(total=Sum('cantidad'))['total'] or 0

                # Si es la bodega inicial donde se creó el producto, parte con el stock global original menos lo movido
                # Para simplificar y hacerlo exacto por movimientos:
                # Stock en esta bodega = (Entradas recibidas) - (Salidas enviadas)
                # Si el producto se creó con un stock inicial en esta bodega:
                is_primary = (p.bodegas.first() == b)
                base_stock = p.stock if is_primary else 0
                
                calc_stock = base_stock + entradas - salidas
                if calc_stock < 0:
                    calc_stock = 0
                
                stock_por_bodega[b.id][p.id] = calc_stock

    return render(request, 'stock/inventario_global.html', {
        'bodegas': bodegas,
        'productos': productos,
        'stock_por_bodega': stock_por_bodega
    })'''

# 2. Actualizar registrar_movimiento para que NO altere el stock global destructivamente, 
# sino que registre el movimiento de transferencia limpiamente.
nueva_registrar_movimiento = '''@login_required
def registrar_movimiento(request):
    from stock.models import Bodega, Producto, Movimiento
    productos = Producto.objects.all()
    bodegas = Bodega.objects.all()
    
    if request.method == 'POST':
        tipo_raw = request.POST.get('tipo', 'TRASLADO')
        tipo = tipo_raw.upper() if tipo_raw else 'TRASLADO'
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
            
            # Registrar el movimiento de transferencia
            Movimiento.objects.create(
                tipo='TRASLADO' if bodega_dest_obj else 'SALIDA',
                producto=producto,
                bodega=bodega_origen,
                bodega_destino=bodega_dest_obj,
                cantidad=cantidad
            )

            # Asegurar vinculación en la relación ManyToMany para que aparezca en el inventario de la bodega destino
            if bodega_dest_obj:
                producto.bodegas.add(bodega_dest_obj)
            
            messages.success(request, f"¡Se han transferido {cantidad} unidades correctamente!")
            return redirect('lista_movimientos')
            
        except Exception as e:
            messages.error(request, f"Error al procesar el movimiento: {e}")
            return render(request, 'stock/form_movimiento.html', {'productos': productos, 'bodegas': bodegas})
            
    return render(request, 'stock/form_movimiento.html', {'productos': productos, 'bodegas': bodegas})'''

# Reemplazar funciones en views.py de forma segura
# (Omitimos el cambio complejo de inventario_global si prefieres mantener el ajuste directo en la plantilla)
