#!/bin/bash

# Script de inicio y monitoreo para VPS
echo "🚀 Iniciando WhatsApp Bot en VPS..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar si estamos en el directorio correcto
if [ ! -f "app.py" ]; then
    echo -e "${RED}❌ Error: app.py no encontrado. Ejecuta desde el directorio del proyecto.${NC}"
    exit 1
fi

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Creando entorno virtual...${NC}"
    python3 -m venv venv
fi

# Activar entorno virtual
source venv/bin/activate

# Instalar dependencias si es necesario
if [ ! -f "venv/pyvenv.cfg" ] || [ requirements.txt -nt venv/pyvenv.cfg ]; then
    echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
    pip install -r requirements.txt
fi

# Verificar archivos de configuración
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Archivo .env no encontrado. Copia .env.template y configúralo.${NC}"
    exit 1
fi

if [ ! -f "credentials.json" ]; then
    echo -e "${RED}❌ Archivo credentials.json no encontrado. Copia credentials.json.template y configúralo.${NC}"
    exit 1
fi

# Función para verificar servicios
check_service() {
    local name=$1
    local port=$2
    local process=$3
    
    if pgrep -f "$process" > /dev/null; then
        echo -e "${GREEN}✅ $name está corriendo${NC}"
        return 0
    else
        echo -e "${RED}❌ $name no está corriendo${NC}"
        return 1
    fi
}

# Función para iniciar el bot
start_bot() {
    echo -e "${YELLOW}🤖 Iniciando bot de WhatsApp...${NC}"
    nohup python app.py > bot.log 2>&1 &
    echo $! > bot.pid
    sleep 3
    
    if check_service "Bot WhatsApp" 5000 "app.py"; then
        echo -e "${GREEN}✅ Bot iniciado correctamente${NC}"
    else
        echo -e "${RED}❌ Error al iniciar el bot${NC}"
        echo "Logs del bot:"
        tail -n 10 bot.log
        return 1
    fi
}

# Función para iniciar ngrok
start_ngrok() {
    echo -e "${YELLOW}🌐 Iniciando ngrok...${NC}"
    nohup ngrok http 5000 > ngrok.log 2>&1 &
    echo $! > ngrok.pid
    sleep 5
    
    if check_service "ngrok" 4040 "ngrok"; then
        echo -e "${GREEN}✅ ngrok iniciado correctamente${NC}"
        # Obtener URL
        ./get_ngrok_url.sh
    else
        echo -e "${RED}❌ Error al iniciar ngrok${NC}"
        echo "Logs de ngrok:"
        tail -n 10 ngrok.log
        return 1
    fi
}

# Función para parar servicios
stop_services() {
    echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
    
    if [ -f "bot.pid" ]; then
        kill $(cat bot.pid) 2>/dev/null
        rm bot.pid
    fi
    
    if [ -f "ngrok.pid" ]; then
        kill $(cat ngrok.pid) 2>/dev/null
        rm ngrok.pid
    fi
    
    # Matar procesos por nombre si quedan
    pkill -f "app.py" 2>/dev/null
    pkill -f "ngrok" 2>/dev/null
    
    echo -e "${GREEN}✅ Servicios detenidos${NC}"
}

# Función para mostrar estado
show_status() {
    echo -e "${YELLOW}📊 Estado de servicios:${NC}"
    check_service "Bot WhatsApp" 5000 "app.py"
    check_service "ngrok" 4040 "ngrok"
    
    if [ -f ".ngrok_url" ]; then
        echo -e "${GREEN}🔗 URL actual: $(cat .ngrok_url)${NC}"
        echo -e "${GREEN}📱 Webhook: $(cat .webhook_url)${NC}"
    fi
}

# Función para mostrar logs
show_logs() {
    echo -e "${YELLOW}📋 Logs del bot (últimas 20 líneas):${NC}"
    if [ -f "bot.log" ]; then
        tail -n 20 bot.log
    else
        echo "No hay logs del bot"
    fi
    
    echo -e "${YELLOW}📋 Logs de ngrok (últimas 10 líneas):${NC}"
    if [ -f "ngrok.log" ]; then
        tail -n 10 ngrok.log
    else
        echo "No hay logs de ngrok"
    fi
}

# Función para reiniciar servicios
restart_services() {
    echo -e "${YELLOW}🔄 Reiniciando servicios...${NC}"
    stop_services
    sleep 2
    start_bot
    start_ngrok
}

# Procesar argumentos
case "$1" in
    start)
        stop_services
        start_bot
        start_ngrok
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    url)
        ./get_ngrok_url.sh
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs|url}"
        echo ""
        echo "Comandos:"
        echo "  start   - Iniciar bot y ngrok"
        echo "  stop    - Detener servicios"
        echo "  restart - Reiniciar servicios"
        echo "  status  - Mostrar estado"
        echo "  logs    - Mostrar logs"
        echo "  url     - Obtener URL de ngrok"
        exit 1
        ;;
esac
