// Função para inicializar o controle da câmera
function initCamera(options) {
    // Elementos DOM
    const cameraContainer = document.getElementById('camera-container');
    const cameraVideo = document.getElementById('camera-video');
    const cameraCanvas = document.getElementById('camera-canvas');
    const cameraPhoto = document.getElementById('camera-photo');
    const captureBtn = document.getElementById('capture-btn');
    const retakeBtn = document.getElementById('retake-btn');
    const uploadBtn = document.getElementById('upload-btn');
    const closeCamera = document.getElementById('close-camera');
    const btnCamera = document.getElementById('btn-camera');
    const uploadFeedback = document.getElementById('upload-feedback');
    const closeFeedback = document.getElementById('close-feedback');
    
    // Verificar compatibilidade
    const compatibility = options.apiCompatible || { compatible: true };
    
    // Controle de stream e status
    let mediaStream = null;
    
    // Verifica se o dispositivo é compatível
    if (!compatibility.compatible) {
        btnCamera.addEventListener('click', function() {
            alert('Seu dispositivo não é compatível com a captura de fotos pelo navegador. Por favor, use um dispositivo com iOS 16+ ou Android 10+.');
        });
        return;
    }
    
    // Inicializar botão de câmera
    btnCamera.addEventListener('click', openCamera);
    
    // Abrir câmera
    function openCamera() {
        // Configurações da câmera - preferência para câmera traseira
        const constraints = {
            video: { 
                facingMode: { ideal: 'environment' },
                width: { ideal: 1280 },
                height: { ideal: 720 }
            }
        };
        
        // Tentar acessar a câmera
        navigator.mediaDevices.getUserMedia(constraints)
            .then(function(stream) {
                mediaStream = stream;
                cameraVideo.srcObject = stream;
                cameraVideo.style.display = 'block';
                cameraPhoto.style.display = 'none';
                
                // Mostrar container da câmera
                cameraContainer.style.display = 'flex';
                
                // Configurar botões
                captureBtn.style.display = 'inline-block';
                retakeBtn.style.display = 'none';
                uploadBtn.style.display = 'none';
            })
            .catch(function(err) {
                console.error('Erro ao acessar a câmera: ', err);
                alert('Não foi possível acessar a câmera. Verifique as permissões do navegador.');
            });
    }
    
    // Capturar foto
    captureBtn.addEventListener('click', function() {
        if (!mediaStream) return;
        
        // Configurar canvas para capturar o frame
        cameraCanvas.width = cameraVideo.videoWidth;
        cameraCanvas.height = cameraVideo.videoHeight;
        
        // Desenhar o frame atual no canvas
        const context = cameraCanvas.getContext('2d');
        context.drawImage(cameraVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);
        
        // Converter para imagem
        const photoUrl = cameraCanvas.toDataURL('image/jpeg', 0.9);
        cameraPhoto.src = photoUrl;
        
        // Mostrar a foto capturada
        cameraVideo.style.display = 'none';
        cameraPhoto.style.display = 'block';
        
        // Alterar visibilidade dos botões
        captureBtn.style.display = 'none';
        retakeBtn.style.display = 'inline-block';
        uploadBtn.style.display = 'inline-block';
    });
    
    // Tirar nova foto
    retakeBtn.addEventListener('click', function() {
        // Voltar para o modo de câmera
        cameraVideo.style.display = 'block';
        cameraPhoto.style.display = 'none';
        
        // Restaurar botões
        captureBtn.style.display = 'inline-block';
        retakeBtn.style.display = 'none';
        uploadBtn.style.display = 'none';
    });
    
    // Enviar foto
    uploadBtn.addEventListener('click', function() {
        const photoData = cameraPhoto.src;
        
        // Preparar dados para envio
        const formData = new FormData();
        formData.append('photo_data', photoData);
        
        // Enviar para o servidor
        fetch(options.uploadUrl, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Fechar câmera
                closeStream();
                cameraContainer.style.display = 'none';
                
                // Mostrar feedback de sucesso
                uploadFeedback.style.display = 'flex';
            } else {
                alert('Erro ao enviar a foto: ' + (data.message || 'Erro desconhecido'));
            }
        })
        .catch(error => {
            console.error('Erro:', error);
            alert('Ocorreu um erro ao enviar a foto.');
        });
    });
    
    // Fechar câmera
    closeCamera.addEventListener('click', function() {
        closeStream();
        cameraContainer.style.display = 'none';
    });
    
    // Fechar feedback
    if (closeFeedback) {
        closeFeedback.addEventListener('click', function() {
            uploadFeedback.style.display = 'none';
        });
    }
    
    // Função para fechar o stream da câmera
    function closeStream() {
        if (mediaStream) {
            mediaStream.getTracks().forEach(track => track.stop());
            mediaStream = null;
        }
    }
    
    // Garantir que o stream seja fechado ao sair da página
    window.addEventListener('beforeunload', closeStream);
}
