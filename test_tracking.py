from tracking_data import consultar_estado
import json

tracking = 'PRSPTY0825125743'
datos = consultar_estado(tracking)

if datos:
    print('=== DATOS DE LA GUÍA ===')
    print(f'Tracking: {datos.get("tracking_number")}')
    print(f'Estado: {datos.get("estado")}')
    print(f'País: {datos.get("pais")}')
    print(f'Destino: {datos.get("destino")}')
    print(f'Depto_Destino: {datos.get("depto_destino")}')
    print(f'Destino_City: {datos.get("destino_city")}')
    print(f'Cliente: {datos.get("client")}')
    print(f'Nombre: {datos.get("nombre")}')
    print('')
    print('=== DATOS COMPLETOS ===')
    for key, value in datos.items():
        print(f'{key}: {value}')
else:
    print('❌ No se encontraron datos para la guía')
