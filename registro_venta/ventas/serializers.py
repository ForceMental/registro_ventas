from rest_framework import serializers
from .models import Venta
import requests

class VentaSerializer(serializers.ModelSerializer):
    cliente_info = serializers.SerializerMethodField()

    class Meta:
        model = Venta
        fields = [f.name for f in Venta._meta.fields] + ['cliente_info']

    def get_cliente_info(self, obj):
        cliente_data = self.context.get('clientes_info', {}).get(obj.visita_id)  # Cambio aquí
        if cliente_data:
            return cliente_data
        return None


    def obtener_datos_cliente(self, cliente_id):
        url = f"http://localhost:8001/clientes/{cliente_id}/"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return None
