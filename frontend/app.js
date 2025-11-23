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
let searchFilter = ''; // Filtro de busca no histórico
const TYPING_MESSAGE_ID = '__typing_indicator__'; // ID especial para mensagem de digitação
const MAX_QUESTION_LENGTH = 2000; // Máximo de caracteres (do backend)

// =========================================
// Elementos DOM
// =========================================
const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const themeToggle = document.getElementById('theme-toggle');

// Elementos que serão criados dinamicamente
let cancelButton = null;
let charCounter = null;
let searchInput = null;

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
    
    // Cria botão cancelar
    if (!cancelButton) {
        cancelButton = document.createElement('button');
        cancelButton.type = 'button';
        cancelButton.className = 'cancel-button';
        cancelButton.textContent = 'Cancelar';
        cancelButton.setAttribute('data-testid', 'cancel-button');
        cancelButton.setAttribute('aria-label', 'Cancelar envio da mensagem');
        cancelButton.style.display = 'none';
        cancelButton.addEventListener('click', cancelRequest);
        sendButton.parentElement.appendChild(cancelButton);
    }
    
    // Cria input de busca (se não existir)
    if (!searchInput) {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            const searchWrapper = document.createElement('div');
            searchWrapper.className = 'search-wrapper';
            searchInput = document.createElement('input');
            searchInput.type = 'text';
            searchInput.className = 'search-input';
            searchInput.placeholder = 'Buscar no histórico...';
            searchInput.setAttribute('data-testid', 'search-input');
            searchInput.setAttribute('aria-label', 'Buscar mensagens no histórico');
            searchInput.addEventListener('input', (e) => {
                searchFilter = e.target.value.toLowerCase();
                renderMessages();
            });
            searchWrapper.appendChild(searchInput);
            // Insere antes do chat-container
            const chatContainer = document.getElementById('chat-container');
            if (chatContainer) {
                mainContent.insertBefore(searchWrapper, chatContainer);
            }
        }
    }
    
    // Atualiza contador inicial
    updateCharCounter();
}

// =========================================
// Contador de Caracteres
// =========================================
function updateCharCounter() {
    if (!charCounter) return;
    
    const length = userInput.value.length;
    const remaining = MAX_QUESTION_LENGTH - length;
    const percentage = (length / MAX_QUESTION_LENGTH) * 100;
    
    charCounter.textContent = `${length}/${MAX_QUESTION_LENGTH}`;
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
function cancelRequest() {
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
        
        hideTypingIndicator();
        hideSkeletonLoading();
        isLoading = false;
        updateUIState();
        
        showToast('Requisição cancelada pelo usuário.', 'info');
        addMessage('assistant', {
            erro: '❌ Requisição cancelada pelo usuário.',
            errorType: 'cancelled'
        });
    }
}

// =========================================
// Event Listeners
// =========================================
function setupEventListeners() {
    // Formulário de envio
    chatForm.addEventListener('submit', handleFormSubmit);
    
    // Enter no textarea (sem Shift = enviar, com Shift = nova linha)
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
    avatar.textContent = message.role === 'user' ? '👤' : '💜';
    
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
    updateUIState();
    
    // Adiciona mensagem do usuário
    addMessage('user', pergunta);
    
    // Limpa o input
    userInput.value = '';
    
    // Adiciona indicador de digitação (typing indicator)
    showTypingIndicator();
    // Mostra skeleton loading também
    showSkeletonLoading();
    
    // AbortController para timeout e cancelamento
    currentAbortController = new AbortController();
    const controller = currentAbortController;
    // Timeout usando constante do backend
    const timeoutId = setTimeout(() => controller.abort(), frontendConfig.request_timeout_ms);
    
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
        
        // Remove indicador de digitação e skeleton
        hideTypingIndicator();
        hideSkeletonLoading();
        
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
        hideSkeletonLoading();
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
        sendButton.style.opacity = '0.6';
        sendButton.setAttribute('aria-label', 'Enviando mensagem...');
        if (cancelButton) {
            cancelButton.style.display = 'inline-block';
        }
    } else {
        sendButton.style.opacity = '1';
        sendButton.setAttribute('aria-label', 'Enviar mensagem');
        if (cancelButton) {
            cancelButton.style.display = 'none';
        }
        // Auto-resize textarea ao desabilitar
        if (userInput.tagName === 'TEXTAREA') {
            autoResizeTextarea(userInput);
        }
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

