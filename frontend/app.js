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
    
    const bubble = document.createElement('div');
    bubble.className = 'message-bubble';
    
    if (message.role === 'user') {
        bubble.textContent = message.content;
    } else {
        // Mensagem do assistente - pode ser string ou objeto
        if (typeof message.content === 'string') {
            bubble.innerHTML = formatMarkdown(message.content);
        } else if (typeof message.content === 'object') {
            if (message.content.erro) {
                bubble.className += ' error';
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
    
    const header = document.createElement('button');
    header.className = 'expander-header';
    header.setAttribute('type', 'button');
    header.setAttribute('aria-expanded', isExpanded);
    header.setAttribute('aria-controls', `content-${Date.now()}-${Math.random()}`);
    
    const titleSpan = document.createElement('span');
    titleSpan.innerHTML = title;
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
    
    // Converte markdown simples para HTML
    return text
        // Parágrafos (quebras de linha duplas)
        .split('\n\n')
        .map(paragraph => {
            if (!paragraph.trim()) return '';
            
            // Listas não ordenadas
            if (paragraph.trim().startsWith('-') || paragraph.trim().startsWith('*')) {
                const items = paragraph
                    .split('\n')
                    .filter(line => line.trim().startsWith('-') || line.trim().startsWith('*'))
                    .map(item => `<li>${item.replace(/^[-*]\s+/, '').trim()}</li>`)
                    .join('');
                return `<ul>${items}</ul>`;
            }
            
            // Links
            paragraph = paragraph.replace(
                /\[([^\]]+)\]\(([^)]+)\)/g,
                '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
            );
            
            // Negrito
            paragraph = paragraph.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
            
            // Itálico
            paragraph = paragraph.replace(/\*([^*]+)\*/g, '<em>$1</em>');
            
            // Código inline
            paragraph = paragraph.replace(/`([^`]+)`/g, '<code>$1</code>');
            
            return `<p>${paragraph}</p>`;
        })
        .join('');
}

function scrollToBottom() {
    if (chatContainer) {
        chatContainer.scrollTop = chatContainer.scrollHeight;
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
    
    // Adiciona indicador de carregamento
    const loadingMessage = { role: 'assistant', content: '🔎 Gerando resposta...', isLoading: true };
    messages.push(loadingMessage);
    renderMessages();
    
    try {
        const response = await fetch(API_CHAT_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ pergunta }),
        });
        
        // Remove mensagem de loading
        messages.pop();
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ detail: 'Erro desconhecido' }));
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }
        
        const data = await response.json();
        
        // Adiciona resposta do assistente
        addMessage('assistant', data.resposta);
        
    } catch (error) {
        // Remove mensagem de loading
        messages.pop();
        
        // Adiciona mensagem de erro
        addMessage('assistant', {
            erro: `❌ Erro ao processar sua pergunta: ${error.message}. Por favor, tente novamente.`
        });
        
        console.error('Erro ao enviar mensagem:', error);
    } finally {
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

