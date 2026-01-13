import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

load_dotenv()

def descargar_imagen(media_url, content_type, nombre_archivo):
    sid = os.getenv("TWILIO_ACCOUNT_SID")
    token = os.getenv("TWILIO_AUTH_TOKEN")

    if not sid or not token:
        print("❌ TWILIO_ACCOUNT_SID o AUTH_TOKEN no están definidos")
        return None

    try:
        # Crear directorio evidencias si no existe
        os.makedirs("evidencias", exist_ok=True)
        
        # Guardar en directorio evidencias
        ruta_completa = os.path.join("evidencias", nombre_archivo)
        
        response = requests.get(media_url, auth=HTTPBasicAuth(sid, token))
        if response.status_code == 200:
            with open(ruta_completa, "wb") as f:
                f.write(response.content)
            print(f"✅ Imagen guardada como {ruta_completa}")
            return ruta_completa
        else:
            print(f"❌ Error al descargar imagen: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Excepción al descargar imagen: {e}")
        return None
