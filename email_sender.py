from flask_mail import Mail, Message
from app import app

# Inicializar Mail
mail = Mail(app)

def send_qr_code_email(to, event_name, event_date, qr_path):
    """
    Envia um email com o QR Code do evento
    
    Args:
        to: Email do destinatário
        event_name: Nome do evento
        event_date: Data do evento
        qr_path: Caminho completo para o arquivo QR Code
    """
    try:
        # Formatar data
        formatted_date = event_date.strftime('%d/%m/%Y às %H:%M')
        
        # Criar mensagem
        msg = Message(
            subject=f"QR Code para o evento: {event_name}",
            recipients=[to],
            body=f"""
            Olá,

            Seu evento foi criado com sucesso!

            Nome do evento: {event_name}
            Data: {formatted_date}

            O QR Code para o evento está anexado a este email.

            Obrigado,
            Lígia e Paulo.
            """
        )
        
        # Anexar QR Code ao email
        with open(qr_path, 'rb') as qr_file:
            msg.attach("qrcode_evento.png", "image/png", qr_file.read())
        
        # Enviar email
        mail.send(msg)
        print(f"Email enviado com sucesso para {to}")
        return True
    
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False
