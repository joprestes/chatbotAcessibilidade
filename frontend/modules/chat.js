/**
 * Módulo Chat - Gerenciamento de Mensagens e Interface
 * 
 * Responsável por:
 * - Gerenciar lista de mensagens
 * - Renderizar interface do chat
 * - Processar Markdown e sanitização
 * - Gerenciar indicador de digitação
 * - Integrar com Storage e Avatar
 */

import {
    saveMessagesToStorage,
    loadMessagesFromStorage,
    clearMessagesFromStorage
} from './storage.js';

import {
    updateAvatar,
    AVATAR_STATES,
    getAvatarPath
} from './avatar.js';

// =========================================
// Constantes
// =========================================
const TYPING_MESSAGE_ID = 'typing-indicator-message';
const TYPING_SPEED = 30; // ms por caractere para efeito de digitação (opcional)

// Estado interno
let messages = [];
let chatContainer = null;
let userInput = null;
let searchFilter = '';
let isTTSEnabled = false; // Será atualizado via config
let playSoundFn = null;   // Função de som injetada
let speakFn = null;       // Função de TTS injetada

// =========================================
// Inicialização
// =========================================
/**
 * Inicializa o módulo de chat
 * @param {HTMLElement} container - Container das mensagens
 * @param {HTMLElement} input - Input do usuário
 * @param {Object} options - Opções e dependências (playSound, speak, etc.)
 */
export function initChat(container, input, options = {}) {
    if (!container || !input) {
        console.error('Container ou input do chat não fornecidos');
        return;
    }

    chatContainer = container;
    userInput = input;

    // Injeta dependências
    playSoundFn = options.playSound || (() => { });
    speakFn = options.speak || (() => { });

    // Carrega mensagens salvas
    messages = loadMessagesFromStorage();
    renderMessages();

    console.log('Chat inicializado com', messages.length, 'mensagens');
}

/**
 * Atualiza configuração de TTS
 * @param {boolean} enabled - Se TTS está habilitado
 */
export function setTTSEnabled(enabled) {
    isTTSEnabled = enabled;
}

/**
 * Define filtro de busca
 * @param {string} filter - Texto para filtrar
 */
export function setSearchFilter(filter) {
    searchFilter = filter ? filter.toLowerCase() : '';
    renderMessages();
}

// =========================================
// Gerenciamento de Mensagens
// =========================================
/**
 * Adiciona uma nova mensagem ao chat
 * @param {string} role - 'user' ou 'assistant'
 * @param {string|Object} content - Conteúdo da mensagem
 */
export function addMessage(role, content) {
    // Evita duplicar indicador de digitação
    if (content === TYPING_MESSAGE_ID) return;

    const message = {
        role,
        content,
        timestamp: Date.now()
    };

    messages.push(message);
    saveMessagesToStorage(messages);
    renderMessages();

    // Feedback de Acessibilidade e Áudio
    handleMessageFeedback(role, content);
}

/**
 * Remove a última mensagem de erro do assistente
 */
export function removeLastErrorMessage() {
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

    if (removed) {
        saveMessagesToStorage(messages);
        renderMessages();
    }
}

/**
 * Limpa todas as mensagens
 */
export function clearChat() {
    messages = [];
    clearMessagesFromStorage();
    renderMessages();

    if (userInput) {
        userInput.focus();
    }

    // Reseta avatar para IDLE
    updateAvatar(AVATAR_STATES.IDLE);
}

// =========================================
// Indicador de Digitação
// =========================================
/**
 * Mostra indicador de digitação
 */
export function showTypingIndicator() {
    // Verifica se já existe
    if (messages.some(msg => msg.content === TYPING_MESSAGE_ID)) return;

    const typingMessage = {
        role: 'assistant',
        content: TYPING_MESSAGE_ID,
        timestamp: Date.now()
    };

    messages.push(typingMessage);
    // Não salva indicador no storage
    renderMessages();
}

/**
 * Esconde indicador de digitação
 */
export function hideTypingIndicator() {
    const typingIndex = messages.findIndex(msg => msg.content === TYPING_MESSAGE_ID);
    if (typingIndex !== -1) {
        messages.splice(typingIndex, 1);
        // Não precisa salvar storage pois indicador não é salvo
        renderMessages();
    }
}

// =========================================
// Renderização
// =========================================
/**
 * Renderiza todas as mensagens no container
 */
export function renderMessages() {
    if (!chatContainer) return;

    // Filtra mensagens reais (sem indicador) para lógica de UI
    const realMessages = messages.filter(msg => msg.content !== TYPING_MESSAGE_ID);
    const hasMessages = realMessages.length > 0;

    // Gerencia visibilidade de elementos externos (Intro Card, Chips)
    updateExternalUI(hasMessages);

    // Limpa container (mantendo apenas mensagens novas)
    // Nota: Em uma implementação React/Vue isso seria virtual DOM
    // Aqui fazemos limpeza total por simplicidade, mas idealmente seria incremental
    chatContainer.innerHTML = '';

    // Filtra mensagens para busca
    let filteredMessages = messages;
    if (searchFilter) {
        filteredMessages = messages.filter(msg => {
            if (msg.content === TYPING_MESSAGE_ID) return false;
            const content = typeof msg.content === 'string'
                ? msg.content
                : (msg.content.erro || JSON.stringify(msg.content));
            return content.toLowerCase().includes(searchFilter);
        });
    }

    // Mensagem de "Nenhum resultado"
    if (filteredMessages.length === 0 && searchFilter) {
        renderNoResults();
        return;
    }

    // Renderiza mensagens
    filteredMessages.forEach((message, index) => {
        const messageElement = createMessageElement(message, index);
        chatContainer.appendChild(messageElement);
    });

    // Scroll para o final
    scrollToBottom();
}

