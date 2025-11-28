/**
 * Aplicação JavaScript para o Chatbot de Acessibilidade Digital
 * Gerencia o estado do chat, comunicação com API e renderização
 */

// =========================================
// Configuração e Constantes
// =========================================
const API_BASE_URL = window.location.origin; // Usa a mesma origem
const API_CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;
const API_CONFIG_ENDPOINT = `${API_BASE_URL}/api/config`;
const STORAGE_KEY = 'chatbot_messages';

// Configurações do frontend (serão carregadas do backend)
let frontendConfig = {
    request_timeout_ms: 120000, // Valor padrão até carregar do backend
    error_announcement_duration_ms: 1000
};

// =========================================
// Estado da Aplicação
// =========================================
let messages = [];
let isLoading = false;
let currentAbortController = null; // Para cancelar requisições

// Timeout Ajustável (WCAG 2.2.6)
let timeoutWarningShown = false;
let timeoutExtensionCount = 0;
let warningTimerId = null;
const MAX_EXTENSIONS = 3;
const WARNING_BEFORE_TIMEOUT_MS = 20000; // Avisa 20s antes do timeout
let searchFilter = ''; // Filtro de busca no histórico
const TYPING_MESSAGE_ID = '__typing_indicator__'; // ID especial para mensagem de digitação
const MAX_QUESTION_LENGTH = 2000; // Máximo de caracteres (do backend)
let isCodeMode = false; // Estado do modo de código

// =========================================
// Sistema de Avatar Dinâmico
// =========================================
const AVATAR_STATES = {
    GREETING: 'ada-greeting',
    IDLE: 'ada-idle',
    SURPRISED: 'ada-surprised',
    THINKING: 'ada-thinking',
    EUREKA: 'ada-eureka',
    HAPPY: 'ada-happy',
    SLEEP: 'ada-sleep',
    CONFUSED: 'ada-confused',
    SAD: 'ada-sad',
    ERROR: 'ada-error',
    BACK_SOON: 'ada-back-soon'
};

let currentAvatarState = AVATAR_STATES.GREETING;
let lastActivityTime = Date.now();
let sleepTimeout = null;
let userTyping = false;
let foundAnswer = false; // Flag para detectar quando encontra resposta

/**
 * Retorna o caminho do avatar baseado no estado
 */
function getAvatarPath(state = null) {
    const avatarState = state || currentAvatarState;
    return `/assets/ada-states/${avatarState}.png`;
}

/**
 * Atualiza o avatar em todos os lugares (header, intro card, mensagens)
 */
function updateAvatar(state, animate = true) {
    if (state === currentAvatarState && !animate) return;

    const avatarPath = getAvatarPath(state);
    const previousState = currentAvatarState;
    currentAvatarState = state;

    // Atualiza avatar no header - REMOVIDO para manter logo estático
    // O header agora usa um logo fixo e não deve mudar com o estado do bot

    // Atualiza avatar no card de introdução
    const introAvatar = document.querySelector('.intro-card-avatar');
    if (introAvatar) {
        if (animate) {
            introAvatar.classList.add('avatar-transitioning');
            setTimeout(() => {
                introAvatar.src = avatarPath;
                introAvatar.addEventListener('load', () => {
                    introAvatar.classList.remove('avatar-transitioning');
                }, { once: true });
            }, 150);
        } else {
            introAvatar.src = avatarPath;
        }
    }

    // Atualiza avatares nas mensagens do assistente
    const messageAvatars = document.querySelectorAll('.message.assistant .message-avatar img');
    messageAvatars.forEach(avatar => {
        if (animate) {
            avatar.classList.add('avatar-transitioning');
            setTimeout(() => {
                avatar.src = avatarPath;
                avatar.addEventListener('load', () => {
                    avatar.classList.remove('avatar-transitioning');
                }, { once: true });
            }, 150);
        } else {
            avatar.src = avatarPath;
        }
    });
}

/**
 * Gerencia timeout de inatividade (5 minutos para SLEEP)
 */
function resetSleepTimeout() {
    lastActivityTime = Date.now();

    if (sleepTimeout) {
        clearTimeout(sleepTimeout);
    }

    // Após 5 minutos de inatividade, muda para SLEEP
    sleepTimeout = setTimeout(() => {
        if (Date.now() - lastActivityTime >= 300000 && !isLoading) { // 5 minutos
            updateAvatar(AVATAR_STATES.SLEEP, true);
        }
    }, 300000);
}

/**
 * Inicializa sistema de clique no avatar para acordar
 */
function setupAvatarClickHandler() {
    // Click handler removido pois o header agora é um logo estático
}

// =========================================
// Elementos DOM
// =========================================
const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const themeToggle = document.getElementById('theme-toggle');
const codeModeToggle = document.getElementById('code-mode-toggle');
const personaToggle = document.getElementById('persona-toggle');

// Elementos que serão criados dinamicamente
let cancelButton = null;
let charCounter = null;
let searchInput = null;
let searchToggle = null;
let searchWrapper = null;
let suggestionChipsEmpty = null;

// =========================================
// Carregamento de Configuração
// =========================================
async function loadFrontendConfig() {
    try {
        const response = await fetch(API_CONFIG_ENDPOINT);
        if (response.ok) {
            const config = await response.json();
            frontendConfig = { ...frontendConfig, ...config };
            console.log('Configuração do frontend carregada:', frontendConfig);
        }
    } catch (error) {
        console.warn('Não foi possível carregar configuração do backend, usando valores padrão:', error);
    }
}

// =========================================
// Tratamento de Reconexão
// =========================================
function setupReconnectionHandling() {
    // Listener para quando a conexão volta
    window.addEventListener('online', () => {
        console.log('Conexão restaurada');
        // Tenta verificar saúde da API
        checkAPIHealth().catch(() => {
            // Ignora erros silenciosamente
        });
    });

    // Listener para quando a conexão cai
    window.addEventListener('offline', () => {
        console.log('Conexão perdida');
    });
}

// =========================================
// Inicialização
// =========================================
document.addEventListener('DOMContentLoaded', async () => {
    await loadFrontendConfig();
    setupReconnectionHandling();
    initializeTheme();
    createUXElements();
    loadMessagesFromStorage();
    renderMessages();
    setupEventListeners();
    checkAPIHealth();

    // Inicializa sistema de avatar
    const realMessages = messages.filter(msg => msg.content !== TYPING_MESSAGE_ID);
    if (realMessages.length === 0) {
        updateAvatar(AVATAR_STATES.GREETING, false);
    } else {
        updateAvatar(AVATAR_STATES.IDLE, false);
    }
    setupAvatarClickHandler();
    resetSleepTimeout();
});

// =========================================
// Gerenciamento de Tema
// =========================================
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeToggle();
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeToggle();
}

