#!/bin/bash

# Script de gestión para WhatsApp Bot con Gunicorn + PM2

case "$1" in
    start)
        echo "🚀 Iniciando WhatsApp Bot con Gunicorn..."
        pm2 start ecosystem.config.js
        pm2 save
        echo "✅ Bot iniciado. Logs disponibles con: pm2 logs whatsapp-bot"
        ;;
    stop)
        echo "🛑 Deteniendo WhatsApp Bot..."
        pm2 stop whatsapp-bot
        echo "✅ Bot detenido"
        ;;
    restart)
        echo "🔄 Reiniciando WhatsApp Bot..."
        pm2 restart whatsapp-bot
        echo "✅ Bot reiniciado"
        ;;
    status)
        echo "📊 Estado del WhatsApp Bot:"
        pm2 list whatsapp-bot
        ;;
    logs)
        echo "📜 Mostrando logs del WhatsApp Bot..."
        pm2 logs whatsapp-bot --lines 50
        ;;
    monitor)
        echo "📈 Abriendo monitor de PM2..."
        pm2 monit
        ;;
    deploy)
        echo "🚀 Desplegando nueva versión..."
        git pull
        pm2 restart whatsapp-bot
        echo "✅ Despliegue completado"
        ;;
    test-gunicorn)
        echo "🧪 Probando Gunicorn directamente..."
        gunicorn app:app --config gunicorn.conf.py
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|monitor|deploy|test-gunicorn}"
        echo ""
        echo "Comandos disponibles:"
        echo "  start         - Inicia el bot con PM2 + Gunicorn"
        echo "  stop          - Detiene el bot"
        echo "  restart       - Reinicia el bot"
        echo "  status        - Muestra el estado del bot"
        echo "  logs          - Muestra los logs del bot"
        echo "  monitor       - Abre el monitor de PM2"
        echo "  deploy        - Actualiza código y reinicia"
        echo "  test-gunicorn - Prueba Gunicorn sin PM2"
        exit 1
        ;;
esac
