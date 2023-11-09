
from django.urls import path, include
from ventas.views import ListaVentasView, VentaListCreateView, AprobarVentaView

urlpatterns = [
    path('ventas/', VentaListCreateView.as_view(), name='venta-list-create'),
    path('Listaventas/', ListaVentasView.as_view(), name='lista_ventas'),
    path('ventas/aprobar/<int:venta_id>/', AprobarVentaView.as_view(), name='aprobar-venta'),
    # path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta-detail'),
    # path('procesar_venta/<int:venta_id>/', ProcesarVentaView.as_view(), name='procesar-venta'), # 'venta_id'
]

