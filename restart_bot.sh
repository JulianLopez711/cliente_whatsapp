#!/bin/bash
# Script para reiniciar el bot de WhatsApp en el servidor

echo "🔄 Deteniendo proceso actual de whatsapp-bot..."
pm2 delete whatsapp-bot 2>/dev/null || true

echo "📁 Creando directorio de logs si no existe..."
mkdir -p logs

echo "🚀 Iniciando whatsapp-bot con PM2..."
pm2 start ecosystem.config.js

echo "✅ Proceso iniciado. Mostrando estado..."
pm2 status whatsapp-bot

echo ""
echo "📊 Para ver logs en tiempo real:"
echo "   pm2 logs whatsapp-bot"
echo ""
echo "🔍 Para ver el estado:"
echo "   pm2 status"
echo ""
echo "🛑 Para detener:"
echo "   pm2 stop whatsapp-bot"