function updateThemeToggle() {
    const theme = document.documentElement.getAttribute('data-theme');
    const themeIcon = document.getElementById('theme-icon');

    themeToggle.setAttribute('aria-label',
        theme === 'dark'
            ? 'Alternar para tema claro'
            : 'Alternar para tema escuro'
    );

    // Atualiza o ícone SVG (lua para sol e vice-versa)
    if (themeIcon) {
        const moonPath = themeIcon.querySelector('.theme-icon-moon');
        let sunGroup = themeIcon.querySelector('.theme-icon-sun');

        if (theme === 'dark') {
            // Modo escuro ativo - mostra ícone de sol (para alternar para claro)
            if (moonPath) moonPath.style.display = 'none';

            if (!sunGroup) {
                // Cria o ícone do sol se não existir
                sunGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
                sunGroup.setAttribute('class', 'theme-icon-sun');

                // Círculo do sol
                const sun = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
                sun.setAttribute('cx', '12');
                sun.setAttribute('cy', '12');
                sun.setAttribute('r', '5');
                sunGroup.appendChild(sun);

                // Raios do sol
                const rays = [
                    { x1: '12', y1: '1', x2: '12', y2: '3' },
                    { x1: '12', y1: '21', x2: '12', y2: '23' },
                    { x1: '4.22', y1: '4.22', x2: '5.64', y2: '5.64' },
                    { x1: '18.36', y1: '18.36', x2: '19.78', y2: '19.78' },
                    { x1: '1', y1: '12', x2: '3', y2: '12' },
                    { x1: '21', y1: '12', x2: '23', y2: '12' },
                    { x1: '4.22', y1: '19.78', x2: '5.64', y2: '18.36' },
                    { x1: '18.36', y1: '5.64', x2: '19.78', y2: '4.22' }
                ];

                rays.forEach(ray => {
                    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
                    line.setAttribute('x1', ray.x1);
                    line.setAttribute('y1', ray.y1);
                    line.setAttribute('x2', ray.x2);
                    line.setAttribute('y2', ray.y2);
                    sunGroup.appendChild(line);
                });

                themeIcon.appendChild(sunGroup);
            } else {
                sunGroup.style.display = '';
            }
        } else {
            // Modo claro ativo - mostra ícone de lua (para alternar para escuro)
            if (sunGroup) sunGroup.style.display = 'none';
            if (moonPath) moonPath.style.display = '';
        }
    }
}

// =========================================
// Criação de Elementos de UX
// =========================================
function createUXElements() {
    // Cria contador de caracteres
    if (!charCounter) {
        charCounter = document.createElement('div');
        charCounter.className = 'char-counter';
        charCounter.setAttribute('data-testid', 'char-counter');
        charCounter.setAttribute('aria-live', 'polite');
        charCounter.setAttribute('aria-label', 'Contador de caracteres');
        // Adiciona após o form
        if (chatForm && chatForm.parentElement) {
            chatForm.parentElement.appendChild(charCounter);
        }
    }

    // Busca botão cancelar (já existe no HTML)
    cancelButton = document.getElementById('cancel-button');
    if (cancelButton) {
        // Remove todos os event listeners anteriores (evita duplicação)
        const newCancelButton = cancelButton.cloneNode(true);
        cancelButton.parentNode.replaceChild(newCancelButton, cancelButton);
        cancelButton = newCancelButton;

        // Adiciona novo event listener
        cancelButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            cancelRequest(e);
        });

        // Também adiciona via onclick como fallback
        cancelButton.onclick = (e) => {
            e.preventDefault();
            e.stopPropagation();
            cancelRequest(e);
        };

        console.log('Botão cancelar configurado com múltiplos listeners');
    } else {
        console.warn('Botão cancelar não encontrado no DOM');
    }

    // Busca elementos de busca e sugestões
    searchToggle = document.getElementById('search-toggle');
    searchWrapper = document.getElementById('search-wrapper');
    searchInput = document.getElementById('search-input');
    suggestionChipsEmpty = document.getElementById('suggestion-chips-empty');

    // Configura busca
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchFilter = e.target.value.toLowerCase();
            renderMessages();
        });
    }

    if (searchToggle && searchWrapper) {
        searchToggle.addEventListener('click', () => {
            const isHidden = searchWrapper.classList.contains('hidden');
            if (isHidden) {
                searchWrapper.classList.remove('hidden');
                searchToggle.setAttribute('aria-expanded', 'true');
                searchInput?.focus();
            } else {
                searchWrapper.classList.add('hidden');
                searchToggle.setAttribute('aria-expanded', 'false');
                searchFilter = '';
                renderMessages();
                searchToggle.focus(); // Retorna foco ao botão ao fechar busca
            }
        });
    }

    // Atualiza contador inicial
    updateCharCounter();

    // Botão de Ajuda Contextual (WCAG 3.3.5)
    const helpButton = document.querySelector('.help-button');
    if (helpButton) {
        helpButton.addEventListener('click', () => {
            showToast(
                'Dicas de uso:\n' +
                '• Use o botão </> para ativar o Modo de Código\n' +
                '• Use o ícone de usuário para Analisar Cenários\n' +
                '• Pergunte sobre qualquer critério WCAG',
                'info',
                10000 // 10 segundos
            );
        });
    }
    if (codeModeToggle) {
        codeModeToggle.addEventListener('click', toggleCodeMode);
    }

    // Botão de Personas
    if (personaToggle) {
        personaToggle.addEventListener('click', openPersonaModal);
    }
}

function openPersonaModal() {
    const content = `
        <p class="modal-description" style="margin-bottom: 20px; color: var(--text-secondary);">
            Teste como seu conteúdo é percebido por diferentes tecnologias e necessidades. 
            Isso ajuda a identificar barreiras invisíveis para quem navega visualmente.
        </p>
        <div class="persona-grid">
            <button class="persona-btn" onclick="selectPersona('leitor-tela')">
                <span class="persona-icon">🔈</span>
                <span class="persona-name">Leitor de Tela</span>
                <span class="persona-desc">Cenário de uso sem visão</span>
            </button>
            <button class="persona-btn" onclick="selectPersona('zoom-contraste')">
                <span class="persona-icon">🔍</span>
                <span class="persona-name">Zoom e Contraste</span>
                <span class="persona-desc">Cenário de baixa visão</span>
            </button>
            <button class="persona-btn" onclick="selectPersona('teclado')">
                <span class="persona-icon">⌨️</span>
                <span class="persona-name">Navegação por Teclado</span>
                <span class="persona-desc">Cenário com limitações motoras</span>
            </button>
            <button class="persona-btn" onclick="selectPersona('linguagem-simples')">
                <span class="persona-icon">🧩</span>
                <span class="persona-name">Linguagem Simples</span>
                <span class="persona-desc">Cenário cognitivo/atenção</span>
            </button>
        </div>
    `;

    openModal('Escolha um Cenário de Acessibilidade', content, {
        hideConfirmButton: true,
        cancelText: 'Fechar'
    });
}

