#!/usr/bin/env python3
"""
Script para limpiar archivos de prueba y desarrollo
"""

import os

def limpiar_archivos_prueba():
    """
    Elimina archivos de prueba identificados
    """
    archivos_a_eliminar = [
        "test_asignacion_especifica.py",
        "obtener_agentes.py",
        "consultar_colas_agentes.py",
        "buscar_usuario_selfx.py",
        "investigar_usuarios_colas.py",
        "consultar_colas_asignadas.py",
        "verificar_estructura.py",
        "migrate_tickets_table.py",
        "crear_tabla_manual.py",
        "setup_tickets.py",
        "TICKETS_SETUP.md",
    ]
    
    print("🧹 LIMPIEZA DE ARCHIVOS DE PRUEBA")
    print("=" * 40)
    
    eliminados = 0
    errores = 0
    
    for archivo in archivos_a_eliminar:
        try:
            if os.path.exists(archivo):
                os.remove(archivo)
                print(f"   ✅ Eliminado: {archivo}")
                eliminados += 1
            else:
                print(f"   ⚠️  No existe: {archivo}")
        except Exception as e:
            print(f"   ❌ Error eliminando {archivo}: {e}")
            errores += 1
    
    print(f"\n📊 RESULTADO:")
    print(f"   • Archivos eliminados: {eliminados}")
    print(f"   • Errores: {errores}")
    print(f"   • Total archivos procesados: {len(archivos_a_eliminar)}")
    
    if eliminados > 0:
        print(f"\n✨ ¡Limpieza completada! Proyecto listo para producción.")
    
if __name__ == "__main__":
    limpiar_archivos_prueba()
