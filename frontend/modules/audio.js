/**
 * Módulo Audio - Gerenciamento de Som e Voz
 * 
 * Responsável por:
 * - Efeitos sonoros (Sound FX)
 * - Text-to-Speech (TTS)
 * - Speech-to-Text (STT / Reconhecimento de Voz)
 * - Gerenciamento de preferências de áudio
 */

import {
    loadSoundPreference,
    loadTTSPreference,
    saveSoundPreference,
    saveTTSPreference
} from './storage.js';

// =========================================
// Constantes e Configuração
// =========================================
const SOUNDS = {
    SENT: '/assets/sounds/sent.mp3',
    RECEIVED: '/assets/sounds/received.mp3',
    ERROR: '/assets/sounds/error.mp3',
    NOTIFICATION: '/assets/sounds/notification.mp3',
    START_RECORD: '/assets/sounds/start-record.mp3',
    STOP_RECORD: '/assets/sounds/stop-record.mp3'
};

// Estado interno
let isSoundEnabled = true;
let isTTSEnabled = false;
let recognition = null;
let isRecording = false;
let synthesisVoice = null;

// Callbacks para eventos de STT
let onSpeechResult = null;
let onSpeechStart = null;
let onSpeechEnd = null;
let onSpeechError = null;

// =========================================
// Inicialização
// =========================================
/**
 * Inicializa o módulo de áudio
 * @param {Object} callbacks - Callbacks para eventos de fala (onResult, onStart, onEnd, onError)
 */
export function initAudio(callbacks = {}) {
    // Carrega preferências
    isSoundEnabled = loadSoundPreference();
    isTTSEnabled = loadTTSPreference();

    // Configura callbacks
    onSpeechResult = callbacks.onResult || (() => { });
    onSpeechStart = callbacks.onStart || (() => { });
    onSpeechEnd = callbacks.onEnd || (() => { });
    onSpeechError = callbacks.onError || (() => { });

    // Inicializa voz para TTS
    initTTS();

    // Inicializa reconhecimento de voz
    initSpeechRecognition();

    console.log('Áudio inicializado. Som:', isSoundEnabled, 'TTS:', isTTSEnabled);
}

/**
 * Retorna estado do som
 */
export function getSoundEnabled() {
    return isSoundEnabled;
}

/**
 * Define estado do som
 */
export function setSoundEnabled(enabled) {
    isSoundEnabled = enabled;
    saveSoundPreference(enabled);
}

/**
 * Retorna estado do TTS
 */
export function getTTSEnabled() {
    return isTTSEnabled;
}

/**
 * Define estado do TTS
 */
export function setTTSEnabled(enabled) {
    isTTSEnabled = enabled;
    saveTTSPreference(enabled);
    if (!enabled) {
        stopSpeaking();
    }
}

// =========================================
// Efeitos Sonoros
// =========================================
/**
 * Toca um efeito sonoro
 * @param {string} type - Tipo do som (chave de SOUNDS)
 */
export function playSound(type) {
    if (!isSoundEnabled) return;

    const soundPath = SOUNDS[type];
    if (!soundPath) {
        console.warn(`Som não encontrado: ${type}`);
        return;
    }

    const audio = new Audio(soundPath);
    audio.volume = 0.5;
    audio.play().catch(e => console.warn('Erro ao tocar som:', e));
}

// =========================================
// Text-to-Speech (TTS)
// =========================================
function initTTS() {
    if ('speechSynthesis' in window) {
        // Carrega vozes
        window.speechSynthesis.onvoiceschanged = () => {
            const voices = window.speechSynthesis.getVoices();
            // Tenta encontrar voz em português do Brasil
            synthesisVoice = voices.find(voice => voice.lang === 'pt-BR') || voices[0];
        };
    } else {
        console.warn('Navegador não suporta Speech Synthesis');
    }
}

/**
 * Fala um texto usando TTS
 * @param {string} text - Texto a ser falado
 */
export function speak(text) {
    if (!isTTSEnabled || !('speechSynthesis' in window)) return;

    // Cancela fala anterior
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'pt-BR';
    utterance.rate = 1.1; // Um pouco mais rápido que o normal
    utterance.pitch = 1.0;

    if (synthesisVoice) {
        utterance.voice = synthesisVoice;
    }

    window.speechSynthesis.speak(utterance);
}

/**
 * Para a fala atual
 */
export function stopSpeaking() {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
    }
}

// =========================================
// Speech-to-Text (STT)
// =========================================
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();

        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'pt-BR';

        recognition.onstart = () => {
            isRecording = true;
            playSound('START_RECORD');
            onSpeechStart();
        };

        recognition.onend = () => {
            isRecording = false;
            playSound('STOP_RECORD');
            onSpeechEnd();
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            onSpeechResult(transcript);
        };

        recognition.onerror = (event) => {
            console.error('Erro no reconhecimento de voz:', event.error);
            isRecording = false;
            playSound('ERROR');

            let errorMessage = 'Erro ao reconhecer voz.';
            if (event.error === 'no-speech') errorMessage = 'Não detectei fala.';
            if (event.error === 'audio-capture') errorMessage = 'Microfone não encontrado.';
            if (event.error === 'not-allowed') errorMessage = 'Permissão de microfone negada.';

            onSpeechError(errorMessage);
        };
    } else {
        console.warn('Navegador não suporta Speech Recognition');
    }
}

/**
 * Alterna estado do reconhecimento de voz (Inicia/Para)
 */
export function toggleVoiceInput() {
    if (!recognition) {
        alert('Seu navegador não suporta reconhecimento de voz.');
        return;
    }

    if (isRecording) {
        recognition.stop();
    } else {
        // Para TTS antes de ouvir para não ouvir a si mesmo
        stopSpeaking();
        try {
            recognition.start();
        } catch (e) {
            console.error('Erro ao iniciar reconhecimento:', e);
            isRecording = false;
            onSpeechEnd(); // Força update de UI
        }
    }
}

/**
 * Retorna se está gravando
 */
export function isVoiceRecording() {
    return isRecording;
}

/**
 * Verifica suporte a reconhecimento de voz
 */
export function isSpeechRecognitionSupported() {
    return !!recognition;
}
