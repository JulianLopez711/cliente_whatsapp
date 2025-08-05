# Guía de Despliegue en VPS

## Pasos para desplegar el bot de WhatsApp en una VPS

### 1. Preparar el servidor VPS

```bash
# Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python y pip
sudo apt install python3 python3-pip python3-venv -y

# Instalar git
sudo apt install git -y

# Instalar nginx (opcional, para proxy reverso)
sudo apt install nginx -y

# Instalar supervisor para mantener el proceso funcionando
sudo apt install supervisor -y
```

### 2. Clonar y configurar el proyecto

```bash
# Clonar el repositorio
git clone https://github.com/JulianLopez711/cliente_whatsapp.git
cd cliente_whatsapp

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configurar archivos de credenciales

```bash
# Copiar plantillas
cp .env.template .env
cp credentials.json.template credentials.json

# Editar las configuraciones (usar nano o vim)
nano .env
nano credentials.json
```

### 4. Instalar y configurar ngrok

```bash
# Descargar ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Autenticar ngrok con tu token
ngrok config add-authtoken TU_AUTHTOKEN_DE_NGROK

# Crear script para obtener la URL de ngrok
cat > get_ngrok_url.sh << 'EOF'
#!/bin/bash
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        url = tunnels[0]['public_url']
        print(f'URL de ngrok: {url}')
        print(f'Webhook URL: {url}/whatsapp')
    else:
        print('No hay túneles activos')
except:
    print('Error al obtener la URL de ngrok')
"
EOF

chmod +x get_ngrok_url.sh
```

### 5. Crear archivos de configuración para supervisor

```bash
# Crear configuración para el bot
sudo tee /etc/supervisor/conf.d/whatsapp_bot.conf << EOF
[program:whatsapp_bot]
command=/home/usuario/cliente_whatsapp/venv/bin/python app.py
directory=/home/usuario/cliente_whatsapp
user=usuario
autostart=true
autorestart=true
stderr_logfile=/var/log/whatsapp_bot.err.log
stdout_logfile=/var/log/whatsapp_bot.out.log
environment=PATH="/home/usuario/cliente_whatsapp/venv/bin"
EOF

# Crear configuración para ngrok
sudo tee /etc/supervisor/conf.d/ngrok.conf << EOF
[program:ngrok]
command=/usr/local/bin/ngrok http 5000
user=usuario
autostart=true
autorestart=true
stderr_logfile=/var/log/ngrok.err.log
stdout_logfile=/var/log/ngrok.out.log
EOF
```

### 6. Iniciar servicios

```bash
# Recargar configuración de supervisor
sudo supervisorctl reread
sudo supervisorctl update

# Iniciar servicios
sudo supervisorctl start whatsapp_bot
sudo supervisorctl start ngrok

# Verificar estado
sudo supervisorctl status
```

### 7. Obtener la URL de ngrok

```bash
# Esperar unos segundos para que ngrok se inicie
sleep 10

# Ejecutar script para obtener URL
./get_ngrok_url.sh
```

### 8. Comandos útiles para administrar

```bash
# Ver logs del bot
sudo tail -f /var/log/whatsapp_bot.out.log

# Ver logs de ngrok
sudo tail -f /var/log/ngrok.out.log

# Reiniciar servicios
sudo supervisorctl restart whatsapp_bot
sudo supervisorctl restart ngrok

# Parar servicios
sudo supervisorctl stop whatsapp_bot
sudo supervisorctl stop ngrok

# Ver estado de todos los servicios
sudo supervisorctl status

# Obtener URL de ngrok en cualquier momento
./get_ngrok_url.sh
```

### 9. Configurar Twilio Webhook

Una vez que obtengas la URL de ngrok:

1. Ve a tu consola de Twilio
2. Navega a WhatsApp > Senders
3. Configura el webhook con: `https://TU_URL_NGROK.ngrok.io/whatsapp`

### 10. Script de monitoreo (opcional)

```bash
# Crear script de monitoreo
cat > monitor.sh << 'EOF'
#!/bin/bash

check_service() {
    local service=$1
    if sudo supervisorctl status $service | grep -q "RUNNING"; then
        echo "✅ $service está funcionando"
    else
        echo "❌ $service no está funcionando"
        sudo supervisorctl start $service
    fi
}

echo "=== Monitor de Servicios WhatsApp Bot ==="
check_service whatsapp_bot
check_service ngrok

echo ""
echo "=== URL actual de ngrok ==="
./get_ngrok_url.sh
EOF

chmod +x monitor.sh
```

### Notas importantes:

1. **Reemplaza** `/home/usuario/cliente_whatsapp` con la ruta real de tu proyecto
2. **Cambia** `usuario` por tu nombre de usuario en la VPS
3. **Configura** tu authtoken de ngrok obtenido desde https://dashboard.ngrok.com/
4. **Verifica** que el puerto 5000 esté disponible en tu VPS
5. **Considera** usar un dominio propio en lugar de ngrok para producción

### Solución de problemas:

```bash
# Si el bot no inicia, verificar logs
sudo tail -f /var/log/whatsapp_bot.err.log

# Si ngrok no funciona
curl http://localhost:4040/api/tunnels

# Verificar puertos en uso
sudo netstat -tlnp | grep :5000
sudo netstat -tlnp | grep :4040
```
