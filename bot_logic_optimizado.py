# ========================================
# VERSIÓN OPTIMIZADA DE bot_logic.py
# Cambios principales:
# 1. Mensajes de estado más cortos
# 2. Límite de reintentos para opciones inválidas
# 3. Validaciones simplificadas
# 4. Logging de costos por mensaje
# ========================================

import re
import os
from datetime import datetime
from mail import enviar_correo
from tracking_data import consultar_estado
from state import (
    get_estado, set_estado, set_tracking, get_tracking,
    reset_usuario, set_nombre, get_nombre,
    set_estado_temporal, get_estado_temporal,
    set_pais, get_pais
)

# USAR MENSAJES OPTIMIZADOS
from messages_optimizado import (
    MENSAJE_BIENVENIDA,
    MENSAJE_OPCION_INVALIDA,
    MENSAJE_PEDIR_TRACKING,
    MENSAJE_TRACKING_INVALIDO,
    MENSAJE_ENTREGADO_NO_RECIBIDO,
    MENSAJE_CAMBIO_DATOS,
    MENSAJE_MALA_ATENCION,
    MENSAJE_COBRO_INCORRECTO,
    MENSAJE_PEDIDO_INCOMPLETO,
    MENSAJE_DEVOLUCION,
    MENSAJE_MENU_ENTREGA,
    MENSAJE_ESPERA_AGENTE,
    MENSAJE_PEDIR_DESCRIPCION,
    MENSAJE_PREGUNTAR_EVIDENCIA,
    MENSAJE_CASO_CONFIRMADO,
    MENSAJE_TRANSITO_INTERNACIONAL,
    MENSAJE_TIENDA_NO_ENTREGADO,
    MENSAJE_RECOGIDA_PEDIDO,
    MENSAJE_VOLVER_MENU,
    MENSAJE_CONVERSACION_FINALIZADA,
    MENSAJE_ENVIAR_IMAGEN,
    MENSAJE_OPCION_IMAGEN_INVALIDA,
    MENSAJE_OPCION_CONTINUAR_INVALIDA,
    MENSAJE_OPCION_NO_DISPONIBLE,
    MENSAJE_RECOGIDA_NO_DISPONIBLE,
    MENSAJE_ERROR_GENERAL,
    ESTADOS_TRADUCIDOS,
    get_mensajes_pais
)
from helpers import (
    get_or_create_usuario, 
    registrar_mensaje, 
    crear_caso, 
    crear_o_actualizar_tracking, 
    crear_ticket_central,
    incrementar_reintentos,
    resetear_reintentos,
    obtener_reintentos
)
from drive import subir_a_drive

# ========================================
# FUNCIÓN PARA LOGGING DE COSTOS
# ========================================

