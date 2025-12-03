/**
 * Ada - Chatbot de Acessibilidade Digital
 * Arquivo Principal (Refatorado)
 * 
 * Orquestra a inicialização e integração dos módulos:
 * - API: Comunicação com backend
 * - Storage: Persistência local
 * - Avatar: Gerenciamento do avatar Lottie
 * - Audio: TTS, STT e efeitos sonoros
 * - Accessibility: Temas, fontes, filtros
 * - UI: Modais, sidebar, toasts
 * - Chat: Lógica de mensagens
 */

import { sendMessage, checkAPIHealth as checkHealth } from './modules/api.js';
import { initAvatar, updateAvatar, AVATAR_STATES } from './modules/avatar.js';
import { initAudio, playSound, speak, stopSpeaking, toggleVoiceInput, isVoiceRecording, toggleTTS, getTTSEnabled } from './modules/audio.js';
import { initAccessibility, toggleTheme, changeFontSize, toggleDyslexiaFont, applyColorFilter, announceToScreenReader } from './modules/accessibility.js';
import { initUI, showToast, openModal, closeModal, toggleSidebar, updateCharCounter, autoResizeTextarea, resetTextarea } from './modules/ui.js';
import { initChat, addMessage, clearChat, showTypingIndicator, hideTypingIndicator, setTTSEnabled } from './modules/chat.js';

// =========================================
// Inicialização
// =========================================
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Inicializando Ada (Modular)...');

    // 1. Inicializa Áudio (com callbacks para UI)
    initAudio({
        onResult: (text) => {
            const input = document.getElementById('user-input');
            if (input) {
                const currentVal = input.value;
                input.value = currentVal ? `${currentVal} ${text}` : text;
                updateCharCounter();
                autoResizeTextarea(input);
                input.focus();
            }
        },
        onStart: () => {
            const micBtn = document.getElementById('mic-button');
            if (micBtn) {
                micBtn.classList.add('mic-active');
                micBtn.setAttribute('aria-label', 'Parar ditado');
            }
            showToast('Ouvindo...', 'info');
            updateAvatar(AVATAR_STATES.LISTENING);
        },
        onEnd: () => {
            const micBtn = document.getElementById('mic-button');
            if (micBtn) {
                micBtn.classList.remove('mic-active');
                micBtn.setAttribute('aria-label', 'Ativar ditado por voz');
            }
            updateAvatar(AVATAR_STATES.IDLE);
        },
        onError: (msg) => {
            showToast(msg, 'error');
            updateAvatar(AVATAR_STATES.CONFUSED);
        }
    });

    // 2. Inicializa Acessibilidade
    initAccessibility();

    // 3. Inicializa UI
    initUI();

    // 4. Inicializa Chat
    const chatContainer = document.getElementById('chat-container');
    const userInput = document.getElementById('user-input');

    initChat(chatContainer, userInput, {
        playSound: playSound,
        speak: speak
    });

    // Sincroniza configuração de TTS do Chat com Audio
    setTTSEnabled(getTTSEnabled());

    // 5. Inicializa Avatar
    // Procura container do avatar no header
    const avatarContainer = document.querySelector('.ada-header-avatar');
    // Se for imagem estática, substitui por div para Lottie (se necessário)
    // O módulo avatar.js lida com isso se passarmos o container correto
    // Mas o HTML atual tem uma <img>. O módulo avatar.js espera um container.
    // Vamos ajustar:
    if (avatarContainer && avatarContainer.tagName === 'IMG') {
        const parent = avatarContainer.parentElement;
        const newContainer = document.createElement('div');
        newContainer.className = 'ada-avatar-container';
        newContainer.style.width = '60px'; // Ajuste conforme CSS original
        newContainer.style.height = '60px';
        parent.replaceChild(newContainer, avatarContainer);
        initAvatar(newContainer);
    } else if (avatarContainer) {
        initAvatar(avatarContainer);
    }

    // 6. Configura Event Listeners Globais
    setupEventListeners();

    // 7. Verifica Backend
    try {
        const isHealthy = await checkHealth();
        if (isHealthy) {
            console.log('Backend online');
        } else {
            showToast('Servidor offline ou instável', 'warning');
            updateAvatar(AVATAR_STATES.SAD);
        }
    } catch (e) {
        console.error('Erro ao verificar health:', e);
    }

    // Expõe função global para os chips de sugestão (onclick="fillInput(...)")
    window.fillInput = (text) => {
        const input = document.getElementById('user-input');
        if (input) {
            input.value = text;
            input.focus();
            updateCharCounter();
            autoResizeTextarea(input);
        }
    };
});

