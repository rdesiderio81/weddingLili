from flask_mail import Message
from app import mail, app

def send_qr_code_email(to, event_name, event_date, qr_path):
    try:
        formatted_date = event_date.strftime('%d/%m/%Y às %H:%M')
        msg = Message(
            subject=f"QR Code para o evento: {event_name}",
            recipients=[to]
        )
        msg.html = f"""
        <b>Nome do evento:</b> {event_name}<br>
        <b>Data:</b> {formatted_date}<br>
        Compartilhe o QR Code abaixo com seus convidados para que eles possam enviar fotos diretamente para a galeria do evento.<br>
        <img src="{qr_path}" alt="QR Code do Evento">
        """
        with app.app_context():
            mail.send(msg)
        return True
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
        return False
