from django.db import models


class Venta(models.Model):
    ESTADO_CHOICES = (
        ('A', 'Aprobada'),
        ('P', 'Pendiente'),
        ('C', 'Cancelada'),
    )

    estado_venta = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    productos = models.JSONField(
        blank=False,
        default={'id': 0, 'nombre': '', 'cantidad': 0, 'precio': 0.0},
    )
    fecha_venta = models.DateField(auto_now_add=True)
    visita_id = models.IntegerField()
    compra_confirmada = models.BooleanField(default=False)
    cliente_id = models.IntegerField(null=False, default=0)  
    ejecutivo_id = models.IntegerField(null=False, default=0)  

    def __str__(self):
        return f"Venta {self.id} - {self.get_estado_venta_display()}"