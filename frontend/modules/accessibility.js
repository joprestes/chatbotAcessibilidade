/**
 * Módulo Accessibility - Recursos de Acessibilidade (WCAG AAA)
 * 
 * Responsável por:
 * - Gerenciamento de Temas (Claro/Escuro)
 * - Controle de Tamanho de Fonte
 * - Filtros de Daltonismo
 * - Fonte para Dislexia (OpenDyslexic)
 * - Anúncios para Leitor de Tela (Live Regions)
 * - Navegação por Teclado e Foco
 */

import {
    loadTheme,
    saveTheme,
    loadFontSize,
    saveFontSize,
    loadDyslexiaFontPreference,
    saveDyslexiaFontPreference,
    loadColorFilter,
    saveColorFilter
} from './storage.js';

import { playSound } from './audio.js';

// =========================================
// Constantes
// =========================================
const MIN_FONT_SIZE = 75;  // 75%
const MAX_FONT_SIZE = 200; // 200% (WCAG 1.4.4)
const FONT_STEP = 12.5;    // Incremento suave

// Estado interno
let currentFontSize = 100;
let currentTheme = 'light';
let isDyslexicFontEnabled = false;
let currentColorFilter = '';

// =========================================
// Inicialização
// =========================================
/**
 * Inicializa o módulo de acessibilidade
 */
export function initAccessibility() {
    // Carrega preferências
    currentTheme = loadTheme();
    currentFontSize = loadFontSize() || 100;
    isDyslexicFontEnabled = loadDyslexiaFontPreference();
    currentColorFilter = loadColorFilter();

    // Aplica configurações iniciais
    applyTheme(currentTheme);
    applyFontSize(currentFontSize);
    toggleDyslexiaFont(isDyslexicFontEnabled);
    applyColorFilter(currentColorFilter);

    // Configura navegação por teclado
    setupKeyboardNavigation();

    console.log('Acessibilidade inicializada');
}

// =========================================
// Gerenciamento de Tema
// =========================================
/**
 * Alterna entre tema claro e escuro
 */
export function toggleTheme() {
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    applyTheme(newTheme);
    saveTheme(newTheme);

    // Feedback sonoro e visual
    playSound('ON');
    const themeName = newTheme === 'dark' ? 'escuro' : 'claro';
    announceToScreenReader(`Tema ${themeName} ativado`);

    return newTheme;
}

/**
 * Aplica um tema específico
 * @param {string} theme - 'light' ou 'dark'
 */
export function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    updateThemeToggleUI();
}

function updateThemeToggleUI() {
    const btn = document.getElementById('theme-toggle');
    if (!btn) return;

    const isDark = currentTheme === 'dark';
    btn.setAttribute('aria-label', isDark ? 'Alternar para tema claro' : 'Alternar para tema escuro');

    // Atualiza ícone (SVG)
    const themeIcon = document.getElementById('theme-icon');
    if (themeIcon) {
        const moonPath = themeIcon.querySelector('.theme-icon-moon');
        let sunGroup = themeIcon.querySelector('.theme-icon-sun');

        if (isDark) {
            if (moonPath) moonPath.style.display = 'none';
            if (sunGroup) sunGroup.style.display = 'block';
            else createSunIcon(themeIcon);
        } else {
            if (moonPath) moonPath.style.display = 'block';
            if (sunGroup) sunGroup.style.display = 'none';
        }
    }
}

function createSunIcon(container) {
    const sunGroup = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    sunGroup.setAttribute('class', 'theme-icon-sun');

    const sun = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    sun.setAttribute('cx', '12');
    sun.setAttribute('cy', '12');
    sun.setAttribute('r', '5');
    sunGroup.appendChild(sun);

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

    container.appendChild(sunGroup);
}

// =========================================
// Controle de Fonte
// =========================================
/**
 * Altera o tamanho da fonte
 * @param {number} direction - 1 (aumentar) ou -1 (diminuir)
 */
