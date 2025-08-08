#!/usr/bin/env python3
"""
Script para identificar archivos de prueba vs archivos de producción
"""

import os
from pathlib import Path

def clasificar_archivos():
    """
    Clasifica archivos en producción vs prueba/desarrollo
    """
    print("🔍 CLASIFICACIÓN DE ARCHIVOS DEL PROYECTO")
    print("=" * 60)
    
    # Archivos críticos para producción
    archivos_produccion = {
        # Core del bot
        "app.py": "Aplicación principal Flask",
        "bot_logic.py": "Lógica principal del bot de WhatsApp",
        "db.py": "Modelos de base de datos y conexiones",
        "helpers.py": "Funciones helper para tickets y casos",
        
        # Módulos funcionales
        "tracking_data.py": "Consulta de datos de tracking",
        "messages.py": "Manejo de mensajes",
        "mail.py": "Envío de correos",
        "drive.py": "Integración con Google Drive",
        "state.py": "Manejo de estados de usuario",
        "utils.py": "Utilidades generales",
        
        # Configuración
        "requirements.txt": "Dependencias del proyecto",
        ".env.template": "Template de variables de entorno",
        "credentials.json.template": "Template de credenciales",
        
        # Deployment
        "whatsapp-bot.service": "Servicio systemd",
        "supervisor.conf": "Configuración de supervisor",
        "start_vps.sh": "Script de inicio en VPS",
        "install_vps.sh": "Script de instalación en VPS",
        "get_ngrok_url.sh": "Script para obtener URL de ngrok",
        
        # Documentación esencial
        "README.md": "Documentación principal",
        "deploy_vps.md": "Instrucciones de deployment",
        "FLUJO_POR_PAIS.md": "Documentación de flujos",
        
        # Migración necesaria
        "migrate_db.py": "Migración de base de datos",
        "migrate_add_cities.py": "Migración para ciudades"
    }
    
    # Archivos de prueba/desarrollo que se pueden eliminar
    archivos_prueba = {
        # Scripts de prueba específicos
        "test_tickets.py": "Prueba básica de tickets",
        "test_asignacion_automatica.py": "Prueba de asignación automática",
        "test_asignacion_especifica.py": "Prueba de asignación específica",
        "test_solicitante_selfx.py": "Prueba de solicitante selfx",
        "test_conexion_central.py": "Prueba de conexión a BD central",
        "prueba_flujo_completo.py": "Prueba de flujo completo",
        
        # Scripts de configuración/consulta
        "obtener_agentes.py": "Script para obtener agentes disponibles",
        "consultar_colas_agentes.py": "Consulta de colas y agentes",
        "buscar_usuario_selfx.py": "Buscar usuario selfx",
        "investigar_usuarios_colas.py": "Investigar relación usuarios-colas",
        "consultar_colas_asignadas.py": "Consultar tabla colas_asignadas_usuario",
        "verificar_estructura.py": "Verificar estructura de BD",
        
        # Scripts de migración/setup
        "migrate_tickets_table.py": "Migración tabla tickets",
        "crear_tabla_manual.py": "Crear tabla tickets manualmente",
        "setup_tickets.py": "Setup automático de tickets",
        
        # Documentación de setup (opcional)
        "TICKETS_SETUP.md": "Documentación setup tickets"
    }
    
    print("\n✅ ARCHIVOS DE PRODUCCIÓN (MANTENER):")
    print("-" * 40)
    for archivo, descripcion in archivos_produccion.items():
        existe = "✅" if os.path.exists(archivo) else "❌"
        print(f"   {existe} {archivo:<30} | {descripcion}")
    
    print(f"\n🧪 ARCHIVOS DE PRUEBA/DESARROLLO (ELIMINAR):")
    print("-" * 50)
    archivos_a_eliminar = []
    for archivo, descripcion in archivos_prueba.items():
        if os.path.exists(archivo):
            archivos_a_eliminar.append(archivo)
            print(f"   🗑️  {archivo:<30} | {descripcion}")
        else:
            print(f"   ❌ {archivo:<30} | {descripcion} (no existe)")
    
    print(f"\n📊 RESUMEN:")
    print(f"   • Archivos de producción: {len(archivos_produccion)}")
    print(f"   • Archivos de prueba encontrados: {len(archivos_a_eliminar)}")
    print(f"   • Espacio que se liberará: ~{len(archivos_a_eliminar) * 5}KB aprox")
    
    return archivos_a_eliminar

def crear_script_limpieza(archivos_a_eliminar):
    """
    Crea un script para eliminar archivos de prueba
    """
    script_content = """#!/usr/bin/env python3
\"\"\"
Script para limpiar archivos de prueba y desarrollo
\"\"\"

import os

def limpiar_archivos_prueba():
    \"\"\"
    Elimina archivos de prueba identificados
    \"\"\"
    archivos_a_eliminar = [
"""
    
    for archivo in archivos_a_eliminar:
        script_content += f'        "{archivo}",\n'
    
    script_content += """    ]
    
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
    
    print(f"\\n📊 RESULTADO:")
    print(f"   • Archivos eliminados: {eliminados}")
    print(f"   • Errores: {errores}")
    print(f"   • Total archivos procesados: {len(archivos_a_eliminar)}")
    
    if eliminados > 0:
        print(f"\\n✨ ¡Limpieza completada! Proyecto listo para producción.")
    
if __name__ == "__main__":
    limpiar_archivos_prueba()
"""
    
    with open("limpiar_proyecto.py", "w", encoding="utf-8") as f:
        f.write(script_content)
    
    print(f"\n📝 Script de limpieza creado: limpiar_proyecto.py")

def mostrar_instrucciones():
    """
    Muestra instrucciones finales
    """
    print(f"\n📋 INSTRUCCIONES PARA PRODUCCIÓN:")
    print("-" * 35)
    print("1. Revisar la clasificación de archivos arriba")
    print("2. Ejecutar: python limpiar_proyecto.py")
    print("3. Verificar que solo queden archivos de producción")
    print("4. Configurar variables de entorno (.env)")
    print("5. Deployar en servidor")
    
    print(f"\n🚀 ARCHIVOS MÍNIMOS PARA PRODUCCIÓN:")
    archivos_minimos = [
        "app.py", "bot_logic.py", "db.py", "helpers.py",
        "tracking_data.py", "messages.py", "mail.py", "drive.py",
        "state.py", "utils.py", "requirements.txt"
    ]
    for archivo in archivos_minimos:
        print(f"   • {archivo}")

if __name__ == "__main__":
    archivos_a_eliminar = clasificar_archivos()
    
    if archivos_a_eliminar:
        crear_script_limpieza(archivos_a_eliminar)
        
        print(f"\n❓ ¿PROCEDER CON LA LIMPIEZA?")
        print("   Esto eliminará todos los archivos de prueba identificados")
        print("   Ejecuta: python limpiar_proyecto.py")
    else:
        print(f"\n✅ No hay archivos de prueba para eliminar")
    
    mostrar_instrucciones()
