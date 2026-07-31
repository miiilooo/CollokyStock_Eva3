from django.db import models

# Definición del modelo Producto requerido en la tarea SCRUM-7
class Producto(models.Model):
    # Campo para el nombre del producto con un máximo de 100 caracteres
    nombre = models.CharField(max_length=100)
    
    # Campo para el precio del producto
    precio = models.IntegerField()
    
    # Campo booleano para indicar disponibilidad
    disponible = models.BooleanField(default=True)

    # Método para representación en cadena del objeto
    def __str__(self):
        return self.nombre


        