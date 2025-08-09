#!/usr/bin/env python3
"""
Script para probar la asignación de tickets por países (Colombia vs Panamá)
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from helpers import obtener_datos_tracking, crear_ticket_central, obtener_agentes_servicio_cliente

def test_asignacion_por_pais():
    """Prueba la asignación de tickets según el país detectado"""
    print("🌍 PRUEBA DE ASIGNACIÓN POR PAÍS")
    print("=" * 50)
    
    # Test 1: Simular tracking de Colombia
    print("\n🇨🇴 TEST 1: COLOMBIA")
    print("-" * 30)
    
    # Simular datos de tracking de Colombia
    datos_colombia = {
        'carrier': 'SERVIENTREGA',
        'pais': 'Colombia',
        'estado_actual': 'En tránsito',
        'origen_city': 'Bogotá',
        'destino_city': 'Medellín',
        'destino': 'Carrera 80 #12-34'
    }
    
    print(f"📦 Datos simulados: {datos_colombia}")
    
    try:
        # Simular creación de ticket para Colombia
        resultado_colombia = crear_ticket_central(
            asunto="[PEDIDO NO ENTREGADO] Caso automático - COL123456789",
            descripcion="El paquete no ha llegado",
            usuario_nombre="Cliente Colombia",
            usuario_telefono="+573001234567",
            tracking_code="COL123456789",
            tipo_caso="pedido no entregado",
            prioridad="alta"
        )
        
        if resultado_colombia:
            print(f"✅ Ticket Colombia creado: ID {resultado_colombia.id}")
            print(f"   Cola asignada: {resultado_colombia.cola_id} (debería ser 1)")
        else:
            print("❌ Error creando ticket de Colombia")
            
    except Exception as e:
        print(f"❌ Error en test Colombia: {e}")
    
    # Test 2: Simular tracking de Panamá
    print("\n🇵🇦 TEST 2: PANAMÁ")
    print("-" * 30)
    
    # Simular datos de tracking de Panamá
    datos_panama = {
        'carrier': 'FEDEX',
        'pais': 'Panama',
        'estado_actual': 'En almacén',
        'origen_city': 'Ciudad de Panamá',
        'destino_city': 'Colón',
        'destino': 'Avenida Central #45-67'
    }
    
    print(f"📦 Datos simulados: {datos_panama}")
    
    try:
        # Simular creación de ticket para Panamá
        resultado_panama = crear_ticket_central(
            asunto="[MALA ATENCIÓN] Caso automático - PAN987654321",
            descripcion="Problema con el repartidor",
            usuario_nombre="Cliente Panamá",
            usuario_telefono="+5075551234",
            tracking_code="PAN987654321",
            tipo_caso="mala atención",
            prioridad="media"
        )
        
        if resultado_panama:
            print(f"✅ Ticket Panamá creado: ID {resultado_panama.id}")
            print(f"   Cola asignada: {resultado_panama.cola_id} (debería ser 13)")
        else:
            print("❌ Error creando ticket de Panamá")
            
    except Exception as e:
        print(f"❌ Error en test Panamá: {e}")

def test_agentes_por_cola():
    """Prueba la obtención de agentes por cola"""
    print("\n👥 PRUEBA DE AGENTES POR COLA")
    print("=" * 40)
    
    # Test agentes Colombia (cola 1)
    print("\n🇨🇴 Agentes Cola 1 (Colombia):")
    try:
        agentes_colombia = obtener_agentes_servicio_cliente(1)
        print(f"   Total agentes: {len(agentes_colombia)}")
        print(f"   IDs: {agentes_colombia}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test agentes Panamá (cola 13)
    print("\n🇵🇦 Agentes Cola 13 (Panamá):")
    try:
        agentes_panama = obtener_agentes_servicio_cliente(13)
        print(f"   Total agentes: {len(agentes_panama)}")
        print(f"   IDs: {agentes_panama}")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_deteccion_pais():
    """Prueba la detección de país desde datos de tracking"""
    print("\n🔍 PRUEBA DE DETECCIÓN DE PAÍS")
    print("=" * 40)
    
    casos_prueba = [
        {'pais': 'Colombia', 'esperado': 'colombia'},
        {'pais': 'Panama', 'esperado': 'panama'},
        {'pais': 'Panamá', 'esperado': 'panama'},
        {'pais': 'PANAMA', 'esperado': 'panama'},
        {'pais': 'venezuela', 'esperado': 'colombia'},  # Default
        {'pais': None, 'esperado': 'colombia'},  # Default
    ]
    
    for caso in casos_prueba:
        pais_input = caso['pais']
        esperado = caso['esperado']
        
        # Simular lógica de detección
        pais_detectado = 'colombia'  # Default
        if pais_input:
            pais_lower = pais_input.lower()
            if 'panama' in pais_lower or 'panamá' in pais_lower:
                pais_detectado = 'panama'
        
        resultado = "✅" if pais_detectado == esperado else "❌"
        print(f"   {resultado} '{pais_input}' → {pais_detectado} (esperado: {esperado})")

def test_tracking_real():
    """Prueba con un tracking real del usuario"""
    print("\n🎯 PRUEBA CON TRACKING REAL")
    print("=" * 30)
    
    tracking_input = input("📦 Ingresa un número de tracking real para probar (Enter para omitir): ").strip()
    
    if tracking_input:
        print(f"\n🔍 Consultando tracking: {tracking_input}")
        try:
            datos = obtener_datos_tracking(tracking_input)
            print("📊 Datos obtenidos:")
            for key, value in datos.items():
                print(f"   • {key}: {value}")
            
            # Determinar a qué cola se asignaría
            pais = 'colombia'  # Default
            if datos.get('pais'):
                pais_detectado = datos['pais'].lower()
                if 'panama' in pais_detectado or 'panamá' in pais_detectado:
                    pais = 'panama'
            
            cola_id = 13 if pais == 'panama' else 1
            cola_nombre = "ServicioCliente-Panama" if pais == 'panama' else "Servicio al Cliente"
            
            print(f"\n🎯 Asignación resultante:")
            print(f"   • País detectado: {pais.title()}")
            print(f"   • Cola ID: {cola_id}")
            print(f"   • Cola nombre: {cola_nombre}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⏭️ Prueba omitida")

if __name__ == "__main__":
    print("🚀 SISTEMA DE PRUEBAS - ASIGNACIÓN POR PAÍS")
    print("=" * 50)
    
    try:
        # Ejecutar todas las pruebas
        test_deteccion_pais()
        test_agentes_por_cola()
        test_asignacion_por_pais()
        test_tracking_real()
        
        print("\n🎉 TODAS LAS PRUEBAS COMPLETADAS")
        print("=" * 50)
        print("✅ Verificar que:")
        print("   • Colombia se asigna a Cola ID 1")
        print("   • Panamá se asigna a Cola ID 13")
        print("   • Los agentes se asignan según la cola correcta")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Pruebas interrumpidas por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
