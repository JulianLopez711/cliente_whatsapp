# 🚀 GUÍA DE MIGRACIÓN: TWILIO → META WHATSAPP BUSINESS API

## 💰 AHORRO ESPERADO
- **Actual con Twilio optimizado:** $400/mes (5,000 conversaciones)
- **Con Meta directo:** $200/mes (5,000 conversaciones)
- **AHORRO ADICIONAL: $200/mes = $2,400/año** (50% más barato)

---

## 📋 PRE-REQUISITOS (Ya los tienes ✅)

✅ Números aprobados en Meta/Facebook
✅ Cuenta de Meta Business
✅ Acceso a WhatsApp Business API

---

## 🔧 CAMBIOS NECESARIOS EN EL CÓDIGO

### 1. Actualizar Dependencias

**Remover:**
```bash
twilio
```

**Agregar:**
```bash
pip install requests python-dotenv
```

### 2. Actualizar Variables de Entorno (.env)

**Cambiar de:**
```env
# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**A:**
```env
# Meta WhatsApp Business API
META_WHATSAPP_TOKEN=EAAxxxxxxxxxxxxx
META_PHONE_NUMBER_ID=123456789012345
META_BUSINESS_ACCOUNT_ID=123456789012345
META_WEBHOOK_VERIFY_TOKEN=tu_token_secreto_aleatorio
```

### 3. Nuevo archivo: whatsapp_meta.py

Crear este archivo para manejar la API de Meta:

```python
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppMeta:
    def __init__(self):
        self.token = os.getenv("META_WHATSAPP_TOKEN")
        self.phone_id = os.getenv("META_PHONE_NUMBER_ID")
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_id}"
        
    def send_message(self, to_number, message_text):
        """
        Envía un mensaje de texto
        to_number: formato +573001234567 (sin 'whatsapp:')
        """
        url = f"{self.base_url}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": to_number.replace("whatsapp:", ""),
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return None
    
    def download_media(self, media_id):
        """
        Descarga un archivo multimedia (imagen, video, etc)
        """
        # Paso 1: Obtener URL del media
        url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            media_url = response.json().get("url")
            
            # Paso 2: Descargar el archivo
            media_response = requests.get(media_url, headers=headers)
            media_response.raise_for_status()
            
            return media_response.content
        except Exception as e:
            print(f"❌ Error descargando media: {e}")
            return None
```

### 4. Actualizar app.py

**Reemplazar completamente con:**

```python
from flask import Flask, request, jsonify
import os
from datetime import datetime
from dotenv import load_dotenv
from bot_logic import procesar_mensaje
from whatsapp_meta import WhatsAppMeta
import hmac
import hashlib

app = Flask(__name__)
load_dotenv()

whatsapp = WhatsAppMeta()

