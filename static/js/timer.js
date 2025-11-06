// timer.js: Pomodoro timer with gamification features

/**
 * Pomodoro Timer Logic with Gamification
 * - Start, pause, reset timer
 * - Update timer display
 * - Track progress (sessions completed, focus time)
 * - XP and level system
 * - Achievements and streaks
 * - Statistics and charts
 */
document.addEventListener('DOMContentLoaded', function() {
    initializeTimer();
    loadGamificationStats();
    setupStatsTabs();
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
    document.getElementById('close-modal-btn').addEventListener('click', closeLevelUpModal);
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
            
            // Call gamification API
            handlePomodoroCompletion();
            
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
 * Gamification Functions
 */

/**
 * Handle Pomodoro completion - call gamification API
 */
async function handlePomodoroCompletion() {
    try {
        const response = await fetch('/gamification/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                focusTime: timerDuration
            })
        });
        
        const result = await response.json();
        
        // Update gamification UI
        if (result.leveled_up) {
            showLevelUpModal(result.level);
        }
        
        if (result.new_achievements && result.new_achievements.length > 0) {
            result.new_achievements.forEach(achievement => {
                showAchievementNotification(achievement);
            });
        }
        
        // Reload gamification stats
        loadGamificationStats();
        
    } catch (error) {
        console.error('Error handling Pomodoro completion:', error);
    }
}

/**
 * Load and display gamification statistics
 */
async function loadGamificationStats() {
    try {
        const response = await fetch('/gamification/stats');
        const data = await response.json();
        
        const stats = data.stats;
        const xpProgress = data.xp_progress;
        
        // Update level display
        document.getElementById('level-display').textContent = `Level ${stats.level}`;
        
        // Update streak display
        const streakText = stats.current_streak === 1 ? 'day' : 'days';
        document.getElementById('streak-display').textContent = `🔥 ${stats.current_streak} ${streakText} streak`;
        
        // Update XP bar
        const xpBar = document.getElementById('xp-bar');
        xpBar.style.width = `${xpProgress.progress_percentage}%`;
        
        // Update XP text
        if (xpProgress.max_level) {
            document.getElementById('xp-text').textContent = `Max Level! ${xpProgress.current_xp} XP`;
        } else {
            document.getElementById('xp-text').textContent = 
                `${xpProgress.xp_progress} / ${xpProgress.xp_needed} XP to Level ${xpProgress.next_level}`;
        }
        
        // Update achievements
        updateAchievementsDisplay(stats.achievements, stats.available_achievements);
        
        // Update charts
        loadChartData();
        
    } catch (error) {
        console.error('Error loading gamification stats:', error);
    }
}

/**
 * Update achievements display
 */
function updateAchievementsDisplay(unlockedAchievements, availableAchievements) {
    const container = document.getElementById('achievements-container');
    
    // Clear loading text
    container.innerHTML = '';
    
    // Show unlocked achievements first
    unlockedAchievements.forEach(achievement => {
        const badge = createAchievementBadge(achievement, true);
        container.appendChild(badge);
    });
    
    // Show locked achievements
    availableAchievements.slice(0, 3).forEach(achievement => {
        const badge = createAchievementBadge(achievement, false);
        container.appendChild(badge);
    });
    
    // If no achievements at all, show message
    if (unlockedAchievements.length === 0 && availableAchievements.length === 0) {
        container.innerHTML = '<p class="loading-text">Complete your first Pomodoro to unlock achievements!</p>';
    }
}

/**
 * Create achievement badge element
 */
function createAchievementBadge(achievement, unlocked) {
    const badge = document.createElement('div');
    badge.className = `achievement-badge ${unlocked ? 'unlocked' : 'locked'}`;
    
    const icon = unlocked ? '🏆' : '🔒';
    
    badge.innerHTML = `
        <div class="achievement-icon">${icon}</div>
        <div class="achievement-name">${achievement.name}</div>
        <div class="achievement-description">${achievement.description}</div>
    `;
    
    return badge;
}

/**
 * Show level up modal
 */
function showLevelUpModal(level) {
    const modal = document.getElementById('level-up-modal');
    const text = document.getElementById('level-up-text');
    text.textContent = `You've reached Level ${level}!`;
    modal.classList.add('show');
}

/**
 * Close level up modal
 */
function closeLevelUpModal() {
    const modal = document.getElementById('level-up-modal');
    modal.classList.remove('show');
}

/**
 * Show achievement notification
 */
function showAchievementNotification(achievement) {
    const notification = document.getElementById('achievement-notification');
    const title = notification.querySelector('.notification-title');
    const description = notification.querySelector('.notification-description');
    
    title.textContent = achievement.name;
    description.textContent = achievement.description;
    
    notification.classList.add('show');
    
    // Auto-hide after 4 seconds
    setTimeout(() => {
        notification.classList.remove('show');
    }, 4000);
}

/**
 * Load and display chart data
 */
async function loadChartData() {
    try {
        const response = await fetch('/gamification/charts');
        const data = await response.json();
        
        // Render weekly chart
        renderChart('weekly-canvas', data.weekly, 'Weekly Sessions');
        
        // Render monthly chart
        renderChart('monthly-canvas', data.monthly, 'Monthly Sessions');
        
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

/**
 * Render a simple bar chart on canvas
 */
function renderChart(canvasId, data, title) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');
    
    // Set canvas size
    canvas.width = canvas.offsetWidth;
    canvas.height = canvas.offsetHeight;
    
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    if (data.length === 0) {
        // No data to display
        ctx.fillStyle = '#999';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data yet', width / 2, height / 2);
        return;
    }
    
    // Calculate max value for scaling
    const maxValue = Math.max(...data.map(d => d.value), 1);
    
    // Chart dimensions
    const padding = 40;
    const chartHeight = height - padding * 2;
    const chartWidth = width - padding * 2;
    const barWidth = chartWidth / data.length - 10;
    
    // Draw bars
    data.forEach((item, index) => {
        const barHeight = (item.value / maxValue) * chartHeight;
        const x = padding + index * (chartWidth / data.length) + 5;
        const y = height - padding - barHeight;
        
        // Draw bar
        ctx.fillStyle = '#7f7fd5';
        ctx.fillRect(x, y, barWidth, barHeight);
        
        // Draw value on top
        ctx.fillStyle = '#333';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(item.value, x + barWidth / 2, y - 5);
        
        // Draw label
        ctx.fillStyle = '#666';
        ctx.font = '10px Arial';
        ctx.save();
        ctx.translate(x + barWidth / 2, height - padding + 15);
        ctx.rotate(-Math.PI / 4);
        ctx.textAlign = 'right';
        ctx.fillText(item.label, 0, 0);
        ctx.restore();
    });
}

/**
 * Setup statistics tabs
 */
function setupStatsTabs() {
    const tabs = document.querySelectorAll('.stat-tab');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            tabs.forEach(t => t.classList.remove('active'));
            
            // Add active class to clicked tab
            tab.classList.add('active');
            
            // Show corresponding chart
            const tabType = tab.getAttribute('data-tab');
            
            document.getElementById('weekly-chart').style.display = 
                tabType === 'weekly' ? 'block' : 'none';
            document.getElementById('monthly-chart').style.display = 
                tabType === 'monthly' ? 'block' : 'none';
        });
    });
}
