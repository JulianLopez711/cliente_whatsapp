# 🎯 GUÍA PASO A PASO: Obtener Credenciales de Meta WhatsApp Business

## 📱 RUTA CORRECTA: Administrador de WhatsApp

### 🔗 URL DIRECTA
**https://business.facebook.com/wa/manage/home/**

---

## 📋 PASO 1: ACCEDER AL ADMINISTRADOR DE WHATSAPP

1. Ve a: **https://business.facebook.com**
2. En el menú lateral izquierdo, busca **"WhatsApp Business"** o **"Administrador de WhatsApp"**
3. O usa la URL directa: **https://business.facebook.com/wa/manage/home/**

---

## 🔑 PASO 2: OBTENER EL TOKEN DE ACCESO (META_WHATSAPP_TOKEN)

### Opción A: Desde Administrador de WhatsApp

1. En el Administrador de WhatsApp, ve a:
   ```
   ⚙️ Configuración (arriba a la derecha)
   → API de WhatsApp Business
   → Token de acceso
   ```

2. Click en **"Generar token"** o **"Crear token"**

3. Selecciona permisos:
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_management`

4. **Copia el token** (empieza con `EAA...`)
   ⚠️ **¡IMPORTANTE!** Solo se muestra una vez, guárdalo de inmediato

### Opción B: Desde Meta for Developers

1. Ve a: **https://developers.facebook.com/apps/**
2. Selecciona tu aplicación (o crea una nueva)
3. En el menú izquierdo: **WhatsApp → Inicio rápido**
4. Busca la sección **"Token de acceso temporal"**
5. Click en **"Generar token"**
6. Copia el token

⚠️ **Token temporal vs permanente:**
- Temporal: Expira en 24 horas (para testing)
- Permanente: Dura 60 días o más (para producción)

---

## 📞 PASO 3: OBTENER ID DEL NÚMERO DE TELÉFONO (META_PHONE_NUMBER_ID)

### Ruta correcta:

1. En el **Administrador de WhatsApp**: https://business.facebook.com/wa/manage/home/
2. Click en tu número de teléfono en la lista
3. O ve a: **Números de teléfono** en el menú lateral
4. Selecciona tu número
5. En la URL verás algo como:
   ```
   https://business.facebook.com/wa/manage/phone-numbers/123456789012345/
                                                        ^^^^^^^^^^^^^^^^^^^
                                                        Este es tu PHONE_NUMBER_ID
   ```

### Alternativa desde la API:

1. En **Administrador de WhatsApp**
2. Ve a **Configuración** → **API de WhatsApp Business**
3. Busca la sección **"Información de la configuración"**
4. Ahí verás el **"ID del número de teléfono"**

---

## 🏢 PASO 4: OBTENER ID DE CUENTA DE NEGOCIO (META_BUSINESS_ACCOUNT_ID)

1. En el **Administrador de WhatsApp**
2. Mira la URL, verás algo como:
   ```
   https://business.facebook.com/wa/manage/home/?business_id=123456789012345
                                                              ^^^^^^^^^^^^^^^^^^^
                                                              Este es tu BUSINESS_ACCOUNT_ID
   ```

3. O ve a: **⚙️ Configuración → Información de cuenta**

---

## 🔐 PASO 5: GENERAR TOKEN PERMANENTE (RECOMENDADO)

Los tokens temporales expiran rápido. Para producción:

### Método 1: Tokens del sistema (Recomendado)

1. Ve a **Meta Business Suite**: https://business.facebook.com/settings
2. En el menú izquierdo: **Usuarios → Usuarios del sistema**
3. Click **"Agregar"** para crear un nuevo usuario del sistema
4. Dale permisos de **Administrador** a tu aplicación de WhatsApp
5. Click en **"Generar nuevo token"**
6. Selecciona tu aplicación
7. Marca permisos:
   - ✅ `whatsapp_business_messaging`
   - ✅ `whatsapp_business_management`
8. **Copia el token** - Este no expira (o expira en 60+ días)

### Método 2: Desde Graph API Explorer

1. Ve a: https://developers.facebook.com/tools/explorer/
2. En la esquina superior derecha, selecciona tu aplicación
3. Click en **"Generar token de acceso"**
4. Selecciona permisos de WhatsApp
5. Click en el ícono **"ℹ️"** al lado del token
6. Click en **"Extender token de acceso"**
7. Copia el nuevo token extendido

---

## 🎬 VIDEOS RECOMENDADOS

### Video oficial de Meta (inglés):
**"How to Set Up WhatsApp Business API"**
https://www.youtube.com/results?search_query=meta+whatsapp+business+api+setup+2025

### Búsqueda en YouTube (español):
- "Configurar WhatsApp Business API Meta 2025"
- "Obtener token de acceso WhatsApp Business"
- "WhatsApp Cloud API tutorial español"

---

## 📸 CAPTURA DE PANTALLA EJEMPLO

```
Administrador de WhatsApp
├── 📱 Números de teléfono
│   └── +57 300 123 4567 ← Tu número
│       ├── 🔑 ID del número: 123456789012345
│       └── ⚙️ Configuración
│
├── ⚙️ Configuración
│   ├── API de WhatsApp Business
│   │   ├── 🔐 Token de acceso ← Aquí generas el token
│   │   └── 📊 Información de la configuración
│   │
│   └── Webhooks ← Lo configurarás después
│
└── 📊 Información de cuenta
    └── 🏢 ID de cuenta: 123456789012345
