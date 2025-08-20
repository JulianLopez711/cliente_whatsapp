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
    MENSAJE_MENU_RECOLECCION,
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
    get_mensajes_pais,
    get_mensaje_recogida_panama,
    get_mensaje_recogida_por_pais,
    get_mensaje_devolucion_por_pais
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
    depto_destino = datos.get("depto_destino", "")
    
    # Verificar si el estado indica devolución
    estado_lower = str(estado_paquete).lower() if estado_paquete else ""
    if "devolucion" in estado_lower or "devolución" in estado_lower:
        # Si hay devolución, mostrar mensaje dinámico según país y departamento
        return get_mensaje_devolucion_por_pais(pais, depto_destino)
    
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
                    "2️⃣ Tengo una novedad con una recolección\n"
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
        if mensaje == "1":
            set_estado(numero, "MENU_ENTREGA")
            return MENSAJE_MENU_ENTREGA
        elif mensaje == "2":
            set_estado(numero, "MENU_RECOLECCION")
            return MENSAJE_MENU_RECOLECCION
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
            return MENSAJE_OPCION_INVALIDA

    elif estado == "MENU_ENTREGA":
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
                # Obtener datos del tracking para conseguir el departamento de destino
                datos_tracking = consultar_estado(tracking_code)
                depto_destino = None
                
                if datos_tracking:
                    # Usar el campo correcto depto_destino de la base de datos
                    depto_destino = datos_tracking.get('depto_destino')
                
                mensaje_recogida = get_mensaje_recogida_panama(depto_destino, tracking_code)
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

    elif estado == "MENU_RECOLECCION":
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
            tipo_caso = "recolección no realizada"
        elif mensaje == "2":
            # Cambiar datos de recolección - No se puede hacer por este canal
            set_estado(numero, "PREGUNTA_CONTINUAR")
            return (
                "✏️ Entendemos que a veces necesitas actualizar los datos de recolección, pero no podemos hacer estos cambios desde este canal.\n\n"
                "👉 Por favor contacta directamente con el servicio que programó la recolección o llama a nuestro centro de atención.\n\n"
                "😊 Si necesitas ayuda, estoy aquí para orientarte.\n\n"
                "❓ ¿Te puedo ayudar en algo más?\n1️⃣ Sí, volver al menú principal\n2️⃣ No, finalizar conversación"
            )
        elif mensaje == "3":
            tipo_caso = "reprogramar recolección"
        elif mensaje == "4":
            tipo_caso = "mala atención del recolector"
        elif mensaje == "5":
            tipo_caso = "cobro no reconocido en recolección"
        elif mensaje == "6":
            tipo_caso = "problema con empaque"
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

            # Enviar correo de notificación y obtener ticket
            ticket = enviar_correo_caso(usuario_actualizado, tracking_code, tipo_caso, descripcion, None)

            set_estado(numero, "PREGUNTA_CONTINUAR")
            if ticket and hasattr(ticket, 'id'):
                return (
                    f"✅ ¡Gracias! Tu caso ha sido registrado correctamente.\n"
                    f"📌 Número de caso: *#{ticket.id}*\n"
                    "Nuestro equipo lo revisará y te contactará en un máximo de *15 días hábiles*.\n\n"
                    "¿Te puedo ayudar en algo más?\n1️⃣ Sí, volver al menú principal\n2️⃣ No, finalizar conversación"
                )
            else:
                return (
                    "✅ ¡Gracias! Tu caso ha sido registrado correctamente.\n"
                    "📌 Nuestro equipo lo revisará y te contactará en un máximo de *15 días hábiles*.\n\n"
                    "¿Te puedo ayudar en algo más?\n1️⃣ Sí, volver al menú principal\n2️⃣ No, finalizar conversación"
                )
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
        if mensaje == "1":
            set_estado(numero, "MENU_PRINCIPAL")
            return MENSAJE_VOLVER_MENU
        elif mensaje == "2":
            reset_usuario(numero)
            return MENSAJE_CONVERSACION_FINALIZADA
        else:
            return MENSAJE_OPCION_CONTINUAR_INVALIDA

    else:
        return MENSAJE_ERROR_GENERAL

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
            "pedido incompleto": "alta",
            "recolección no realizada": "alta",
            "reprogramar recolección": "media",
            "mala atención del recolector": "media",
            "cobro no reconocido en recolección": "alta",
            "problema con empaque": "media"
        }
        
        prioridad = determinar_prioridad_caso.get(tipo_caso, "media")
        
        ticket = crear_ticket_central(
            asunto=asunto,
            descripcion=descripcion,
            usuario_nombre=usuario.nombre,
            usuario_telefono=usuario.numero,
            tracking_code=tracking_code,
            tipo_caso=tipo_caso,
            prioridad=prioridad
        )
        print(f"✅ Correo enviado y ticket creado para caso: {tipo_caso} - {tracking_code}")
        return ticket
    except Exception as e:
        print(f"❌ Error al enviar correo del caso: {e}")
        return None