// =========================================
// Event Listeners Globais
// =========================================
function setupEventListeners() {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    // Envio de Mensagem
    async function handleSubmit(e) {
        if (e) e.preventDefault();

        const message = userInput.value.trim();
        if (!message) return;

        // UI Updates
        userInput.value = '';
        resetTextarea(userInput);
        updateCharCounter();

        // Adiciona mensagem do usuário
        addMessage('user', message);
        updateAvatar(AVATAR_STATES.THINKING);
        showTypingIndicator();

        try {
            // Envia para API
            const response = await sendMessage(message);

            hideTypingIndicator();

            // Processa resposta
            if (response.erro) {
                addMessage('assistant', { erro: response.erro });
                updateAvatar(AVATAR_STATES.SAD);
                playSound('ERROR');
            } else {
                addMessage('assistant', response.resposta);
                updateAvatar(AVATAR_STATES.HAPPY);

                // Anuncia resposta para leitor de tela (resumo)
                announceToScreenReader('Resposta recebida da Ada');
            }

        } catch (error) {
            hideTypingIndicator();
            console.error('Erro no envio:', error);
            addMessage('assistant', { erro: 'Erro de conexão. Tente novamente.' });
            updateAvatar(AVATAR_STATES.ERROR);
            playSound('ERROR');
        }
    }

    if (chatForm) {
        chatForm.addEventListener('submit', handleSubmit);
    }

    if (userInput) {
        userInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit();
            }
        });

        userInput.addEventListener('input', () => {
            updateCharCounter();
            autoResizeTextarea(userInput);
        });
    }

    // Botões de Acessibilidade
    document.getElementById('font-increase')?.addEventListener('click', () => changeFontSize(1));
    document.getElementById('font-decrease')?.addEventListener('click', () => changeFontSize(-1));
    document.getElementById('theme-toggle')?.addEventListener('click', toggleTheme);

    // Botões de Áudio
    document.getElementById('mic-button')?.addEventListener('click', toggleVoiceInput);
    document.getElementById('tts-toggle')?.addEventListener('click', () => {
        toggleTTS();
        const enabled = getTTSEnabled();
        setTTSEnabled(enabled); // Sincroniza com Chat module
        showToast(enabled ? 'Leitura de respostas ativada' : 'Leitura desativada', 'info');
    });

    // Botão Limpar Chat
    document.getElementById('clear-chat-button')?.addEventListener('click', () => {
        openModal(
            'Limpar Histórico',
            '<p>Tem certeza que deseja limpar todo o histórico?</p>',
            {
                confirmText: 'Limpar',
                onConfirm: () => {
                    clearChat();
                    showToast('Histórico limpo', 'success');
                }
            }
        );
    });

    // Botão Configurações (Exemplo - poderia abrir um modal mais complexo)
    document.getElementById('settings-toggle')?.addEventListener('click', () => {
        openModal(
            'Configurações',
            `
            <div class="settings-modal">
                <h3>Acessibilidade</h3>
                <button class="modal-button" onclick="window.toggleDyslexia()">Alternar Fonte Dislexia</button>
                <div class="filter-options">
                    <p>Filtros de Cor:</p>
                    <button onclick="window.applyFilter('protanopia')">Protanopia</button>
                    <button onclick="window.applyFilter('deuteranopia')">Deuteranopia</button>
                    <button onclick="window.applyFilter('')">Nenhum</button>
                </div>
            </div>
            `,
            { hideConfirmButton: true, cancelText: 'Fechar' }
        );
    });

    // Helpers globais para o modal de settings (já que o HTML é string)
    window.toggleDyslexia = () => {
        // Lógica simplificada, idealmente gerenciada por estado
        const isEnabled = document.body.classList.contains('font-dyslexic');
        toggleDyslexiaFont(!isEnabled);
    };
    window.applyFilter = (filter) => applyColorFilter(filter);
}