# Verificación del webhook (requerido por Meta)
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    """
    Meta enviará un GET request para verificar el webhook
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    
    verify_token = os.getenv("META_WEBHOOK_VERIFY_TOKEN")
    
    if mode == "subscribe" and token == verify_token:
        print("✅ Webhook verificado correctamente")
        return challenge, 200
    else:
        print("❌ Verificación de webhook fallida")
        return "Forbidden", 403

# Recibir mensajes
@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Meta enviará los mensajes entrantes aquí
    """
    try:
        data = request.get_json()
        
        # Verificar que sea un mensaje de WhatsApp
        if not data.get("entry"):
            return jsonify({"status": "ok"}), 200
        
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                
                # Ignorar mensajes de estado
                if "messages" not in value:
                    continue
                
                messages = value.get("messages", [])
                
                for message in messages:
                    # Obtener datos del mensaje
                    from_number = message.get("from")
                    message_type = message.get("type")
                    timestamp = message.get("timestamp")
                    
                    # Agregar prefijo whatsapp: para compatibilidad con código existente
                    numero = f"whatsapp:+{from_number}"
                    
                    # Manejar diferentes tipos de mensajes
                    mensaje_texto = ""
                    imagen_guardada = None
                    
                    if message_type == "text":
                        mensaje_texto = message.get("text", {}).get("body", "")
                    
                    elif message_type == "image":
                        # Descargar imagen
                        media_id = message.get("image", {}).get("id")
                        caption = message.get("image", {}).get("caption", "")
                        
                        if media_id:
                            content = whatsapp.download_media(media_id)
                            if content:
                                os.makedirs("evidencias", exist_ok=True)
                                timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                                numero_limpio = from_number[-10:]
                                filename = f"evidencias/evidencia_{numero_limpio}_{timestamp_str}.jpg"
                                
                                with open(filename, "wb") as f:
                                    f.write(content)
                                
                                imagen_guardada = filename
                                print(f"✅ Imagen guardada: {filename}")
                        
                        mensaje_texto = caption if caption else ""
                    
                    elif message_type == "button":
                        # Respuesta a botón interactivo
                        mensaje_texto = message.get("button", {}).get("text", "")
                    
                    elif message_type == "interactive":
                        # Respuesta a lista o botones
                        interactive = message.get("interactive", {})
                        if interactive.get("type") == "button_reply":
                            mensaje_texto = interactive.get("button_reply", {}).get("title", "")
                        elif interactive.get("type") == "list_reply":
                            mensaje_texto = interactive.get("list_reply", {}).get("title", "")
                    
                    # Procesar mensaje con la lógica del bot
                    respuesta = procesar_mensaje(numero, mensaje_texto, imagen_guardada)
                    
                    # Enviar respuesta
                    whatsapp.send_message(from_number, respuesta)
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"❌ Error procesando webhook: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
```

---

## 🔐 CONFIGURACIÓN EN META

### Paso 1: Obtener credenciales

1. Ve a **Meta Business Suite**: https://business.facebook.com
2. Selecciona tu cuenta de negocio
3. Ve a **Configuración del sistema** → **WhatsApp Business API**
4. Copia el **Token de acceso** (META_WHATSAPP_TOKEN)
5. Copia el **ID del número de teléfono** (META_PHONE_NUMBER_ID)
6. Copia el **ID de cuenta de negocio** (META_BUSINESS_ACCOUNT_ID)

### Paso 2: Configurar Webhook

1. En Meta Business, ve a **Configuración de WhatsApp**
2. Click en **Configuración** → **Webhooks**
3. Click **Editar**
4. Ingresa tu URL: `https://tu-dominio.com/webhook`
5. Ingresa el token de verificación (el que pusiste en .env)
6. Suscríbete a estos eventos:
   - ✅ `messages` (mensajes entrantes)
   - ✅ `message_status` (estado de mensajes)

### Paso 3: Generar token permanente

Los tokens de Meta expiran, necesitas generar uno de larga duración:

1. Ve a **Configuración** → **Tokens de acceso del sistema**
2. Click **Generar nuevo token**
3. Selecciona permisos: `whatsapp_business_messaging`, `whatsapp_business_management`
4. Copia el token y actualiza tu .env

---

## 🧪 TESTING

### 1. Probar webhook localmente

```bash
# Instalar ngrok si no lo tienes
npm install -g ngrok

# Exponer puerto local
ngrok http 5000

# Usar la URL de ngrok en la configuración de Meta
# Ejemplo: https://abc123.ngrok.io/webhook
```

### 2. Verificar que el webhook funciona

```bash
# Meta enviará un GET request, deberías ver en logs:
✅ Webhook verificado correctamente
```

### 3. Enviar mensaje de prueba

Envía un mensaje de WhatsApp a tu número y verifica:
- ✅ Se recibe el mensaje
- ✅ Se procesa correctamente
- ✅ Se envía la respuesta
- ✅ Ves el emoji 💰 con el costo en logs

---

## 📊 COMPARATIVA DE CÓDIGO

### Twilio (Anterior)
```python
from twilio.twiml.messaging_response import MessagingResponse

twilio_resp = MessagingResponse()
twilio_resp.message(respuesta)
return str(twilio_resp)
```

