# Flujo por País - Bot WhatsApp X-Cargo

## Resumen de Cambios

Se ha implementado un **flujo específico por país** que diferencia entre **Colombia** y **Panamá**, proporcionando mensajes, contactos y opciones personalizadas según la ubicación del envío.

## Nuevas Funcionalidades

### 1. Detección Automática de País
- **Fuente**: Campo `pais` en BigQuery
- **Países soportados**: Colombia, Panamá
- **Por defecto**: Colombia (si no se especifica país)

```python
def detectar_pais_desde_datos(datos):
    if datos.get("pais", "").lower() in ["panama", "panamá"]:
        return "panama"
    else:
        return "colombia"
```

### 2. Mensajes Personalizados por País

#### Colombia 🇨🇴
- **Tiempo de respuesta**: 15 días hábiles
- **WhatsApp**: 316 198 7694
- **Email**: selfx@x-cargo.co
- **Moneda**: COP
- **Recogida en oficina**: No disponible

#### Panamá 🇵🇦
- **Tiempo de respuesta**: 10 días hábiles
- **WhatsApp**: +507 6XXX-XXXX
- **Email**: panama@x-cargo.co
- **Moneda**: PAB
- **Recogida en oficina**: Disponible

### 3. Flujos Diferenciados

#### Consulta de Estado
- **Colombia**: Muestra bandera 🇨🇴 y "Colombia" en el título
- **Panamá**: Muestra bandera 🇵🇦 y "Panamá" en el título
- Ambos incluyen información personalizada según el país

#### Devoluciones
- **Colombia**: Horarios específicos L-J: 8am-1pm y 2pm-5pm, V: 8am-1pm y 2pm-4pm, S: 8am-11am
- **Panamá**: Horarios L-V: 8am-5pm, S: 8am-12pm

#### Recogida de Pedidos
- **Colombia**: No disponible (mensaje informativo)
- **Panamá**: Disponible con dirección específica en Ciudad de Panamá

## Archivos Modificados

### 1. `messages.py`
- ✅ Agregados `MENSAJES_COLOMBIA` y `MENSAJES_PANAMA`
- ✅ Función `get_mensajes_pais(pais)` para obtener mensajes específicos

### 2. `bot_logic.py`
- ✅ Nuevas funciones:
  - `detectar_pais_desde_datos(datos)`
  - `aplicar_flujo_por_pais(pais, nombre, tracking_code, datos)`
  - `get_mensaje_devolucion_por_pais(pais)`
  - `get_mensaje_recogida_por_pais(pais, tracking_code)`
- ✅ Actualizada lógica del menú principal para usar flujos por país
- ✅ Optimización para evitar consultas innecesarias a BigQuery

### 3. `state.py`
- ✅ Agregadas funciones `set_pais(usuario, pais)` y `get_pais(usuario)`
- ✅ Almacenamiento en memoria del país detectado por sesión

## Flujo de Usuario

### Paso 1: Registro de Tracking
1. Usuario ingresa número de tracking
2. Sistema consulta BigQuery
3. **NUEVO**: Se detecta automáticamente el país
4. Se guarda el país en la sesión del usuario

### Paso 2: Opciones del Menú
- **Opción 1**: Novedad con entrega (igual para ambos países)
- **Opción 2**: Devolución → **Flujo específico por país**
- **Opción 3**: Consultar estado → **Flujo específico por país**

### Paso 3: Submenu de Entrega
- Opciones 1, 2, 4, 5, 6: Iguales para ambos países
- **Opción 3 (Recogida)**: Solo disponible para Panamá

## Ejemplos de Uso

### Colombia 🇨🇴
```
🇨🇴 Estado de tu guía BSCO123456789 - Colombia

📦 Estado: Disponible en centro de distribución
🚀 Origen: Miami
📍 Destino: Bogotá
📅 Última actualización: 08/08/2025 10:30

Juan, ¿te puedo ayudar en algo más?
1️⃣ Sí, volver al menú principal
2️⃣ No, finalizar conversación
```

### Panamá 🇵🇦
```
🇵🇦 Estado de tu guía BSPA987654321 - Panamá

📦 Estado: Disponible en estación de última milla
🚀 Origen: Miami
📍 Destino: Ciudad de Panamá
📅 Última actualización: 08/08/2025 15:45

María, ¿te puedo ayudar en algo más?
1️⃣ Sí, volver al menú principal
2️⃣ No, finalizar conversación
```

## Optimizaciones Implementadas

### 1. Cache en Sesión
- El país se detecta **una vez** y se guarda en memoria
- Se evitan consultas repetidas a BigQuery
- Mejora el rendimiento del bot

### 2. Fallback Inteligente
- Si no se detecta país → Por defecto Colombia
- Si falla la consulta → Se mantiene flujo estándar
- Garantiza funcionamiento continuo

### 3. Modularidad
- Funciones separadas por responsabilidad
- Fácil agregar nuevos países en el futuro
- Mantenimiento simplificado

## Pruebas

Ejecutar las pruebas con:
```bash
python test_flujo_pais_simple.py
```

Las pruebas verifican:
- ✅ Detección correcta de país
- ✅ Mensajes específicos por país
- ✅ Flujo de consulta de estado
- ✅ Flujo de devoluciones
- ✅ Flujo de recogida

## Futuras Mejoras

1. **Más Países**: Agregar México, Costa Rica, etc.
2. **Personalización Avanzada**: Idiomas, monedas locales
3. **Integración**: APIs locales para cada país
4. **Analytics**: Métricas por país de uso del bot

---

**Fecha de implementación**: 8 de agosto de 2025  
**Desarrollado por**: GitHub Copilot  
**Estado**: Implementado y probado ✅
