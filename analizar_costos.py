#!/usr/bin/env python3
"""
Script de análisis de costos del chatbot WhatsApp
Analiza los logs para calcular costos reales y comparar con proyecciones
"""

import re
from datetime import datetime, timedelta
from collections import defaultdict
import json

def analizar_logs_costos(archivo_log='bot.log', dias=7):
    """
    Analiza los logs del bot para calcular costos reales
    Busca líneas con el formato: 💰 [ESTADO] numero: X chars, Y seg, ~$Z
    """
    
    if not archivo_log:
        print("⚠️ Analizando logs de PM2 o terminal...")
        # Aquí podrías leer desde pm2 logs
        return analizar_logs_pm2()
    
    try:
        with open(archivo_log, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"❌ Archivo {archivo_log} no encontrado")
        return None
    
    # Estadísticas
    stats = {
        'total_mensajes': 0,
        'total_caracteres': 0,
        'total_segmentos': 0,
        'total_costo': 0.0,
        'por_estado': defaultdict(lambda: {'count': 0, 'chars': 0, 'segs': 0, 'cost': 0.0}),
        'por_usuario': defaultdict(lambda: {'count': 0, 'chars': 0, 'segs': 0, 'cost': 0.0}),
        'mensajes_largos': [],  # Mensajes >160 caracteres
        'usuarios_con_mas_mensajes': [],
    }
    
    # Patrón para detectar logs de costo
    # 💰 [ESTADO] +1234567890: 150 chars, 1 seg, ~$0.0080
    patron = r'💰 \[([^\]]+)\] ([^:]+): (\d+) chars, (\d+) seg, ~\$([0-9.]+)'
    
    for linea in lineas:
        match = re.search(patron, linea)
        if match:
            estado, numero, chars, segs, costo = match.groups()
            chars = int(chars)
            segs = int(segs)
            costo = float(costo)
            
            # Estadísticas globales
            stats['total_mensajes'] += 1
            stats['total_caracteres'] += chars
            stats['total_segmentos'] += segs
            stats['total_costo'] += costo
            
            # Por estado
            stats['por_estado'][estado]['count'] += 1
            stats['por_estado'][estado]['chars'] += chars
            stats['por_estado'][estado]['segs'] += segs
            stats['por_estado'][estado]['cost'] += costo
            
            # Por usuario
            stats['por_usuario'][numero]['count'] += 1
            stats['por_usuario'][numero]['chars'] += chars
            stats['por_usuario'][numero]['segs'] += segs
            stats['por_usuario'][numero]['cost'] += costo
            
            # Detectar mensajes largos
            if chars > 160:
                stats['mensajes_largos'].append({
                    'estado': estado,
                    'numero': numero,
                    'chars': chars,
                    'segs': segs,
                    'costo': costo
                })
    
    return stats