function selectPersona(persona) {
    const examples = {
        'leitor-tela': 'Estou tentando comprar um ingresso, mas o leitor de tela não anuncia o preço quando navego pela tabela de assentos.',
        'zoom-contraste': 'O texto cinza claro do rodapé fica ilegível quando aumento o zoom da página para 200%.',
        'teclado': 'Não consigo acessar o submenu "Configurações" usando apenas a tecla Tab; o foco pula direto para o próximo link.',
        'linguagem-simples': 'A mensagem de erro "Falha na validação do input X509" é muito técnica e não entendo o que preciso corrigir.'
    };

    const exampleText = examples[persona] || '';
    userInput.value = `/simular ${persona} ${exampleText}`;

    closeModal(false); // Não restaura foco para o botão, pois queremos focar no input

    // Aguarda um pouco para garantir que o modal não interfira no foco
    setTimeout(() => {
        userInput.focus();
        // Move cursor para o final
        userInput.selectionStart = userInput.selectionEnd = userInput.value.length;
    }, 150);

    showToast(`Cenário selecionado. Exemplo carregado.`, 'info');
}

// Expõe para o HTML
window.selectPersona = selectPersona;

function toggleCodeMode() {
    isCodeMode = !isCodeMode;
    const codeModeBtn = document.getElementById('code-mode-toggle');

    if (isCodeMode) {
        userInput.classList.add('code-mode-active');
        codeModeBtn.classList.add('active');
        codeModeBtn.setAttribute('aria-pressed', 'true');
        userInput.placeholder = "Cole seu código aqui para refatoração...";
        showToast('Modo de Código Ativado. Cole seu snippet.', 'info');
    } else {
        userInput.classList.remove('code-mode-active');
        codeModeBtn.classList.remove('active');
        codeModeBtn.setAttribute('aria-pressed', 'false');
        userInput.placeholder = "Pergunte sobre WCAG, ARIA ou testes...";
        showToast('Modo de Código Desativado.', 'info');
    }
    userInput.focus();
}

// Lógica de Expansão do Input
const expandBtn = document.getElementById('expand-input-toggle');
if (expandBtn) {
    expandBtn.addEventListener('click', () => {
        const isExpanded = userInput.classList.toggle('input-expanded');
        const iconExpand = document.getElementById('icon-expand');
        const iconCollapse = document.getElementById('icon-collapse');

        // Atualiza ARIA e Tooltip
        expandBtn.setAttribute('aria-expanded', isExpanded);
        expandBtn.setAttribute('data-tooltip', isExpanded ? 'Reduzir área de texto' : 'Aumentar área de digitação');

        // Alterna visibilidade dos ícones
        if (isExpanded) {
            iconExpand.style.display = 'none';
            iconCollapse.style.display = 'block';
        } else {
            iconExpand.style.display = 'block';
            iconCollapse.style.display = 'none';
        }

        userInput.focus();
    });
}

// =========================================
// Auto-resize Textarea
// =========================================
function autoResizeTextarea(textarea) {
    if (!textarea) return;

    // Reset height to auto para recalcular
    textarea.style.height = 'auto';

    // Calcula a altura necessária (scrollHeight inclui padding)
    const newHeight = Math.min(textarea.scrollHeight, 200); // Max 200px

    // Aplica a nova altura
    textarea.style.height = `${newHeight}px`;

    // Se atingiu o máximo, permite scroll
    if (textarea.scrollHeight > 200) {
        textarea.style.overflowY = 'auto';
    } else {
        textarea.style.overflowY = 'hidden';
    }
}

// =========================================
// Contador de Caracteres
// =========================================
function updateCharCounter() {
    if (!charCounter) return;

    const length = userInput.value.length;
    const remaining = MAX_QUESTION_LENGTH - length;
    const percentage = (length / MAX_QUESTION_LENGTH) * 100;

    // Formata com separador de milhar se necessário
    const formattedLength = length.toLocaleString('pt-BR');
    const formattedMax = MAX_QUESTION_LENGTH.toLocaleString('pt-BR');

    charCounter.textContent = `${formattedLength}/${formattedMax}`;
    charCounter.setAttribute('aria-label', `${length} de ${MAX_QUESTION_LENGTH} caracteres`);

    // Muda cor baseado na quantidade
    if (percentage >= 90) {
        charCounter.className = 'char-counter char-counter-warning';
    } else if (percentage >= 100) {
        charCounter.className = 'char-counter char-counter-error';
    } else {
        charCounter.className = 'char-counter';
    }
}

// =========================================
// Cancelamento de Requisição
// =========================================
function cancelRequest(e) {
    e?.preventDefault(); // Previne comportamento padrão se for evento
    e?.stopPropagation(); // Para propagação do evento

    console.log('Cancelar clicado, currentAbortController:', currentAbortController);

    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;

        hideTypingIndicator();
        isLoading = false;
        updateUIState();

        showToast('Requisição cancelada pelo usuário.', 'info');
        addMessage('assistant', {
            erro: '❌ Requisição cancelada pelo usuário.',
            errorType: 'cancelled'
        });
    } else {
        console.warn('Tentativa de cancelar, mas não há requisição ativa');
    }
}

// =========================================
// Timeout Ajustável (WCAG 2.2.6)
// =========================================
function showTimeoutWarning(controller, timeoutId) {
    timeoutWarningShown = true;

    const canExtend = timeoutExtensionCount < MAX_EXTENSIONS;
    const extensionsLeft = MAX_EXTENSIONS - timeoutExtensionCount;

    let message = '⏱️ A requisição está demorando mais que o esperado.';

    if (canExtend) {
        message += `\n\nDeseja estender o tempo de espera por mais 2 minutos?\n(${extensionsLeft} extensões restantes)`;

        if (confirm(message)) {
            extendTimeout(controller, timeoutId);
        }
    } else {
        message += '\n\nLimite de extensões atingido. A requisição será cancelada em breve.';
        showToast(message, 'warning', 10000);
    }
}

function extendTimeout(controller, oldTimeoutId) {
    timeoutExtensionCount++;
    timeoutWarningShown = false;

    // Cancela o timeout antigo
    clearTimeout(oldTimeoutId);
    if (warningTimerId) {
        clearTimeout(warningTimerId);
        warningTimerId = null;
    }

    // Cria novo timeout de 120 segundos (2 minutos)
    const newTimeoutMs = 120000;
    const newTimeoutId = setTimeout(() => controller.abort(), newTimeoutMs);

    // Cria novo timer de aviso
    const warningTime = Math.max(newTimeoutMs - WARNING_BEFORE_TIMEOUT_MS, 5000);
    warningTimerId = setTimeout(() => {
        if (isLoading && !timeoutWarningShown && currentAbortController === controller) {
            showTimeoutWarning(controller, newTimeoutId);
        }
    }, warningTime);

    showToast(
        `⏱️ Tempo estendido por mais 2 minutos (${timeoutExtensionCount}/${MAX_EXTENSIONS})`,
        'info',
        5000
    );
}

