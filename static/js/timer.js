// timer.js: Placeholder for Pomodoro timer logic
// Step 3 will implement timer functionality

/**
 * Pomodoro Timer Logic
 * - Start, pause, reset timer
 * - Update timer display
 * - Track progress (sessions completed, focus time)
 * - Save/load progress to/from localStorage
 * - (Optional) Sync progress with backend via API calls
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeTimer();
});

// Timer state
let timerDuration = 25 * 60; // 25 minutes in seconds
let timerRemaining = timerDuration;
let timerInterval = null;
let isRunning = false;

// Progress tracking state
let sessionsCompleted = 0;
let focusTime = 0; // in seconds

// User settings
let workDuration = 25; // in minutes
let breakDuration = 5; // in minutes
let currentTheme = 'light';
let soundEnabled = true;

// Audio context for sound effects (reusable)
let audioContext = null;

/**
 * Initialize the timer and UI elements
 * - Set up event listeners
 * - Load progress from localStorage
 * - Update UI displays
 */
function initializeTimer() {
    loadSettingsFromLocalStorage();
    updateTimerDisplay();
    updateProgressBar();
    loadProgressFromLocalStorage();
    
    // Timer button event listeners
    document.getElementById('start-btn').addEventListener('click', handleStartButton);
    document.getElementById('reset-btn').addEventListener('click', handleResetButton);
    
    // Settings event listeners
    document.getElementById('work-duration').addEventListener('change', handleWorkDurationChange);
    document.getElementById('break-duration').addEventListener('change', handleBreakDurationChange);
    document.getElementById('theme-selector').addEventListener('change', handleThemeChange);
    document.getElementById('sound-enabled').addEventListener('change', handleSoundToggle);
}

/**
 * Start the Pomodoro timer
 * - Initialize timer values
 * - Start countdown interval
 * @returns 
 */
function startTimer() {
    if (isRunning) return;
    isRunning = true;
    playSound('start');
    timerInterval = setInterval(() => {
        if (timerRemaining > 0) {
            timerRemaining--;
            updateTimerDisplay();
            updateProgressBar();
        } else {
            clearInterval(timerInterval);
            isRunning = false;
            playSound('end');
            // Session complete logic
            sessionsCompleted++;
            focusTime += timerDuration;
            updateProgressStats();
            saveProgressToLocalStorage();
            resetTimer();
        }
    }, 1000);
}

/**
 * Reset the Pomodoro timer
 * - Clear interval
 * - Reset timer values
 * - Update UI displays
 */
function resetTimer() {
    clearInterval(timerInterval);
    timerRemaining = timerDuration;
    isRunning = false;
    updateTimerDisplay();
    updateProgressBar();
}

/**
 * Update the timer display in MM:SS format
 */
function updateTimerDisplay() {
    const minutes = Math.floor(timerRemaining / 60).toString().padStart(2, '0');
    const seconds = (timerRemaining % 60).toString().padStart(2, '0');
    document.getElementById('timer-display').textContent = `${minutes}:${seconds}`;
}

/**
 * Update the circular progress bar based on remaining time
 */
function updateProgressBar() {
    const progressBar = document.getElementById('progress-bar');
    const percent = 1 - timerRemaining / timerDuration;
    // Simple circular progress using conic-gradient
    progressBar.style.background = `conic-gradient(#7f7fd5 ${percent * 360}deg, #e0e0e0 0deg)`;
}

/**
 * Update progress statistics display
 * - Sessions completed
 * - Total focus time
 * Display focus time in minutes/hours
 */
function updateProgressStats() {
    document.getElementById('sessions-completed').textContent = sessionsCompleted;
    // Show focus time in minutes/hours (English)
    let minutes = Math.floor(focusTime / 60);
    let hours = Math.floor(minutes / 60);
    let display = hours > 0 ? `${hours} hr ${minutes % 60} min` : `${minutes} min`;
    document.getElementById('focus-time').textContent = display;
}

/**
 * Save progress to localStorage
 */
function saveProgressToLocalStorage() {
    localStorage.setItem('pomodoro_sessionsCompleted', sessionsCompleted);
    localStorage.setItem('pomodoro_focusTime', focusTime);
}

