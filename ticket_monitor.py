import time
from datetime import datetime
from sqlalchemy import create_engine, text
from db import SessionLocal, TicketWhatsapp
from dotenv import load_dotenv
import os

load_dotenv()

def enviar_notificacion_whatsapp(numero, mensaje):
    from twilio.rest import Client
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    twilio_number = os.getenv('TWILIO_WHATSAPP_NUMBER')
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=mensaje,
        from_=twilio_number,
        to=f'whatsapp:{numero}'
    )
    print(f"✅ Notificación enviada a {numero}: {message.sid}")

def obtener_respuesta_agente(ticket_id, tickets_engine):
    with tickets_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT ht.comentario, u.nombre
            FROM historial_ticket ht
            LEFT JOIN usuarios u ON ht.usuario_id = u.id
            WHERE ht.ticket_id = :ticket_id
            AND ht.comentario IS NOT NULL AND ht.comentario != ''
            ORDER BY ht.fecha_accion DESC
            LIMIT 1
        """), {'ticket_id': ticket_id})
        respuesta = result.fetchone()
        if respuesta:
            return respuesta[0], respuesta[1] or 'Agente de Soporte'
        return None, None

def verificar_tickets_cerrados():
    TICKETS_DATABASE_URL = os.getenv('TICKETS_DATABASE_URL')
    tickets_engine = create_engine(TICKETS_DATABASE_URL)
    db_local = SessionLocal()
    with tickets_engine.connect() as conn:
        result = conn.execute(text("""
            SELECT t.id, t.estado, t.fecha_cierre
            FROM tickets t
            WHERE t.estado IN ('cerrado', 'resuelto', 'finalizado')
            AND t.fecha_cierre >= NOW() - INTERVAL '2 hours'
            AND t.canal = 'whatsapp'
        """))
        tickets_cerrados = result.fetchall()
        for ticket in tickets_cerrados:
            ticket_id = ticket[0]
            estado = ticket[1]
            fecha_cierre = ticket[2]
            ticket_whatsapp = db_local.query(TicketWhatsapp).filter(
                TicketWhatsapp.ticket_id == ticket_id,
                TicketWhatsapp.notificado_cierre == False
            ).first()
            if ticket_whatsapp:
                comentario, agente_nombre = obtener_respuesta_agente(ticket_id, tickets_engine)
                mensaje = f"""
🎉 *Tu caso ha sido resuelto*

📋 *Detalles:*
• Caso: #{ticket_id}
• Tracking: {ticket_whatsapp.tracking_codigo or 'N/A'}
• Estado: *{estado.upper()}*
• Fecha resolución: {fecha_cierre.strftime('%d/%m/%Y %H:%M') if fecha_cierre else 'N/A'}

💬 *Respuesta de nuestro equipo:*
_{comentario or 'Tu caso ha sido atendido por nuestro equipo. Si tienes dudas, contáctanos.'}_

👤 Atendido por: {agente_nombre or 'Agente de Soporte'}

✅ Tu solicitud ha sido resuelta satisfactoriamente.

*Gracias por usar X-Cargo* 🚚
                """.strip()
                enviar_notificacion_whatsapp(ticket_whatsapp.usuario_numero, mensaje)
                ticket_whatsapp.notificado_cierre = True
                ticket_whatsapp.estado_ticket = estado
                ticket_whatsapp.cerrado_en = fecha_cierre
                db_local.commit()
    db_local.close()

if __name__ == "__main__":
    while True:
        verificar_tickets_cerrados()
        time.sleep(900)  # 15 minutos