// =========================================
// Sistema de Modal Acessível (WCAG 2.4.3)
// =========================================
let modalElement = null;
let modalLastFocusedElement = null;
let modalFocusableElements = [];
let modalFirstFocusable = null;
let modalLastFocusable = null;

function openModal(title, content, options = {}) {
    modalElement = document.getElementById('accessible-modal');
    if (!modalElement) return;

    // Salva elemento que tinha foco antes do modal
    modalLastFocusedElement = document.activeElement;

    // Define título e conteúdo
    const modalTitle = modalElement.querySelector('#modal-title');
    const modalContent = modalElement.querySelector('#modal-content');

    if (modalTitle) modalTitle.textContent = title;
    if (modalContent) modalContent.innerHTML = content;

    // Configura botões do footer
    const cancelButton = modalElement.querySelector('[data-action="cancel"]');
    const confirmButton = modalElement.querySelector('[data-action="confirm"]');

    if (options.hideCancelButton) {
        cancelButton.style.display = 'none';
    } else {
        cancelButton.style.display = '';
        cancelButton.textContent = options.cancelText || 'Cancelar';
    }

    if (options.hideConfirmButton) {
        confirmButton.style.display = 'none';
    } else {
        confirmButton.style.display = '';
        confirmButton.textContent = options.confirmText || 'Confirmar';
    }

    // Callbacks
    if (options.onConfirm) {
        confirmButton.onclick = () => {
            options.onConfirm();
            closeModal();
        };
    }

    if (options.onCancel) {
        cancelButton.onclick = () => {
            options.onCancel();
            closeModal();
        };
    } else {
        cancelButton.onclick = closeModal;
    }

    // Mostra modal
    modalElement.removeAttribute('hidden');
    modalElement.setAttribute('aria-hidden', 'false');

    // Previne scroll do body
    document.body.style.overflow = 'hidden';

    // Configura focus trap
    setupModalFocusTrap();

    // Foca no primeiro elemento focável
    setTimeout(() => {
        if (modalFirstFocusable) {
            modalFirstFocusable.focus();
        }
    }, 100);
}

function closeModal(restoreFocus = true) {
    if (!modalElement) return;

    // Esconde modal
    modalElement.setAttribute('aria-hidden', 'true');

    // Captura elemento para uso no timeout
    const elementToHide = modalElement;

    // Aguarda animação antes de adicionar hidden
    setTimeout(() => {
        if (elementToHide) {
            elementToHide.setAttribute('hidden', '');
        }
    }, 300);

    // Restaura scroll do body
    document.body.style.overflow = '';

    // Retorna foco ao elemento anterior
    if (restoreFocus && modalLastFocusedElement) {
        modalLastFocusedElement.focus();
    }

    // Remove event listeners
    if (modalElement) {
        modalElement.removeEventListener('keydown', handleModalKeydown);
        modalElement.removeEventListener('click', handleModalClick);
    }

    // Limpa referências
    modalElement = null;
    modalLastFocusedElement = null;
    modalFocusableElements = [];
}

function handleModalClick(e) {
    if (e.target === modalElement) {
        closeModal();
    }
}

function setupModalFocusTrap() {
    if (!modalElement) return;

    // Encontra todos os elementos focáveis dentro do modal
    const focusableSelectors = 'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])';
    modalFocusableElements = Array.from(modalElement.querySelectorAll(focusableSelectors));

    if (modalFocusableElements.length === 0) return;

    modalFirstFocusable = modalFocusableElements[0];
    modalLastFocusable = modalFocusableElements[modalFocusableElements.length - 1];

    // Event listener para Tab (focus trap)
    modalElement.addEventListener('keydown', handleModalKeydown);

    // Event listener para fechar com X
    const closeButton = modalElement.querySelector('.modal-close');
    if (closeButton) {
        closeButton.onclick = closeModal;
    }

    // Event listener para fechar ao clicar no overlay
    modalElement.addEventListener('click', handleModalClick);
}

function handleModalKeydown(e) {
    // Escape fecha o modal
    if (e.key === 'Escape') {
        closeModal();
        return;
    }

    // Tab navigation (focus trap)
    if (e.key === 'Tab') {
        if (e.shiftKey) {
            // Shift + Tab
            if (document.activeElement === modalFirstFocusable) {
                e.preventDefault();
                modalLastFocusable.focus();
            }
        } else {
            // Tab
            if (document.activeElement === modalLastFocusable) {
                e.preventDefault();
                modalFirstFocusable.focus();
            }
        }
    }
}

// =========================================
// Event Listeners
// =========================================
function setupEventListeners() {
    window.setupStarted = true;
    console.log('Starting setupEventListeners');

    // Formulário de envio
    chatForm.addEventListener('submit', handleFormSubmit);

    // Enter no textarea (sem Shift = enviar, com Shift = nova linha)
    // Detecta quando usuário começa a digitar (SURPRISED)
    userInput.addEventListener('input', () => {
        if (userInput.value.length > 0 && !userTyping) {
            userTyping = true;
            if (currentAvatarState === AVATAR_STATES.IDLE || currentAvatarState === AVATAR_STATES.GREETING) {
                updateAvatar(AVATAR_STATES.SURPRISED, true);
            }
            resetSleepTimeout();
        } else if (userInput.value.length === 0 && userTyping) {
            userTyping = false;
            if (currentAvatarState === AVATAR_STATES.SURPRISED) {
                const realMessages = messages.filter(msg => msg.content !== TYPING_MESSAGE_ID);
                if (realMessages.length === 0) {
                    updateAvatar(AVATAR_STATES.GREETING, true);
                } else {
                    updateAvatar(AVATAR_STATES.IDLE, true);
                }
            }
        }
    });

    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isLoading && userInput.value.trim()) {
                handleFormSubmit(e);
            }
        }
    });

    // Auto-expansão do textarea
    userInput.addEventListener('input', () => {
        updateCharCounter();
        autoResizeTextarea(userInput);
    });

    // Toggle de tema
    themeToggle.addEventListener('click', toggleTheme);

    // Botão limpar chat (Event Delegation para robustez)
    document.addEventListener('click', (e) => {
        const clearBtn = e.target.closest('#clear-chat-button');
        if (clearBtn) {
            console.log('Clear chat button clicked (delegation)');
            openModal(
                'Limpar Histórico',
                '<p>Tem certeza que deseja limpar todo o histórico do chat? Esta ação não pode ser desfeita.</p>',
                {
                    confirmText: 'Limpar',
                    cancelText: 'Cancelar',
                    onConfirm: () => {
                        clearMessages();
                        showToast('Histórico limpo com sucesso.', 'success');
                    }
                }
            );
        }
    });

    // Fallback: atribuição direta ao onclick
    const clearChatBtnDirect = document.getElementById('clear-chat-button');
    if (clearChatBtnDirect) {
        console.log('Found clearChatBtnDirect, attaching onclick');
        clearChatBtnDirect.onclick = (e) => {
            e.preventDefault(); // Previne comportamento padrão se houver
            e.stopPropagation(); // Previne propagação para o document listener (evita duplo modal)
            console.log('Clear chat button clicked (direct)');
            openModal(
                'Limpar Histórico',
                '<p>Tem certeza que deseja limpar todo o histórico do chat? Esta ação não pode ser desfeita.</p>',
                {
                    confirmText: 'Limpar',
                    cancelText: 'Cancelar',
                    onConfirm: () => {
                        clearMessages();
                        showToast('Histórico limpo com sucesso.', 'success');
                    }
                }
            );
        };
    } else {
        console.error('clearChatBtnDirect NOT FOUND');
    }

    // Atalho Escape para cancelar requisição (WCAG 2.1.1)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isLoading) {
            cancelRequest();
        }
    });

    // Foco automático no input
    userInput.focus();

    window.setupDone = true;
    console.log('Finished setupEventListeners');
}

