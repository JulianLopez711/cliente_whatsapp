from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Obtener ruta de credenciales desde .env
CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE", "credentials.json")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH")

# Determinar qué archivo de credenciales usar (priorizar credenciales de Drive)
if os.path.exists("drive-credentials.json"):
    SERVICE_ACCOUNT_FILE = "drive-credentials.json"
elif os.path.exists("credentials-drive-template.json"):
    SERVICE_ACCOUNT_FILE = "credentials-drive-template.json"
elif GOOGLE_CREDENTIALS_PATH and os.path.exists(GOOGLE_CREDENTIALS_PATH):
    SERVICE_ACCOUNT_FILE = GOOGLE_CREDENTIALS_PATH
elif os.path.exists(CREDENTIALS_FILE):
    SERVICE_ACCOUNT_FILE = CREDENTIALS_FILE
elif os.path.exists("credentials.json"):
    SERVICE_ACCOUNT_FILE = "credentials.json"
else:
    SERVICE_ACCOUNT_FILE = None

FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
SHARED_DRIVE_ID = os.getenv("GOOGLE_SHARED_DRIVE_ID")  # ID de la unidad compartida

# Carpeta específica para evidencias de tickets
EVIDENCIAS_FOLDER_ID = "1_xk6k3OrvAbnIwrWSi9cS2CLvB49txmY"  # Subcarpeta Evidencias

def subir_a_drive(nombre_archivo):
    """
    Intenta subir archivo a Google Drive. Si falla, lo copia a una carpeta local.
    """
    try:
        # Verificar si el archivo existe
        if not os.path.exists(nombre_archivo):
            print(f"Archivo no encontrado: {nombre_archivo}")
            return None
            
        # Verificar si el archivo de credenciales existe
        if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
            print(f"❌ Archivo de credenciales no encontrado: {SERVICE_ACCOUNT_FILE}")
            print("💡 Configuración requerida:")
            print("   1. Crear credentials.json o configurar CREDENTIALS_FILE en .env")
            print("   2. Habilitar Google Drive API en Google Cloud Console")
            print("   3. Dar permisos a la cuenta de servicio en la carpeta de Drive")
            return guardar_localmente(nombre_archivo)
            
        # Intentar subir a Google Drive
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        service = build("drive", "v3", credentials=creds)

        # Configurar metadata del archivo
        file_metadata = {
            "name": os.path.basename(nombre_archivo),
        }
        
        # Usar la carpeta específica de evidencias por defecto
        file_metadata["parents"] = [EVIDENCIAS_FOLDER_ID]
        
        # Configurar parámetros de subida
        create_params = {
            "body": file_metadata,
            "media_body": MediaFileUpload(nombre_archivo, resumable=True),
            "fields": "id"
        }

        archivo = service.files().create(**create_params).execute()

        file_id = archivo.get("id")

        # Hacer el archivo público
        permission_params = {
            "fileId": file_id,
            "body": {"type": "anyone", "role": "reader"}
        }
            
        service.permissions().create(**permission_params).execute()

        print(f"✅ Archivo subido a Drive en carpeta de evidencias: {os.path.basename(nombre_archivo)}")
        # Devolver enlace público
        return f"https://drive.google.com/file/d/{file_id}/view"
    
    except HttpError as e:
        error_details = e.error_details[0] if e.error_details else {}
        error_reason = error_details.get('reason', 'unknown')
        
        if error_reason == 'notFound':
            print(f"Error: Carpeta de Google Drive no encontrada (ID: {FOLDER_ID})")
            print("Verifica que el ID de la carpeta sea correcto y que la cuenta de servicio tenga permisos.")
        elif error_reason == 'storageQuotaExceeded':
            print("Error: Las cuentas de servicio no tienen cuota de almacenamiento.")
            print("Guardando archivo localmente como respaldo...")
            return guardar_localmente(nombre_archivo)
        else:
            print(f"Error de Google Drive ({error_reason}): {e}")
        
        # Si Google Drive falla, guardar localmente
        return guardar_localmente(nombre_archivo)
        
    except FileNotFoundError:
        print(f"Archivo no encontrado: {nombre_archivo}")
        return None
    except Exception as e:
        print(f"Error inesperado al subir archivo: {e}")
        return guardar_localmente(nombre_archivo)

def guardar_localmente(nombre_archivo):
    """
    Guarda el archivo en la carpeta local de respaldo: cliente_whatsapp\\evidencias
    """
    try:
        # Obtener la ruta del directorio del proyecto (cliente_whatsapp)
        directorio_proyecto = os.path.dirname(os.path.abspath(__file__))
        carpeta_evidencias = os.path.join(directorio_proyecto, "evidencias")
        
        # Crear carpeta de evidencias si no existe
        os.makedirs(carpeta_evidencias, exist_ok=True)
        
        # Copiar archivo a la carpeta de evidencias
        nombre_base = os.path.basename(nombre_archivo)
        ruta_destino = os.path.join(carpeta_evidencias, nombre_base)
        shutil.copy2(nombre_archivo, ruta_destino)
        
        print(f"✅ Archivo guardado localmente en: {ruta_destino}")
        print(f"📁 Carpeta de respaldo: {carpeta_evidencias}")
        return f"Archivo guardado localmente: {nombre_base}"
        
    except Exception as e:
        print(f"❌ Error al guardar localmente: {e}")
        return None
