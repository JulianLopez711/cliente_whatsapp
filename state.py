import json
from db import SessionLocal, Sesion
from sqlalchemy.exc import IntegrityError

def get_or_create_sesion(numero):
    """Obtiene o crea una sesión para el usuario"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=numero).first()
        if not sesion:
            sesion = Sesion(numero=numero, estado="INICIO")
            db.add(sesion)
            db.commit()
            db.refresh(sesion)
        return sesion
    except IntegrityError:
        db.rollback()
        sesion = db.query(Sesion).filter_by(numero=numero).first()
        return sesion
    finally:
        db.close()

def get_estado(usuario):
    """Obtiene el estado actual del usuario desde la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if sesion:
            return sesion.estado
        return "INICIO"
    finally:
        db.close()

def set_estado(usuario, estado):
    """Actualiza el estado del usuario en la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if not sesion:
            sesion = Sesion(numero=usuario, estado=estado)
            db.add(sesion)
        else:
            sesion.estado = estado
        db.commit()
    finally:
        db.close()

def reset_usuario(usuario):
    """Resetea la sesión del usuario a estado inicial"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if sesion:
            sesion.estado = "INICIO"
            sesion.tracking_code = None
            sesion.nombre = None
            sesion.pais = "colombia"
            sesion.datos_temporales = None
            db.commit()
    finally:
        db.close()

def set_tracking(usuario, tracking):
    """Guarda el tracking del usuario en la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if not sesion:
            sesion = Sesion(numero=usuario, tracking_code=tracking)
            db.add(sesion)
        else:
            sesion.tracking_code = tracking
        db.commit()
    finally:
        db.close()

def get_tracking(usuario):
    """Obtiene el tracking del usuario desde la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if sesion:
            return sesion.tracking_code
        return None
    finally:
        db.close()

def set_nombre(usuario, nombre):
    """Guarda el nombre del usuario en la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if not sesion:
            sesion = Sesion(numero=usuario, nombre=nombre)
            db.add(sesion)
        else:
            sesion.nombre = nombre
        db.commit()
    finally:
        db.close()

def get_nombre(usuario):
    """Obtiene el nombre del usuario desde la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if sesion:
            return sesion.nombre
        return None
    finally:
        db.close()

def set_pais(usuario, pais):
    """Guarda el país del usuario en la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if not sesion:
            sesion = Sesion(numero=usuario, pais=pais)
            db.add(sesion)
        else:
            sesion.pais = pais
        db.commit()
    finally:
        db.close()

def get_pais(usuario):
    """Obtiene el país del usuario desde la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if sesion:
            return sesion.pais or "colombia"
        return "colombia"
    finally:
        db.close()

def set_estado_temporal(usuario, clave, valor):
    """Guarda datos temporales del usuario en la BD (como JSON)"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if not sesion:
            sesion = Sesion(numero=usuario)
            db.add(sesion)
            db.flush()
        
        # Obtener datos temporales existentes o crear nuevo dict
        datos = {}
        if sesion.datos_temporales:
            try:
                datos = json.loads(sesion.datos_temporales)
            except:
                datos = {}
        
        # Actualizar con nuevo valor
        datos[clave] = valor
        sesion.datos_temporales = json.dumps(datos)
        db.commit()
    finally:
        db.close()

def get_estado_temporal(usuario, clave):
    """Obtiene datos temporales del usuario desde la BD"""
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=usuario).first()
        if sesion and sesion.datos_temporales:
            try:
                datos = json.loads(sesion.datos_temporales)
                return datos.get(clave)
            except:
                return None
        return None
    finally:
        db.close()

