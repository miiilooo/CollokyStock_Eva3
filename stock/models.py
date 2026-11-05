from django.db import models

class Bodega(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    ubicacion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    bodegas = models.ManyToManyField(Bodega, blank=True)
    nombre = models.CharField(max_length=100)
    sku = models.CharField(max_length=50, unique=True)
    stock = models.IntegerField(null=False, blank=False)
    talla = models.CharField(max_length=20, default='21 - 27')
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)

    def __str__(self):
        return f"{self.nombre} ({self.sku})"

class Movimiento(models.Model):
    TIPO_CHOICES = (
        ('ENTRADA', 'Entrada'),
        ('SALIDA', 'Salida'),
    )
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    bodega = models.ForeignKey(Bodega, on_delete=models.PROTECT, null=False, blank=False)
    bodega_destino = models.ForeignKey(Bodega, on_delete=models.PROTECT, null=True, blank=True, related_name='movimientos_destino')
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo} - {self.producto.nombre} ({self.cantidad})"