/**
 * Load progress from localStorage
 */
function loadProgressFromLocalStorage() {
    sessionsCompleted = parseInt(localStorage.getItem('pomodoro_sessionsCompleted')) || 0;
    focusTime = parseInt(localStorage.getItem('pomodoro_focusTime')) || 0;
    updateProgressStats();
}

/**
 * (Optional) Send progress data to backend API
 * - sessionsCompleted
 * - focusTime
 */
function sendProgressToBackend() {
    fetch('/progress', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            sessionsCompleted: sessionsCompleted,
            focusTime: focusTime
        })
    });
}

/**
 * (Optional) Fetch progress data from backend API
 * - Update local state and UI
 */
function fetchProgressFromBackend() {
    fetch('/progress')
        .then(response => response.json())
        .then(data => {
            sessionsCompleted = data.sessionsCompleted || 0;
            focusTime = data.focusTime || 0;
            updateProgressStats();
        });
}

// Optionally call fetchProgressFromBackend in initializeTimer if you want server-side persistence
function handleStartButton() {
    startTimer();
}

// Handle reset button click
function handleResetButton() {
    resetTimer();
}

/**
 * Handle work duration change
 */
function handleWorkDurationChange(event) {
    workDuration = parseInt(event.target.value);
    timerDuration = workDuration * 60;
    resetTimer();
    saveSettingsToLocalStorage();
}

/**
 * Handle break duration change
 */
function handleBreakDurationChange(event) {
    breakDuration = parseInt(event.target.value);
    saveSettingsToLocalStorage();
}

/**
 * Handle theme change
 */
function handleThemeChange(event) {
    currentTheme = event.target.value;
    applyTheme(currentTheme);
    saveSettingsToLocalStorage();
}

/**
 * Handle sound toggle
 */
function handleSoundToggle(event) {
    soundEnabled = event.target.checked;
    saveSettingsToLocalStorage();
}

/**
 * Apply theme to the page
 */
function applyTheme(theme) {
    document.body.classList.remove('light-theme', 'dark-theme', 'focus-theme');
    document.body.classList.add(`${theme}-theme`);
}

/**
 * Save settings to localStorage
 */
function saveSettingsToLocalStorage() {
    localStorage.setItem('pomodoro_workDuration', workDuration);
    localStorage.setItem('pomodoro_breakDuration', breakDuration);
    localStorage.setItem('pomodoro_theme', currentTheme);
    localStorage.setItem('pomodoro_soundEnabled', soundEnabled);
}

/**
 * Load settings from localStorage
 */
function loadSettingsFromLocalStorage() {
    const savedWorkDuration = parseInt(localStorage.getItem('pomodoro_workDuration'));
    const savedBreakDuration = parseInt(localStorage.getItem('pomodoro_breakDuration'));
    
    workDuration = (!isNaN(savedWorkDuration) && savedWorkDuration > 0) ? savedWorkDuration : 25;
    breakDuration = (!isNaN(savedBreakDuration) && savedBreakDuration > 0) ? savedBreakDuration : 5;
    currentTheme = localStorage.getItem('pomodoro_theme') || 'light';
    soundEnabled = localStorage.getItem('pomodoro_soundEnabled') !== 'false';
    
    // Update UI to reflect loaded settings
    document.getElementById('work-duration').value = workDuration;
    document.getElementById('break-duration').value = breakDuration;
    document.getElementById('theme-selector').value = currentTheme;
    document.getElementById('sound-enabled').checked = soundEnabled;
    
    // Apply theme
    applyTheme(currentTheme);
    
    // Update timer duration based on work duration
    timerDuration = workDuration * 60;
    timerRemaining = timerDuration;
}

/**
 * Play sound effect
 */
function playSound(soundType) {
    if (!soundEnabled) return;
    
    // Initialize audio context if not already created
    if (!audioContext) {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    // Different frequencies for different events
    if (soundType === 'start') {
        oscillator.frequency.value = 440; // A4
    } else if (soundType === 'end') {
        oscillator.frequency.value = 880; // A5
    } else if (soundType === 'tick') {
        oscillator.frequency.value = 220; // A3
    }
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.1);
}
