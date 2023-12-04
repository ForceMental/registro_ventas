from rest_framework import generics
from .models import Venta
from .serializers import VentaSerializer
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status

BASE_URL = 'http://107.22.174.168'

class ListaVentasView(ListAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

    def get(self, request, *args, **kwargs):
        # Obtén todas las ventas
        ventas = self.get_queryset()
        # Serializa las ventas
        serializer = self.get_serializer(ventas, many=True)
        
        # Itera a través de las ventas y obtén datos de cliente de la API externa
        for venta in ventas:
            cliente_id = venta.cliente_id
            if cliente_id:
                # Construye la URL de la API externa
                cliente_url = f"{BASE_URL}:8000/api/clientes/{cliente_id}/"
                
                # Realiza la solicitud GET a la API externa
                response = requests.get(cliente_url)
                
                if response.status_code == 200:
                    # Si la solicitud es exitosa, agrega los datos del cliente a la respuesta
                    cliente_data = response.json()
                    venta.cliente_info = cliente_data
                    
                    # Imprime los datos de la venta y el cliente para depuración
                    print(f"Datos de venta {venta.id}: {venta}")
                    print(f"Datos del cliente para venta {venta.id}: {cliente_data}")

        # Devuelve la respuesta con los datos de ventas y clientes
        return Response(serializer.data)   

class VentaListCreateView(generics.ListCreateAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer

class CancelarVentaView(APIView):
    def put(self, request, venta_id, format=None):
        try:
            venta = Venta.objects.get(pk=venta_id)
        except Venta.DoesNotExist:
            return Response({'error': 'La venta no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        if venta.estado_venta == 'C':
            return Response({'error': 'La venta ya está cancelada'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambia el estado de la venta a "Cancelada"
        venta.estado_venta = 'C'
        venta.save()
        
        # Aquí podrías agregar lógica adicional si es necesario, como deshacer cambios en el stock o realizar otras operaciones relacionadas con la cancelación de la venta.
        
        serializer = VentaSerializer(venta)
        return Response(serializer.data)

class AprobarVentaView(APIView):
    def put(self, request, venta_id, format=None):
        try:
            venta = Venta.objects.get(pk=venta_id)
        except Venta.DoesNotExist:
            return Response({'error': 'La venta no existe'}, status=status.HTTP_404_NOT_FOUND)
        
        if venta.estado_venta == 'A':
            return Response({'error': 'La venta ya está aprobada'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambia el estado de la venta a "Aprobada"
        venta.estado_venta = 'A'
        venta.save()
        
        # Llama a la función para actualizar el stock
        if not self.actualizar_stock(venta.productos):
            return Response({'error': 'Error al actualizar el stock del producto'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializer = VentaSerializer(venta)
        return Response(serializer.data)
    
    def actualizar_stock(self, productos):
        # Verificar que la lista de productos no esté vacía
        if not productos:
            return False

        for producto in productos:
            producto_id = producto.get('id')
            if producto_id:
 
                stock_url = f"http://107.22.174.168:8020/api/productos/{producto_id}/"

                # Realizar una solicitud GET para obtener los datos del producto
                response = requests.get(stock_url)

                if response.status_code == 200:
                    producto_data = response.json()
                    cantidad_vendida = producto.get('cantidad', 0)


                    producto_data['stock_producto'] -= cantidad_vendida

                    # Realizar una solicitud PUT para actualizar el stock
                    response = requests.put(stock_url, json=producto_data)

                    if response.status_code != 200:
                        return False
                else:
                    return False

        return True
# class VentaDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Venta.objects.all()
#     serializer_class = VentaSerializer
    

# class ProcesarVentaView(APIView):

#     def post(self, request, venta_id, *args, **kwargs):
#         venta, error = procesar_venta_existente(venta_id)
        
#         if error:
#             return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
#         if venta:
#             serializer = VentaSerializer(venta)
#             return Response(serializer.data, status=status.HTTP_200_OK)
        
#         return Response({"error": "No se pudo procesar la venta"}, status=status.HTTP_400_BAD_REQUEST)

    


# def obtener_datos_visita(pk):
#     # el proyecto registro_visitas se ejecuta en localhost en el puerto 8001
#     url = f"{BASE_URL}:8000/api/visitas/{pk}/"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return None




    
    
# def obtener_datos_empleado(pk):
#     url = f"http://localhost:8001/empleados/{pk}/"
#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return None
    

# def crear_venta(visita_id):
#     datos_visita = obtener_datos_visita(visita_id)
#     if not datos_visita:
#         print("Error al obtener datos de la visita.")
#         return
    
#     datos_cliente = obtener_datos_cliente(datos_visita['cliente'])
#     if not datos_cliente:
#         print("Error al obtener datos del cliente.")
#         return

#     # Crear el registro de venta en estado pendiente.
#     venta = Venta(
#         estado_venta='P',  # 'P' es para ventas pendientes.
#         producto_vendido="alarma",  # Por ahora, es una constante.
#         stock_entregado=0,  # Inicialmente, no se ha entregado stock.
#         visita_id=visita_id,
#         nombre_cliente=datos_cliente['nombre'],
#         apellido_cliente=datos_cliente['apellido'],
#         rut_cliente=datos_cliente['rut'],
#         direccion_cliente=datos_cliente['direccion'],
#         comuna_cliente=datos_cliente['comuna']['nombre_comuna'],
#         region_cliente=datos_cliente['comuna']['region']['nombre_region'],
#     )
#     venta.save()
#     print(f"Venta creada en estado pendiente para el cliente {datos_cliente['nombre']} {datos_cliente['apellido']}.")
#     return venta


   

# def procesar_venta_existente(venta_id):
#     try:
#         venta = Venta.objects.get(id=venta_id)
#     except Venta.DoesNotExist:
#         return None, "La venta con el ID proporcionado no existe."

#     datos_visita = obtener_datos_visita(venta.visita_id)
#     if not datos_visita:
#         return None, "Error al obtener datos de la visita."

#     # Obtener datos del cliente
#     datos_cliente = obtener_datos_cliente(datos_visita['cliente']['id'])
#     if not datos_cliente:
#         return None, "Error al obtener datos del cliente."
#     # A partir de aquí, tienes la variable datos_cliente que contiene los datos del cliente.

#     datos_empleado = obtener_datos_empleado(datos_visita['empleado']['id'])
#     if not datos_empleado:
#         return None, "Error al obtener datos del empleado."

#     stock_empleado = datos_empleado['stock_disponible']
#     producto = venta.producto_vendido
#     stock_a_vender = 1  # Puede cambiar según la lógica de negocio.

#     if stock_a_vender > stock_empleado:
#         return None, "El empleado no tiene suficiente stock para procesar la venta."

#     # Lógica para reducir el stock del empleado localmente.
#     stock_empleado -= stock_a_vender
#     # Actualizar el stock en el proyecto `registrar_visitas` usando una solicitud API.
#     if not actualizar_stock_empleado(datos_visita['empleado']['id'], stock_empleado):
#         return None, "Error al actualizar el stock del empleado."

#     # Actualizar la venta.
#     venta.estado_venta = 'A'  # 'A' para ventas aprobadas.
#     venta.stock_entregado = stock_a_vender
#     venta.save()

#     return venta, None

# def actualizar_stock_empleado(empleado_id, nuevo_stock):
#     # Primero, obtener todos los datos actuales del empleado
#     empleado_data = obtener_datos_empleado(empleado_id)
#     if not empleado_data:
#         print("Error al obtener los datos del empleado.")
#         return False
    
#     # Actualizar solo el stock del empleado
#     empleado_data['stock_disponible'] = nuevo_stock

#     # Enviar todos los datos actualizados
#     url = f"http://localhost:8001/empleados/{empleado_id}/"
#     response = requests.put(url, data=empleado_data)
    
#     if response.status_code != 200:
#         print(f"Error al actualizar el stock del empleado: {response.status_code}: {response.text}")
#         return False

#     return True
