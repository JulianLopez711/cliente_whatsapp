#!/usr/bin/env python3
"""
Script para migrar la base de datos y agregar las columnas Origen_City y Destino_City
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables de entorno
load_dotenv()

def migrar_database():
    """
    Agrega las columnas origen_city y destino_city a la tabla trackings
    """
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        if not DATABASE_URL:
            print("❌ Error: DATABASE_URL no está configurada en .env")
            return False
            
        engine = create_engine(DATABASE_URL)
        
        print("🔄 Conectando a la base de datos...")
        
        with engine.connect() as conn:
            # Verificar si las columnas ya existen
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'trackings' 
                AND column_name IN ('origen_city', 'destino_city')
            """))
            
            existing_columns = [row[0] for row in result]
            
            # Agregar origen_city si no existe
            if 'origen_city' not in existing_columns:
                print("➕ Agregando columna origen_city...")
                conn.execute(text("ALTER TABLE trackings ADD COLUMN origen_city VARCHAR"))
                conn.commit()
                print("✅ Columna origen_city agregada")
            else:
                print("✅ Columna origen_city ya existe")
            
            # Agregar destino_city si no existe
            if 'destino_city' not in existing_columns:
                print("➕ Agregando columna destino_city...")
                conn.execute(text("ALTER TABLE trackings ADD COLUMN destino_city VARCHAR"))
                conn.commit()
                print("✅ Columna destino_city agregada")
            else:
                print("✅ Columna destino_city ya existe")
        
        print("🎉 Migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def verificar_migracion():
    """
    Verifica que las columnas se hayan agregado correctamente
    """
    try:
        DATABASE_URL = os.getenv("DATABASE_URL")
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'trackings' 
                AND column_name IN ('origen_city', 'destino_city')
                ORDER BY column_name
            """))
            
            columns = list(result)
            
            if len(columns) == 2:
                print("\n📋 Columnas verificadas:")
                for col in columns:
                    print(f"   ✅ {col[0]} - {col[1]} (nullable: {col[2]})")
                return True
            else:
                print(f"❌ Error: Solo se encontraron {len(columns)} columnas de 2 esperadas")
                return False
                
    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando migración de base de datos...")
    print("=" * 50)
    
    # Ejecutar migración
    if migrar_database():
        # Verificar que todo esté correcto
        if verificar_migracion():
            print("\n🎯 La migración se completó exitosamente!")
            print("Ahora puedes usar las columnas origen_city y destino_city en tu bot.")
        else:
            print("\n⚠️  La migración se ejecutó pero hubo problemas en la verificación.")
            sys.exit(1)
    else:
        print("\n💥 La migración falló.")
        sys.exit(1)
