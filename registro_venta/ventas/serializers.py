from rest_framework import serializers
from .models import Venta
import requests

class VentaSerializer(serializers.ModelSerializer):
    cliente_info = serializers.JSONField(read_only=True)

    class Meta:
        model = Venta
        fields = [f.name for f in Venta._meta.fields] + ['cliente_info']

    def get_cliente_info(self, obj):
        cliente_data = self.context.get('clientes_info', {}).get(obj.visita_id)
        if cliente_data:
            return cliente_data
        return None

    def validate_productos(self, value):
        # Validar que los campos requeridos estén presentes en el objeto JSON
        required_fields = ['id', 'nombre', 'cantidad', 'precio']
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"El campo '{field}' es obligatorio en 'productos'.")
        return value

    def validate_productos(self, value):
        for product in value:
            # Validar que los campos requeridos estén presentes en cada objeto de la lista "productos"
            required_fields = ['id', 'nombre', 'cantidad', 'precio']
            for field in required_fields:
                if field not in product:
                    raise serializers.ValidationError(f"El campo '{field}' es obligatorio en 'productos'.")
        return value