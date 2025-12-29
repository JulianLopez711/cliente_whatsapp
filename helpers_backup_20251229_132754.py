from db import SessionLocal, Usuario, Mensaje, Caso, Tracking, Ticket, TicketsSessionLocal
from sqlalchemy.exc import IntegrityError
import random
from tracking_data import consultar_estado

def get_or_create_usuario(numero, nombre=None):
    db = SessionLocal()
    try:
        usuario = db.query(Usuario).filter_by(numero=numero).first()
        if not usuario:
            usuario = Usuario(numero=numero, nombre=nombre)
            db.add(usuario)
            db.commit()
            db.refresh(usuario)
        elif nombre and usuario.nombre != nombre:
            # Actualizar el nombre si es diferente
            usuario.nombre = nombre
            db.commit()
            db.refresh(usuario)
        return usuario
    except IntegrityError:
        db.rollback()
        usuario = db.query(Usuario).filter_by(numero=numero).first()
        if nombre and usuario and usuario.nombre != nombre:
            usuario.nombre = nombre
            db.commit()
            db.refresh(usuario)
        return usuario
    finally:
        db.close()

def registrar_mensaje(usuario_id, texto, tipo):
    db = SessionLocal()
    try:
        mensaje = Mensaje(usuario_id=usuario_id, mensaje=texto, tipo=tipo)
        db.add(mensaje)
        db.commit()
    finally:
        db.close()

def obtener_trackings_usuario(usuario_id, activo=True):
    """
    Obtiene todos los trackings de un usuario
    """
    db = SessionLocal()
    try:
        query = db.query(Tracking).filter_by(usuario_id=usuario_id)
        if activo is not None:
            query = query.filter_by(activo=activo)
        return query.all()
    finally:
        db.close()

def obtener_datos_tracking(codigo_tracking):
    """Obtiene los datos del tracking desde la API externa y la base de datos local"""
    try:
        # Primero intentar obtener desde la API externa (BigQuery)
        datos_api = consultar_estado(codigo_tracking)
        
        if datos_api:
            return {
                'carrier': datos_api.get('carrier', 'No disponible'),
                'pais': datos_api.get('pais', 'No disponible'),
                'estado_actual': datos_api.get('estado', 'No disponible'),
                'origen_city': datos_api.get('origen_city', 'No disponible'),
                'destino_city': datos_api.get('destino_city', 'No disponible'),
                'destino': datos_api.get('destino', 'No disponible')
            }
        else:
            # Si no está en API, buscar en base de datos local
            db = SessionLocal()
            try:
                tracking = db.query(Tracking).filter(Tracking.codigo == codigo_tracking).first()
                
                if tracking:
                    return {
                        'carrier': 'No disponible',
                        'pais': 'No disponible',
                        'estado_actual': tracking.estado or 'No disponible',
                        'origen_city': tracking.origen_city or 'No disponible',
                        'destino_city': tracking.destino_city or 'No disponible',
                        'destino': tracking.direccion or 'No disponible'
                    }
                else:
                    return {
                        'carrier': 'No encontrado',
                        'pais': 'No encontrado',
                        'estado_actual': 'No encontrado',
                        'origen_city': 'No encontrado',
                        'destino_city': 'No encontrado',
                        'destino': 'No encontrado'
                    }
            finally:
                db.close()
    except Exception as e:
        print(f"Error obteniendo datos del tracking: {e}")
        return {
            'carrier': 'Error al consultar',
            'pais': 'Error al consultar',
            'estado_actual': 'Error al consultar',
            'origen_city': 'Error al consultar',
            'destino_city': 'Error al consultar',
            'destino': 'Error al consultar'
        }

def crear_o_actualizar_tracking(usuario_id, codigo_tracking, estado=None, direccion=None, fecha_entrega=None, origen_city=None, destino_city=None):
    """
    Crea o actualiza un tracking en la base de datos
    """
    db = SessionLocal()
    try:
        # Buscar si ya existe un tracking activo para este usuario y código
        tracking_existente = db.query(Tracking).filter_by(
            usuario_id=usuario_id, 
            codigo=codigo_tracking, 
            activo=True
        ).first()
        
        if tracking_existente:
            # Actualizar el tracking existente
            if estado:
                tracking_existente.estado = estado
            if direccion:
                tracking_existente.direccion = direccion
            if fecha_entrega:
                tracking_existente.fecha_entrega = fecha_entrega
            if origen_city:
                tracking_existente.origen_city = origen_city
            if destino_city:
                tracking_existente.destino_city = destino_city
            db.commit()
            db.refresh(tracking_existente)
            return tracking_existente
        else:
            # Crear nuevo tracking
            nuevo_tracking = Tracking(
                usuario_id=usuario_id,
                codigo=codigo_tracking,
                estado=estado,
                direccion=direccion,
                fecha_entrega=fecha_entrega,
                origen_city=origen_city,
                destino_city=destino_city,
                activo=True
            )
            db.add(nuevo_tracking)
            db.commit()
            db.refresh(nuevo_tracking)
            return nuevo_tracking
    finally:
        db.close()

