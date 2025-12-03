/**
 * Módulo Avatar - Gerenciamento do Avatar Dinâmico
 * 
 * Gerencia o avatar Lottie e seus estados emocionais:
 * - Carregamento da animação Lottie
 * - Transições de estado (IDLE, THINKING, HAPPY, etc.)
 * - Feedback visual para o usuário
 */

// =========================================
// Constantes e Estados
// =========================================
export const AVATAR_STATES = {
    IDLE: 'idle',           // Estado neutro/padrão
    LISTENING: 'listening', // Ouvindo usuário (microfone)
    THINKING: 'thinking',   // Processando resposta
    HAPPY: 'happy',         // Resposta encontrada/sucesso
    SAD: 'sad',             // Erro ou não entendeu
    CONFUSED: 'confused',   // Dúvida ou rate limit
    SURPRISED: 'surprised', // Easter eggs ou novidades
    EUREKA: 'eureka',       // Encontrou algo importante (busca)
    ERROR: 'error',         // Erro crítico
    SLEEP: 'sleep',         // Inativo por muito tempo
    GREETING: 'greeting',   // Boas vindas
    BACK_SOON: 'back-soon'  // Timeout/espera
};

// Configuração do Lottie
const LOTTIE_PATH = 'https://assets2.lottiefiles.com/packages/lf20_w51pcehl.json'; // Robô amigável

// Estado interno
let lottieInstance = null;
let currentAvatarState = AVATAR_STATES.GREETING;
let avatarContainer = null;

// =========================================
// Inicialização
// =========================================
/**
 * Inicializa o avatar no container especificado
 * @param {HTMLElement} container - Elemento DOM onde o avatar será renderizado
 */
export function initAvatar(container) {
    if (!container) {
        console.error('Container do avatar não fornecido');
        return;
    }

    avatarContainer = container;

    try {
        // Verifica se lottie está carregado (global)
        if (typeof lottie === 'undefined') {
            console.warn('Biblioteca Lottie não carregada. Avatar estático será usado.');
            container.innerHTML = '<div class="static-avatar">🤖</div>';
            return;
        }

        lottieInstance = lottie.loadAnimation({
            container: container,
            renderer: 'svg',
            loop: true,
            autoplay: true,
            path: LOTTIE_PATH
        });

        // Define estado inicial
        updateAvatar(AVATAR_STATES.GREETING);

        console.log('Avatar inicializado com sucesso');
    } catch (error) {
        console.error('Erro ao inicializar avatar:', error);
        container.innerHTML = '<div class="static-avatar">🤖</div>';
    }
}

// =========================================
// Gerenciamento de Estado
// =========================================
/**
 * Atualiza o estado do avatar
 * @param {string} state - Novo estado (use AVATAR_STATES)
 * @param {boolean} animate - Se deve animar a transição (padrão: true)
 */
export function updateAvatar(state, animate = true) {
    if (!Object.values(AVATAR_STATES).includes(state)) {
        console.warn(`Estado de avatar inválido: ${state}`);
        return;
    }

    currentAvatarState = state;

    // Atualiza atributo data-state para CSS
    if (avatarContainer) {
        avatarContainer.setAttribute('data-state', state);

        // Adiciona classe para animações CSS
        if (animate) {
            avatarContainer.classList.add('state-change');
            setTimeout(() => {
                avatarContainer.classList.remove('state-change');
            }, 500);
        }
    }

    // Ajusta velocidade/animação do Lottie baseado no estado
    if (lottieInstance) {
        switch (state) {
            case AVATAR_STATES.THINKING:
                lottieInstance.setSpeed(1.5);
                break;
            case AVATAR_STATES.HAPPY:
            case AVATAR_STATES.EUREKA:
                lottieInstance.setSpeed(1.2);
                break;
            case AVATAR_STATES.SLEEP:
                lottieInstance.setSpeed(0.5);
                break;
            case AVATAR_STATES.ERROR:
            case AVATAR_STATES.SAD:
                lottieInstance.setSpeed(0.8);
                break;
            default:
                lottieInstance.setSpeed(1.0);
        }
    }
}

/**
 * Retorna o estado atual do avatar
 * @returns {string} Estado atual
 */
export function getCurrentAvatarState() {
    return currentAvatarState;
}

// =========================================
// Utilitários
// =========================================
/**
 * Define a velocidade da animação manualmente
 * @param {number} speed - Velocidade (1.0 = normal)
 */
export function setAvatarSpeed(speed) {
    if (lottieInstance) {
        lottieInstance.setSpeed(speed);
    }
}

/**
 * Pausa a animação
 */
export function pauseAvatar() {
    if (lottieInstance) {
        lottieInstance.pause();
    }
}

/**
 * Retoma a animação
 */
export function playAvatar() {
    if (lottieInstance) {
        lottieInstance.play();
    }
}

/**
 * Retorna o caminho da imagem estática para um estado
 * @param {string} state - Estado do avatar
 * @returns {string} Caminho da imagem
 */
export function getAvatarPath(state) {
    // Mapeamento de estados para arquivos de imagem
    // Ajuste conforme os nomes reais dos arquivos na pasta assets
    const stateMap = {
        [AVATAR_STATES.IDLE]: 'ada-idle.png',
        [AVATAR_STATES.LISTENING]: 'ada-listening.png',
        [AVATAR_STATES.THINKING]: 'ada-thinking.png',
        [AVATAR_STATES.HAPPY]: 'ada-happy.png',
        [AVATAR_STATES.SAD]: 'ada-sad.png',
        [AVATAR_STATES.CONFUSED]: 'ada-confused.png',
        [AVATAR_STATES.SURPRISED]: 'ada-surprised.png',
        [AVATAR_STATES.EUREKA]: 'ada-eureka.png',
        [AVATAR_STATES.ERROR]: 'ada-error.png',
        [AVATAR_STATES.SLEEP]: 'ada-sleep.png',
        [AVATAR_STATES.GREETING]: 'ada-greeting.png',
        [AVATAR_STATES.BACK_SOON]: 'ada-back-soon.png'
    };

    const filename = stateMap[state] || 'ada-idle.png';
    return `/assets/ada-states/${filename}`;
}

/**
 * Destrói a instância do avatar (limpeza)
 */
export function destroyAvatar() {
    if (lottieInstance) {
        lottieInstance.destroy();
        lottieInstance = null;
    }
}