// =========================================
// Gerenciamento de Mensagens
// =========================================
function loadMessagesFromStorage() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            messages = JSON.parse(stored);
        }
    } catch (error) {
        console.error('Erro ao carregar mensagens do localStorage:', error);
        messages = [];
    }
}

function saveMessagesToStorage() {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
        console.error('Erro ao salvar mensagens no localStorage:', error);
    }
}

function addMessage(role, content) {
    messages.push({ role, content, timestamp: Date.now() });
    saveMessagesToStorage();
    renderMessages();
}

function clearMessages() {
    messages = [];
    saveMessagesToStorage();
    renderMessages();
    userInput.focus(); // Retorna foco ao input após limpar chat
}

function removeLastErrorMessage() {
    // Remove a última mensagem de erro do assistente, se existir
    let removed = false;
    for (let i = messages.length - 1; i >= 0; i--) {
        const message = messages[i];
        if (message.role === 'assistant' &&
            typeof message.content === 'object' &&
            message.content.erro) {
            messages.splice(i, 1);
            removed = true;
            break;
        }
    }
    // Só salva e re-renderiza se realmente removeu algo
    // O renderMessages() já preserva o indicador se isLoading for true
    if (removed) {
        saveMessagesToStorage();
        renderMessages();
    }
}

// =========================================
// Renderização
// =========================================
function renderMessages() {
    if (!chatContainer) return;

    // Remove mensagem de digitação da contagem para lógica de sugestões
    const realMessages = messages.filter(msg => msg.content !== TYPING_MESSAGE_ID);
    const hasMessages = realMessages.length > 0;

    // Gerencia visibilidade do card de introdução e sugestões
    const introCard = document.getElementById('intro-card');
    if (introCard) {
        if (hasMessages || searchFilter) {
            introCard.classList.add('hidden');
        } else {
            introCard.classList.remove('hidden');
        }
    }

    if (suggestionChipsEmpty) {
        if (hasMessages || searchFilter) {
            suggestionChipsEmpty.classList.add('hidden');
        } else {
            suggestionChipsEmpty.classList.remove('hidden');
        }
    }

    // Remove apenas mensagens existentes, mantém intro-card se existir
    const existingMessages = chatContainer.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());

    // Filtra mensagens se houver busca
    let filteredMessages = messages;
    if (searchFilter) {
        filteredMessages = messages.filter(msg => {
            if (msg.content === TYPING_MESSAGE_ID) return false; // Não mostra indicador na busca
            const content = typeof msg.content === 'string'
                ? msg.content
                : (msg.content.erro || JSON.stringify(msg.content));
            return content.toLowerCase().includes(searchFilter);
        });
    }

    if (filteredMessages.length === 0) {
        if (searchFilter) {
            const noResults = document.createElement('div');
            noResults.className = 'no-results';
            noResults.textContent = `Nenhuma mensagem encontrada para "${searchFilter}"`;
            chatContainer.appendChild(noResults);
        }
        return; // Deixa o ::before do CSS mostrar a mensagem padrão
    }

    filteredMessages.forEach((message, index) => {
        const messageElement = createMessageElement(message, index);
        chatContainer.appendChild(messageElement);
    });

    // Scroll para o final
    scrollToBottom();
}

