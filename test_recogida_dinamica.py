from tracking_data import consultar_estado
from messages import get_mensaje_recogida_panama
from bot_logic import aplicar_flujo_por_pais

# Probar con la guía de Bocas Del Toro
tracking = 'PRSPTY0825125743'
datos = consultar_estado(tracking)

if datos:
    print("=== DATOS DE LA GUÍA ===")
    print(f"Tracking: {tracking}")
    print(f"Depto_Destino: {datos.get('depto_destino')}")
    print(f"Destino: {datos.get('destino')}")
    print(f"País: {datos.get('pais')}")
    print()
    
    print("=== MENSAJE DE RECOGIDA DINÁMICO ===")
    depto_destino = datos.get('depto_destino')
    mensaje_recogida = get_mensaje_recogida_panama(depto_destino, tracking)
    print(mensaje_recogida)
    
else:
    print("❌ No se encontraron datos")