```

---

## ✅ CHECKLIST DE CREDENCIALES

Una vez que tengas todo, tu archivo `.env` debe verse así:

```env
# Meta WhatsApp Business API
META_WHATSAPP_TOKEN=EAAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
META_PHONE_NUMBER_ID=123456789012345
META_BUSINESS_ACCOUNT_ID=123456789012345
META_WEBHOOK_VERIFY_TOKEN=mi_secreto_aleatorio_123
```

### Verificación rápida:

- [ ] `META_WHATSAPP_TOKEN` empieza con `EAA`
- [ ] `META_PHONE_NUMBER_ID` tiene 15 dígitos
- [ ] `META_BUSINESS_ACCOUNT_ID` tiene 15 dígitos
- [ ] `META_WEBHOOK_VERIFY_TOKEN` es cualquier string que tú elijas

---

## 🧪 PROBAR QUE FUNCIONA

Una vez que tengas las credenciales, prueba con este script:

```python
import requests

TOKEN = "tu_token_aqui"
PHONE_ID = "tu_phone_id_aqui"

# Probar que el token funciona
url = f"https://graph.facebook.com/v21.0/{PHONE_ID}"
headers = {"Authorization": f"Bearer {TOKEN}"}

response = requests.get(url, headers=headers)
print(response.json())

# Si ves info del número, ¡funciona! ✅
# Si ves error 401, el token es inválido ❌
# Si ves error 404, el PHONE_ID es incorrecto ❌
```

---

## ❓ PROBLEMAS COMUNES

### "No encuentro el token de acceso"
→ Asegúrate de estar en el **Administrador de WhatsApp**, no en Meta Business Suite general
→ URL directa: https://business.facebook.com/wa/manage/home/

### "El token expira muy rápido"
→ Usa un **Token del sistema** (no expira)
→ O genera un **token de larga duración** desde Graph API Explorer

### "No veo mi número de teléfono"
→ Verifica que el número esté **verificado y aprobado** en Meta
→ Ve a **Números de teléfono** en el Administrador de WhatsApp

### "No tengo acceso a la API"
→ Verifica que tu cuenta de negocio esté **verificada**
→ Algunos países requieren verificación adicional

---

## 📞 SOPORTE

Si sigues teniendo problemas:

1. **Centro de ayuda de Meta WhatsApp:**
   https://business.facebook.com/business/help/whatsapp

2. **Comunidad de desarrolladores:**
   https://developers.facebook.com/community/

3. **Verificar estado de la API:**
   https://developers.facebook.com/status/

---

## 🎯 PRÓXIMO PASO

Una vez que tengas las 3 credenciales:
1. Actualiza tu archivo `.env`
2. Prueba el script de verificación
3. Avísame y te ayudo a actualizar `app.py` para usar Meta

---

**Última actualización:** 2 de enero de 2026
**Versión:** 2.0 - Rutas actualizadas
