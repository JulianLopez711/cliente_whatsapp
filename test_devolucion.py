from messages import get_mensaje_devolucion_por_pais
from bot_logic import aplicar_flujo_por_pais

# Datos de prueba de la guía
datos_prueba = {
    "tracking_number": "PRSPTY0825152345",
    "estado": "400 - Solicitud de devolución",  # Simulamos estado de devolución
    "pais": "Panama",
    "destino": "Tonosi", 
    "depto_destino": "Los Santos",
    "fecha_estado": "2025-08-15 09:56:20+00:00",
    "nombre": "LIBRADA ATENCIO",
    "origen_city": "Panamá",
    "destino_city": "Tonosi"
}

print("=== PRUEBA 1: Función de devolución directa ===")
mensaje_devolucion = get_mensaje_devolucion_por_pais("panama", "Los Santos")
print(mensaje_devolucion)
print("\n" + "="*60 + "\n")

print("=== PRUEBA 2: Flujo completo con estado de devolución ===")
respuesta_flujo = aplicar_flujo_por_pais("panama", "LIBRADA ATENCIO", "PRSPTY0825152345", datos_prueba)
print(respuesta_flujo)
print("\n" + "="*60 + "\n")

print("=== PRUEBA 3: Flujo con estado normal ===")
datos_normal = datos_prueba.copy()
datos_normal["estado"] = "101 - Creación del número de órden"
respuesta_normal = aplicar_flujo_por_pais("panama", "LIBRADA ATENCIO", "PRSPTY0825152345", datos_normal)
print(respuesta_normal)
