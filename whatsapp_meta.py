import requests
import os
from dotenv import load_dotenv

load_dotenv()

class WhatsAppMeta:
    """
    Cliente para WhatsApp Business API de Meta/Facebook
    Ahorro: 50% vs Twilio
    """
    
    def __init__(self):
        self.token = os.getenv("META_WHATSAPP_TOKEN")
        self.phone_id = os.getenv("META_PHONE_NUMBER_ID")
        self.api_version = "v21.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_id}"
        
        if not self.token or not self.phone_id:
            print("⚠️ Advertencia: META_WHATSAPP_TOKEN o META_PHONE_NUMBER_ID no configurados")
    
    def send_message(self, to_number, message_text):
        """
        Envía un mensaje de texto por WhatsApp
        
        Args:
            to_number: Número en formato +573001234567 (puede incluir 'whatsapp:')
            message_text: Texto del mensaje
            
        Returns:
            dict: Respuesta de la API o None si hay error
        """
        url = f"{self.base_url}/messages"
        
        # Limpiar formato del número
        clean_number = to_number.replace("whatsapp:", "").replace("+", "").strip()
        if not clean_number.startswith("57") and not clean_number.startswith("507"):
            clean_number = f"57{clean_number}"  # Asumir Colombia por defecto
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message_text
            }
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            result = response.json()
            print(f"✅ Mensaje enviado a +{clean_number}: {len(message_text)} chars")
            return result
        except requests.exceptions.HTTPError as e:
            print(f"❌ Error HTTP {e.response.status_code}: {e.response.text}")
            return None
        except Exception as e:
            print(f"❌ Error enviando mensaje: {e}")
            return None
    
    def send_template(self, to_number, template_name, language_code="es", components=None):
        """
        Envía una plantilla pre-aprobada (más barato)
        
        Args:
            to_number: Número destino
            template_name: Nombre de la plantilla aprobada
            language_code: Código de idioma (es, en, etc)
            components: Parámetros de la plantilla
            
        Returns:
            dict: Respuesta de la API
        """
        url = f"{self.base_url}/messages"
        
        clean_number = to_number.replace("whatsapp:", "").replace("+", "").strip()
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        }
        
        if components:
            payload["template"]["components"] = components
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            print(f"✅ Plantilla '{template_name}' enviada a +{clean_number}")
            return response.json()
        except Exception as e:
            print(f"❌ Error enviando plantilla: {e}")
            return None
    
    def download_media(self, media_id):
        """
        Descarga un archivo multimedia (imagen, video, audio, documento)
        
        Args:
            media_id: ID del media proporcionado por Meta
            
        Returns:
            bytes: Contenido del archivo o None si hay error
        """
        try:
            # Paso 1: Obtener URL del media
            url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            media_data = response.json()
            
            media_url = media_data.get("url")
            mime_type = media_data.get("mime_type", "unknown")
            
            if not media_url:
                print(f"❌ No se encontró URL para media {media_id}")
                return None
            
            # Paso 2: Descargar el archivo
            media_response = requests.get(media_url, headers=headers, timeout=30)
            media_response.raise_for_status()
            
            print(f"✅ Media descargado: {media_id} ({mime_type})")
            return media_response.content
            
        except Exception as e:
            print(f"❌ Error descargando media {media_id}: {e}")
            return None
    
    def mark_as_read(self, message_id):
        """
        Marca un mensaje como leído
        
        Args:
            message_id: ID del mensaje
        """
        url = f"{self.base_url}/messages"
        
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": message_id
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"⚠️ No se pudo marcar como leído: {e}")
            return False
    
    def get_media_url(self, media_id):
        """
        Obtiene la URL de un archivo multimedia sin descargarlo
        
        Args:
            media_id: ID del media
            
        Returns:
            str: URL del media
        """
        try:
            url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.json().get("url")
        except Exception as e:
            print(f"❌ Error obteniendo URL de media: {e}")
            return None
