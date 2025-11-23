/**
 * Aplicação JavaScript para o Chatbot de Acessibilidade Digital
 * Gerencia o estado do chat, comunicação com API e renderização
 */

// =========================================
// Configuração e Constantes
// =========================================
const API_BASE_URL = window.location.origin; // Usa a mesma origem
const API_CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;
const STORAGE_KEY = 'chatbot_messages';

// =========================================
// Estado da Aplicação
// =========================================
let messages = [];
let isLoading = false;
const TYPING_MESSAGE_ID = '__typing_indicator__'; // ID especial para mensagem de digitação

// =========================================
// Elementos DOM
// =========================================
const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const themeToggle = document.getElementById('theme-toggle');

// =========================================
// Inicialização
// =========================================
document.addEventListener('DOMContentLoaded', () => {
    initializeTheme();
    loadMessagesFromStorage();
    renderMessages();
    setupEventListeners();
    checkAPIHealth();
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
    themeToggle.setAttribute('aria-label', 
        theme === 'dark' 
            ? 'Alternar para tema claro' 
            : 'Alternar para tema escuro'
    );
}

// =========================================
// Event Listeners
// =========================================
function setupEventListeners() {
    // Formulário de envio
    chatForm.addEventListener('submit', handleFormSubmit);
    
    // Enter no input (sem Shift = enviar, com Shift = nova linha)
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!isLoading && userInput.value.trim()) {
                handleFormSubmit(e);
            }
        }
    });
    
    // Toggle de tema
    themeToggle.addEventListener('click', toggleTheme);
    
    // Botão limpar chat
    const clearChatButton = document.getElementById('clear-chat-button');
    if (clearChatButton) {
        clearChatButton.addEventListener('click', () => {
            if (confirm('Tem certeza que deseja limpar todo o histórico do chat?')) {
                clearMessages();
            }
        });
    }
    
    // Foco automático no input
    userInput.focus();
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
    
    chatContainer.innerHTML = '';
    
    if (messages.length === 0) {
        return; // Deixa o ::before do CSS mostrar a mensagem padrão
    }
    
    messages.forEach((message, index) => {
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
    messageDiv.setAttribute('data-testid', `chat-mensagem`);
    messageDiv.setAttribute('data-message-id', index);
    messageDiv.setAttribute('data-message-role', message.role);
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (message.role === 'user') {
        bubble.textContent = message.content;
    } else {
        // Verifica se é a mensagem de digitação
        if (message.content === TYPING_MESSAGE_ID) {
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
        } else if (typeof message.content === 'string') {
            bubble.innerHTML = formatMarkdown(message.content);
        } else if (typeof message.content === 'object') {
            if (message.content.erro) {
                const errorType = message.content.errorType || 'generic';
                messageDiv.className += ` error error-${errorType}`;
                bubble.className += ` error error-${errorType}`;
                bubble.textContent = message.content.erro;
            } else {
                // Renderiza as seções como expanders
                const sectionsDiv = document.createElement('div');
                sectionsDiv.className = 'response-sections';
                
                Object.entries(message.content).forEach(([title, content], idx) => {
                    const section = createExpanderSection(title, content, idx === 0);
                    sectionsDiv.appendChild(section);
                });
                
                bubble.appendChild(sectionsDiv);
            }
        }
    }
    
    messageDiv.appendChild(bubble);
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
    
    const titleSpan = document.createElement('span');
    // Remove formatação markdown (asteriscos) do título
    const cleanTitle = title.replace(/\*\*/g, '').trim();
    titleSpan.textContent = cleanTitle;
    titleSpan.style.flex = '1';
    header.appendChild(titleSpan);
    
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
    
    // Headers (##, ###, ####)
    html = html.replace(/^####\s+(.+)$/gm, '<h4>$1</h4>');
    html = html.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>');
    html = html.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>');
    
    // Código em bloco (```)
    html = html.replace(/```([\s\S]*?)```/g, (match, code) => {
        return `<pre><code>${code.trim()}</code></pre>`;
    });
    
    // Listas ordenadas (1. item)
    html = html.replace(/^(\d+\.\s+.+)$/gm, '<li>$1</li>');
    html = html.replace(/(<li>\d+\.\s+)(.+)(<\/li>)/g, '<li>$2</li>');
    // Agrupa listas ordenadas consecutivas
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
        if (match.includes('<li>')) {
            return `<ol>${match}</ol>`;
        }
        return match;
    });
    
    // Listas não ordenadas (- ou *)
    html = html.replace(/^[-*]\s+(.+)$/gm, '<li>$1</li>');
    // Agrupa listas não ordenadas consecutivas
    html = html.replace(/(<li>.*<\/li>\n?)+/g, (match) => {
        if (match.includes('<li>') && !match.includes('<ol>')) {
            return `<ul>${match}</ul>`;
        }
        return match;
    });
    
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
    
    // Parágrafos (quebras de linha duplas)
    const paragraphs = html.split('\n\n');
    html = paragraphs
        .map(para => {
            para = para.trim();
            if (!para) return '';
            // Se já é um elemento HTML (h1-h4, ul, ol, pre), não envolve em <p>
            if (/^<(h[1-4]|ul|ol|pre|li)/.test(para)) {
                return para;
            }
            return `<p>${para}</p>`;
        })
        .join('\n');
    
    return html;
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
    updateUIState();
    
    // Adiciona mensagem do usuário
    addMessage('user', pergunta);
    
    // Limpa o input
    userInput.value = '';
    
    // Adiciona indicador de digitação (typing indicator)
    showTypingIndicator();
    
    // AbortController para timeout
    const controller = new AbortController();
    // Timeout de 120 segundos (usando constante do backend)
    const FRONTEND_REQUEST_TIMEOUT_MS = 120000;
    const timeoutId = setTimeout(() => controller.abort(), FRONTEND_REQUEST_TIMEOUT_MS);
    
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
        
        // Remove indicador de digitação
        hideTypingIndicator();
        
        // Remove qualquer mensagem de erro anterior do assistente
        removeLastErrorMessage();
        
        // Adiciona resposta do assistente (aparecerá abaixo do indicador que foi removido)
        addMessage('assistant', data.resposta);
        
    } catch (error) {
        clearTimeout(timeoutId);
        
        // Remove indicador de digitação
        hideTypingIndicator();
        
        // Mensagens de erro específicas
        let errorMessage = '';
        if (error.name === 'AbortError' || error.message === 'AbortError') {
            errorMessage = '⏱️ A requisição demorou muito para responder (timeout). Por favor, tente novamente.';
        } else if (error.message === 'OFFLINE') {
            errorMessage = '📡 Você está offline. Verifique sua conexão com a internet e tente novamente.';
        } else if (error.message === 'RATE_LIMIT') {
            errorMessage = '🚦 Muitas requisições no momento. Por favor, aguarde um minuto e tente novamente.';
        } else if (error.message === 'SERVER_ERROR') {
            errorMessage = '🔧 Erro no servidor. Nossa equipe foi notificada. Por favor, tente novamente em alguns instantes.';
        } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
            errorMessage = '🌐 Erro de conexão. Verifique sua internet e tente novamente.';
        } else {
            errorMessage = `❌ Erro ao processar sua pergunta: ${error.message}. Por favor, tente novamente.`;
        }
        
        // Adiciona mensagem de erro com tipo específico
        addMessage('assistant', {
            erro: errorMessage,
            errorType: getErrorType(error)
        });
        
        // Anuncia erro para leitores de tela
        const errorAnnouncement = document.createElement('div');
        errorAnnouncement.setAttribute('role', 'alert');
        errorAnnouncement.setAttribute('aria-live', 'assertive');
        errorAnnouncement.className = 'sr-only';
        errorAnnouncement.textContent = errorMessage;
        document.body.appendChild(errorAnnouncement);
        const ERROR_ANNOUNCEMENT_DURATION_MS = 1000;
        setTimeout(() => errorAnnouncement.remove(), ERROR_ANNOUNCEMENT_DURATION_MS);
        
        console.error('Erro ao enviar mensagem:', error);
    } finally {
        // Garante que o indicador seja removido quando terminar (sucesso ou erro)
        hideTypingIndicator();
        isLoading = false;
        updateUIState();
    }
}

// =========================================
// UI State Management
// =========================================
function updateUIState() {
    userInput.disabled = isLoading;
    sendButton.disabled = isLoading;
    
    if (isLoading) {
        sendButton.textContent = 'Enviando...';
    } else {
        sendButton.textContent = 'Enviar';
        userInput.focus();
    }
}

// =========================================
// Handlers
// =========================================
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const pergunta = userInput.value.trim();
    
    if (!pergunta || isLoading) {
        return;
    }
    
    await sendMessage(pergunta);
}

