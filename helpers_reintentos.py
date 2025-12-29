# ========================================
# FUNCIONES ADICIONALES PARA helpers.py
# Control de reintentos para reducir costos
# ========================================

from db import SessionLocal, Sesion

def incrementar_reintentos(numero):
    """
    Incrementa el contador de reintentos de un usuario
    Retorna el número actual de reintentos
    """
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=numero).first()
        if sesion:
            # Obtener reintentos actuales desde datos_temporales
            if sesion.datos_temporales:
                import json
                try:
                    datos_temp = json.loads(sesion.datos_temporales)
                except:
                    datos_temp = {}
            else:
                datos_temp = {}
            
            reintentos = datos_temp.get('reintentos', 0) + 1
            datos_temp['reintentos'] = reintentos
            
            import json
            sesion.datos_temporales = json.dumps(datos_temp)
            db.commit()
            
            print(f"⚠️ Reintentos para {numero}: {reintentos}/3")
            return reintentos
        return 0
    finally:
        db.close()

def resetear_reintentos(numero):
    """
    Resetea el contador de reintentos de un usuario
    """
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=numero).first()
        if sesion:
            if sesion.datos_temporales:
                import json
                try:
                    datos_temp = json.loads(sesion.datos_temporales)
                    if 'reintentos' in datos_temp:
                        datos_temp['reintentos'] = 0
                        sesion.datos_temporales = json.dumps(datos_temp)
                        db.commit()
                except:
                    pass
    finally:
        db.close()

def obtener_reintentos(numero):
    """
    Obtiene el número actual de reintentos de un usuario
    """
    db = SessionLocal()
    try:
        sesion = db.query(Sesion).filter_by(numero=numero).first()
        if sesion and sesion.datos_temporales:
            import json
            try:
                datos_temp = json.loads(sesion.datos_temporales)
                return datos_temp.get('reintentos', 0)
            except:
                return 0
        return 0
    finally:
        db.close()

# ========================================
# AGREGAR ESTAS FUNCIONES AL ARCHIVO helpers.py EXISTENTE
# Las puedes copiar y pegar al final del archivo helpers.py
# ========================================
