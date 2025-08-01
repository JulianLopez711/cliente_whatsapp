from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.service_account import Credentials
from googleapiclient.errors import HttpError
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
SERVICE_ACCOUNT_FILE = "credentials.json"
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")
SHARED_DRIVE_ID = os.getenv("GOOGLE_SHARED_DRIVE_ID")  # ID de la unidad compartida

def subir_a_drive(nombre_archivo):
    """
    Intenta subir archivo a Google Drive. Si falla, lo copia a una carpeta local.
    """
    try:
        # Verificar si el archivo existe
        if not os.path.exists(nombre_archivo):
            print(f"Archivo no encontrado: {nombre_archivo}")
            return None
            
        # Intentar subir a Google Drive
        creds = Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES
        )

        service = build("drive", "v3", credentials=creds)

        # Configurar metadata del archivo
        file_metadata = {
            "name": os.path.basename(nombre_archivo),
        }
        
        # Usar unidad compartida si está configurada, sino carpeta normal
        if SHARED_DRIVE_ID:
            file_metadata["parents"] = [SHARED_DRIVE_ID]
            # Para unidades compartidas, necesitamos especificar supportsAllDrives
            create_params = {
                "body": file_metadata,
                "media_body": MediaFileUpload(nombre_archivo, resumable=True),
                "fields": "id",
                "supportsAllDrives": True
            }
        elif FOLDER_ID:
            file_metadata["parents"] = [FOLDER_ID]
            create_params = {
                "body": file_metadata,
                "media_body": MediaFileUpload(nombre_archivo, resumable=True),
                "fields": "id"
            }
        else:
            create_params = {
                "body": file_metadata,
                "media_body": MediaFileUpload(nombre_archivo, resumable=True),
                "fields": "id"
            }

        archivo = service.files().create(**create_params).execute()

        file_id = archivo.get("id")

        # Hacer el archivo público (con soporte para unidades compartidas)
        permission_params = {
            "fileId": file_id,
            "body": {"type": "anyone", "role": "reader"}
        }
        
        if SHARED_DRIVE_ID:
            permission_params["supportsAllDrives"] = True
            
        service.permissions().create(**permission_params).execute()

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
    Guarda el archivo en una carpeta local de respaldo
    """
    try:
        # Crear carpeta de evidencias si no existe
        carpeta_evidencias = os.path.join(os.path.dirname(__file__), "evidencias")
        os.makedirs(carpeta_evidencias, exist_ok=True)
        
        # Copiar archivo a la carpeta de evidencias
        nombre_base = os.path.basename(nombre_archivo)
        ruta_destino = os.path.join(carpeta_evidencias, nombre_base)
        shutil.copy2(nombre_archivo, ruta_destino)
        
        print(f"Archivo guardado localmente en: {ruta_destino}")
        return f"Archivo guardado localmente: {nombre_base}"
        
    except Exception as e:
        print(f"Error al guardar localmente: {e}")
        return None
