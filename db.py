import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Cargar variables del entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
TICKETS_DATABASE_URL = os.getenv("TICKETS_DATABASE_URL", DATABASE_URL)  # URL de la base de datos central de tickets

# Configuración optimizada del pool de conexiones
ENGINE_OPTS = {
    "pool_size": 10,
    "max_overflow": 20,
    "pool_timeout": 30,
    "pool_recycle": 1800,  # Reciclar conexiones cada 30 minutos
    "pool_pre_ping": True,  # Verificar conexiones antes de usar
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
}

# Conexión principal
engine = create_engine(DATABASE_URL, **ENGINE_OPTS)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Conexión para la base de datos central de tickets
tickets_engine = create_engine(TICKETS_DATABASE_URL, **ENGINE_OPTS)
TicketsSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=tickets_engine)

Base = declarative_base()

# Modelos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, nullable=False)
    nombre = Column(String)
    creado_en = Column(DateTime, server_default=func.now())

    trackings = relationship("Tracking", back_populates="usuario")
    mensajes = relationship("Mensaje", back_populates="usuario")
    casos = relationship("Caso", back_populates="usuario")


class Tracking(Base):
    __tablename__ = "trackings"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    codigo = Column(String, nullable=False)
    estado = Column(String)
    direccion = Column(String)
    fecha_entrega = Column(Date)
    activo = Column(Boolean, default=True)
    origen_city = Column(String, nullable=True)  # ✅ NUEVO CAMPO
    destino_city = Column(String, nullable=True)  # ✅ NUEVO CAMPO

    usuario = relationship("Usuario", back_populates="trackings")
    casos = relationship("Caso", back_populates="tracking")


class Mensaje(Base):
    __tablename__ = "mensajes"
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    mensaje = Column(Text)
    tipo = Column(String)  # 'entrada' o 'salida'
    enviado_en = Column(DateTime, server_default=func.now())

    usuario = relationship("Usuario", back_populates="mensajes")


class Caso(Base):
    __tablename__ = "casos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    tracking_id = Column(Integer, ForeignKey("trackings.id"), nullable=True)
    tipo = Column(String)
    descripcion = Column(Text)
    telefono = Column(String)
    estado = Column(String, default="Abierto")
    fecha_creado = Column(DateTime, server_default=func.now())
    imagen_url = Column(String)  # ✅ NUEVO CAMPO

    usuario = relationship("Usuario", back_populates="casos")
    tracking = relationship("Tracking", back_populates="casos")
    
class Status(Base):
    __tablename__ = "Status"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(String)
    creado_en = Column(DateTime, server_default=func.now())


# ✅ NUEVO: Modelo para sesiones de usuario (estados del bot)
class Sesion(Base):
    __tablename__ = "sesiones"
    
    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, nullable=False, index=True)
    estado = Column(String, default="INICIO")
    tracking_code = Column(String, nullable=True)
    nombre = Column(String, nullable=True)
    pais = Column(String, default="colombia")
    datos_temporales = Column(Text, nullable=True)  # JSON para almacenar datos temporales
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
    creado_en = Column(DateTime, server_default=func.now())


# Modelo para la tabla tickets de la base de datos central
class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    asunto = Column(Text, nullable=False)
    descripcion = Column(Text)
    estado = Column(Text, nullable=False, default="Abierto")
    prioridad = Column(Text, nullable=False, default="media")
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_actualizacion = Column(DateTime, server_default=func.now())
    fecha_cierre = Column(DateTime)
    sla_vencimiento = Column(DateTime)
    solicitante_id = Column(Integer)
    agente_id = Column(Integer)
    cola_id = Column(Integer)
    app_origen_id = Column(Integer)
    canal = Column(Text, default="whatsapp")
    ticket_padre_id = Column(Integer)
    tipo_id = Column(Integer)
    empresa_id = Column(Integer, nullable=False, default=1)  # Valor por defecto para X-Cargo


# Crear las tablas
def init_db():
    """Crear tablas en la base de datos principal"""
    Base.metadata.create_all(bind=engine)

def init_tickets_db():
    """Crear tabla tickets en la base de datos central"""
    # Solo crear la tabla tickets en la base central
    Ticket.metadata.create_all(bind=tickets_engine)
