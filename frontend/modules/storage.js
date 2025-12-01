/**
 * Módulo Storage - Gerenciamento de LocalStorage
 * 
 * Gerencia persistência de dados no navegador:
 * - Mensagens do chat
 * - Preferências de acessibilidade
 * - Configurações de tema
 */

// =========================================
// Constantes
// =========================================
const STORAGE_KEY = 'chatbot_messages';
const THEME_KEY = 'theme';
const FONT_SIZE_KEY = 'fontSize';
const SOUND_KEY = 'soundEnabled';
const TTS_KEY = 'ttsEnabled';
const DYSLEXIA_FONT_KEY = 'dyslexiaFont';
const COLOR_FILTER_KEY = 'colorFilter';

// =========================================
// Mensagens do Chat
// =========================================
/**
 * Carrega mensagens do localStorage
 * @returns {Array} Array de mensagens ou array vazio
 */
export function loadMessagesFromStorage() {
    try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored) {
            return JSON.parse(stored);
        }
    } catch (error) {
        console.error('Erro ao carregar mensagens do localStorage:', error);
    }
    return [];
}

/**
 * Salva mensagens no localStorage
 * @param {Array} messages - Array de mensagens para salvar
 */
export function saveMessagesToStorage(messages) {
    try {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(messages));
    } catch (error) {
        console.error('Erro ao salvar mensagens no localStorage:', error);
    }
}

/**
 * Limpa mensagens do localStorage
 */
export function clearMessagesFromStorage() {
    try {
        localStorage.removeItem(STORAGE_KEY);
    } catch (error) {
        console.error('Erro ao limpar mensagens do localStorage:', error);
    }
}

// =========================================
// Tema
// =========================================
/**
 * Carrega tema salvo
 * @returns {string} Tema salvo ou 'light' como padrão
 */
export function loadTheme() {
    try {
        return localStorage.getItem(THEME_KEY) || 'light';
    } catch (error) {
        console.error('Erro ao carregar tema:', error);
        return 'light';
    }
}

/**
 * Salva tema
 * @param {string} theme - Tema a ser salvo ('light' ou 'dark')
 */
export function saveTheme(theme) {
    try {
        localStorage.setItem(THEME_KEY, theme);
    } catch (error) {
        console.error('Erro ao salvar tema:', error);
    }
}

// =========================================
// Tamanho de Fonte
// =========================================
/**
 * Carrega tamanho de fonte salvo
 * @returns {number|null} Tamanho da fonte ou null se não houver
 */
export function loadFontSize() {
    try {
        const saved = localStorage.getItem(FONT_SIZE_KEY);
        return saved ? parseInt(saved) : null;
    } catch (error) {
        console.error('Erro ao carregar tamanho de fonte:', error);
        return null;
    }
}

/**
 * Salva tamanho de fonte
 * @param {number} size - Tamanho da fonte em porcentagem
 */
export function saveFontSize(size) {
    try {
        localStorage.setItem(FONT_SIZE_KEY, size.toString());
    } catch (error) {
        console.error('Erro ao salvar tamanho de fonte:', error);
    }
}

// =========================================
// Som
// =========================================
/**
 * Carrega preferência de som
 * @returns {boolean|null} Preferência de som ou null se não houver
 */
export function loadSoundPreference() {
    try {
        const saved = localStorage.getItem(SOUND_KEY);
        return saved !== null ? saved === 'true' : null;
    } catch (error) {
        console.error('Erro ao carregar preferência de som:', error);
        return null;
    }
}

/**
 * Salva preferência de som
 * @param {boolean} enabled - Se o som está habilitado
 */
export function saveSoundPreference(enabled) {
    try {
        localStorage.setItem(SOUND_KEY, enabled.toString());
    } catch (error) {
        console.error('Erro ao salvar preferência de som:', error);
    }
}

// =========================================
// TTS (Text-to-Speech)
// =========================================
/**
 * Carrega preferência de TTS
 * @returns {boolean|null} Preferência de TTS ou null se não houver
 */
export function loadTTSPreference() {
    try {
        const saved = localStorage.getItem(TTS_KEY);
        return saved !== null ? saved === 'true' : null;
    } catch (error) {
        console.error('Erro ao carregar preferência de TTS:', error);
        return null;
    }
}

/**
 * Salva preferência de TTS
 * @param {boolean} enabled - Se o TTS está habilitado
 */
export function saveTTSPreference(enabled) {
    try {
        localStorage.setItem(TTS_KEY, enabled.toString());
    } catch (error) {
        console.error('Erro ao salvar preferência de TTS:', error);
    }
}

// =========================================
// Fonte para Dislexia
// =========================================
/**
 * Carrega preferência de fonte para dislexia
 * @returns {boolean|null} Preferência ou null se não houver
 */
export function loadDyslexiaFontPreference() {
    try {
        const saved = localStorage.getItem(DYSLEXIA_FONT_KEY);
        return saved !== null ? saved === 'true' : null;
    } catch (error) {
        console.error('Erro ao carregar preferência de fonte dislexia:', error);
        return null;
    }
}

/**
 * Salva preferência de fonte para dislexia
 * @param {boolean} enabled - Se a fonte está habilitada
 */
export function saveDyslexiaFontPreference(enabled) {
    try {
        localStorage.setItem(DYSLEXIA_FONT_KEY, enabled.toString());
    } catch (error) {
        console.error('Erro ao salvar preferência de fonte dislexia:', error);
    }
}

// =========================================
// Filtro de Cores (Daltonismo)
// =========================================
/**
 * Carrega filtro de cores salvo
 * @returns {string|null} Nome do filtro ou null se não houver
 */
export function loadColorFilter() {
    try {
        return localStorage.getItem(COLOR_FILTER_KEY);
    } catch (error) {
        console.error('Erro ao carregar filtro de cores:', error);
        return null;
    }
}

/**
 * Salva filtro de cores
 * @param {string} filterName - Nome do filtro ('protanopia', 'deuteranopia', etc.)
 */
export function saveColorFilter(filterName) {
    try {
        localStorage.setItem(COLOR_FILTER_KEY, filterName);
    } catch (error) {
        console.error('Erro ao salvar filtro de cores:', error);
    }
}

/**
 * Remove filtro de cores
 */
export function clearColorFilter() {
    try {
        localStorage.removeItem(COLOR_FILTER_KEY);
    } catch (error) {
        console.error('Erro ao remover filtro de cores:', error);
    }
}

// =========================================
// Utilitários
// =========================================
/**
 * Limpa todos os dados do localStorage
 */
export function clearAllStorage() {
    try {
        localStorage.clear();
    } catch (error) {
        console.error('Erro ao limpar localStorage:', error);
    }
}

/**
 * Verifica se localStorage está disponível
 * @returns {boolean} true se disponível
 */
export function isStorageAvailable() {
    try {
        const test = '__storage_test__';
        localStorage.setItem(test, test);
        localStorage.removeItem(test);
        return true;
    } catch (error) {
        return false;
    }
}
