import qrcode
import os
from app import app

def generate_qr_code(event_id, unique_code, base_url):
    """
    Gera um QR Code para um evento
    
    Args:
        event_id: ID do evento
        unique_code: Código único do evento
        base_url: URL base da aplicação
    
    Returns:
        Caminho relativo para o QR Code gerado
    """
    # URL completa para o evento
    event_url = f"{base_url}evento/{unique_code}"
    
    # Configurar QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(event_url)
    qr.make(fit=True)
    
    # Gerar imagem
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Salvar imagem
    qr_filename = f"qrcode_event_{event_id}.png"
    relative_path = os.path.join('qrcodes', qr_filename)
    full_path = os.path.join(app.static_folder, relative_path)
    
    img.save(full_path)
    
    return relative_path