def crear_caso(usuario_id, tracking_id, tipo, descripcion, telefono, imagen_url=None):
    db = SessionLocal()
    try:
        caso = Caso(
            usuario_id=usuario_id,
            tracking_id=tracking_id,
            tipo=tipo,
            descripcion=descripcion,
            telefono=telefono,
            imagen_url=imagen_url  # ✅ almacenar la URL
        )
        db.add(caso)
        db.commit()
        db.refresh(caso)
        return caso
    finally:
        db.close()


def obtener_agentes_servicio_cliente(cola_id=1):
    """
    Obtiene lista de agentes específicamente asignados a una cola de Servicio al Cliente
    """
    db = TicketsSessionLocal()
    try:
        from sqlalchemy import text
        
        # Obtener agentes específicamente asignados a la cola especificada
        result = db.execute(text("""
            SELECT DISTINCT 
                cau.usuario_id,
                u.nombre,
                u.email
            FROM colas_asignadas_usuario cau
            INNER JOIN usuarios u ON cau.usuario_id = u.id
            WHERE cau.cola_id = :cola_id
            AND u.empresa_id = 1
            ORDER BY u.nombre
        """), {'cola_id': cola_id})
        
        agentes = result.fetchall()
        agentes_ids = [agente[0] for agente in agentes]
        
        print(f"👥 Agentes específicos de Cola ID {cola_id}: {len(agentes_ids)}")
        return agentes_ids
        
    except Exception as e:
        print(f"⚠️ Error al obtener agentes específicos para cola {cola_id}: {e}")
        # Listas específicas según la cola
        if cola_id == 13:  # ServicioCliente-Panama
            agentes_panama = [55, 62, 56]  # Agentes específicos para Panamá (ajustar según necesidad)
            print(f"📋 Usando lista específica de Panamá: {len(agentes_panama)} agentes")
            return agentes_panama
        else:  # Servicio al Cliente Colombia (cola_id = 1)
            agentes_colombia = [55, 62, 56, 59, 52, 54, 61, 63, 58, 53, 57, 64, 60, 10]
            print(f"📋 Usando lista específica de Colombia: {len(agentes_colombia)} agentes")
            return agentes_colombia
    finally:
        db.close()

def asignar_agente_aleatorio(cola_id=1):
    """
    Asigna un agente aleatorio según la cola de Servicio al Cliente
    """
    agentes_disponibles = obtener_agentes_servicio_cliente(cola_id)
    
    if agentes_disponibles:
        agente_seleccionado = random.choice(agentes_disponibles)
        print(f"🎯 Agente asignado aleatoriamente para cola {cola_id}: ID {agente_seleccionado}")
        return agente_seleccionado
    else:
        print(f"⚠️ No hay agentes disponibles para cola {cola_id}, asignando None")
        return None