function createMessageElement(message, index) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role}`;
    messageDiv.setAttribute('role', message.role === 'user' ? 'user' : 'assistant');
    messageDiv.setAttribute('data-testid', `chat-mensagem-${message.role}`);
    messageDiv.setAttribute('data-message-id', index);
    messageDiv.setAttribute('data-message-role', message.role);

    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.setAttribute('data-testid', `avatar-${message.role}`);
    avatar.setAttribute('aria-hidden', 'true');

    let avatarImg = null; // Declara fora do if para poder usar depois

    if (message.role === 'user') {
        // Tenta usar avatar personalizado, senão usa emoji
        const userAvatarImg = document.createElement('img');
        userAvatarImg.src = '/assets/user-avatar.png';
        userAvatarImg.alt = 'Você';
        userAvatarImg.style.width = '100%';
        userAvatarImg.style.height = '100%';
        userAvatarImg.style.objectFit = 'contain';
        userAvatarImg.onerror = () => {
            // Se avatar não existir, usa emoji como fallback
            avatar.textContent = '👤';
            userAvatarImg.remove();
        };
        avatar.appendChild(userAvatarImg);
    } else {
        // Usa avatar da Ada - escolhe baseado no estado da mensagem
        avatarImg = document.createElement('img');

        // Se é mensagem de digitação, usa THINKING
        if (message.content === TYPING_MESSAGE_ID) {
            avatarImg.src = getAvatarPath(AVATAR_STATES.THINKING);
        }
        // Se a mensagem contém erro, usa avatar de erro
        else if (typeof message.content === 'object' && message.content.erro) {
            const errorMsg = message.content.erro.toLowerCase();
            if (errorMsg.includes('offline') || errorMsg.includes('conexão')) {
                avatarImg.src = getAvatarPath(AVATAR_STATES.SAD);
            } else if (errorMsg.includes('servidor') || errorMsg.includes('500')) {
                avatarImg.src = getAvatarPath(AVATAR_STATES.ERROR);
            } else if (errorMsg.includes('timeout')) {
                avatarImg.src = getAvatarPath(AVATAR_STATES.BACK_SOON);
            } else {
                avatarImg.src = getAvatarPath(AVATAR_STATES.CONFUSED);
            }
        } else {
            // Mensagem de sucesso - usa HAPPY
            avatarImg.src = getAvatarPath(AVATAR_STATES.HAPPY);
        }

        avatarImg.alt = 'Ada';
        avatarImg.style.width = '100%';
        avatarImg.style.height = '100%';
        avatarImg.style.objectFit = 'contain';
        avatar.appendChild(avatarImg);
    }

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    bubble.setAttribute('data-testid', `message-bubble-${message.role}`);

    // Timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'message-timestamp';
    timestamp.setAttribute('data-testid', 'message-timestamp');
    const messageDate = message.timestamp ? new Date(message.timestamp) : new Date();
    timestamp.textContent = messageDate.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

    if (message.role === 'user') {
        bubble.textContent = message.content;
        bubble.appendChild(timestamp);
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(bubble);
    } else {
        // Verifica se é a mensagem de digitação
        if (message.content === TYPING_MESSAGE_ID) {
            // Avatar já está configurado como THINKING acima
            bubble.className += ' typing-indicator';
            bubble.setAttribute('data-testid', 'typing-indicator');
            bubble.setAttribute('aria-live', 'polite');
            bubble.setAttribute('aria-label', 'Bot está pesquisando resposta');

            // Texto informativo
            const textSpan = document.createElement('span');
            textSpan.className = 'typing-text';
            textSpan.textContent = 'Aguarde que estou pesquisando';
            bubble.appendChild(textSpan);

            // Dots animados
            const dots = document.createElement('div');
            dots.className = 'typing-dots';
            dots.setAttribute('aria-hidden', 'true');

            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('span');
                dot.className = 'typing-dot';
                dot.style.animationDelay = `${i * 0.2}s`;
                dots.appendChild(dot);
            }

            bubble.appendChild(dots);
            bubble.appendChild(timestamp);
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(bubble);
        } else if (typeof message.content === 'string') {
            bubble.innerHTML = formatMarkdown(message.content);
            bubble.appendChild(timestamp);
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(bubble);
        } else if (typeof message.content === 'object') {
            if (message.content.erro) {
                const errorType = message.content.errorType || 'generic';
                messageDiv.className += ` error error-${errorType}`;
                bubble.className += ` error error-${errorType}`;
                bubble.textContent = message.content.erro;
                bubble.appendChild(timestamp);
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(bubble);
            } else {
                // Renderiza as seções como expanders
                const sectionsDiv = document.createElement('div');
                sectionsDiv.className = 'response-sections';

                Object.entries(message.content).forEach(([title, content], idx) => {
                    const section = createExpanderSection(title, content, idx === 0);
                    sectionsDiv.appendChild(section);
                });

                bubble.appendChild(sectionsDiv);
                bubble.appendChild(timestamp);
                messageDiv.appendChild(avatar);
                messageDiv.appendChild(bubble);
            }
        }
    }

    return messageDiv;
}

function createExpanderSection(title, content, isExpanded = false) {
    const section = document.createElement('div');
    section.className = 'response-section';
    section.setAttribute('data-testid', 'expander-section');

    const uniqueId = `content-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    const header = document.createElement('button');
    header.className = 'expander-header';
    header.setAttribute('type', 'button');
    header.setAttribute('data-testid', 'expander-header');
    header.setAttribute('aria-expanded', isExpanded);
    header.setAttribute('aria-controls', uniqueId);

    const titleHeading = document.createElement('h3');
    titleHeading.className = 'expander-title';
    // Remove formatação markdown (asteriscos) do título
    const cleanTitle = title.replace(/\*\*/g, '').trim();
    titleHeading.textContent = cleanTitle;
    header.appendChild(titleHeading);

    const icon = document.createElement('span');
    icon.className = 'expander-icon';
    icon.setAttribute('aria-hidden', 'true');
    header.appendChild(icon);

    const contentDiv = document.createElement('div');
    contentDiv.className = 'expander-content';
    contentDiv.id = header.getAttribute('aria-controls');
    contentDiv.setAttribute('aria-hidden', !isExpanded);
    contentDiv.innerHTML = formatMarkdown(content);

    // Toggle ao clicar
    header.addEventListener('click', () => {
        const expanded = header.getAttribute('aria-expanded') === 'true';
        header.setAttribute('aria-expanded', !expanded);
        contentDiv.setAttribute('aria-hidden', expanded);
    });

    // Suporte a teclado
    header.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            header.click();
        }
    });

    section.appendChild(header);
    section.appendChild(contentDiv);

    return section;
}