/**
 * Cria elemento DOM para uma mensagem
 */
function createMessageElement(message, index) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role}`;
    messageDiv.setAttribute('data-testid', `chat-mensagem-${message.role}`);
    messageDiv.setAttribute('data-message-id', index);
    messageDiv.setAttribute('data-message-role', message.role);

    // Avatar
    const avatarDiv = createAvatarElement(message);
    messageDiv.appendChild(avatarDiv);

    // Conteúdo
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    if (message.content === TYPING_MESSAGE_ID) {
        contentDiv.innerHTML = createTypingIndicatorHTML();
        messageDiv.classList.add('typing');
    } else if (typeof message.content === 'object' && message.content.erro) {
        contentDiv.innerHTML = `<p class="error-message">${message.content.erro}</p>`;
        messageDiv.classList.add('error');
    } else {
        // Processa Markdown e Sanitiza
        const rawContent = typeof message.content === 'string' ? message.content : JSON.stringify(message.content);
        contentDiv.innerHTML = processContent(rawContent);
    }

    // Timestamp e Ações
    if (message.content !== TYPING_MESSAGE_ID) {
        const metaDiv = createMessageMeta(message);
        contentDiv.appendChild(metaDiv);
    }

    messageDiv.appendChild(contentDiv);
    return messageDiv;
}

/**
 * Cria elemento de avatar para a mensagem
 */
function createAvatarElement(message) {
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    avatarDiv.setAttribute('aria-hidden', 'true');

    const img = document.createElement('img');

    if (message.role === 'user') {
        img.src = '/assets/user-avatar.png';
        img.alt = 'Você';
        img.onerror = () => {
            avatarDiv.textContent = '👤';
            img.remove();
        };
    } else {
        // Lógica de avatar do assistente baseada no conteúdo/estado
        let state = AVATAR_STATES.HAPPY;

        if (message.content === TYPING_MESSAGE_ID) {
            state = AVATAR_STATES.THINKING;
        } else if (typeof message.content === 'object' && message.content.erro) {
            const errorMsg = message.content.erro.toLowerCase();
            if (errorMsg.includes('offline') || errorMsg.includes('conexão')) state = AVATAR_STATES.SAD;
            else if (errorMsg.includes('servidor') || errorMsg.includes('500')) state = AVATAR_STATES.ERROR;
            else if (errorMsg.includes('timeout')) state = AVATAR_STATES.BACK_SOON;
            else state = AVATAR_STATES.CONFUSED;
        }

        // Usa função importada de avatar.js (se disponível) ou path direto
        // Aqui assumimos que getAvatarPath foi importado ou implementado
        img.src = `/assets/ada-states/ada-${state}.png`; // Fallback simples
        if (typeof getAvatarPath === 'function') {
            img.src = getAvatarPath(state);
        }

        img.alt = 'Ada';
    }

    if (img.src) {
        img.style.width = '100%';
        img.style.height = '100%';
        img.style.objectFit = 'contain';
        avatarDiv.appendChild(img);
    }

    return avatarDiv;
}

// =========================================
// Processamento de Conteúdo (Markdown/Sanitize)
// =========================================
function processContent(text) {
    if (!text) return '';

    // 1. Markdown (usando marked se disponível)
    let html = text;
    if (typeof marked !== 'undefined') {
        try {
            html = marked.parse(text);
        } catch (e) {
            console.error('Erro no marked:', e);
        }
    }

    // 2. Sanitização (usando DOMPurify se disponível)
    if (typeof DOMPurify !== 'undefined') {
        html = DOMPurify.sanitize(html, {
            ADD_TAGS: ['code', 'pre', 'span'],
            ADD_ATTR: ['class', 'id']
        });
    }

    return html;
}

// =========================================
// Utilitários Internos
// =========================================
function handleMessageFeedback(role, content) {
    if (role === 'user') {
        playSoundFn('SENT');
    } else if (role === 'assistant') {
        playSoundFn('RECEIVED');

        if (isTTSEnabled) {
            if (typeof content === 'string') {
                const cleanText = cleanTextForTTS(content);
                speakFn(cleanText);
            } else if (content.erro) {
                speakFn(`Erro: ${content.erro}`);
                playSoundFn('ERROR');
            }
        }
    }
}

function cleanTextForTTS(text) {
    return text
        .replace(/#{1,6}\s/g, '')
        .replace(/\*\*/g, '')
        .replace(/\*/g, '')
        .replace(/```/g, '')
        .replace(/`/g, '')
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
}

function createTypingIndicatorHTML() {
    return `
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
}

function createMessageMeta(message) {
    const metaDiv = document.createElement('div');
    metaDiv.className = 'message-meta';

    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    metaDiv.appendChild(timeSpan);

    // Botões de ação (copiar, ouvir) podem ser adicionados aqui

    return metaDiv;
}

function updateExternalUI(hasMessages) {
    const introCard = document.getElementById('intro-card');
    const suggestionChipsEmpty = document.getElementById('suggestion-chips-empty');

    if (introCard) {
        if (hasMessages || searchFilter) introCard.classList.add('hidden');
        else introCard.classList.remove('hidden');
    }

    if (suggestionChipsEmpty) {
        if (hasMessages || searchFilter) suggestionChipsEmpty.classList.add('hidden');
        else suggestionChipsEmpty.classList.remove('hidden');
    }
}

function renderNoResults() {
    const noResults = document.createElement('div');
    noResults.className = 'no-results';
    noResults.textContent = `Nenhuma mensagem encontrada para "${searchFilter}"`;
    chatContainer.appendChild(noResults);
}

function scrollToBottom() {
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
