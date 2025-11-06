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

// Particles system state
let particles = [];
let canvas, ctx;
const maxParticles = 50;

// Progress bar constants
const PROGRESS_RADIUS = 90;
const PROGRESS_CIRCUMFERENCE = 2 * Math.PI * PROGRESS_RADIUS;

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
    initializeParticles();
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
    document.querySelector('.container').classList.add('focus-mode');
    startParticleAnimation();
    
    timerInterval = setInterval(() => {
        if (timerRemaining > 0) {
            timerRemaining--;
            updateTimerDisplay();
            updateProgressBar();
        } else {
            clearInterval(timerInterval);
            isRunning = false;
            document.querySelector('.container').classList.remove('focus-mode');
            stopParticleAnimation();
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
    document.querySelector('.container').classList.remove('focus-mode');
    stopParticleAnimation();
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
 * Also update color gradient: blue → yellow → red
 */
function updateProgressBar() {
    const progressBar = document.querySelector('.progress-fill');
    const percent = timerRemaining / timerDuration;
    const offset = PROGRESS_CIRCUMFERENCE * (1 - percent);
    
    progressBar.style.strokeDashoffset = offset;
    
    // Color gradient transition based on time remaining
    let color;
    if (percent > 0.66) {
        // Blue phase (100% - 66%)
        color = '#4a90e2';
    } else if (percent > 0.33) {
        // Yellow phase (66% - 33%)
        const yellowProgress = (percent - 0.33) / 0.33;
        color = interpolateColor('#4a90e2', '#f5a623', 1 - yellowProgress);
    } else {
        // Red phase (33% - 0%)
        const redProgress = percent / 0.33;
        color = interpolateColor('#f5a623', '#e74c3c', 1 - redProgress);
    }
    
    progressBar.style.stroke = color;
}

/**
 * Interpolate between two hex colors
 */
function interpolateColor(color1, color2, factor) {
    const c1 = hexToRgb(color1);
    const c2 = hexToRgb(color2);
    
    const r = Math.round(c1.r + factor * (c2.r - c1.r));
    const g = Math.round(c1.g + factor * (c2.g - c1.g));
    const b = Math.round(c1.b + factor * (c2.b - c1.b));
    
    return rgbToHex(r, g, b);
}

/**
 * Convert hex color to RGB
 */
function hexToRgb(hex) {
    const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
    return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
    } : null;
}

/**
 * Convert RGB to hex color
 */
function rgbToHex(r, g, b) {
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
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
 * Initialize particle system
 */
function initializeParticles() {
    canvas = document.getElementById('particles-canvas');
    ctx = canvas.getContext('2d');
    
    // Set canvas size accounting for device pixel ratio for crisp rendering
    const dpr = window.devicePixelRatio || 1;
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    canvas.style.width = window.innerWidth + 'px';
    canvas.style.height = window.innerHeight + 'px';
    ctx.scale(dpr, dpr);
    
    // Resize canvas on window resize
    window.addEventListener('resize', () => {
        const dpr = window.devicePixelRatio || 1;
        canvas.width = window.innerWidth * dpr;
        canvas.height = window.innerHeight * dpr;
        canvas.style.width = window.innerWidth + 'px';
        canvas.style.height = window.innerHeight + 'px';
        ctx.scale(dpr, dpr);
    });
}

/**
 * Particle class for animation
 */
class Particle {
    constructor() {
        this.x = Math.random() * window.innerWidth;
        this.y = Math.random() * window.innerHeight;
        this.vx = (Math.random() - 0.5) * 0.5;
        this.vy = (Math.random() - 0.5) * 0.5;
        this.radius = Math.random() * 2 + 1;
        this.opacity = Math.random() * 0.5 + 0.2;
    }
    
    update() {
        this.x += this.vx;
        this.y += this.vy;
        
        // Wrap around edges
        if (this.x < 0) this.x = window.innerWidth;
        if (this.x > window.innerWidth) this.x = 0;
        if (this.y < 0) this.y = window.innerHeight;
        if (this.y > window.innerHeight) this.y = 0;
    }
    
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
        ctx.fill();
    }
}

/**
 * Start particle animation
 */
function startParticleAnimation() {
    // Create particles
    particles = [];
    for (let i = 0; i < maxParticles; i++) {
        particles.push(new Particle());
    }
    
    animateParticles();
}

/**
 * Stop particle animation
 */
function stopParticleAnimation() {
    particles = [];
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
}

/**
 * Animate particles
 */
function animateParticles() {
    if (particles.length === 0) return;
    
    ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
    
    particles.forEach(particle => {
        particle.update();
        particle.draw();
    });
    
    requestAnimationFrame(animateParticles);
}
