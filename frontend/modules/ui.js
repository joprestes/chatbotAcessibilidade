/**
 * Módulo UI - Interface do Usuário e Interações
 * 
 * Responsável por:
 * - Sistema de Modais Acessíveis (WCAG 2.4.3)
 * - Notificações Toast
 * - Sidebar Responsiva
 * - Utilitários de Formulário (Contador, Resize)
 * - Feedback Visual
 */

import { trapFocus } from './accessibility.js';
import { playSound } from './audio.js';

// =========================================
// Estado Interno
// =========================================
let modalElement = null;
let modalLastFocusedElement = null;
let activeToasts = [];

// =========================================
// Inicialização
// =========================================
/**
 * Inicializa componentes de UI
 */
export function initUI() {
    // Configura listeners globais de UI se necessário
    setupGlobalUIListeners();
    console.log('UI inicializada');
}

function setupGlobalUIListeners() {
    // Fecha modal ao clicar fora ou ESC (já tratado no accessibility.js, mas reforço aqui se necessário)
    document.addEventListener('click', (e) => {
        if (modalElement && e.target === modalElement) {
            closeModal();
        }
    });

    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', toggleSidebar);
    }
}

// =========================================
// Sistema de Modal Acessível
// =========================================
/**
 * Abre um modal acessível
 * @param {string} title - Título do modal
 * @param {string} content - Conteúdo HTML do modal
 * @param {Object} options - Opções (onConfirm, onCancel, textos, hideButtons)
 */
export function openModal(title, content, options = {}) {
    modalElement = document.getElementById('accessible-modal');
    if (!modalElement) {
        console.error('Elemento #accessible-modal não encontrado');
        return;
    }

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

    if (cancelButton) {
        if (options.hideCancelButton) {
            cancelButton.style.display = 'none';
        } else {
            cancelButton.style.display = '';
            cancelButton.textContent = options.cancelText || 'Cancelar';
            cancelButton.onclick = () => {
                if (options.onCancel) options.onCancel();
                closeModal();
            };
        }
    }

    if (confirmButton) {
        if (options.hideConfirmButton) {
            confirmButton.style.display = 'none';
        } else {
            confirmButton.style.display = '';
            confirmButton.textContent = options.confirmText || 'Confirmar';
            confirmButton.onclick = () => {
                if (options.onConfirm) options.onConfirm();
                closeModal();
            };
        }
    }

    // Mostra modal
    modalElement.removeAttribute('hidden');
    modalElement.setAttribute('aria-hidden', 'false');
    modalElement.classList.add('open');

    // Previne scroll do body
    document.body.style.overflow = 'hidden';

    // Configura focus trap
    trapFocus(modalElement);

    // Foca no primeiro elemento focável ou no modal
    setTimeout(() => {
        const firstFocusable = modalElement.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
        if (firstFocusable) {
            firstFocusable.focus();
        } else {
            modalElement.focus();
        }
    }, 100);

    playSound('NOTIFICATION');
}

/**
 * Fecha o modal ativo
 * @param {boolean} restoreFocus - Se deve restaurar o foco ao elemento anterior
 */
export function closeModal(restoreFocus = true) {
    if (!modalElement) return;

    // Esconde modal
    modalElement.setAttribute('aria-hidden', 'true');
    modalElement.classList.remove('open');
    modalElement.setAttribute('hidden', '');

    // Restaura scroll do body
    document.body.style.overflow = '';

    // Retorna foco ao elemento anterior
    if (restoreFocus && modalLastFocusedElement) {
        modalLastFocusedElement.focus();
    }

    modalElement = null;
    modalLastFocusedElement = null;
}

// =========================================
// Notificações Toast
// =========================================
/**
 * Exibe uma notificação Toast
 * @param {string} message - Mensagem
 * @param {string} type - 'info', 'success', 'error', 'warning'
 * @param {number} duration - Duração em ms
 */
export function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

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

    container.appendChild(toast);
    activeToasts.push(toast);

    // Animação de entrada
    requestAnimationFrame(() => {
        toast.classList.add('show');
    });

    // Som de notificação (exceto erro que já tem som próprio no catch)
    if (type !== 'error') {
        playSound('NOTIFICATION');
    }

    // Remove após duração
    setTimeout(() => {
        removeToast(toast);
    }, duration);
}

function removeToast(toast) {
    toast.classList.remove('show');
    toast.addEventListener('transitionend', () => {
        if (toast.parentElement) {
            toast.remove();
        }
        activeToasts = activeToasts.filter(t => t !== toast);
    });
}

// =========================================
// Sidebar Responsiva
// =========================================
/**
 * Alterna visibilidade da sidebar em mobile
 */
export function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const toggleBtn = document.getElementById('sidebar-toggle');

    if (!sidebar || !overlay) return;

    const isOpen = sidebar.classList.contains('open');

    if (isOpen) {
        sidebar.classList.remove('open');
        overlay.classList.remove('active');
        toggleBtn?.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    } else {
        sidebar.classList.add('open');
        overlay.classList.add('active');
        toggleBtn?.setAttribute('aria-expanded', 'true');
        document.body.style.overflow = 'hidden'; // Previne scroll do fundo

        // Fecha ao clicar no overlay
        overlay.onclick = () => toggleSidebar();
    }
}

// =========================================
// Utilitários de Formulário
// =========================================
/**
 * Atualiza contador de caracteres do input
 */
export function updateCharCounter() {
    const input = document.getElementById('user-input');
    const counter = document.getElementById('char-counter');
    const maxLength = input?.getAttribute('maxlength') || 2000;

    if (input && counter) {
        const currentLength = input.value.length;
        counter.textContent = `${currentLength}/${maxLength}`;

        // Feedback visual se próximo do limite
        if (currentLength >= maxLength * 0.9) {
            counter.classList.add('warning');
        } else {
            counter.classList.remove('warning');
        }
    }
}

/**
 * Redimensiona textarea automaticamente
 * @param {HTMLTextAreaElement} textarea 
 */
export function autoResizeTextarea(textarea) {
    if (!textarea) return;

    textarea.style.height = 'auto';
    const newHeight = Math.min(textarea.scrollHeight, 200); // Max height 200px
    textarea.style.height = `${newHeight}px`;
}

/**
 * Reseta altura do textarea
 * @param {HTMLTextAreaElement} textarea 
 */
export function resetTextarea(textarea) {
    if (!textarea) return;
    textarea.style.height = '';
}
