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

/**
 * Initialize the timer and UI elements
 * - Set up event listeners
 * - Load progress from localStorage
 * - Update UI displays
 */
function initializeTimer() {
    updateTimerDisplay();
    updateProgressBar();
    loadProgressFromLocalStorage();
    document.getElementById('start-btn').addEventListener('click', handleStartButton);
    document.getElementById('reset-btn').addEventListener('click', handleResetButton);
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
    timerInterval = setInterval(() => {
        if (timerRemaining > 0) {
            timerRemaining--;
            updateTimerDisplay();
            updateProgressBar();
        } else {
            clearInterval(timerInterval);
            isRunning = false;
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