export function changeFontSize(direction) {
    const newSize = currentFontSize + (direction * FONT_STEP);

    if (newSize >= MIN_FONT_SIZE && newSize <= MAX_FONT_SIZE) {
        currentFontSize = newSize;
        applyFontSize(currentFontSize);
        saveFontSize(currentFontSize);
        playSound('ON');

        const action = direction > 0 ? 'aumentado' : 'diminuído';
        announceToScreenReader(`Tamanho do texto ${action} para ${currentFontSize}%`);
    } else {
        playSound('ERROR');
        announceToScreenReader('Limite de tamanho de fonte atingido');
    }
}

function applyFontSize(size) {
    document.documentElement.style.fontSize = `${size}%`;
}

// =========================================
// Fonte para Dislexia
// =========================================
/**
 * Alterna fonte amigável para dislexia
 * @param {boolean} enable - Habilitar ou desabilitar
 */
export function toggleDyslexiaFont(enable) {
    isDyslexicFontEnabled = enable;

    if (enable) {
        document.body.classList.add('font-dyslexic');
        announceToScreenReader('Fonte para dislexia ativada');
    } else {
        document.body.classList.remove('font-dyslexic');
        announceToScreenReader('Fonte padrão restaurada');
    }

    saveDyslexiaFontPreference(enable);
}

// =========================================
// Filtros de Daltonismo
// =========================================
/**
 * Aplica filtro de daltonismo
 * @param {string} filterName - Nome do filtro (protanopia, deuteranopia, etc.)
 */
export function applyColorFilter(filterName) {
    // Remove filtros anteriores
    document.body.classList.remove(
        'filter-protanopia',
        'filter-deuteranopia',
        'filter-tritanopia',
        'filter-achromatopsia'
    );

    if (filterName) {
        document.body.classList.add(`filter-${filterName}`);
        announceToScreenReader(`Filtro ${filterName} aplicado`);
    } else if (currentColorFilter) {
        announceToScreenReader('Filtros de cor removidos');
    }

    currentColorFilter = filterName;
    saveColorFilter(filterName);
}

// =========================================
// Leitor de Tela (Live Regions)
// =========================================
/**
 * Anuncia mensagem para leitor de tela
 * @param {string} message - Mensagem a ser anunciada
 * @param {string} priority - 'polite' (padrão) ou 'assertive'
 */
export function announceToScreenReader(message, priority = 'polite') {
    const liveRegion = document.getElementById('sr-announcements');
    if (liveRegion) {
        liveRegion.setAttribute('aria-live', priority);
        // Limpa e atualiza com delay para garantir detecção
        liveRegion.textContent = '';
        setTimeout(() => {
            liveRegion.textContent = message;
        }, 100);
    }
}

// =========================================
// Navegação por Teclado
// =========================================
/**
 * Configura navegação por teclado e atalhos
 */
export function setupKeyboardNavigation() {
    // Foco visível ao usar Tab
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            document.body.classList.add('user-is-tabbing');
        }
    });

    document.addEventListener('mousedown', () => {
        document.body.classList.remove('user-is-tabbing');
    });

    // Atalho ESC para cancelar/fechar modais
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            // Fecha modais se houver
            const openModal = document.querySelector('.modal[aria-hidden="false"]');
            if (openModal) {
                // Lógica de fechar modal seria chamada aqui
                // Como o modal UI ainda não foi extraído, deixamos o hook
            }

            // Cancela requisição se estiver carregando
            // Lógica de cancelamento está no módulo API/UI
        }
    });
}

/**
 * Gerencia trap de foco em modais
 * @param {HTMLElement} element - Elemento container do modal
 */
export function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
    );

    if (focusableElements.length === 0) return;

    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];

    element.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            if (e.shiftKey) { // Shift + Tab
                if (document.activeElement === firstElement) {
                    e.preventDefault();
                    lastElement.focus();
                }
            } else { // Tab
                if (document.activeElement === lastElement) {
                    e.preventDefault();
                    firstElement.focus();
                }
            }
        }
    });
}
