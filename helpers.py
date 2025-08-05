from db import SessionLocal, Usuario, Mensaje, Caso, Tracking
from sqlalchemy.exc import IntegrityError

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

