#!/usr/bin/env python3
"""
Script para crear la tabla de sesiones en la base de datos
"""
from db import engine, Base, Sesion
from sqlalchemy import inspect

def migrate():
    inspector = inspect(engine)
    
    # Verificar si la tabla ya existe
    if 'sesiones' in inspector.get_table_names():
        print("⚠️  La tabla 'sesiones' ya existe.")
        respuesta = input("¿Deseas recrearla? Esto borrará todos los datos de sesiones (y/n): ")
        if respuesta.lower() == 'y':
            print("🗑️  Eliminando tabla 'sesiones'...")
            Sesion.__table__.drop(engine)
            print("✅ Tabla eliminada.")
        else:
            print("❌ Migración cancelada.")
            return
    
    # Crear la tabla
    print("📦 Creando tabla 'sesiones'...")
    Sesion.__table__.create(engine)
    print("✅ Tabla 'sesiones' creada exitosamente!")
    print("\n📊 Estructura de la tabla:")
    print("  - id (PK)")
    print("  - numero (unique, indexed)")
    print("  - estado")
    print("  - tracking_code")
    print("  - nombre")
    print("  - pais")
    print("  - datos_temporales (JSON)")
    print("  - actualizado_en")
    print("  - creado_en")

if __name__ == "__main__":
    print("🔧 Migrando base de datos para soporte de sesiones persistentes...")
    migrate()