### Meta (Nuevo)
```python
from whatsapp_meta import WhatsAppMeta

whatsapp = WhatsAppMeta()
whatsapp.send_message(numero, respuesta)
return jsonify({"status": "ok"}), 200
```

**Más simple y directo** ✅

---

## ⚠️ DIFERENCIAS IMPORTANTES

### 1. Formato de número
- **Twilio:** `whatsapp:+573001234567`
- **Meta:** `+573001234567` (sin prefijo)

### 2. Webhook
- **Twilio:** POST simple con form data
- **Meta:** GET (verificación) + POST (mensajes) con JSON

### 3. Respuesta
- **Twilio:** TwiML response
- **Meta:** API REST call separado

### 4. Descarga de medios
- **Twilio:** URL directa con auth básica
- **Meta:** Dos pasos (obtener URL → descargar)

---

## 🚀 PROCESO DE MIGRACIÓN

### Día 1: Preparación
1. ✅ Crear archivo `whatsapp_meta.py`
2. ✅ Actualizar `app.py`
3. ✅ Configurar variables de entorno
4. ✅ Instalar dependencias

### Día 2: Testing local
1. ✅ Probar con ngrok
2. ✅ Configurar webhook en Meta
3. ✅ Enviar mensajes de prueba
4. ✅ Verificar que todo funcione

### Día 3: Migración a producción
1. ✅ Actualizar código en servidor
2. ✅ Actualizar configuración de webhook en Meta
3. ✅ Cambiar webhook URL de Twilio a tu servidor
4. ✅ Monitorear logs

### Día 4-7: Monitoreo
1. ✅ Verificar que todos los mensajes se entreguen
2. ✅ Revisar costos en Meta Business
3. ✅ Comparar con costos anteriores de Twilio
4. ✅ Documentar ahorro

---

## 💰 AHORRO ESPERADO (Proyección)

Con **5,000 conversaciones/mes**:

| Concepto | Twilio Optimizado | Meta Directo | Ahorro |
|----------|-------------------|--------------|--------|
| Costo por mensaje | $0.008 | $0.004 | 50% |
| Costo mensual | $400 | $200 | $200 |
| Costo anual | $4,800 | $2,400 | **$2,400** |

**Ahorro total con ambas optimizaciones:**
- Mensajes optimizados: -50% ($2,400/año)
- Migración a Meta: -50% adicional ($2,400/año)
- **TOTAL: 75% de reducción = $4,800/año ahorrado** 🎉

---

## 📞 SOPORTE

### Documentación oficial:
- **Meta WhatsApp API:** https://developers.facebook.com/docs/whatsapp
- **Webhooks:** https://developers.facebook.com/docs/graph-api/webhooks

### En caso de problemas:
1. Verificar logs del servidor
2. Revisar configuración de webhook en Meta
3. Verificar que el token no haya expirado
4. Consultar la documentación de Meta

---

## ✅ CHECKLIST DE MIGRACIÓN

### Pre-migración
- [ ] Backup completo del código actual
- [ ] Backup de base de datos
- [ ] Documentar configuración actual de Twilio
- [ ] Obtener credenciales de Meta

### Implementación
- [ ] Crear `whatsapp_meta.py`
- [ ] Actualizar `app.py`
- [ ] Actualizar `.env` con credenciales Meta
- [ ] Instalar dependencias necesarias
- [ ] Testing local con ngrok

### Producción
- [ ] Desplegar código actualizado
- [ ] Configurar webhook en Meta
- [ ] Cambiar URL de webhook desde Twilio
- [ ] Enviar mensaje de prueba
- [ ] Verificar logs

### Post-migración
- [ ] Monitorear primeras 100 conversaciones
- [ ] Verificar costos en Meta Business
- [ ] Comparar con costos anteriores
- [ ] Documentar resultados
- [ ] Cancelar Twilio (después de confirmar que todo funciona)

---

**Fecha de creación:** 2 de enero de 2026
**Versión:** 1.0
**Estado:** Listo para implementación
