# ========================================
# MENSAJES OPTIMIZADOS PARA REDUCIR COSTOS
# Objetivo: Reducir de ~350 caracteres a ~120-150
# Ahorro estimado: 40-50% en costos de Twilio
# ========================================

MENSAJE_BIENVENIDA = "Hola! Bienvenido a X-Cargo. ¿En qué te ayudamos?"

MENSAJE_PEDIR_TRACKING = "Escribe tu número de guía o tracking."

MENSAJE_TRACKING_INVALIDO = "Número de guía inválido. Debe tener 8-25 caracteres alfanuméricos. Intenta de nuevo."

MENSAJE_OPCION_INVALIDA = "Opción no válida. Escribe un número del menú."

MENSAJE_ENTREGADO_NO_RECIBIDO = (
    "Caso registrado: pedido no entregado.\n"
    "Te contactaremos en máx. 15 días hábiles.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_CAMBIO_DATOS = (
    "Para cambiar datos de entrega, usa la app donde hiciste el pedido.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_MALA_ATENCION = (
    "Caso registrado: mala atención.\n"
    "Te contactaremos en máx. 15 días hábiles.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_COBRO_INCORRECTO = (
    "Caso registrado: cobro no reconocido.\n"
    "Te contactaremos en máx. 15 días hábiles.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_PEDIDO_INCOMPLETO = (
    "Caso registrado: pedido incompleto.\n"
    "Te contactaremos en máx. 15 días hábiles.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_MENU_ENTREGA = (
    "Novedad con entrega:\n"
    "1. Pedido no recibido\n"
    "2. Cambiar datos\n"
    "3. Recoger pedido\n"
    "4. Mala atención\n"
    "5. Cobro incorrecto\n"
    "6. Pedido incompleto"
)

