# Cliente WhatsApp Bot

Bot de WhatsApp para gestión de clientes con integración de Google Drive, correo electrónico y OpenAI.

## Configuración

### 1. Credenciales
Copia los archivos de plantilla y configurálos con tus credenciales reales:

```bash
cp .env.template .env
cp credentials.json.template credentials.json
```

### 2. Variables de Entorno (.env)
Edita el archivo `.env` con tus credenciales:

- **TWILIO_ACCOUNT_SID**: Tu Account SID de Twilio
- **TWILIO_AUTH_TOKEN**: Tu Auth Token de Twilio  
- **TWILIO_WHATSAPP_NUMBER**: Número de WhatsApp de Twilio
- **EMAIL_ADDRESS**: Tu dirección de correo
- **EMAIL_PASSWORD**: Contraseña de aplicación de tu correo
- **OPENAI_API_KEY**: Tu API key de OpenAI

### 3. Credenciales de Google Cloud
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto y habilita Google Drive API
3. Crea una cuenta de servicio
4. Descarga el archivo JSON de credenciales
5. Renómbralo a `datos-clientes-441216-e0f1e3740f41.json`
6. Colócalo en el directorio `credentials/`

### 4. Instalación
```bash
pip install -r requirements.txt
```

### 5. Ejecución
```bash
python app.py
```

## Estructura del Proyecto

- `app.py` - Aplicación principal
- `bot_logic.py` - Lógica del bot
- `db.py` - Manejo de base de datos
- `drive.py` - Integración con Google Drive
- `mail.py` - Envío de correos
- `messages.py` - Manejo de mensajes
- `helpers.py` - Funciones auxiliares
- `state.py` - Manejo de estado
- `utils.py` - Utilidades
- `tracking_data.py` - Seguimiento de datos

## Seguridad

**IMPORTANTE**: Nunca subas archivos con credenciales reales al repositorio. Usa siempre los archivos de plantilla (.template) y configura tus credenciales localmente.
