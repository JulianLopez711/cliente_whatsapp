#!/usr/bin/env python3
"""
Script para probar el correo con datos del tracking
"""
import sys
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from helpers import obtener_datos_tracking
from bot_logic import enviar_correo_caso
from db import SessionLocal, Usuario

def test_correo_con_tracking():
    """Prueba el sistema de correo con datos del tracking"""
    print("🧪 INICIANDO PRUEBA DE CORREO CON TRACKING")
    print("=" * 50)
    
    # Datos de prueba
    usuario_numero = "+573001234567"
    nombre_usuario = "Cliente de Prueba"
    tracking_codigo = "ABC123456789"  # Usar un tracking real de tu DB
    tipo_caso = "pedido no entregado"
    descripcion_caso = "El paquete no ha llegado después de una semana"
    
    print(f"📋 Datos de prueba:")
    print(f"   • Usuario: {nombre_usuario}")
    print(f"   • Teléfono: {usuario_numero}")
    print(f"   • Tracking: {tracking_codigo}")
    print(f"   • Tipo: {tipo_caso}")
    print(f"   • Descripción: {descripcion_caso}")
    print()
    
    # 1. Test obtener datos del tracking
    print("🔍 PASO 1: Obteniendo datos del tracking...")
    try:
        datos_tracking = obtener_datos_tracking(tracking_codigo)
        print(f"✅ Datos obtenidos:")
        print(f"   • Carrier: {datos_tracking['carrier']}")
        print(f"   • País: {datos_tracking['pais']}")
        print(f"   • Estado: {datos_tracking['estado_actual']}")
        print(f"   • Origen: {datos_tracking['origen_city']}")
        print(f"   • Destino: {datos_tracking['destino_city']}")
        print(f"   • Dirección: {datos_tracking['destino']}")
    except Exception as e:
        print(f"❌ Error obteniendo datos: {e}")
        return False
    
    print()
    
    # 2. Crear usuario de prueba
    print("👤 PASO 2: Creando usuario de prueba...")
    try:
        from helpers import get_or_create_usuario
        usuario = get_or_create_usuario(usuario_numero, nombre_usuario)
        print(f"✅ Usuario creado/obtenido: ID {usuario.id}")
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False
    
    print()
    
    # 3. Test envío de correo
    print("📧 PASO 3: Enviando correo de prueba...")
    try:
        resultado = enviar_correo_caso(
            usuario=usuario,
            tracking_code=tracking_codigo,
            tipo_caso=tipo_caso,
            descripcion=descripcion_caso,
            drive_url=None,
            imagen_guardada=None,
            datos_tracking=datos_tracking
        )
        
        print(f"✅ Proceso completado")
        
    except Exception as e:
        print(f"❌ Error enviando correo: {e}")
        return False
    
    print()
    print("🎉 PRUEBA COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print("✅ El correo debe incluir:")
    print("   • Datos del cliente")
    print("   • Información completa del envío (Carrier, País, Estado)")
    print("   • Detalles del caso")
    print("   • Formato HTML mejorado")
    print("✅ El ticket debe estar creado en la base central")
    
    return True

def test_datos_tracking_especifico():
    """Prueba con un tracking específico real"""
    print("\n🎯 PRUEBA CON TRACKING ESPECÍFICO")
    print("-" * 30)
    
    # Solicitar tracking al usuario
    tracking_input = input("📦 Ingresa un número de tracking real para probar (Enter para omitir): ").strip()
    
    if tracking_input:
        print(f"\n🔍 Consultando tracking: {tracking_input}")
        try:
            datos = obtener_datos_tracking(tracking_input)
            print("📊 Resultados:")
            for key, value in datos.items():
                print(f"   • {key}: {value}")
        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print("⏭️ Prueba omitida")

if __name__ == "__main__":
    print("🚀 SISTEMA DE PRUEBAS - CORREO CON TRACKING")
    print("=" * 50)
    
    try:
        # Ejecutar prueba principal
        exito = test_correo_con_tracking()
        
        if exito:
            # Ejecutar prueba específica
            test_datos_tracking_especifico()
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Prueba interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error general: {e}")
        import traceback
        traceback.print_exc()
