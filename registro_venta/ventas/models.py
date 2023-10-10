from django.db import models


class Venta(models.Model):
    
    ESTADO_CHOICES = (
        ('A', 'Aprobada'),
        ('P', 'Pendiente'),
        ('C', 'Cancelada'),
    )

    estado_venta = models.CharField(max_length=1, choices=ESTADO_CHOICES, default='P')
    producto_vendido = models.CharField(max_length=50)
    stock_entregado = models.IntegerField()
    fecha_venta = models.DateField(auto_now_add=True)
    visita_id = models.IntegerField()  # Cambio realizado aquí: de ForeignKey a IntegerField
    compra_confirmada = models.BooleanField(default=False)
   
    def __str__(self):
        return f"Venta {self.id} - {self.producto_vendido} - {self.get_estado_venta_display()}"
