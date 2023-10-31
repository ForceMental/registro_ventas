
from django.urls import path, include
from ventas.views import VentaListCreateView, ProcesarVentaView, VentaDetailView

urlpatterns = [
    path('ventas/', VentaListCreateView.as_view(), name='venta-list-create'),
    path('ventas/<int:pk>/', VentaDetailView.as_view(), name='venta-detail'),
    path('procesar_venta/<int:venta_id>/', ProcesarVentaView.as_view(), name='procesar-venta'), # 'venta_id'
]

