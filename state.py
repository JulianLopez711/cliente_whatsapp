from collections import defaultdict

# Estados activos por usuario
estados = {}
tracking_codes = {}
nombres = {}

# Almacenamiento temporal para info de caso
temporales = defaultdict(dict)

def get_estado(usuario):
    return estados.get(usuario, "INICIO")

def set_estado(usuario, estado):
    estados[usuario] = estado

def reset_usuario(usuario):
    estados[usuario] = "INICIO"
    tracking_codes.pop(usuario, None)
    nombres.pop(usuario, None)
    temporales.pop(usuario, None)

def set_tracking(usuario, tracking):
    tracking_codes[usuario] = tracking

def get_tracking(usuario):
    return tracking_codes.get(usuario)

def set_nombre(usuario, nombre):
    nombres[usuario] = nombre

def get_nombre(usuario):
    return nombres.get(usuario)

# Variables temporales para descripción e imagen
def set_estado_temporal(usuario, clave, valor):
    temporales[usuario][clave] = valor

def get_estado_temporal(usuario, clave):
    return temporales[usuario].get(clave)
