import smtplib
from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

def crear_html_personalizado(cuerpo):
    """Convierte el contenido en HTML con diseño personalizado manteniendo el formato de líneas"""
    
    # Convertir el texto manteniendo los saltos de línea y formato
    cuerpo_formateado = cuerpo.replace('\n', '<br>')
    
    # Hacer que el texto en negrita (*texto*) se vea en negrita
    import re
    cuerpo_formateado = re.sub(r'\*(.*?)\*', r'<strong>\1</strong>', cuerpo_formateado)
    
    # Agregar estilos especiales para las secciones
    cuerpo_formateado = re.sub(r'📄 <strong>(.*?)</strong>', r'<div style="background:#e3f2fd;padding:15px;margin:10px 0;border-left:4px solid #2196f3;border-radius:5px;">📄 <strong>\1</strong></div>', cuerpo_formateado)
    cuerpo_formateado = re.sub(r'📦 <strong>(.*?)</strong>', r'<div style="background:#f3e5f5;padding:15px;margin:10px 0;border-left:4px solid #9c27b0;border-radius:5px;">📦 <strong>\1</strong></div>', cuerpo_formateado)
    cuerpo_formateado = re.sub(r'📌 <strong>(.*?)</strong>', r'<div style="background:#fff3e0;padding:15px;margin:10px 0;border-left:4px solid #ff9800;border-radius:5px;">📌 <strong>\1</strong></div>', cuerpo_formateado)
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }}
            .container {{ max-width: 700px; margin: 0 auto; background: white; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ background: linear-gradient(135deg, #1C4148, #0F2A2E); color: white; padding: 30px; text-align: center; }}
            .content {{ padding: 40px; font-size: 16px; }}
            .tracking-info {{ background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 14px; }}
            a {{ color: #1C4148; }}
            .highlight {{ background: #fffbf0; padding: 15px; border-left: 4px solid #ffc107; margin: 10px 0; border-radius: 5px; }}
            .emoji {{ font-size: 18px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 X-Cargo Bot</h1>
                <p>Nuevo Caso Reportado</p>
            </div>
            <div class="content">
                {cuerpo_formateado}
            </div>
            <div class="footer">
                <p><strong>X-Cargo</strong> - Sistema Automático</p>
                <p>📧 selfx@x-cargo.co | 🌐 Portal de Soporte</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_template

def enviar_correo(asunto, cuerpo, destino="selfx@x-cargo.co", adjuntos=[], html=True):
    try:
        print(f"📧 Intentando enviar correo: {asunto}")
        
        if html:
            # Crear mensaje con HTML
            msg = MIMEMultipart('alternative')
            msg["Subject"] = asunto
            msg["From"] = f"X-Cargo Bot <{SMTP_USER}>"
            msg["To"] = destino
            
            # Agregar versión texto plano
            text_part = MIMEText(cuerpo, 'plain')
            # Agregar versión HTML personalizada
            html_part = MIMEText(crear_html_personalizado(cuerpo), 'html')
            
            msg.attach(text_part)
            msg.attach(html_part)
        else:
            # Tu código original para texto plano
            msg = EmailMessage()
            msg["Subject"] = asunto
            msg["From"] = f"X-Cargo Bot <{SMTP_USER}>"
            msg["To"] = destino
            msg.set_content(cuerpo)

        # Adjuntar archivos (tu código original)
        for adj in adjuntos:
            if os.path.exists(adj):
                with open(adj, "rb") as f:
                    file_data = f.read()
                    file_name = os.path.basename(adj)
                    msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename=file_name)
                print(f"📎 Archivo adjunto: {file_name}")
            else:
                print(f"⚠️ Archivo no encontrado para adjuntar: {adj}")

        # Enviar correo (tu código original)
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)
            
        print(f"✅ Correo enviado exitosamente a {destino}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Error de autenticación SMTP: {e}")
        print("Verifica SMTP_USER y SMTP_PASS en el archivo .env")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ Error SMTP: {e}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado al enviar correo: {e}")
        return False