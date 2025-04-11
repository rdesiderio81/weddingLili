document.addEventListener('DOMContentLoaded', function() {
    // Contagem regressiva para o casamento
    const countdownElement = document.getElementById('countdown');
    if (countdownElement) {
        const weddingDate = new Date(countdownElement.dataset.weddingDate);
        
        function updateCountdown() {
            const now = new Date();
            const diff = weddingDate - now;
            
            if (diff <= 0) {
                countdownElement.innerHTML = '<div class="countdown-item">O grande dia chegou!</div>';
                return;
            }
            
            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);
            
            countdownElement.innerHTML = `
                <div class="countdown-item">
                    <span class="countdown-value">${days}</span>
                    <span class="countdown-label">Dias</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-value">${hours}</span>
                    <span class="countdown-label">Horas</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-value">${minutes}</span>
                    <span class="countdown-label">Minutos</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-value">${seconds}</span>
                    <span class="countdown-label">Segundos</span>
                </div>
            `;
        }
        
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }
    
    // Detectar compatibilidade de dispositivo
    window.checkApiCompatibility = function() {
        // Verifica se o navegador suporta as APIs necessárias para a câmera
        const hasGetUserMedia = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
        
        // Verifica a plataforma/sistema operacional
        const userAgent = navigator.userAgent.toLowerCase();
        const isIOS = /iphone|ipad|ipod/.test(userAgent);
        const isAndroid = /android/.test(userAgent);
        
        // Verifica versões específicas de iOS (iOS 16+)
        let iOSVersion = 0;
        if (isIOS) {
            const match = userAgent.match(/os \d+_\d+/);
            if (match) {
                iOSVersion = parseInt(match[0].split(' ')[1]);
            }
        }
        
        // Verifica versões específicas de Android (Android 10+)
        let androidVersion = 0;
        if (isAndroid) {
            const match = userAgent.match(/android\s([0-9\.]+)/);
            if (match) {
                androidVersion = parseInt(match[1]);
            }
        }
        
        // Compatibilidade por plataforma
        let isCompatible = hasGetUserMedia;
        
        if (isIOS) {
            isCompatible = isCompatible && iOSVersion >= 16;
        } else if (isAndroid) {
            isCompatible = isCompatible && androidVersion >= 10;
        }
        
        return {
            compatible: isCompatible,
            platform: isIOS ? 'ios' : (isAndroid ? 'android' : 'other'),
            version: isIOS ? iOSVersion : (isAndroid ? androidVersion : 0)
        };
    };
});
