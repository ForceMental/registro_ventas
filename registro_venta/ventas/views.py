from rest_framework import generics
from .models import Venta
from .serializers import VentaSerializer
import requests
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class VentaListCreateView(generics.ListCreateAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    
class VentaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Venta.objects.all()
    serializer_class = VentaSerializer
    

class ProcesarVentaView(APIView):

    def post(self, request, venta_id, *args, **kwargs):
        venta, error = procesar_venta_existente(venta_id)
        
        if error:
            return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
        
        if venta:
            serializer = VentaSerializer(venta)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "No se pudo procesar la venta"}, status=status.HTTP_400_BAD_REQUEST)

    
    
    
    
def obtener_datos_cliente(cliente_id):
    print(f"Intentando obtener datos para el cliente con ID: {cliente_id}")  
    url = f"http://localhost:8001/clientes/{cliente_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        cliente_data = response.json()
        print(cliente_data)  # línea para depurar
        comuna_id = cliente_data.get('comuna', {}).get('id', None)
        
        # Comprueba que el comuna_id es un número entero.
        if comuna_id and isinstance(comuna_id, int):
            comuna_data = obtener_comuna_cliente(comuna_id)
            if comuna_data:
                # Hace una nueva solicitud para obtener datos de la región
                region_data = obtener_datos_region(comuna_data['region'])
                if region_data:
                    cliente_data.update({
                        'nombre_comuna': comuna_data['nombre_comuna'],
                        'nombre_region': region_data['nombre_region']
                    })
                else:
                    print("No se pudo obtener la información de la región.")
            else:
                print("No se pudo obtener la información de la comuna.")
        else:
            print(f"Se esperaba un ID para la comuna, pero se obtuvo: {comuna_id}")
        
        return cliente_data
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None





def obtener_datos_visita(pk):
    # el proyecto registro_visitas se ejecuta en localhost en el puerto 8001
    url = f"http://localhost:8001/visitas/{pk}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None


def obtener_comuna_cliente(comuna_id):
    print(f"Buscando datos para la comuna con ID: {comuna_id}")  # Añadido para depuración
    url = f"http://localhost:8001/comunas/{comuna_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

def obtener_datos_region(region_id):
    url = f"http://localhost:8001/regiones/{region_id}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error {response.status_code}: {response.text}")
        return None

    
    
def obtener_datos_empleado(pk):
    url = f"http://localhost:8001/empleados/{pk}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    

def crear_venta(visita_id):
    datos_visita = obtener_datos_visita(visita_id)
    if not datos_visita:
        print("Error al obtener datos de la visita.")
        return
    
    datos_cliente = obtener_datos_cliente(datos_visita['cliente'])
    if not datos_cliente:
        print("Error al obtener datos del cliente.")
        return

    # Crear el registro de venta en estado pendiente.
    venta = Venta(
        estado_venta='P',  # 'P' es para ventas pendientes.
        producto_vendido="alarma",  # Por ahora, es una constante.
        stock_entregado=0,  # Inicialmente, no se ha entregado stock.
        visita_id=visita_id,
        nombre_cliente=datos_cliente['nombre'],
        apellido_cliente=datos_cliente['apellido'],
        rut_cliente=datos_cliente['rut'],
        direccion_cliente=datos_cliente['direccion'],
        comuna_cliente=datos_cliente['comuna']['nombre_comuna'],
        region_cliente=datos_cliente['comuna']['region']['nombre_region'],
    )
    venta.save()
    print(f"Venta creada en estado pendiente para el cliente {datos_cliente['nombre']} {datos_cliente['apellido']}.")
    return venta


   

def procesar_venta_existente(venta_id):
    try:
        venta = Venta.objects.get(id=venta_id)
    except Venta.DoesNotExist:
        return None, "La venta con el ID proporcionado no existe."

    datos_visita = obtener_datos_visita(venta.visita_id)
    if not datos_visita:
        return None, "Error al obtener datos de la visita."

    # Obtener datos del cliente
    datos_cliente = obtener_datos_cliente(datos_visita['cliente']['id'])
    if not datos_cliente:
        return None, "Error al obtener datos del cliente."
    # A partir de aquí, tienes la variable datos_cliente que contiene los datos del cliente.

    datos_empleado = obtener_datos_empleado(datos_visita['empleado']['id'])
    if not datos_empleado:
        return None, "Error al obtener datos del empleado."

    stock_empleado = datos_empleado['stock_disponible']
    producto = venta.producto_vendido
    stock_a_vender = 1  # Puede cambiar según la lógica de negocio.

    if stock_a_vender > stock_empleado:
        return None, "El empleado no tiene suficiente stock para procesar la venta."

    # Lógica para reducir el stock del empleado localmente.
    stock_empleado -= stock_a_vender
    # Actualizar el stock en el proyecto `registrar_visitas` usando una solicitud API.
    if not actualizar_stock_empleado(datos_visita['empleado']['id'], stock_empleado):
        return None, "Error al actualizar el stock del empleado."

    # Actualizar la venta.
    venta.estado_venta = 'A'  # 'A' para ventas aprobadas.
    venta.stock_entregado = stock_a_vender
    venta.save()

    return venta, None

def actualizar_stock_empleado(empleado_id, nuevo_stock):
    # Primero, obtener todos los datos actuales del empleado
    empleado_data = obtener_datos_empleado(empleado_id)
    if not empleado_data:
        print("Error al obtener los datos del empleado.")
        return False
    
    # Actualizar solo el stock del empleado
    empleado_data['stock_disponible'] = nuevo_stock

    # Enviar todos los datos actualizados
    url = f"http://localhost:8001/empleados/{empleado_id}/"
    response = requests.put(url, data=empleado_data)
    
    if response.status_code != 200:
        print(f"Error al actualizar el stock del empleado: {response.status_code}: {response.text}")
        return False

    return True