def log_costo_mensaje(numero, mensaje, estado):
    """
    Calcula y registra el costo estimado por mensaje
    160 caracteres = 1 segmento
    Costo estimado: $0.008 USD por segmento
    """
    longitud = len(mensaje)
    segmentos = (longitud // 160) + 1
    costo_estimado = segmentos * 0.008  # USD
    
    print(f"💰 [{estado}] {numero}: {longitud} chars, {segmentos} seg, ~${costo_estimado:.4f}")
    
    return {
        'longitud': longitud,
        'segmentos': segmentos,
        'costo_estimado': costo_estimado
    }

# ========================================
# FUNCIONES AUXILIARES (SIN CAMBIOS)
# ========================================

def detectar_pais_desde_datos(datos):
    """Detecta el país desde los datos de BigQuery"""
    if not datos:
        return "Colombia"
    pais = datos.get("pais", "").strip()
    if pais.lower() in ["panama", "panamá"]:
        return "panama"
    return "colombia"

def es_saludo(mensaje):
    texto = mensaje.lower()
    saludos = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches", "hi", "hello", "holi", "saludos", "qué tal"]
    return any(re.search(rf"\\b{re.escape(p)}\\b", texto) for p in saludos)

def traducir_estado(estado_paquete):
    """Traduce el estado del paquete (versión simplificada)"""
    if not estado_paquete or estado_paquete == "No disponible":
        return "No disponible"
    
    codigo_match = re.match(r'^(\\d+)', str(estado_paquete).strip())
    if codigo_match:
        codigo = codigo_match.group(1)
        if codigo in ESTADOS_TRADUCIDOS:
            return ESTADOS_TRADUCIDOS[codigo]
    
    return str(estado_paquete)

# ========================================
# FUNCIÓN PRINCIPAL OPTIMIZADA
# ========================================

def aplicar_flujo_por_pais(pais, nombre, tracking_code, datos):
    """
    Versión OPTIMIZADA con mensaje más corto
    Antes: ~250 caracteres (2 segmentos)
    Después: ~120 caracteres (1 segmento)
    Ahorro: 50%
    """
    estado_paquete = datos.get("estado", "No disponible")
    origen_city = datos.get("origen_city", "Origen")
    destino_city = datos.get("destino_city", "Destino")
    
    fecha_estado = datos.get("fecha_estado", "")
    if fecha_estado and fecha_estado != "No disponible":
        try:
            if isinstance(fecha_estado, str):
                fecha_formateada = fecha_estado[:16]  # Solo fecha corta
            else:
                fecha_formateada = fecha_estado.strftime("%d/%m %H:%M")
        except:
            fecha_formateada = ""
    else:
        fecha_formateada = ""
    
    # Mensaje corto y conciso
    respuesta = f"""Guía {tracking_code}
Estado: {traducir_estado(estado_paquete)}
{origen_city} → {destino_city}"""
    
    if fecha_formateada:
        respuesta += f"\nÚlt. act.: {fecha_formateada}"
    
    respuesta += f"\n\n{nombre}, ¿algo más?\n1. Menú\n2. Salir"
    
    return respuesta

def get_mensaje_devolucion_por_pais(pais):
    """Obtiene el mensaje de devolución específico del país"""
    mensajes_pais = get_mensajes_pais(pais)
    return mensajes_pais["devolucion"]

def get_mensaje_recogida_por_pais(pais, tracking_code):
    """Obtiene el mensaje de recogida específico del país"""
    mensajes_pais = get_mensajes_pais(pais)
    return mensajes_pais["recogida_disponible"].format(tracking=tracking_code)

# ========================================
# PROCESADOR DE MENSAJES CON CONTROL DE REINTENTOS
# ========================================

def procesar_mensaje(numero, mensaje, imagen_guardada=None):
    estado = get_estado(numero)
    mensaje = mensaje.strip()
    
    print(f"📱 {numero} | Estado: {estado} | Mensaje: {mensaje}")

    usuario = get_or_create_usuario(numero)
    registrar_mensaje(usuario.id, mensaje, tipo="entrada")

    respuesta = ""

    # ========================================
    # INICIO
    # ========================================
    if estado == "INICIO":
        resetear_reintentos(numero)  # Reset contador
        if es_saludo(mensaje):
            set_estado(numero, "PEDIR_NOMBRE")
            respuesta = "Hola! ¿Cuál es tu nombre?"
        else:
            set_estado(numero, "PEDIR_NOMBRE")
            respuesta = "Hola! ¿Cuál es tu nombre?"

    # ========================================
    # PEDIR NOMBRE
    # ========================================
    elif estado == "PEDIR_NOMBRE":
        nombre = mensaje.title()
        set_nombre(numero, nombre)
        usuario = get_or_create_usuario(numero, nombre)
        set_estado(numero, "ESPERANDO_TRACKING")
        respuesta = f"Gracias {nombre}! {MENSAJE_PEDIR_TRACKING}"

    # ========================================
    # ESPERANDO TRACKING
    # ========================================
    elif estado == "ESPERANDO_TRACKING":
        if mensaje.isalnum() and 8 <= len(mensaje) <= 25:
            tracking = mensaje
            datos = consultar_estado(tracking)
            if datos:
                pais_detectado = detectar_pais_desde_datos(datos)
                set_pais(numero, pais_detectado)
                set_tracking(numero, tracking)
                
                nombre = get_nombre(numero) or ""
                usuario = get_or_create_usuario(numero, nombre)
                
                estado_paquete = datos.get("estado", "No disponible")
                direccion = datos.get("direccion", "")
                origen_city = datos.get("origen_city", "")
                destino_city = datos.get("destino_city", "")
                
                crear_o_actualizar_tracking(
                    usuario_id=usuario.id,
                    codigo_tracking=tracking,
                    estado=estado_paquete,
                    direccion=direccion,
                    origen_city=origen_city,
                    destino_city=destino_city
                )
                
                set_estado(numero, "MENU_PRINCIPAL")
                resetear_reintentos(numero)  # Reset contador
                respuesta = f"Guía {tracking} registrada.\n\n{MENSAJE_VOLVER_MENU}"
            else:
                respuesta = f"No encontramos la guía {tracking}. Verifica e intenta de nuevo."
        else:
            respuesta = MENSAJE_TRACKING_INVALIDO

    # ========================================
    # MENÚ PRINCIPAL CON LÍMITE DE REINTENTOS
    # ========================================
    elif estado == "MENU_PRINCIPAL":
        if not mensaje.isdigit() or mensaje not in ["1", "2", "3"]:
            # Incrementar contador de reintentos
            reintentos = incrementar_reintentos(numero)
            
            if reintentos >= 3:
                # Después de 3 intentos, mensaje corto y reset
                reset_usuario(numero)
                respuesta = "Demasiados intentos. Escribe 'hola' para reiniciar."
            else:
                nombre = get_nombre(numero) or ""
                respuesta = f"{nombre}, opción inválida.\n\n{MENSAJE_VOLVER_MENU}"
        else:
            resetear_reintentos(numero)  # Reset al seleccionar opción válida
            
            if mensaje == "1":
                set_estado(numero, "MENU_ENTREGA")
                respuesta = MENSAJE_MENU_ENTREGA
            elif mensaje == "2":
                pais_guardado = get_pais(numero)
                mensaje_devolucion = get_mensaje_devolucion_por_pais(pais_guardado)
                set_estado(numero, "PREGUNTA_CONTINUAR")
                respuesta = mensaje_devolucion
            elif mensaje == "3":
                tracking_code = get_tracking(numero)
                datos = consultar_estado(tracking_code)
                
                if datos:
                    nombre = get_nombre(numero) or ""
                    pais_guardado = get_pais(numero)
                    if not pais_guardado:
                        pais_detectado = detectar_pais_desde_datos(datos)
                        set_pais(numero, pais_detectado)
                    else:
                        pais_detectado = pais_guardado
                    
                    respuesta = aplicar_flujo_por_pais(pais_detectado, nombre, tracking_code, datos)
                    set_estado(numero, "PREGUNTA_CONTINUAR")
                else:
                    set_estado(numero, "ESPERANDO_TRACKING")
                    respuesta = f"No encontramos info de guía {tracking_code}. Ingresa nuevamente."

    # ========================================
    # MENÚ ENTREGA CON LÍMITE DE REINTENTOS
    # ========================================
    elif estado == "MENU_ENTREGA":
        if not mensaje.isdigit() or mensaje not in ["1", "2", "3", "4", "5", "6"]:
            reintentos = incrementar_reintentos(numero)
            
            if reintentos >= 3:
                reset_usuario(numero)
                respuesta = "Demasiados intentos. Escribe 'hola' para reiniciar."
            else:
                respuesta = f"Opción inválida.\n\n{MENSAJE_MENU_ENTREGA}"
        else:
            resetear_reintentos(numero)
            
            tracking_code = get_tracking(numero)
            datos = consultar_estado(tracking_code)
            if not datos:
                set_estado(numero, "ESPERANDO_TRACKING")
                respuesta = f"No encontramos guía {tracking_code}. Ingresa nuevamente."
            else:
                tipo_caso = None
                if mensaje == "1":
                    tipo_caso = "pedido no entregado"
                elif mensaje == "2":
                    set_estado(numero, "PREGUNTA_CONTINUAR")
                    respuesta = MENSAJE_CAMBIO_DATOS
                elif mensaje == "3":
                    pais_guardado = get_pais(numero)
                    if pais_guardado == "panama":
                        mensaje_recogida = get_mensaje_recogida_por_pais(pais_guardado, tracking_code)
                        set_estado(numero, "PREGUNTA_CONTINUAR")
                        respuesta = mensaje_recogida
                    else:
                        set_estado(numero, "PREGUNTA_CONTINUAR")
                        respuesta = MENSAJE_RECOGIDA_NO_DISPONIBLE
                elif mensaje == "4":
                    tipo_caso = "mala atención"
                elif mensaje == "5":
                    tipo_caso = "cobro no reconocido"
                elif mensaje == "6":
                    tipo_caso = "pedido incompleto"
                
                if tipo_caso:
                    set_estado_temporal(numero, "tipo_caso", tipo_caso)
                    set_estado(numero, "DESCRIBIR_CASO")
                    respuesta = MENSAJE_PEDIR_DESCRIPCION

    # ========================================
    # DESCRIBIR CASO
    # ========================================
    elif estado == "DESCRIBIR_CASO":
        set_estado_temporal(numero, "descripcion", mensaje)
        set_estado(numero, "PREGUNTAR_EVIDENCIA")
        respuesta = MENSAJE_PREGUNTAR_EVIDENCIA

    # ========================================
    # PREGUNTAR EVIDENCIA
    # ========================================
    elif estado == "PREGUNTAR_EVIDENCIA":
        if mensaje == "1":
            set_estado(numero, "ESPERANDO_IMAGEN")
            respuesta = MENSAJE_ENVIAR_IMAGEN
        elif mensaje == "2":
            tipo_caso = get_estado_temporal(numero, "tipo_caso")
            descripcion = get_estado_temporal(numero, "descripcion")
            tracking_code = get_tracking(numero)
            
            nombre = get_nombre(numero)
            usuario_actualizado = get_or_create_usuario(numero, nombre)

            crear_caso(
                usuario_id=usuario_actualizado.id,
                tracking_id=None,
                tipo=tipo_caso,
                descripcion=descripcion,
                telefono=numero,
                imagen_url=None
            )

            enviar_correo_caso(usuario_actualizado, tracking_code, tipo_caso, descripcion, None)

            set_estado(numero, "PREGUNTA_CONTINUAR")
            respuesta = MENSAJE_CASO_CONFIRMADO
        else:
            respuesta = MENSAJE_OPCION_IMAGEN_INVALIDA

    # ========================================
    # ESPERANDO IMAGEN
    # ========================================
    elif estado == "ESPERANDO_IMAGEN":
        tipo_caso = get_estado_temporal(numero, "tipo_caso")
        descripcion = get_estado_temporal(numero, "descripcion")
        tracking_code = get_tracking(numero)
        drive_url = None

        if imagen_guardada:
            drive_url = subir_a_drive(imagen_guardada)

        nombre = get_nombre(numero)
        usuario_actualizado = get_or_create_usuario(numero, nombre)

        crear_caso(
            usuario_id=usuario_actualizado.id,
            tracking_id=None,
            tipo=tipo_caso,
            descripcion=descripcion,
            telefono=numero,
            imagen_url=drive_url
        )

        enviar_correo_caso(usuario_actualizado, tracking_code, tipo_caso, descripcion, drive_url, imagen_guardada)

        set_estado(numero, "PREGUNTA_CONTINUAR")
        respuesta = MENSAJE_CASO_CONFIRMADO

    # ========================================
    # PREGUNTA CONTINUAR
    # ========================================
    elif estado == "PREGUNTA_CONTINUAR":
        if not mensaje.isdigit() or mensaje not in ["1", "2"]:
            reintentos = incrementar_reintentos(numero)
            
            if reintentos >= 3:
                reset_usuario(numero)
                respuesta = MENSAJE_CONVERSACION_FINALIZADA
            else:
                nombre = get_nombre(numero) or ""
                respuesta = f"{nombre}, responde:\n1. Menú\n2. Salir"
        else:
            resetear_reintentos(numero)
            
            if mensaje == "1":
                set_estado(numero, "MENU_PRINCIPAL")
                respuesta = MENSAJE_VOLVER_MENU
            elif mensaje == "2":
                reset_usuario(numero)
                respuesta = MENSAJE_CONVERSACION_FINALIZADA

    else:
        reset_usuario(numero)
        respuesta = MENSAJE_ERROR_GENERAL

    # ========================================
    # LOGGING DE COSTOS
    # ========================================
    log_costo_mensaje(numero, respuesta, estado)

    return respuesta

# ========================================
# ENVÍO DE CORREO (SIN CAMBIOS FUNCIONALES)
# ========================================

def enviar_correo_caso(usuario, tracking_code, tipo_caso, descripcion, drive_url=None, imagen_guardada=None, datos_tracking=None):
    """Envía correo de notificación y crea ticket"""
    try:
        from helpers import obtener_datos_tracking
        
        if not datos_tracking:
            datos_tracking = obtener_datos_tracking(tracking_code)
        
        asunto = f"[{tipo_caso.upper()}] Caso - {tracking_code}"

        cuerpo = f"""Nuevo caso desde WhatsApp

Cliente: {usuario.nombre or 'No disponible'}
Teléfono: {usuario.numero}
Tracking: {tracking_code}

Tipo: {tipo_caso.title()}
Descripción: {descripcion}

Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""

        if drive_url:
            cuerpo += f"\nEvidencia: {drive_url}"

        adjuntos = []
        if imagen_guardada and os.path.exists(imagen_guardada) and not drive_url:
            adjuntos = [imagen_guardada]

        enviar_correo(asunto, cuerpo, adjuntos=adjuntos)

        determinar_prioridad_caso = {
            "pedido no entregado": "alta",
            "mala atención": "media", 
            "cobro no reconocido": "alta",
            "pedido incompleto": "alta"
        }
        
        prioridad = determinar_prioridad_caso.get(tipo_caso, "media")
        
        crear_ticket_central(
            asunto=asunto,
            descripcion=descripcion,
            usuario_nombre=usuario.nombre,
            usuario_telefono=usuario.numero,
            tracking_code=tracking_code,
            tipo_caso=tipo_caso,
            prioridad=prioridad,
            imagen_url=drive_url
        )

        print(f"✅ Correo enviado y ticket creado: {tipo_caso} - {tracking_code}")

    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