def generar_reporte(stats):
    """Genera un reporte legible de las estadísticas"""
    
    if not stats or stats['total_mensajes'] == 0:
        print("❌ No se encontraron datos para analizar")
        return
    
    print("=" * 60)
    print("📊 REPORTE DE ANÁLISIS DE COSTOS - CHATBOT WHATSAPP")
    print("=" * 60)
    print()
    
    # Resumen general
    print("📈 RESUMEN GENERAL")
    print("-" * 60)
    print(f"Total de mensajes enviados: {stats['total_mensajes']:,}")
    print(f"Total de caracteres: {stats['total_caracteres']:,}")
    print(f"Total de segmentos: {stats['total_segmentos']:,}")
    print(f"Costo total estimado: ${stats['total_costo']:.4f} USD")
    print()
    
    # Promedios
    if stats['total_mensajes'] > 0:
        prom_chars = stats['total_caracteres'] / stats['total_mensajes']
        prom_segs = stats['total_segmentos'] / stats['total_mensajes']
        prom_costo = stats['total_costo'] / stats['total_mensajes']
        
        print("📊 PROMEDIOS")
        print("-" * 60)
        print(f"Caracteres por mensaje: {prom_chars:.1f}")
        print(f"Segmentos por mensaje: {prom_segs:.2f}")
        print(f"Costo por mensaje: ${prom_costo:.4f} USD")
        print()
        
        # Evaluación
        print("🎯 EVALUACIÓN DE OPTIMIZACIÓN")
        print("-" * 60)
        if prom_chars < 130:
            print("✅ EXCELENTE: Promedio de caracteres muy bajo")
        elif prom_chars < 160:
            print("✅ BUENO: Promedio de caracteres dentro del objetivo")
        elif prom_chars < 200:
            print("⚠️ REGULAR: Hay espacio para optimización")
        else:
            print("❌ MEJORABLE: Mensajes demasiado largos")
        
        if prom_segs < 1.3:
            print("✅ EXCELENTE: Casi todos los mensajes en 1 segmento")
        elif prom_segs < 1.5:
            print("✅ BUENO: Mayoría de mensajes en 1 segmento")
        elif prom_segs < 2.0:
            print("⚠️ REGULAR: Muchos mensajes en 2 segmentos")
        else:
            print("❌ MEJORABLE: Demasiados segmentos por mensaje")
        print()
    
    # Top estados por costo
    print("💰 TOP 10 ESTADOS MÁS COSTOSOS")
    print("-" * 60)
    estados_ordenados = sorted(
        stats['por_estado'].items(),
        key=lambda x: x[1]['cost'],
        reverse=True
    )[:10]
    
    for i, (estado, data) in enumerate(estados_ordenados, 1):
        prom_chars_estado = data['chars'] / data['count'] if data['count'] > 0 else 0
        print(f"{i}. {estado:20} | Msgs: {data['count']:4} | "
              f"Prom: {prom_chars_estado:5.1f}c | "
              f"Costo: ${data['cost']:.4f}")
    print()
    
    # Mensajes largos
    if stats['mensajes_largos']:
        print("⚠️ MENSAJES LARGOS (>160 caracteres)")
        print("-" * 60)
        print(f"Total de mensajes largos: {len(stats['mensajes_largos'])}")
        print(f"Porcentaje: {len(stats['mensajes_largos']) / stats['total_mensajes'] * 100:.1f}%")
        
        # Top 5 más largos
        mensajes_ordenados = sorted(
            stats['mensajes_largos'],
            key=lambda x: x['chars'],
            reverse=True
        )[:5]
        
        print("\nTop 5 mensajes más largos:")
        for i, msg in enumerate(mensajes_ordenados, 1):
            print(f"{i}. {msg['estado']:20} | {msg['chars']:4}c | "
                  f"{msg['segs']} segs | ${msg['costo']:.4f}")
        print()
    
    # Top usuarios
    print("👥 TOP 10 USUARIOS CON MÁS INTERACCIONES")
    print("-" * 60)
    usuarios_ordenados = sorted(
        stats['por_usuario'].items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:10]
    
    for i, (numero, data) in enumerate(usuarios_ordenados, 1):
        print(f"{i}. {numero:15} | Msgs: {data['count']:3} | "
              f"Segs: {data['segs']:4} | Costo: ${data['cost']:.4f}")
    print()
    
    # Proyecciones
    print("📈 PROYECCIONES")
    print("-" * 60)
    
    usuarios_unicos = len(stats['por_usuario'])
    if usuarios_unicos > 0:
        costo_por_usuario = stats['total_costo'] / usuarios_unicos
        
        print(f"Usuarios únicos analizados: {usuarios_unicos}")
        print(f"Costo promedio por usuario: ${costo_por_usuario:.4f}")
        print()
        
        print("Proyección para diferentes volúmenes:")
        for volumen in [100, 500, 1000, 5000, 10000]:
            costo_proyectado = volumen * costo_por_usuario
            print(f"  {volumen:5,} usuarios/mes: ${costo_proyectado:8.2f} USD/mes "
                  f"(${costo_proyectado * 12:9.2f} USD/año)")
    print()
    
    # Comparativa con versión anterior
    print("📊 COMPARATIVA CON PROYECCIÓN ORIGINAL")
    print("-" * 60)
    
    # Valores esperados después de optimización
    chars_objetivo = 120
    segs_objetivo = 1.2
    costo_objetivo = 0.080  # Por usuario
    
    if stats['total_mensajes'] > 0:
        diferencia_chars = ((prom_chars - chars_objetivo) / chars_objetivo) * 100
        diferencia_segs = ((prom_segs - segs_objetivo) / segs_objetivo) * 100
        diferencia_costo = ((prom_costo - costo_objetivo/8) / (costo_objetivo/8)) * 100
        
        print(f"Objetivo de caracteres: {chars_objetivo}")
        print(f"Real: {prom_chars:.1f} ({diferencia_chars:+.1f}%)")
        print()
        print(f"Objetivo de segmentos: {segs_objetivo}")
        print(f"Real: {prom_segs:.2f} ({diferencia_segs:+.1f}%)")
        print()
        
        if prom_chars <= chars_objetivo and prom_segs <= segs_objetivo:
            print("🎉 ¡FELICIDADES! Has alcanzado los objetivos de optimización")
        elif prom_chars <= chars_objetivo * 1.2:
            print("✅ Muy cerca de los objetivos. Pequeños ajustes pueden mejorar más")
        else:
            print("⚠️ Aún hay oportunidad de optimización. Revisa los estados más costosos")
    
    print()
    print("=" * 60)

