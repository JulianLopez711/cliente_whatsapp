# 🔧 Solución para Worker Timeout en Bot de WhatsApp

## 📊 Problema Identificado

Los workers de Gunicorn se están bloqueando con el error:
```
[CRITICAL] WORKER TIMEOUT (pid:xxx)
```

**Causas principales:**
1. ❌ Workers síncronos bloqueantes
2. ❌ Pool de conexiones de base de datos no optimizado
3. ❌ Timeout muy bajo (120s)
4. ❌ Conexiones SSL cerrándose inesperadamente

## ✅ Cambios Aplicados

### 1. **Configuración Optimizada de Gunicorn** (`ecosystem.config.js`)

**ANTES:**
```javascript
args: '-w 4 -b 0.0.0.0:5000 app:app --timeout 120 --worker-class sync'
```

**AHORA:**
```javascript
args: '-w 4 -b 0.0.0.0:5000 app:app --timeout 300 --graceful-timeout 300 --worker-class gthread --threads 2 --keep-alive 5'
```

**Mejoras:**
- ⏱️ Timeout aumentado a 300s (5 minutos)
- 🧵 Worker class cambiado a `gthread` (workers con hilos)
- 🔢 2 threads por worker = 8 threads concurrentes totales
- 💚 Keep-alive configurado para mantener conexiones

### 2. **Pool de Conexiones Optimizado** (`db.py`)

**Configuración añadida:**
```python
ENGINE_OPTS = {
    "pool_size": 10,              # 10 conexiones en el pool
    "max_overflow": 20,           # 20 conexiones adicionales bajo demanda
    "pool_timeout": 30,           # Timeout para obtener conexión
    "pool_recycle": 1800,         # Reciclar conexiones cada 30 min
    "pool_pre_ping": True,        # Verificar conexión antes de usar
    "connect_args": {
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5
    }
}
```

**Beneficios:**
- ✅ Conexiones reutilizables
- ✅ Detección automática de conexiones muertas
- ✅ Reconexión automática
- ✅ Keep-alive a nivel PostgreSQL

## 🚀 Instrucciones de Despliegue

### Paso 1: Subir cambios al servidor

```bash
# En tu máquina local (Windows)
git add ecosystem.config.js db.py DEPLOY_FIX_TIMEOUT.md
git commit -m "Fix: Worker timeout - Optimización de pool y configuración Gunicorn"
git push origin master
```

### Paso 2: En el servidor VPS

```bash
# Conectarse al servidor
ssh devxcargo@tu-servidor

# Ir al directorio del proyecto
cd cliente_whatsapp

# Hacer pull de los cambios
git pull origin master

# Verificar que los cambios se aplicaron
cat ecosystem.config.js | grep "gthread"
cat db.py | grep "pool_size"

# Reiniciar PM2
pm2 restart whatsapp-bot

# Verificar estado
pm2 status

# Monitorear logs en tiempo real
pm2 logs whatsapp-bot --lines 50
```

### Paso 3: Verificación

```bash
# Verificar que no hay errores de timeout
pm2 logs whatsapp-bot | grep "TIMEOUT"

# Verificar conexiones a base de datos
pm2 logs whatsapp-bot | grep "pool"

# Ver estado de los workers
pm2 info whatsapp-bot
```

## 📈 Monitoreo Post-Despliegue

### Comandos útiles:

```bash
# Ver logs en tiempo real
pm2 logs whatsapp-bot

# Ver solo errores
pm2 logs whatsapp-bot --err

# Ver métricas
pm2 monit

# Reiniciar si hay problemas
pm2 restart whatsapp-bot

# Reinicio completo (matar y volver a iniciar)
pm2 delete whatsapp-bot
pm2 start ecosystem.config.js
```

## 🔍 Señales de Éxito

✅ **No más errores de "WORKER TIMEOUT"**
✅ **Respuestas rápidas del bot**
✅ **Sin errores de SSL connection closed**
✅ **Logs limpios sin excepciones de base de datos**

## ⚠️ Si Persisten los Problemas

### Opción A: Aumentar recursos
```javascript
// En ecosystem.config.js
args: '-w 6 -b 0.0.0.0:5000 app:app --timeout 600 --graceful-timeout 600 --worker-class gthread --threads 4'
```

### Opción B: Pool más grande
```python
# En db.py
ENGINE_OPTS = {
    "pool_size": 20,
    "max_overflow": 40,
    # ... resto de configuración
}
```

### Opción C: Usar workers asíncronos
```bash
# Instalar eventlet o gevent
pip install eventlet

# En ecosystem.config.js
args: '-w 4 -b 0.0.0.0:5000 app:app --timeout 300 --worker-class eventlet'
```

## 📝 Notas Importantes

1. **Memoria:** Con estos cambios, el consumo de memoria puede aumentar ligeramente
2. **Conexiones DB:** Asegúrate de que PostgreSQL soporte al menos 50 conexiones concurrentes
3. **Monitoreo:** Vigila los logs durante las primeras horas después del despliegue

## 🆘 Rollback (Si es necesario)

```bash
# En el servidor
cd cliente_whatsapp
git checkout HEAD~1 ecosystem.config.js db.py
pm2 restart whatsapp-bot
```

---

**Creado:** 2 de diciembre de 2025  
**Autor:** GitHub Copilot  
**Versión:** 1.0
