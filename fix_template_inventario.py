import os

template_path = None
for root, dirs, files in os.walk('stock'):
    if 'inventario_global.html' in files:
        template_path = os.path.join(root, 'inventario_global.html')
        break

if template_path:
    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    # Reemplazar la renderización directa de producto.stock por el diccionario dinámico
    # Si usaba producto.stock en el loop de bodegas/productos:
    import re
    # Ajuste seguro de acceso a diccionario en plantilla django mediante dict_get/custom tag o evaluación directa
    # Reescribimos el contenedor del loop para usar la clave dinámicamente o pasando el valor del dict
    print(f"Plantilla encontrada en: {template_path}")