def crear_ticket_central(asunto, descripcion, usuario_nombre=None, usuario_telefono=None, tracking_code=None, tipo_caso=None, prioridad="media", imagen_url=None):
    """
    Crea un ticket en la base de datos central de tickets
    Asigna automáticamente a la cola de Servicio al Cliente según el país:
    - Colombia: Cola ID 1 (Servicio al Cliente)
    - Panamá: Cola ID 13 (ServicioCliente-Panama)
    """
    from sqlalchemy import create_engine, text
    import os
    from dotenv import load_dotenv
    from datetime import datetime
    
    load_dotenv()
    
    try:
        # Obtener datos del tracking si se proporciona
        datos_tracking = None
        if tracking_code:
            datos_tracking = obtener_datos_tracking(tracking_code)
        
        # Determinar cola y agente según el país
        pais = 'colombia'  # Default
        if datos_tracking and datos_tracking.get('pais'):
            pais_detectado = datos_tracking['pais'].lower()
            if 'panama' in pais_detectado or 'panamá' in pais_detectado:
                pais = 'panama'
        
        # Configurar cola según el país
        if pais == 'panama':
            COLA_ID = 13  # ServicioCliente-Panama
            NOMBRE_COLA = "ServicioCliente-Panama"
            print(f"🇵🇦 Detectado país Panamá - Asignando a cola {COLA_ID}")
        else:
            COLA_ID = 1   # Servicio al Cliente (Colombia)
            NOMBRE_COLA = "Servicio al Cliente"
            print(f"🇨🇴 Detectado país Colombia - Asignando a cola {COLA_ID}")
        
        # Usar conexión directa como en el script que funciona
        TICKETS_DATABASE_URL = 'postgresql://postgres:Xcargo25*@72.167.223.67:5432/tickets_central'
        engine = create_engine(TICKETS_DATABASE_URL)
        
        # IDs de configuración
        EMPRESA_XCARGO_ID = 1  # ID de X-Cargo
        SOLICITANTE_SELFX_ID = 66  # ID del usuario selfx@x-cargo.co
        
        # Asignar agente aleatorio según la cola
        agente_id = asignar_agente_aleatorio(COLA_ID)
        
        # Preparar descripción completa con datos del tracking
        descripcion_completa = f"""
🛑 Caso reportado desde WhatsApp Bot

📄 *Datos del cliente:*
• 👤 Nombre: {usuario_nombre or 'No disponible'}
• 📱 Teléfono: {usuario_telefono or 'No disponible'}
• 🧾 Tracking: {tracking_code or 'No disponible'}

📦 *Información del envío:*"""
        
        if datos_tracking:
            descripcion_completa += f"""
• � Carrier: {datos_tracking['carrier']}
• 🌍 País: {datos_tracking['pais']}
• 📊 Estado Actual: {datos_tracking['estado_actual']}
• 🏙️ Ciudad Origen: {datos_tracking['origen_city']}
• 🏙️ Ciudad Destino: {datos_tracking['destino_city']}
• 📍 Dirección: {datos_tracking['destino']}"""
        else:
            descripcion_completa += """
• ⚠️ Información del envío no disponible"""
        
        descripcion_completa += f"""

📌 *Detalles del caso:*
• Tipo de caso: {tipo_caso or 'No especificado'}
• 📝 Descripción del cliente: {descripcion or 'Sin descripción'}"""

        # Agregar URL de la imagen si existe
        if imagen_url:
            descripcion_completa += f"""
• 🖼️ Evidencia adjunta: {imagen_url}"""

        descripcion_completa += f"""

📱 Canal: WhatsApp Bot Automático
🤖 Generado automáticamente por el sistema
👥 Asignado automáticamente a: {NOMBRE_COLA}
🌍 País detectado: {pais.title()}
📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """
        
        with engine.connect() as conn:
            # Usar SQL directo para insertar
            result = conn.execute(text("""
                INSERT INTO tickets (
                    asunto, 
                    descripcion, 
                    estado, 
                    prioridad, 
                    canal, 
                    cola_id, 
                    agente_id, 
                    empresa_id,
                    solicitante_id
                ) VALUES (
                    :asunto,
                    :descripcion,
                    :estado,
                    :prioridad,
                    :canal,
                    :cola_id,
                    :agente_id,
                    :empresa_id,
                    :solicitante_id
                ) RETURNING id, asunto, cola_id, agente_id, solicitante_id
            """), {
                'asunto': asunto,
                'descripcion': descripcion_completa,
                'estado': 'Abierto',
                'prioridad': prioridad,
                'canal': 'whatsapp',
                'cola_id': COLA_ID,
                'agente_id': agente_id,
                'empresa_id': EMPRESA_XCARGO_ID,
                'solicitante_id': SOLICITANTE_SELFX_ID
            })
            
            ticket_info = result.fetchone()
            conn.commit()
            
            print(f"✅ Ticket creado en base central:")
            print(f"   ID: {ticket_info[0]}")
            print(f"   Asunto: {ticket_info[1]}")
            print(f"   Cola: {NOMBRE_COLA} (ID: {ticket_info[2]})")
            print(f"   Agente: ID {ticket_info[3]}")
            print(f"   Solicitante: selfx@x-cargo.co (ID: {ticket_info[4]})")
            print(f"   Estado: Abierto")
            print(f"   Prioridad: {prioridad}")
            print(f"   País: {pais.title()}")
            
            # Crear objeto similar para compatibilidad
            class TicketResult:
                def __init__(self, id, asunto, cola_id, agente_id, solicitante_id):
                    self.id = id
                    self.asunto = asunto
                    self.cola_id = cola_id
                    self.agente_id = agente_id
                    self.solicitante_id = solicitante_id
                    self.estado = "Abierto"
                    self.prioridad = prioridad
                    self.canal = "whatsapp"
            
            return TicketResult(ticket_info[0], ticket_info[1], ticket_info[2], ticket_info[3], ticket_info[4])
        
    except Exception as e:
        print(f"❌ Error al crear ticket en base central: {e}")
        return None

