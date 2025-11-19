from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import os
from datetime import datetime
from dotenv import load_dotenv
from bot_logic import procesar_mensaje
from utils import descargar_imagen  # si defines esta función aparte

app = Flask(__name__)
load_dotenv()

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    numero = request.form.get("From")
    mensaje = request.form.get("Body")
    num_media = int(request.form.get("NumMedia", 0))

    # Manejar imagen adjunta
    imagen_guardada = None
    if num_media > 0:
        media_url = request.form.get("MediaUrl0")
        content_type = request.form.get("MediaContentType0")
        
        # Crear nombre único con fecha y hora
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        numero_limpio = numero[-10:]  # Últimos 10 dígitos del número
        nombre_archivo = f"evidencia_{numero_limpio}_{timestamp}.jpg"
        
        imagen_guardada = descargar_imagen(media_url, content_type, nombre_archivo)

    # Procesar mensaje como siempre
    respuesta = procesar_mensaje(numero, mensaje, imagen_guardada)


    # Puedes pasar imagen_guardada al procesador si quieres incluirla en correo
    twilio_resp = MessagingResponse()
    twilio_resp.message(respuesta)
    return str(twilio_resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    # Usar debug=False para producción con PM2
    app.run(host="0.0.0.0", port=port, debug=False)

