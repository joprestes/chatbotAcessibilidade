/**
 * Módulo API - Comunicação com o Backend
 * 
 * Gerencia todas as interações com a API do chatbot:
 * - Carregamento de configurações
 * - Envio de mensagens
 * - Cancelamento de requisições
 * - Health checks
 */

// =========================================
// Configuração
// =========================================
const API_BASE_URL = window.location.origin;
const API_CHAT_ENDPOINT = `${API_BASE_URL}/api/chat`;
const API_CONFIG_ENDPOINT = `${API_BASE_URL}/api/config`;

// Configurações do frontend (carregadas do backend)
let frontendConfig = {
    request_timeout_ms: 120000,
    error_announcement_duration_ms: 1000
};

// Estado de requisições
let currentAbortController = null;

// =========================================
// Carregamento de Configuração
// =========================================
/**
 * Carrega configurações do frontend a partir do backend
 */
export async function loadFrontendConfig() {
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

/**
 * Retorna as configurações atuais do frontend
 */
export function getFrontendConfig() {
    return frontendConfig;
}

// =========================================
// Health Check
// =========================================
/**
 * Verifica a saúde da API
 */
export async function checkAPIHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/health`);
        if (!response.ok) {
            console.warn('API não está respondendo corretamente');
        }
    } catch (error) {
        console.error('Erro ao verificar saúde da API:', error);
    }
}

// =========================================
// Cancelamento de Requisições
// =========================================
/**
 * Cancela a requisição atual
 * @param {Event} e - Evento de clique (opcional)
 */
export function cancelRequest(e) {
    e?.preventDefault();
    e?.stopPropagation();

    console.log('Cancelar clicado, currentAbortController:', currentAbortController);

    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
        return true; // Indica que havia requisição para cancelar
    } else {
        console.warn('Tentativa de cancelar, mas não há requisição ativa');
        return false;
    }
}

/**
 * Retorna o AbortController atual
 */
export function getCurrentAbortController() {
    return currentAbortController;
}

// =========================================
// Envio de Mensagens
// =========================================
/**
 * Envia uma mensagem para a API do chatbot
 * @param {string} pergunta - Pergunta do usuário
 * @param {Object} callbacks - Callbacks para eventos
 * @param {Function} callbacks.onStart - Chamado ao iniciar
 * @param {Function} callbacks.onSuccess - Chamado em sucesso
 * @param {Function} callbacks.onError - Chamado em erro
 * @param {Function} callbacks.onWarning - Chamado em aviso de timeout
 * @param {Function} callbacks.onFinally - Chamado sempre ao final
 * @returns {Promise<Object>} Resposta da API
 */
export async function sendMessage(pergunta, callbacks = {}) {
    const {
        onStart,
        onSuccess,
        onError,
        onWarning,
        onFinally
    } = callbacks;

    // Callback de início
    if (onStart) onStart();

    // AbortController para timeout e cancelamento
    currentAbortController = new AbortController();
    const controller = currentAbortController;

    // Timeout configurável (WCAG 2.2.6)
    const timeoutMs = frontendConfig.request_timeout_ms || 120000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

    // Timer de aviso (20s antes do timeout)
    const WARNING_BEFORE_TIMEOUT_MS = 20000;
    const warningTime = Math.max(timeoutMs - WARNING_BEFORE_TIMEOUT_MS, 5000);
    const warningTimerId = setTimeout(() => {
        if (currentAbortController === controller && onWarning) {
            onWarning(controller, timeoutId);
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
        clearTimeout(warningTimerId);

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

        // Callback de sucesso
        if (onSuccess) onSuccess(data);

        return data;

    } catch (error) {
        clearTimeout(timeoutId);
        clearTimeout(warningTimerId);

        // Se foi cancelado manualmente pelo usuário, não trata como erro
        if (error.name === 'AbortError' && controller.signal.aborted && !currentAbortController) {
            console.log('Requisição cancelada manualmente pelo usuário');
            return null;
        }

        // Callback de erro
        if (onError) onError(error);

        throw error;

    } finally {
        // Limpa o controller se ainda for o atual
        if (currentAbortController === controller) {
            currentAbortController = null;
        }

        // Callback final
        if (onFinally) onFinally();
    }
}

// =========================================
// Utilitários
// =========================================
/**
 * Determina o tipo de erro baseado no erro recebido
 * @param {Error} error - Erro a ser classificado
 * @returns {string} Tipo do erro
 */
export function getErrorType(error) {
    if (error.name === 'AbortError' || error.message === 'AbortError') {
        return 'timeout';
    } else if (error.message === 'OFFLINE') {
        return 'offline';
    } else if (error.message === 'RATE_LIMIT') {
        return 'rate_limit';
    } else if (error.message === 'SERVER_ERROR') {
        return 'server_error';
    } else if (error.message.includes('Failed to fetch') || error.message.includes('NetworkError')) {
        return 'network';
    } else if (error.message.includes('validação') || error.message.includes('422')) {
        return 'validation';
    } else {
        return 'unknown';
    }
}

/**
 * Retorna mensagem de erro amigável baseada no tipo
 * @param {Error} error - Erro a ser formatado
 * @returns {string} Mensagem de erro amigável
 */
export function getErrorMessage(error) {
    const type = getErrorType(error);

    const messages = {
        timeout: '⏱️ A requisição demorou muito para responder (timeout). Por favor, tente novamente.',
        offline: '📡 Você está offline. Verifique sua conexão com a internet e tente novamente.',
        rate_limit: '🚦 Muitas requisições no momento. Por favor, aguarde um minuto e tente novamente.',
        server_error: '🔧 Erro no servidor. Nossa equipe foi notificada. Por favor, tente novamente em alguns instantes.',
        network: '🌐 Erro de conexão. Verifique sua internet e tente novamente.',
        validation: `❌ ${error.message}`,
        unknown: `❌ Erro ao processar sua pergunta: ${error.message}. Por favor, tente novamente.`
    };

    return messages[type] || messages.unknown;
}
