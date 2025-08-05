#!/bin/bash

# Script para obtener la URL de ngrok automáticamente
echo "🔍 Obteniendo URL de ngrok..."

# Verificar si ngrok está corriendo
if ! pgrep -f "ngrok" > /dev/null; then
    echo "❌ ngrok no está corriendo"
    echo "Iniciando ngrok..."
    nohup ngrok http 5000 > /dev/null 2>&1 &
    echo "⏳ Esperando que ngrok se inicie..."
    sleep 5
fi

# Intentar obtener la URL
for i in {1..10}; do
    URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    if tunnels:
        url = tunnels[0]['public_url']
        print(url)
    else:
        print('')
except:
    print('')
" 2>/dev/null)
    
    if [ ! -z "$URL" ]; then
        echo "✅ URL de ngrok encontrada:"
        echo "📱 URL pública: $URL"
        echo "🔗 Webhook para Twilio: $URL/whatsapp"
        echo ""
        echo "📋 Configurar en Twilio:"
        echo "   1. Ve a https://console.twilio.com/"
        echo "   2. WhatsApp > Senders"
        echo "   3. Configura webhook: $URL/whatsapp"
        
        # Guardar URL en archivo para referencia
        echo "$URL" > .ngrok_url
        echo "$URL/whatsapp" > .webhook_url
        
        break
    else
        echo "⏳ Intento $i/10 - Esperando ngrok..."
        sleep 2
    fi
done

if [ -z "$URL" ]; then
    echo "❌ No se pudo obtener la URL de ngrok"
    echo "Verifica que ngrok esté corriendo: pgrep -f ngrok"
    echo "O inicia manualmente: ngrok http 5000"
fi
