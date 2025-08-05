#!/usr/bin/env python3
"""
Script de prueba para verificar que los trackings se guardan correctamente en la base de datos
"""

from helpers import get_or_create_usuario, crear_o_actualizar_tracking, obtener_trackings_usuario
from tracking_data import consultar_estado
from db import SessionLocal

def probar_guardar_tracking():
    """
    Simula el flujo de que un usuario proporciona un tracking válido
    """
    print("🔍 Probando el guardado de trackings en la base de datos...\n")
    
    # Simular datos de usuario
    numero_telefono = "+573001234567"
    nombre_usuario = "Usuario Prueba"
    codigo_tracking = "6544573856984798"  # Tracking que sabemos que funciona
    
    # 1. Crear o obtener usuario
    print(f"👤 Creando usuario: {nombre_usuario} ({numero_telefono})")
    usuario = get_or_create_usuario(numero_telefono, nombre_usuario)
    print(f"✅ Usuario creado/obtenido con ID: {usuario.id}")
    
    # 2. Consultar datos del tracking en BigQuery
    print(f"\n📦 Consultando tracking: {codigo_tracking}")
    datos_tracking = consultar_estado(codigo_tracking)
    
    if datos_tracking:
        print("✅ Tracking encontrado en BigQuery:")
        print(f"   Estado: {datos_tracking.get('estado')}")
        print(f"   Destino: {datos_tracking.get('destino')}")
        print(f"   Dirección: {datos_tracking.get('direccion')}")
        print(f"   Origen City: {datos_tracking.get('origen_city')}")  # ✅ NUEVO
        print(f"   Destino City: {datos_tracking.get('destino_city')}")  # ✅ NUEVO
        
        # 3. Guardar tracking en la base de datos
        print(f"\n💾 Guardando tracking en la base de datos...")
        tracking_db = crear_o_actualizar_tracking(
            usuario_id=usuario.id,
            codigo_tracking=codigo_tracking,
            estado=datos_tracking.get('estado'),
            direccion=datos_tracking.get('direccion'),
            origen_city=datos_tracking.get('origen_city'),  # ✅ NUEVO
            destino_city=datos_tracking.get('destino_city')  # ✅ NUEVO
        )
        print(f"✅ Tracking guardado con ID: {tracking_db.id}")
        
        # 4. Verificar que se guardó correctamente
        print(f"\n🔎 Verificando trackings del usuario...")
        trackings_usuario = obtener_trackings_usuario(usuario.id)
        print(f"✅ Usuario tiene {len(trackings_usuario)} tracking(s) registrado(s)")
        
        for tracking in trackings_usuario:
            print(f"   📋 ID: {tracking.id}")
            print(f"   📦 Código: {tracking.codigo}")
            print(f"   📍 Estado: {tracking.estado}")
            print(f"   🏠 Dirección: {tracking.direccion}")
            print(f"   🚀 Origen City: {tracking.origen_city}")  # ✅ NUEVO
            print(f"   📍 Destino City: {tracking.destino_city}")  # ✅ NUEVO
            print(f"   ✅ Activo: {tracking.activo}")
            print()
            
    else:
        print("❌ No se encontró el tracking en BigQuery")
        return False
    
    return True

def verificar_tabla_trackings():
    """
    Consulta directa a la tabla trackings para verificar los datos
    """
    print("\n📊 Consultando tabla trackings directamente...")
    db = SessionLocal()
    try:
        from db import Tracking
        trackings = db.query(Tracking).all()
        
        if trackings:
            print(f"✅ Se encontraron {len(trackings)} registros en la tabla trackings:")
            for tracking in trackings:
                print(f"   ID: {tracking.id} | Usuario ID: {tracking.usuario_id} | Código: {tracking.codigo}")
                print(f"   Estado: {tracking.estado} | Activo: {tracking.activo}")
                print(f"   Origen: {tracking.origen_city} | Destino: {tracking.destino_city}")  # ✅ NUEVO
                print()
        else:
            print("❌ La tabla trackings está vacía")
            
    except Exception as e:
        print(f"❌ Error al consultar la tabla: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 PRUEBA DE GUARDADO DE TRACKINGS EN BASE DE DATOS")
    print("=" * 60)
    
    # Verificar estado inicial
    verificar_tabla_trackings()
    
    # Ejecutar prueba
    if probar_guardar_tracking():
        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("=" * 60)
        
        # Verificar estado final
        verificar_tabla_trackings()
    else:
        print("\n" + "=" * 60)
        print("❌ PRUEBA FALLÓ")
        print("=" * 60)
