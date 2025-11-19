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
from messages import (
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
from helpers import get_or_create_usuario, registrar_mensaje, crear_caso, crear_o_actualizar_tracking, crear_ticket_central
from drive import subir_a_drive

def detectar_pais_desde_datos(datos):
    """
    Detecta el país desde los datos de BigQuery
    """
    if not datos:
        return "Colombia"  # Por defecto
        
    pais = datos.get("pais", "").strip()
    if pais.lower() in ["panama", "panamá"]:
        return "panama"
    else:
        return "colombia"

def aplicar_flujo_por_pais(pais, nombre, tracking_code, datos):
    """
    Aplica el flujo específico según el país detectado
    """
    mensajes_pais = get_mensajes_pais(pais)
    
    # Datos comunes
    estado_paquete = datos.get("estado", "No disponible")
    fecha_estado = datos.get("fecha_estado", "No disponible")
    destino = datos.get("destino", "No disponible")
    origen_city = datos.get("origen_city", "Origen")
    destino_city = datos.get("destino_city", destino)
    
    # Formatear fecha
    if fecha_estado and fecha_estado != "No disponible":
        try:
            if isinstance(fecha_estado, str):
                fecha_formateada = fecha_estado
            else:
                fecha_formateada = fecha_estado.strftime("%d/%m/%Y %H:%M")
        except:
            fecha_formateada = str(fecha_estado)
    else:
        fecha_formateada = "No disponible"
    
    # Mensaje base personalizado por país
    if pais == "panama":
        emoji_bandera = "🇵🇦"
        prefijo_pais = "Panamá"
    else:
        emoji_bandera = "🇨🇴"
        prefijo_pais = "Colombia"
    
    respuesta = f"""{emoji_bandera} *Estado de tu guía {tracking_code} - {prefijo_pais}*

📦 *Estado:* {traducir_estado(estado_paquete)}
🚀 *Origen:* {origen_city}
📍 *Destino:* {destino_city}
📅 *Última actualización:* {fecha_formateada}

{nombre}, ¿te puedo ayudar en algo más?
1️⃣ Sí, volver al menú principal
2️⃣ No, finalizar conversación"""
    
    return respuesta

def get_mensaje_devolucion_por_pais(pais):
    """
    Obtiene el mensaje de devolución específico del país
    """
    mensajes_pais = get_mensajes_pais(pais)
    return mensajes_pais["devolucion"]

def get_mensaje_recogida_por_pais(pais, tracking_code):
    """
    Obtiene el mensaje de recogida específico del país
    """
    mensajes_pais = get_mensajes_pais(pais)
    return mensajes_pais["recogida_disponible"].format(tracking=tracking_code)

def es_saludo(mensaje):
    texto = mensaje.lower()
    saludos = ["hola", "buenas", "buenos días", "buenas tardes", "buenas noches", "hi", "hello", "holi", "saludos", "qué tal"]
    return any(re.search(rf"\\b{re.escape(p)}\\b", texto) for p in saludos)

def traducir_estado(estado_paquete):
    """
    Traduce el estado del paquete a un mensaje amigable para el usuario
    Extrae el código numérico del estado y busca su traducción
    """
    if not estado_paquete or estado_paquete == "No disponible":
        return "📦 Estado no disponible"
    
    # Extraer código numérico del estado (ej: "102 - Disponible en centro" -> "102")
    codigo_match = re.match(r'^(\d+)', str(estado_paquete).strip())
    if codigo_match:
        codigo = codigo_match.group(1)
        if codigo in ESTADOS_TRADUCIDOS:
            return ESTADOS_TRADUCIDOS[codigo]
        else:
            # Log para estados no reconocidos (útil para agregar nuevos estados)
            print(f"⚠️ Estado no reconocido: {codigo} - {estado_paquete}")
    
    # Si no encontramos traducción, verificar estados específicos por texto
    estado_lower = str(estado_paquete).lower()
    if "contenerizado" in estado_lower and "devolucion" not in estado_lower:
        return "🚢 En tránsito marítimo"
    elif "descontenerizado" in estado_lower:
        return "✈️ Paquete arribó al destino"
    elif "entregado" in estado_lower:
        return "✅ Paquete entregado exitosamente"
    elif "transito" in estado_lower or "tránsito" in estado_lower:
        return "🚛 Paquete en tránsito"
    elif "retenido" in estado_lower:
        return "🚨 Paquete retenido - Contacta atención al cliente"
    elif "devolucion" in estado_lower or "devolución" in estado_lower:
        return "🔄 En proceso de devolución"
    
    # Fallback: mostrar el estado original con formato mejorado
    print(f"⚠️ Estado sin traducción específica: {estado_paquete}")
    return f"📦 {estado_paquete}"

def obtener_estado_legible(codigo_estado, descripcion_estado=""):
    """
    Función auxiliar para obtener un estado legible
    Útil para logging y debugging
    """
    if codigo_estado in ESTADOS_TRADUCIDOS:
        return ESTADOS_TRADUCIDOS[codigo_estado]
    return f"Estado {codigo_estado}: {descripcion_estado}" if descripcion_estado else f"Estado {codigo_estado}"

def procesar_mensaje(numero, mensaje, imagen_guardada=None):
    estado = get_estado(numero)
    mensaje = mensaje.strip()
    
    # 🔍 Log de depuración
    print(f"📱 {numero} | Estado: {estado} | Mensaje: {mensaje}")

    usuario = get_or_create_usuario(numero)
    registrar_mensaje(usuario.id, mensaje, tipo="entrada")

    if estado == "INICIO":
        if es_saludo(mensaje):
            set_estado(numero, "PEDIR_NOMBRE")
            return "👋 ¡Hola!  ¿Cuál es tu nombre para poder ayudarte mejor?"
        else:
            set_estado(numero, "PEDIR_NOMBRE")
            return "👋 ¡Hola!  Parece que deseas ayuda. ¿Cuál es tu nombre?"

    elif estado == "PEDIR_NOMBRE":
        nombre = mensaje.title()
        set_nombre(numero, nombre)
        
        # Log de confirmación
        print(f"✅ Nombre guardado: {nombre} para {numero}")
        
        # Actualizar el usuario en la base de datos con el nombre
        usuario = get_or_create_usuario(numero, nombre)
        
        set_estado(numero, "ESPERANDO_TRACKING")
        return f"¡Gracias {nombre}! 😊\n\n{MENSAJE_PEDIR_TRACKING}"

    elif estado == "ESPERANDO_TRACKING":
        if mensaje.isalnum() and 8 <= len(mensaje) <= 25:
            tracking = mensaje
            datos = consultar_estado(tracking)
            if datos:
                # Detectar y guardar país del usuario
                pais_detectado = detectar_pais_desde_datos(datos)
                set_pais(numero, pais_detectado)
                
                # Guardar tracking en memoria para la sesión actual
                set_tracking(numero, tracking)
                
                # Obtener usuario actual
                nombre = get_nombre(numero) or ""
                usuario = get_or_create_usuario(numero, nombre)
                
                # Guardar tracking en la base de datos
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
                return (
                    f"✅ ¡Gracias {nombre}! Número de guía registrado correctamente.\n\n"
                    "Selecciona la opción que deseas consultar:\n"
                    "1️⃣ Tengo una novedad con una entrega\n"
                    "2️⃣ Tengo una novedad con una devolución\n"
                    "3️⃣ Consultar estado de mi guía\n\n"
                )
            else:
                return (
                    f"❗ No encontramos información con el número de guía *{tracking}*.\n"
                    "📦 Verifica que esté correcto e ingrésalo nuevamente."
                )
        else:
            return MENSAJE_TRACKING_INVALIDO

    elif estado == "MENU_PRINCIPAL":
        # Validar que sea un número entre 1 y 3
        if not mensaje.isdigit() or mensaje not in ["1", "2", "3"]:
            nombre = get_nombre(numero) or ""
            return (
                f"{nombre}, por favor selecciona una opción válida:\n\n"
                "1️⃣ Tengo una novedad con una entrega\n"
                "2️⃣ Tengo una novedad con una devolución\n"
                "3️⃣ Consultar estado de mi guía"
            )
        
        if mensaje == "1":
            set_estado(numero, "MENU_ENTREGA")
            return MENSAJE_MENU_ENTREGA
        elif mensaje == "2":
            # Usar país guardado en sesión o consultar datos si es necesario
            pais_guardado = get_pais(numero)
            mensaje_devolucion = get_mensaje_devolucion_por_pais(pais_guardado)
            set_estado(numero, "PREGUNTA_CONTINUAR")
            return mensaje_devolucion
        elif mensaje == "3":
            # Consultar estado de la guía
            tracking_code = get_tracking(numero)
            datos = consultar_estado(tracking_code)
            
            if datos:
                nombre = get_nombre(numero) or ""
                
                # Usar país guardado en sesión o detectar desde datos
                pais_guardado = get_pais(numero)
                if not pais_guardado:
                    pais_detectado = detectar_pais_desde_datos(datos)
                    set_pais(numero, pais_detectado)
                else:
                    pais_detectado = pais_guardado
                
                respuesta = aplicar_flujo_por_pais(pais_detectado, nombre, tracking_code, datos)
                
                set_estado(numero, "PREGUNTA_CONTINUAR")
                return respuesta
            else:
                set_estado(numero, "ESPERANDO_TRACKING")
                return (
                    f"❗ No encontramos información actualizada con el número de guía *{tracking_code}*.\n"
                    "Por favor verifica que esté escrito correctamente.\n\n"
                    "📦 Ingresa nuevamente tu número de guía para continuar."
                )
        else:
            nombre = get_nombre(numero) or ""
            return (
                f"{nombre}, opción no válida. Por favor selecciona:\n\n"
                "1️⃣ Tengo una novedad con una entrega\n"
                "2️⃣ Tengo una novedad con una devolución\n"
                "3️⃣ Consultar estado de mi guía"
            )

    elif estado == "MENU_ENTREGA":
        # Validar que sea un número válido
        if not mensaje.isdigit() or mensaje not in ["1", "2", "3", "4", "5", "6"]:
            return (
                "Por favor selecciona una opción válida del menú:\n\n"
                "1️⃣ Mi pedido no fue entregado\n"
                "2️⃣ Deseo cambiar datos de entrega\n"
                "3️⃣ Deseo recoger mi pedido\n"
                "4️⃣ Reportar mala atención\n"
                "5️⃣ Cobro que no reconozco\n"
                "6️⃣ Pedido incompleto o dañado"
            )
        
        tracking_code = get_tracking(numero)
        datos = consultar_estado(tracking_code)
        if not datos:
            set_estado(numero, "ESPERANDO_TRACKING")
            return (
                f"❗ No encontramos información con el número de guía *{tracking_code}*.\n"
                "Por favor verifica que esté escrito correctamente.\n\n"
                "📦 Ingresa nuevamente tu número de guía para continuar."
            )

        tipo_caso = None
        if mensaje == "1":
            tipo_caso = "pedido no entregado"
        elif mensaje == "2":
            # Cambiar datos de entrega - No se puede hacer por este canal
            set_estado(numero, "PREGUNTA_CONTINUAR")
            return MENSAJE_CAMBIO_DATOS
        elif mensaje == "3":
            # Deseo recoger mi pedido - Flujo por país
            tracking_code = get_tracking(numero)
            pais_guardado = get_pais(numero)
            
            if pais_guardado == "panama":
                mensaje_recogida = get_mensaje_recogida_por_pais(pais_guardado, tracking_code)
                set_estado(numero, "PREGUNTA_CONTINUAR")
                return mensaje_recogida
            else:
                set_estado(numero, "PREGUNTA_CONTINUAR")
                return MENSAJE_RECOGIDA_NO_DISPONIBLE
        elif mensaje == "4":
            tipo_caso = "mala atención"
        elif mensaje == "5":
            tipo_caso = "cobro no reconocido"
        elif mensaje == "6":
            tipo_caso = "pedido incompleto"
        else:
            return MENSAJE_OPCION_NO_DISPONIBLE

        # Solo continúa con el flujo guiado si se seleccionó una opción que requiere caso
        if tipo_caso:
            set_estado_temporal(numero, "tipo_caso", tipo_caso)
            set_estado(numero, "DESCRIBIR_CASO")
            return MENSAJE_PEDIR_DESCRIPCION

    elif estado == "DESCRIBIR_CASO":
        set_estado_temporal(numero, "descripcion", mensaje)
        set_estado(numero, "PREGUNTAR_EVIDENCIA")
        return MENSAJE_PREGUNTAR_EVIDENCIA

    elif estado == "PREGUNTAR_EVIDENCIA":
        if mensaje == "1":
            set_estado(numero, "ESPERANDO_IMAGEN")
            return MENSAJE_ENVIAR_IMAGEN
        elif mensaje == "2":
            tipo_caso = get_estado_temporal(numero, "tipo_caso")
            descripcion = get_estado_temporal(numero, "descripcion")
            tracking_code = get_tracking(numero)
            
            # Obtener usuario actualizado con nombre
            nombre = get_nombre(numero)
            usuario_actualizado = get_or_create_usuario(numero, nombre)

            # Crear caso en la base de datos
            crear_caso(
                usuario_id=usuario_actualizado.id,
                tracking_id=None,
                tipo=tipo_caso,
                descripcion=descripcion,
                telefono=numero,
                imagen_url=None
            )

            # Enviar correo de notificación
            enviar_correo_caso(usuario_actualizado, tracking_code, tipo_caso, descripcion, None)

            set_estado(numero, "PREGUNTA_CONTINUAR")
            return MENSAJE_CASO_CONFIRMADO
        else:
            return MENSAJE_OPCION_IMAGEN_INVALIDA

    elif estado == "ESPERANDO_IMAGEN":
        tipo_caso = get_estado_temporal(numero, "tipo_caso")
        descripcion = get_estado_temporal(numero, "descripcion")
        tracking_code = get_tracking(numero)
        drive_url = None

        if imagen_guardada:
            drive_url = subir_a_drive(imagen_guardada)

        # Obtener usuario actualizado con nombre
        nombre = get_nombre(numero)
        usuario_actualizado = get_or_create_usuario(numero, nombre)

        # Crear caso en la base de datos
        crear_caso(
            usuario_id=usuario_actualizado.id,
            tracking_id=None,
            tipo=tipo_caso,
            descripcion=descripcion,
            telefono=numero,
            imagen_url=drive_url
        )

        # Enviar correo de notificación
        enviar_correo_caso(usuario_actualizado, tracking_code, tipo_caso, descripcion, drive_url, imagen_guardada)

        set_estado(numero, "PREGUNTA_CONTINUAR")
        return MENSAJE_CASO_CONFIRMADO

    elif estado == "PREGUNTA_CONTINUAR":
        # Validar que sea 1 o 2
        if not mensaje.isdigit() or mensaje not in ["1", "2"]:
            nombre = get_nombre(numero) or ""
            return (
                f"{nombre}, por favor selecciona:\n\n"
                "1️⃣ Sí, volver al menú principal\n"
                "2️⃣ No, finalizar conversación"
            )
        
        if mensaje == "1":
            set_estado(numero, "MENU_PRINCIPAL")
            return MENSAJE_VOLVER_MENU
        elif mensaje == "2":
            reset_usuario(numero)
            return MENSAJE_CONVERSACION_FINALIZADA
        else:
            nombre = get_nombre(numero) or ""
            return (
                f"{nombre}, por favor selecciona:\n\n"
                "1️⃣ Sí, volver al menú principal\n"
                "2️⃣ No, finalizar conversación"
            )

    else:
        # Estado no reconocido - reiniciar conversación
        reset_usuario(numero)
        return "⚠️ Hubo un problema con tu sesión. Por favor, escribe 'hola' para comenzar de nuevo."

def enviar_correo_caso(usuario, tracking_code, tipo_caso, descripcion, drive_url=None, imagen_guardada=None, datos_tracking=None):
    """
    Envía un correo de notificación cuando se crea un nuevo caso
    y también crea un ticket en la base de datos central
    """
    try:
        from helpers import obtener_datos_tracking
        
        # Obtener datos del tracking si no se proporcionan
        if not datos_tracking:
            datos_tracking = obtener_datos_tracking(tracking_code)
        
        asunto = f"[{tipo_caso.upper()}] Caso automático - {tracking_code}"

        cuerpo = f"""
🛑 *Nuevo caso reportado automáticamente desde WhatsApp*

📄 *Datos del cliente:*
• 👤 Nombre: {usuario.nombre or 'No disponible'}
• 📱 Teléfono: {usuario.numero}
• 🧾 Tracking: {tracking_code}

� *Información del envío:*
• � Carrier: {datos_tracking.get('carrier', 'No disponible')}
• 🌍 País: {datos_tracking.get('pais', 'No disponible')}
• 📊 Estado Actual: {datos_tracking.get('estado_actual', 'No disponible')}
• 🏙️ Ciudad Origen: {datos_tracking.get('origen_city', 'No disponible')}
• 🏙️ Ciudad Destino: {datos_tracking.get('destino_city', 'No disponible')}
• 📍 Dirección: {datos_tracking.get('destino', 'No disponible')}

� *Detalles del caso:*
• Tipo de caso: {tipo_caso.title()}
• � Descripción del cliente: {descripcion}

� *Fecha de creación:* {datetime.now().strftime('%d/%m/%Y %H:%M')}
"""

        if drive_url:
            cuerpo += f"\n🔗 *Evidencia adjunta:* {drive_url}"

        cuerpo += "\n\n📨 Este caso fue generado automáticamente por el sistema de atención al cliente de *X-Cargo*."

        # Enviar correo (solo adjuntar imagen si no se subió a Drive exitosamente)
        adjuntos = []
        if imagen_guardada and os.path.exists(imagen_guardada) and not drive_url:
            adjuntos = [imagen_guardada]

        enviar_correo(asunto, cuerpo, adjuntos=adjuntos)

        # 🎫 Crear ticket en la base de datos central
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

        print(f"✅ Correo enviado y ticket creado para caso: {tipo_caso} - {tracking_code}")

    except Exception as e:
        print(f"❌ Error al enviar correo del caso: {e}")

