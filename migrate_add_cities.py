#!/usr/bin/env python3
"""
Script de migración para agregar las columnas origen_city y destino_city a la tabla trackings
"""

import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Cargar variables del entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("❌ Error: DATABASE_URL no está configurada en .env")
    sys.exit(1)

def agregar_columnas_tracking():
    """
    Agrega las columnas origen_city y destino_city a la tabla trackings
    """
    try:
        # Crear conexión
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            print("🔗 Conectado a la base de datos...")
            
            # Verificar si las columnas ya existen
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'trackings' 
                AND column_name IN ('origen_city', 'destino_city')
            """))
            
            columnas_existentes = [row[0] for row in result]
            print(f"📋 Columnas existentes: {columnas_existentes}")
            
            # Agregar origen_city si no existe
            if 'origen_city' not in columnas_existentes:
                print("➕ Agregando columna origen_city...")
                conn.execute(text("""
                    ALTER TABLE trackings 
                    ADD COLUMN origen_city VARCHAR(255)
                """))
                conn.commit()
                print("✅ Columna origen_city agregada exitosamente")
            else:
                print("ℹ️  Columna origen_city ya existe")
            
            # Agregar destino_city si no existe
            if 'destino_city' not in columnas_existentes:
                print("➕ Agregando columna destino_city...")
                conn.execute(text("""
                    ALTER TABLE trackings 
                    ADD COLUMN destino_city VARCHAR(255)
                """))
                conn.commit()
                print("✅ Columna destino_city agregada exitosamente")
            else:
                print("ℹ️  Columna destino_city ya existe")
            
            # Verificar que las columnas se agregaron correctamente
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'trackings' 
                AND column_name IN ('origen_city', 'destino_city')
                ORDER BY column_name
            """))
            
            print("\n📊 Estado final de las columnas:")
            for row in result:
                column_name, data_type, is_nullable = row
                print(f"  • {column_name}: {data_type} (nullable: {is_nullable})")
                
        print("\n🎉 Migración completada exitosamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False

def main():
    """
    Función principal
    """
    print("🚀 MIGRACIÓN: Agregar columnas origen_city y destino_city")
    print("=" * 50)
    
    if agregar_columnas_tracking():
        print("\n✅ La migración se completó sin errores.")
        print("🔄 Puedes reiniciar la aplicación ahora.")
    else:
        print("\n❌ La migración falló.")
        print("🔍 Revisa los errores anteriores y corrige el problema.")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