def analizar_logs_pm2():
    """
    Analiza logs directamente desde PM2
    """
    import subprocess
    
    try:
        # Obtener logs de PM2
        result = subprocess.run(
            ['pm2', 'logs', 'whatsapp-bot', '--lines', '1000', '--nostream'],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("❌ Error al obtener logs de PM2")
            return None
        
        # Procesar logs como si fueran de archivo
        lineas = result.stdout.split('\n')
        
        # El resto del procesamiento es similar a analizar_logs_costos
        # ... (implementar si es necesario)
        
    except FileNotFoundError:
        print("❌ PM2 no está instalado o no está en el PATH")
        return None

def comparar_periodos(archivo_anterior, archivo_actual):
    """
    Compara dos periodos de logs para ver la mejora
    """
    print("🔄 Comparando periodos...")
    print()
    
    stats_anterior = analizar_logs_costos(archivo_anterior)
    stats_actual = analizar_logs_costos(archivo_actual)
    
    if not stats_anterior or not stats_actual:
        print("❌ No se pudieron cargar ambos periodos")
        return
    
    print("📊 COMPARATIVA DE PERIODOS")
    print("=" * 60)
    
    # Calcular diferencias
    diff_mensajes = stats_actual['total_mensajes'] - stats_anterior['total_mensajes']
    diff_costo = stats_actual['total_costo'] - stats_anterior['total_costo']
    
    prom_chars_ant = stats_anterior['total_caracteres'] / stats_anterior['total_mensajes']
    prom_chars_act = stats_actual['total_caracteres'] / stats_actual['total_mensajes']
    
    prom_segs_ant = stats_anterior['total_segmentos'] / stats_anterior['total_mensajes']
    prom_segs_act = stats_actual['total_segmentos'] / stats_actual['total_mensajes']
    
    print(f"Periodo anterior: {stats_anterior['total_mensajes']:,} mensajes")
    print(f"Periodo actual: {stats_actual['total_mensajes']:,} mensajes")
    print(f"Diferencia: {diff_mensajes:+,} mensajes")
    print()
    
    print(f"Caracteres promedio: {prom_chars_ant:.1f} → {prom_chars_act:.1f} "
          f"({((prom_chars_act - prom_chars_ant) / prom_chars_ant * 100):+.1f}%)")
    print(f"Segmentos promedio: {prom_segs_ant:.2f} → {prom_segs_act:.2f} "
          f"({((prom_segs_act - prom_segs_ant) / prom_segs_ant * 100):+.1f}%)")
    print()
    
    print(f"Costo total: ${stats_anterior['total_costo']:.4f} → ${stats_actual['total_costo']:.4f}")
    print(f"Diferencia: ${diff_costo:+.4f} ({(diff_costo / stats_anterior['total_costo'] * 100):+.1f}%)")
    print()
    
    if diff_costo < 0:
        print(f"🎉 ¡Ahorro logrado! ${abs(diff_costo):.4f} USD")
    elif diff_costo > 0:
        print(f"⚠️ Incremento de costo: ${diff_costo:.4f} USD")
    
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    print("🤖 Analizador de Costos - Chatbot WhatsApp")
    print()
    
    if len(sys.argv) > 1:
        archivo_log = sys.argv[1]
        stats = analizar_logs_costos(archivo_log)
    else:
        # Intentar con nombre por defecto
        stats = analizar_logs_costos('bot.log')
        
        if not stats:
            print("💡 Uso: python analizar_costos.py [archivo_log]")
            print()
            print("Sin archivo especificado, buscando logs comunes...")
            
            # Intentar ubicaciones comunes
            ubicaciones = [
                'bot.log',
                'app.log',
                '/var/log/whatsapp-bot.log',
                '~/.pm2/logs/whatsapp-bot-out.log'
            ]
            
            for ubicacion in ubicaciones:
                stats = analizar_logs_costos(ubicacion)
                if stats:
                    print(f"✅ Logs encontrados en: {ubicacion}")
                    break
    
    if stats:
        generar_reporte(stats)
        
        # Guardar reporte en JSON
        with open('reporte_costos.json', 'w') as f:
            # Convertir defaultdict a dict normal
            stats_json = {
                'total_mensajes': stats['total_mensajes'],
                'total_caracteres': stats['total_caracteres'],
                'total_segmentos': stats['total_segmentos'],
                'total_costo': stats['total_costo'],
                'por_estado': dict(stats['por_estado']),
                'por_usuario': dict(stats['por_usuario']),
                'timestamp': datetime.now().isoformat()
            }
            json.dump(stats_json, f, indent=2)
        
        print("💾 Reporte guardado en: reporte_costos.json")
    else:
        print("❌ No se pudieron analizar los logs")
        print()
        print("Asegúrate de:")
        print("1. Que el bot esté implementado con logging de costos")
        print("2. Que exista el archivo de logs")
        print("3. Que el formato de logs sea correcto (💰 [ESTADO] ...)")
