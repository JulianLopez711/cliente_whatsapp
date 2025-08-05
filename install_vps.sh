# Script de instalación automática para VPS Ubuntu

echo "🚀 Instalando WhatsApp Bot en VPS..."

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Actualizar sistema
echo -e "${YELLOW}📦 Actualizando sistema...${NC}"
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
echo -e "${YELLOW}📦 Instalando dependencias...${NC}"
sudo apt install -y python3 python3-pip python3-venv git curl wget supervisor nginx

# Crear usuario si no existe (opcional)
# sudo useradd -m -s /bin/bash whatsappbot

# Clonar repositorio (si no está clonado)
if [ ! -d "cliente_whatsapp" ]; then
    echo -e "${YELLOW}📥 Clonando repositorio...${NC}"
    git clone https://github.com/JulianLopez711/cliente_whatsapp.git
fi

cd cliente_whatsapp

# Crear entorno virtual
echo -e "${YELLOW}🐍 Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias Python
echo -e "${YELLOW}📦 Instalando dependencias Python...${NC}"
pip install -r requirements.txt

# Configurar archivos
echo -e "${YELLOW}⚙️  Configurando archivos...${NC}"
if [ ! -f ".env" ]; then
    cp .env.template .env
    echo -e "${RED}❗ Configura el archivo .env con tus credenciales${NC}"
fi

if [ ! -f "credentials.json" ]; then
    cp credentials.json.template credentials.json
    echo -e "${RED}❗ Configura el archivo credentials.json${NC}"
fi

# Instalar ngrok
echo -e "${YELLOW}🌐 Instalando ngrok...${NC}"
if [ ! -f "/usr/local/bin/ngrok" ]; then
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    echo -e "${RED}❗ Configura ngrok: ngrok config add-authtoken TU_TOKEN${NC}"
fi

# Hacer scripts ejecutables
chmod +x *.sh

# Configurar supervisor
echo -e "${YELLOW}⚙️  Configurando supervisor...${NC}"
sudo cp supervisor.conf /etc/supervisor/conf.d/whatsapp_bot.conf

# Ajustar rutas en configuración
USER_HOME=$(pwd)
sudo sed -i "s|/home/ubuntu/cliente_whatsapp|$USER_HOME|g" /etc/supervisor/conf.d/whatsapp_bot.conf
sudo sed -i "s|user=ubuntu|user=$USER|g" /etc/supervisor/conf.d/whatsapp_bot.conf

# Recargar supervisor
sudo supervisorctl reread
sudo supervisorctl update

echo -e "${GREEN}✅ Instalación completada!${NC}"
echo ""
echo -e "${YELLOW}📋 Próximos pasos:${NC}"
echo "1. Configura tus credenciales en .env"
echo "2. Configura credentials.json con tu archivo de Google"
echo "3. Configura ngrok: ngrok config add-authtoken TU_TOKEN"
echo "4. Ejecuta: ./start_vps.sh start"
echo "5. Obtén la URL: ./start_vps.sh url"
echo ""
echo -e "${YELLOW}🔧 Comandos útiles:${NC}"
echo "./start_vps.sh start    - Iniciar servicios"
echo "./start_vps.sh status   - Ver estado"
echo "./start_vps.sh logs     - Ver logs"
echo "./start_vps.sh url      - Obtener URL ngrok"
