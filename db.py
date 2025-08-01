import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Cargar variables del entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Conexión
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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
    estado = Column(String, default="abierto")
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



# Crear las tablas
def init_db():
    Base.metadata.create_all(bind=engine)
