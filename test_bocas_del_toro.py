from messages import get_mensaje_devolucion_por_pais, OFICINAS_PANAMA
from bot_logic import aplicar_flujo_por_pais

# Datos de prueba de la guía de Bocas Del Toro
datos_bocas = {
    "tracking_number": "PRSPTY0825125743",
    "estado": "400 - Solicitud de devolución",  # Simulamos estado de devolución
    "pais": "Panama",
    "destino": "Almirante", 
    "depto_destino": "Bocas Del Toro",
    "fecha_estado": "2025-08-07 17:11:53+00:00",
    "nombre": "ÉLIET DEL ROSARIO GRACIA",
    "origen_city": "Panamá",
    "destino_city": "Almirante"
}

print("=== INFORMACIÓN DE OFICINA BOCAS DEL TORO ===")
if "Bocas Del Toro" in OFICINAS_PANAMA:
    oficina = OFICINAS_PANAMA["Bocas Del Toro"]
    print(f"Dirección: {oficina['direccion']}")
    print(f"Horarios: {oficina['horarios']}")
    print(f"Teléfono: {oficina['telefono']}")
else:
    print("❌ No se encontró oficina para Bocas Del Toro")

print("\n" + "="*60 + "\n")

print("=== PRUEBA: Devolución dinámica Bocas Del Toro ===")
mensaje_devolucion = get_mensaje_devolucion_por_pais("panama", "Bocas Del Toro")
print(mensaje_devolucion)
print("\n" + "="*60 + "\n")

print("=== PRUEBA: Flujo completo con estado de devolución ===")
respuesta_flujo = aplicar_flujo_por_pais("panama", "ÉLIET DEL ROSARIO GRACIA", "PRSPTY0825125743", datos_bocas)
print(respuesta_flujo)
print("\n" + "="*60 + "\n")

print("=== COMPARACIÓN: Los Santos vs Bocas Del Toro ===")
print("LOS SANTOS:")
mensaje_los_santos = get_mensaje_devolucion_por_pais("panama", "Los Santos")
print(mensaje_los_santos[:200] + "...")
print("\nBOCAS DEL TORO:")
mensaje_bocas_toro = get_mensaje_devolucion_por_pais("panama", "Bocas Del Toro")
print(mensaje_bocas_toro[:200] + "...")