MENSAJE_DEVOLUCION = (
    "Devoluciones:\n"
    "WhatsApp: 316 198 7694\n"
    "Email: selfx@x-cargo.co\n"
    "Horario: Lun-Vie 8am-5pm\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_ESPERA_AGENTE = "Un agente te contactará en los próximos 15 días."

MENSAJE_PEDIR_DESCRIPCION = "Cuéntanos tu caso brevemente en un solo mensaje."

MENSAJE_PREGUNTAR_EVIDENCIA = (
    "¿Tienes imagen como evidencia?\n"
    "1. Sí, enviarla\n"
    "2. No, continuar"
)

MENSAJE_CASO_CONFIRMADO = (
    "Caso registrado correctamente.\n"
    "Te contactaremos en máx. 15 días hábiles.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_TRANSITO_INTERNACIONAL = "Tu paquete está en tránsito internacional."

MENSAJE_TIENDA_NO_ENTREGADO = "La tienda aún no ha entregado tu paquete."

MENSAJE_RECOGIDA_PEDIDO = (
    "Recogida de pedidos:\n"
    "WhatsApp: 316 198 7694\n"
    "Email: selfx@x-cargo.co\n"
    "Horario: Lun-Vie 8am-5pm\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_VOLVER_MENU = (
    "Selecciona una opción:\n"
    "1. Novedad con entrega\n"
    "2. Novedad con devolución\n"
    "3. Consultar estado de guía"
)

MENSAJE_CONVERSACION_FINALIZADA = "Gracias por contactarnos. Hasta pronto!"

MENSAJE_ENVIAR_IMAGEN = "Envía la imagen como archivo adjunto."

MENSAJE_OPCION_IMAGEN_INVALIDA = "Responde '1' para enviar imagen o '2' para continuar."

MENSAJE_OPCION_CONTINUAR_INVALIDA = "Responde '1' para volver al menú o '2' para finalizar."

MENSAJE_OPCION_NO_DISPONIBLE = "Esta opción no está disponible actualmente."

MENSAJE_RECOGIDA_NO_DISPONIBLE = (
    "Recogida en oficina solo disponible en Panamá.\n\n"
    "¿Algo más?\n1. Menú\n2. Salir"
)

MENSAJE_ERROR_GENERAL = "Algo salió mal. Escribe 'hola' para reiniciar."

# ========================================
# ESTADOS TRADUCIDOS (VERSIÓN OPTIMIZADA)
# Reducidos de 30-60 caracteres a 15-25
# ========================================

ESTADOS_TRADUCIDOS = {
    "101": "Asignando tracking",
    "102": "Listo para recoger",
    "103": "Driver en recolección",
    "104": "En tránsito a estación",
    "105": "En ruta de media milla",
    "106": "Entre estaciones",
    "107": "En tránsito",
    "109": "Primer contacto",
    "110": "Segundo contacto",
    "111": "Tercer contacto",
    "112": "En análisis especial",
    "120": "Saliendo a devolución",
    "121": "Entre estación y centro",
    "122": "Recibido en centro",
    "123": "Devolución completada",
    "124": "Listo para devolución",
    "125": "Con DMA",
    "126": "Documentado",
    "127": "Recolectado para devolución",
    "130": "Contenedor cerrado",
    "131": "Contenedor abierto",
    "132": "No arribó en contenedor",
    "133": "Arribó sin registro",
    "134": "Finalizado con devolución",
    "199": "Recibido en estación",
    "200": "En estación intermedia",
    "201": "En estación",
    "202": "Ubicación errónea",
    "203": "No localizado",
    "204": "Perdido confirmado",
    "205": "Dañado",
    "206": "Regresando a estación",
    "207": "En espera de asignación",
    "208": "En espera por cliente",
    "209": "Para devolución",
    "210": "En espera de envío",
    "211": "Reprogramado",
    "212": "Robado",
    "213": "Datos incorrectos",
    "214": "Orden duplicada",
    "215": "Mal surtida",
    "216": "Estación equivocada",
    "217": "Solicitud cambio dirección",
    "218": "Orden anulada",
    "219": "Cargado a ruta",
    "220": "Cancelado por cliente",
    "221": "Datos actualizados",
    "222": "En estación de origen",
    "223": "Asignado a tercero",
    "224": "Reactivado",
    "225": "Pendiente",
    "226": "Pendiente",
    "227": "Pendiente",
    "228": "Pendiente",
    "229": "Pendiente",
    "230": "En transferencia",
    "231": "Embarcado en circuito",
    "232": "Arribado a estación",
    "233": "Entregado (media milla)",
    "300": "Preasignado a ruta",
    "301": "Asignado a ruta",
    "302": "Recolectado por conductor",
    "303": "En ruta a destino",
    "304": "Código 2FA mostrado",
    "305": "Sin código verificación",
    "306": "Desasignado de ruta",
    "307": "Cliente sin pago",
    "310": "Intento de entrega",
    "311": "Cliente no disponible",
    "312": "Negocio cerrado",
    "313": "Sin acceso",
    "314": "Dirección errónea",
    "316": "No localizable",
    "317": "Extraviado en ruta",
    "318": "Rechazado por cliente",
    "319": "Fuera de cobertura",
    "321": "Entregado en tienda",
    "322": "Recibido en tienda",
    "329": "Abandonado",
    "330": "3 intentos sin éxito",
    "331": "Datos incorrectos",
    "360": "Entregado",
    "361": "Intercambiado entre drivers",
    "370": "Entregado desde tienda",
    "400": "Solicitud de devolución",
    "401": "Devolución recolectada",
    "500": "En tránsito a Colombia",
    "501": "Recibido en Colombia",
    "502": "En aduana destino",
    "503": "No arribó a Colombia",
    "504": "Retenido en aduana",
    "505": "Retenido por valor",
    "506": "Excede cantidad permitida",
    "507": "Pago pendiente",
    "508": "Retornando a origen",
    "509": "Devolución en progreso",
    "510": "Retornado a origen",
    "511": "Retirado exitosamente",
    "512": "Devolución completada",
    "513": "Cliente en domicilio",
    "514": "Ya recogido",
    "600": "Devolución completada"
}

# ========================================
# MENSAJES POR PAÍS (VERSIÓN OPTIMIZADA)
# ========================================

MENSAJES_COLOMBIA = {
    "bienvenida": "Hola! X-Cargo Colombia. ¿En qué te ayudamos?",
    "devolucion": (
        "Devoluciones Colombia:\n"
        "WhatsApp: 316 198 7694\n"
        "Email: selfx@x-cargo.co\n"
        "Horario: Lun-Vie 8am-5pm\n\n"
        "¿Algo más?\n1. Menú\n2. Salir"
    ),
    "recogida_disponible": (
        "Puedes recoger tu paquete:\n"
        "Calle 26 #69B-53, Bogotá\n"
        "Lun-Vie 8am-5pm, Sáb 8am-12pm\n"
        "Lleva: Cédula y guía {tracking}\n\n"
        "¿Algo más?\n1. Menú\n2. Salir"
    ),
    "tiempo_respuesta": "15 días hábiles",
    "moneda": "COP",
    "zona_horaria": "COT"
}

MENSAJES_PANAMA = {
    "bienvenida": "Hola! X-Cargo Panamá. ¿En qué te ayudamos?",
    "devolucion": (
        "Devoluciones Panamá:\n"
        "WhatsApp: +507 6XXX-XXXX\n"
        "Email: panama@x-cargo.co\n"
        "Horario: Lun-Vie 8am-5pm\n\n"
        "¿Algo más?\n1. Menú\n2. Salir"
    ),
    "recogida_disponible": (
        "Puedes recoger tu paquete:\n"
        "Vía España, Plaza NY, Local XX\n"
        "Lun-Vie 8am-5pm, Sáb 8am-12pm\n"
        "Lleva: Cédula y guía {tracking}\n\n"
        "¿Algo más?\n1. Menú\n2. Salir"
    ),
    "tiempo_respuesta": "10 días hábiles",
    "moneda": "PAB",
    "zona_horaria": "EST"
}

def get_mensajes_pais(pais):
    """Obtiene mensajes específicos según el país"""
    if pais and pais.lower() == "panama":
        return MENSAJES_PANAMA
    return MENSAJES_COLOMBIA

# ========================================
# COMPARACIÓN DE TAMAÑOS
# ========================================

# ANTES:
# MENSAJE_MENU_ENTREGA: ~350 caracteres (3 segmentos) = $0.015-$0.036
# MENSAJE_DEVOLUCION: ~280 caracteres (2 segmentos) = $0.010-$0.024
# Estado de paquete: ~250 caracteres (2 segmentos) = $0.010-$0.024

# DESPUÉS:
# MENSAJE_MENU_ENTREGA: ~100 caracteres (1 segmento) = $0.005-$0.012
# MENSAJE_DEVOLUCION: ~120 caracteres (1 segmento) = $0.005-$0.012
# Estado de paquete: ~120 caracteres (1 segmento) = $0.005-$0.012

# AHORRO ESTIMADO: 40-50% por conversación
