from flask_mail import Message
from app import mail, app

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
        
        # Conteúdo HTML do email
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #6b5b95;">Seu evento foi criado com sucesso!</h2>
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
            <p>
                Atenciosamente,<br>
                Lígia e Paulo
            </p>
        </body>
        </html>
        """
        
        # Anexar QR Code
        with open(qr_path, 'rb') as qr:
            msg.attach(
                filename="qrcode_evento.png",
                content_type="image/png",
                data=qr.read()
            )
        
        # Enviar email
        mail.send(msg)
        print(f"Email enviado com sucesso para {to}")
        return True
    
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False

def send_password_reset_email(to, reset_url):
    """
    Envia um email com o link para redefinir a senha
    
    Args:
        to: Email do destinatário
        reset_url: URL para redefinição de senha
    """
    try:
        # Criar mensagem
        msg = Message(
            subject="Redefinição de Senha",
            recipients=[to]
        )
        
        # Conteúdo HTML do email
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2 style="color: #6b5b95;">Redefinição de Senha</h2>
            <p>Foi solicitada a redefinição de senha para sua conta.</p>
            <p>Clique no link abaixo para redefinir sua senha:</p>
            <p>
                <a href="{reset_url}" style="display: inline-block; padding: 10px 20px; background-color: #6b5b95; color: white; text-decoration: none; border-radius: 5px;">
                    Redefinir Senha
                </a>
            </p>
            <p>Este link expira em 24 horas.</p>
            <p>Se você não solicitou a redefinição de senha, ignore este email.</p>
            <p>
                Atenciosamente,<br>
                Lígia e Paulo
            </p>
        </body>
        </html>
        """
        
        # Enviar email
        mail.send(msg)
        print(f"Email de redefinição de senha enviado para {to}")
        return True
    
    except Exception as e:
        print(f"Erro ao enviar email de redefinição: {str(e)}")
        return False
