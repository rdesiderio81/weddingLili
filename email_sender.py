from flask_mail import Mail, Message
from app import app
import os

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
            recipients=[to]
        )
        
        # Conteúdo do email
        msg.html = f"""
        <html>
        <body>
            <h2>Seu evento foi criado com sucesso!</h2>
            <p>
                <strong>Nome do evento:</strong> {event_name}<br>
                <strong>Data:</strong> {formatted_date}
            </p>
            <p>
                Compartilhe o QR Code abaixo com seus convidados para que eles possam
                enviar fotos diretamente para a galeria do evento.
            </p>
            <p>
                <strong>Como usar:</strong><br>
                1. Os convidados devem escanear o QR Code<br>
                2. Na página aberta, eles podem tirar fotos diretamente ou escolher
                   da galeria do dispositivo<br>
                3. As fotos serão enviadas automaticamente para a galeria do evento
            </p>
        </body>
        </html>
        """
        
        # Anexar QR Code
        with app.open_resource(qr_path) as qr:
            msg.attach(
                filename="qrcode_evento.png",
                content_type="image/png",
                data=qr.read()
            )
        
        # Enviar email
        mail.send(msg)
        return True
    
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False
