from db import SessionLocal, Usuario, Mensaje, Caso, Tracking, Ticket, TicketsSessionLocal
from sqlalchemy.exc import IntegrityError
import random

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


def obtener_agentes_servicio_cliente():
    """
    Obtiene lista de agentes específicamente asignados a la cola de Servicio al Cliente
    """
    db = TicketsSessionLocal()
    try:
        from sqlalchemy import text
        
        # Obtener agentes específicamente asignados a la cola de Servicio al Cliente (ID: 1)
        result = db.execute(text("""
            SELECT DISTINCT 
                cau.usuario_id,
                u.nombre,
                u.email
            FROM colas_asignadas_usuario cau
            INNER JOIN usuarios u ON cau.usuario_id = u.id
            WHERE cau.cola_id = 1
            AND u.empresa_id = 1
            ORDER BY u.nombre
        """))
        
        agentes = result.fetchall()
        agentes_ids = [agente[0] for agente in agentes]
        
        print(f"👥 Agentes específicos de Servicio al Cliente: {len(agentes_ids)}")
        return agentes_ids
        
    except Exception as e:
        print(f"⚠️ Error al obtener agentes específicos: {e}")
        # Lista específica de agentes de Servicio al Cliente basada en la consulta exitosa
        agentes_servicio_cliente = [55, 62, 56, 59, 52, 54, 61, 63, 58, 53, 57, 64, 60, 10]
        print(f"📋 Usando lista específica de Servicio al Cliente: {len(agentes_servicio_cliente)} agentes")
        return agentes_servicio_cliente
    finally:
        db.close()

def asignar_agente_aleatorio():
    """
    Asigna un agente aleatorio de Servicio al Cliente
    """
    agentes_disponibles = obtener_agentes_servicio_cliente()
    
    if agentes_disponibles:
        agente_seleccionado = random.choice(agentes_disponibles)
        print(f"🎯 Agente asignado aleatoriamente: ID {agente_seleccionado}")
        return agente_seleccionado
    else:
        print("⚠️ No hay agentes disponibles, asignando None")
        return None

def crear_ticket_central(asunto, descripcion, usuario_nombre=None, usuario_telefono=None, tracking_code=None, tipo_caso=None, prioridad="media"):
    """
    Crea un ticket en la base de datos central de tickets
    Asigna automáticamente a la cola de Servicio al Cliente y a un agente aleatorio
    """
    from sqlalchemy import create_engine, text
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    try:
        # Usar conexión directa como en el script que funciona
        TICKETS_DATABASE_URL = 'postgresql://postgres:Xcargo25*@72.167.223.67:5432/tickets_central'
        engine = create_engine(TICKETS_DATABASE_URL)
        
        # IDs de configuración
        COLA_SERVICIO_CLIENTE_ID = 1  # ID de la cola "Servicio al Cliente"
        EMPRESA_XCARGO_ID = 1  # ID de X-Cargo
        SOLICITANTE_SELFX_ID = 66  # ID del usuario selfx@x-cargo.co
        
        # Asignar agente aleatorio
        agente_id = asignar_agente_aleatorio()
        
        # Preparar descripción completa
        descripcion_completa = f"""
🛑 Caso reportado desde WhatsApp Bot

📄 Datos del cliente:
• 👤 Nombre: {usuario_nombre or 'No disponible'}
• 📱 Teléfono: {usuario_telefono or 'No disponible'}
• 🧾 Tracking: {tracking_code or 'No disponible'}

📌 Tipo de caso: {tipo_caso or 'No especificado'}
📝 Descripción del cliente: {descripcion or 'Sin descripción'}

📱 Canal: WhatsApp Bot Automático
🤖 Generado automáticamente por el sistema
👥 Asignado automáticamente a: Servicio al Cliente
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
                'estado': 'abierto',
                'prioridad': prioridad,
                'canal': 'whatsapp',
                'cola_id': COLA_SERVICIO_CLIENTE_ID,
                'agente_id': agente_id,
                'empresa_id': EMPRESA_XCARGO_ID,
                'solicitante_id': SOLICITANTE_SELFX_ID
            })
            
            ticket_info = result.fetchone()
            conn.commit()
            
            print(f"✅ Ticket creado en base central:")
            print(f"   ID: {ticket_info[0]}")
            print(f"   Asunto: {ticket_info[1]}")
            print(f"   Cola: Servicio al Cliente (ID: {ticket_info[2]})")
            print(f"   Agente: ID {ticket_info[3]}")
            print(f"   Solicitante: selfx@x-cargo.co (ID: {ticket_info[4]})")
            print(f"   Estado: abierto")
            print(f"   Prioridad: {prioridad}")
            
            # Crear objeto similar para compatibilidad
            class TicketResult:
                def __init__(self, id, asunto, cola_id, agente_id, solicitante_id):
                    self.id = id
                    self.asunto = asunto
                    self.cola_id = cola_id
                    self.agente_id = agente_id
                    self.solicitante_id = solicitante_id
                    self.estado = "abierto"
                    self.prioridad = prioridad
                    self.canal = "whatsapp"
            
            return TicketResult(ticket_info[0], ticket_info[1], ticket_info[2], ticket_info[3], ticket_info[4])
        
    except Exception as e:
        print(f"❌ Error al crear ticket en base central: {e}")
        return None