function formatMarkdown(text) {
    if (!text) return '';

    let html = text;

    // Protege blocos de código para não processar markdown dentro deles
    const codeBlocks = [];
    html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
        const placeholder = `__CODE_BLOCK_${codeBlocks.length}__`;
        codeBlocks.push(`<pre><code>${escapeHtml(code.trim())}</code></pre>`);
        return placeholder;
    });

    // Headers (##, ###, ####)
    html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');

    // Tabelas Markdown
    html = html.replace(/(\|.+\|\n\|[-\s|:]+\|\n(?:\|.+\|\n?)+)/g, (match) => {
        const lines = match.trim().split('\n');
        if (lines.length < 2) return match;

        const header = lines[0];
        const separator = lines[1];
        const rows = lines.slice(2);

        // Processa header
        const headerCells = header.split('|').map(cell => cell.trim()).filter(cell => cell);
        const headerHtml = headerCells.map(cell => `<th>${cell}</th>`).join('');

        // Processa rows
        const rowsHtml = rows.map(row => {
            const cells = row.split('|').map(cell => cell.trim()).filter(cell => cell);
            return `<tr>${cells.map(cell => `<td>${cell}</td>`).join('')}</tr>`;
        }).join('');

        return `<table><thead><tr>${headerHtml}</tr></thead><tbody>${rowsHtml}</tbody></table>`;
    });

    // Processa listas (ordenadas e não ordenadas) com suporte a aninhamento
    html = processLists(html);

    // Links
    html = html.replace(
        /\[([^\]]+)\]\(([^)]+)\)/g,
        '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
    );

    // Negrito
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Itálico (apenas se não for negrito)
    html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');

    // Código inline (apenas se não for bloco)
    html = html.replace(/(?<!`)`([^`]+)`(?!`)/g, '<code>$1</code>');

    // Restaura blocos de código
    codeBlocks.forEach((block, index) => {
        html = html.replace(`__CODE_BLOCK_${index}__`, block);
    });

    // Parágrafos (quebras de linha duplas)
    const paragraphs = html.split('\n\n');
    html = paragraphs
        .map(para => {
            para = para.trim();
            if (!para) return '';
            // Se já é um elemento HTML (h1-h4, ul, ol, pre, table, li), não envolve em <p>
            if (/^<(h[1-4]|ul|ol|pre|table|li|tr|td|th)/.test(para)) {
                return para;
            }
            return `<p>${para}</p>`;
        })
        .join('\n');

    return html;
}

// Função auxiliar para processar listas com aninhamento
function processLists(text) {
    const lines = text.split('\n');
    const result = [];
    let inList = false;
    let listType = null; // 'ul' ou 'ol'
    let listStack = []; // Pilha para listas aninhadas

    for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmed = line.trim();

        // Detecta lista ordenada
        const orderedMatch = trimmed.match(/^(\d+)\.\s+(.+)$/);
        // Detecta lista não ordenada
        const unorderedMatch = trimmed.match(/^[-*]\s+(.+)$/);

        // Calcula nível de indentação (espaços ou tabs)
        const indent = line.match(/^(\s*)/)[1].length;
        const indentLevel = Math.floor(indent / 2); // Assume 2 espaços por nível

        if (orderedMatch || unorderedMatch) {
            const itemText = orderedMatch ? orderedMatch[2] : unorderedMatch[1];
            const currentType = orderedMatch ? 'ol' : 'ul';

            // Se mudou o tipo de lista ou nível, fecha listas anteriores
            if (inList && (listType !== currentType || indentLevel < listStack.length)) {
                // Fecha listas até o nível correto
                while (listStack.length > indentLevel) {
                    const lastList = listStack.pop();
                    result.push('</li>');
                    result.push(`</${lastList.type}>`);
                }
            }

            // Se precisa abrir nova lista
            if (!inList || listStack.length < indentLevel) {
                while (listStack.length < indentLevel) {
                    listStack.push({ type: currentType, indent: listStack.length });
                    result.push(`<${currentType}>`);
                }
            }

            result.push(`<li>${itemText}</li>`);
            inList = true;
            listType = currentType;
        } else {
            // Linha não é item de lista
            if (inList) {
                // Fecha todas as listas abertas
                while (listStack.length > 0) {
                    const lastList = listStack.pop();
                    result.push(`</${lastList.type}>`);
                }
                inList = false;
                listType = null;
            }
            result.push(line);
        }
    }

    // Fecha listas restantes
    if (inList) {
        while (listStack.length > 0) {
            const lastList = listStack.pop();
            result.push(`</${lastList.type}>`);
        }
    }

    return result.join('\n');
}

// Função auxiliar para escapar HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function scrollToBottom() {
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}

// =========================================
// Typing Indicator
// =========================================
function showTypingIndicator() {
    // Adiciona uma mensagem temporária do assistente com o indicador
    // Usa um ID especial para identificá-la depois
    const typingMessage = {
        role: 'assistant',
        content: TYPING_MESSAGE_ID, // Conteúdo especial que será renderizado como indicador
        timestamp: Date.now()
    };

    messages.push(typingMessage);
    saveMessagesToStorage();
    renderMessages();
}

function hideTypingIndicator() {
    // Remove a mensagem de digitação do array
    const typingIndex = messages.findIndex(msg => msg.content === TYPING_MESSAGE_ID);
    if (typingIndex !== -1) {
        messages.splice(typingIndex, 1);
        saveMessagesToStorage();
        renderMessages();
    }
}

// =========================================
// Error Type Detection
// =========================================
function getErrorType(error) {
    if (error.name === 'AbortError' || error.message === 'AbortError') {
        return 'timeout';
    } else if (error.message === 'OFFLINE') {
        return 'offline';
    } else if (error.message === 'RATE_LIMIT') {
        return 'rate-limit';
    } else if (error.message === 'SERVER_ERROR') {
        return 'server-error';
    } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        return 'network-error';
    } else {
        return 'generic';
    }
}

// =========================================
// Comunicação com API
// =========================================
async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) {
            console.warn('API não está respondendo corretamente');
        }
    } catch (error) {
        console.error('Erro ao verificar saúde da API:', error);
    }
}

async function sendMessage(pergunta) {
    if (isLoading) return;

    isLoading = true;
    userTyping = false;
    foundAnswer = false;

    // Garante que o botão de cancelar apareça
    if (!cancelButton) {
        cancelButton = document.getElementById('cancel-button');
    }

    updateUIState();

    // Adiciona mensagem do usuário
    addMessage('user', pergunta);

    // Limpa o input
    userInput.value = '';

    // Muda para THINKING quando começa a processar
    updateAvatar(AVATAR_STATES.THINKING, true);

    // Adiciona indicador de digitação (typing indicator)
    showTypingIndicator();

    resetSleepTimeout();
    // Skeleton loading removido - usando apenas typing indicator

    // AbortController para timeout e cancelamento
    currentAbortController = new AbortController();
    const controller = currentAbortController;

    // Timeout configurável (WCAG 2.2.6)
    const timeoutMs = frontendConfig.request_timeout_ms || 120000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    // Reseta variáveis de aviso de timeout
    timeoutWarningShown = false;
    timeoutExtensionCount = 0; // Reseta contador para nova requisição

    // Inicia timer de aviso (20s antes do timeout)
    const warningTime = Math.max(timeoutMs - WARNING_BEFORE_TIMEOUT_MS, 5000);
    if (warningTimerId) clearTimeout(warningTimerId);

    warningTimerId = setTimeout(() => {
        if (isLoading && !timeoutWarningShown && currentAbortController === controller) {
            showTimeoutWarning(controller, timeoutId);
        }
    }, warningTime);

    try {
        // Verifica se está offline
        if (!navigator.onLine) {
            throw new Error('OFFLINE');
        }

        const response = await fetch(API_CHAT_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pergunta }),
            signal: controller.signal,
        });

        clearTimeout(timeoutId);
        if (warningTimerId) {
            clearTimeout(warningTimerId);
            warningTimerId = null;
        }

        // NÃO remove mensagens de erro aqui - só quando a resposta chegar
        // Isso evita que o indicador desapareça prematuramente

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
            const errorMessage = errorData.detail || `Erro ${response.status}`;

            // Mensagens específicas por status
            if (response.status === 429) {
                throw new Error('RATE_LIMIT');
            } else if (response.status >= 500) {
                throw new Error('SERVER_ERROR');
            } else {
                throw new Error(errorMessage);
            }
        }

        const data = await response.json();

        // Verifica se a resposta contém indicação de busca (EUREKA)
        const respostaStr = JSON.stringify(data.resposta).toLowerCase();
        if (respostaStr.includes('google') || respostaStr.includes('busca') || respostaStr.includes('pesquisa')) {
            foundAnswer = true;
            updateAvatar(AVATAR_STATES.EUREKA, true);
            // Após 1 segundo, muda para HAPPY
            setTimeout(() => {
                if (foundAnswer) {
                    updateAvatar(AVATAR_STATES.HAPPY, true);
                }
            }, 1000);
        } else {
            // Resposta direta, vai direto para HAPPY
            updateAvatar(AVATAR_STATES.HAPPY, true);
        }

        // Remove indicador de digitação
        hideTypingIndicator();

        // Remove qualquer mensagem de erro anterior do assistente
        removeLastErrorMessage();

        // Adiciona resposta do assistente (aparecerá abaixo do indicador que foi removido)
        addMessage('assistant', data.resposta);

        // Retorna foco ao input após resposta (WCAG 2.4.3)
        // Melhora navegação por teclado permitindo que usuário continue digitando
        setTimeout(() => {
            if (userInput && !isLoading) {
                userInput.focus();
            }
        }, 100);

        // Após resposta, volta para IDLE após 2 segundos
        setTimeout(() => {
            if (!isLoading && currentAvatarState === AVATAR_STATES.HAPPY) {
                updateAvatar(AVATAR_STATES.IDLE, true);
            }
            resetSleepTimeout();
        }, 2000);

    } catch (error) {
        clearTimeout(timeoutId);
        if (warningTimerId) {
            clearTimeout(warningTimerId);
            warningTimerId = null;
        }

        // Se foi cancelado manualmente pelo usuário, não mostra erro
        // (o cancelRequest já tratou isso)
        if (error.name === 'AbortError' && controller.signal.aborted && !currentAbortController) {
            // Foi cancelado manualmente - já foi tratado em cancelRequest()
            console.log('Requisição cancelada manualmente pelo usuário');
            return; // Não faz nada, o cancelRequest já tratou
        }

        // Remove indicador de digitação
        hideTypingIndicator();

        // Mensagens de erro específicas e estados do avatar
        let errorMessage = '';
        let avatarState = AVATAR_STATES.ERROR;

        if (error.name === 'AbortError' || error.message === 'AbortError') {
            errorMessage = '⏱️ A requisição demorou muito para responder (timeout). Por favor, tente novamente.';
            avatarState = AVATAR_STATES.BACK_SOON; // WORRIED (usando back-soon como equivalente)
        } else if (error.message === 'OFFLINE') {
            errorMessage = '📡 Você está offline. Verifique sua conexão com a internet e tente novamente.';
            avatarState = AVATAR_STATES.SAD;
        } else if (error.message === 'RATE_LIMIT') {
            errorMessage = '🚦 Muitas requisições no momento. Por favor, aguarde um minuto e tente novamente.';
            avatarState = AVATAR_STATES.CONFUSED;
        } else if (error.message === 'SERVER_ERROR') {
            errorMessage = '🔧 Erro no servidor. Nossa equipe foi notificada. Por favor, tente novamente em alguns instantes.';
            avatarState = AVATAR_STATES.ERROR;
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = '🌐 Erro de conexão. Verifique sua internet e tente novamente.';
            avatarState = AVATAR_STATES.BACK_SOON; // WORRIED
        } else if (error.message.includes('validação') || error.message.includes('422')) {
            errorMessage = `❌ ${error.message}`;
            avatarState = AVATAR_STATES.SAD; // Validação falhou
        } else {
            errorMessage = `❌ Erro ao processar sua pergunta: ${error.message}. Por favor, tente novamente.`;
            avatarState = AVATAR_STATES.CONFUSED; // Pergunta ambígua ou erro genérico
        }

        // Atualiza avatar para estado de erro
        updateAvatar(avatarState, true);

        // Adiciona mensagem de erro com tipo específico
        addMessage('assistant', {
            erro: errorMessage,
            errorType: getErrorType(error)
        });

        // Após erro, volta para IDLE após 3 segundos
        setTimeout(() => {
            if (!isLoading && (currentAvatarState === avatarState)) {
                updateAvatar(AVATAR_STATES.IDLE, true);
            }
            resetSleepTimeout();
        }, 3000);

        // Mostra toast notification
        showToast(errorMessage, 'error');

        console.error('Erro ao enviar mensagem:', error);
    } finally {
        // Limpa o controller
        if (currentAbortController === controller) {
            currentAbortController = null;
        }

        // Garante que o indicador seja removido quando terminar (sucesso ou erro)
        hideTypingIndicator();

        // SEMPRE reseta isLoading, mesmo se houver erro
        isLoading = false;
        updateUIState();

        // Log para debug
        console.log('sendMessage finalizado, isLoading:', isLoading);
    }
}

// =========================================
// UI State Management
// =========================================
function updateUIState() {
    // Proteção: se isLoading estiver undefined ou null, reseta para false
    if (isLoading === undefined || isLoading === null) {
        console.warn('isLoading estava undefined/null, resetando para false');
        isLoading = false;
    }

    userInput.disabled = isLoading;
    sendButton.disabled = isLoading;

    if (isLoading) {
        sendButton.style.opacity = '0.6';
        sendButton.setAttribute('aria-label', 'Enviando mensagem...');

        // Garante que o botão de cancelar apareça
        if (!cancelButton) {
            cancelButton = document.getElementById('cancel-button');
        }
        if (cancelButton) {
            cancelButton.classList.remove('hidden');
            cancelButton.style.display = 'flex'; // Força exibição
        } else {
            console.warn('Botão cancelar não encontrado no DOM');
        }
    } else {
        sendButton.style.opacity = '1';
        sendButton.setAttribute('aria-label', 'Enviar mensagem');
        if (cancelButton) {
            cancelButton.classList.add('hidden');
        }
        // Auto-resize textarea ao desabilitar
        if (userInput.tagName === 'TEXTAREA') {
            autoResizeTextarea(userInput);
        }
        userInput.focus();
    }
}

/**
 * Função de emergência para resetar estado travado
 */
function resetStuckState() {
    console.warn('Resetando estado travado...');
    isLoading = false;
    currentAbortController = null;
    hideTypingIndicator();
    updateUIState();
    updateAvatar(AVATAR_STATES.IDLE, false);
}

// Expõe função globalmente para debug (pode ser chamada no console)
window.resetAdaState = resetStuckState;

// Expõe funções de modal globalmente para uso e testes
window.openModal = openModal;
window.openModal = openModal;
window.closeModal = closeModal;

/**
 * Mostra uma notificação toast
 * @param {string} message - Mensagem a ser exibida
 * @param {string} type - Tipo de notificação: 'info', 'success', 'warning', 'error'
 * @param {number} duration - Duração em ms (padrão: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.setAttribute('role', 'alert');

    // Ícone baseado no tipo
    let icon = '';
    switch (type) {
        case 'success': icon = '✅'; break;
        case 'error': icon = '❌'; break;
        case 'warning': icon = '⚠️'; break;
        default: icon = 'ℹ️';
    }

    toast.innerHTML = `
        <span class="toast-icon" aria-hidden="true">${icon}</span>
        <span class="toast-message">${message}</span>
    `;

    toastContainer.appendChild(toast);

    // Animação de entrada
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Remove após duração
    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => {
            toast.remove();
        });
    }, duration);
}

// Expõe globalmente
window.showToast = showToast;

// =========================================
// Handlers
// =========================================
async function handleFormSubmit(e) {
    e.preventDefault();

    const pergunta = userInput.value.trim();

    // Se estiver em modo código, adiciona o comando
    const finalMessage = isCodeMode ? `/refatorar ${pergunta}` : pergunta;

    // Debug: verifica estado
    console.log('handleFormSubmit chamado:', { pergunta: finalMessage.substring(0, 20), isLoading, isCodeMode });

    if (!pergunta) {
        console.log('Pergunta vazia, ignorando');
        return;
    }

    if (isLoading) {
        console.warn('Já está carregando, ignorando nova requisição');
        return;
    }

    try {
        await sendMessage(finalMessage);
    } catch (error) {
        console.error('Erro em handleFormSubmit:', error);
        // Garante que isLoading seja resetado mesmo em caso de erro não tratado
        isLoading = false;
        updateUIState();
    }
}

// Test write
