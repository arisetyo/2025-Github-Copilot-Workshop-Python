"""
End-to-end Playwright tests for the Pomodoro Timer application.
Tests loading the app, starting a timer, and verifying successful session completion.
"""
import pytest
import subprocess
import time
import signal
import os
from playwright.sync_api import Page, expect


@pytest.fixture(scope="module")
def flask_app():
    """Start the Flask app before tests and stop it after."""
    # Start Flask app in a subprocess
    env = os.environ.copy()
    env['FLASK_ENV'] = 'testing'
    process = subprocess.Popen(
        ['python', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(os.path.dirname(__file__)),
        env=env
    )
    
    # Wait for the server to start (give it a few seconds)
    time.sleep(3)
    
    yield process
    
    # Cleanup: stop the Flask app
    process.send_signal(signal.SIGTERM)
    process.wait(timeout=5)


def test_app_loads(page: Page, flask_app):
    """Test that the Pomodoro timer app loads successfully."""
    page.goto("http://localhost:5000")
    
    # Verify page title
    expect(page).to_have_title("Pomodoro Timer")
    
    # Verify main heading
    heading = page.locator("h1")
    expect(heading).to_have_text("Pomodoro Timer")
    
    # Verify timer display is visible
    timer_display = page.locator("#timer-display")
    expect(timer_display).to_be_visible()
    expect(timer_display).to_have_text("25:00")
    
    # Verify buttons are visible
    start_button = page.locator("#start-btn")
    reset_button = page.locator("#reset-btn")
    expect(start_button).to_be_visible()
    expect(reset_button).to_be_visible()


def test_timer_starts_and_counts_down(page: Page, flask_app):
    """Test that the timer starts and counts down when the start button is clicked."""
    page.goto("http://localhost:5000")
    
    # Get initial timer value
    timer_display = page.locator("#timer-display")
    initial_time = timer_display.text_content()
    assert initial_time == "25:00"
    
    # Click start button
    start_button = page.locator("#start-btn")
    start_button.click()
    
    # Wait for timer to count down
    page.wait_for_timeout(2000)  # Wait 2 seconds
    
    # Verify timer has changed
    current_time = timer_display.text_content()
    assert current_time != "25:00"
    assert current_time in ["24:59", "24:58"]  # Account for timing


def test_timer_reset(page: Page, flask_app):
    """Test that the reset button resets the timer to 25:00."""
    page.goto("http://localhost:5000")
    
    # Start the timer
    start_button = page.locator("#start-btn")
    start_button.click()
    
    # Wait for timer to count down
    page.wait_for_timeout(2000)
    
    # Click reset button
    reset_button = page.locator("#reset-btn")
    reset_button.click()
    
    # Verify timer is reset
    timer_display = page.locator("#timer-display")
    expect(timer_display).to_have_text("25:00")


def test_successful_session_completion(page: Page, flask_app):
    """Test that a complete Pomodoro session increments the session counter."""
    page.goto("http://localhost:5000")
    
    # Get initial session count
    sessions_completed = page.locator("#sessions-completed")
    initial_count = int(sessions_completed.text_content())
    
    # Override the timer duration to 3 seconds for faster testing
    page.evaluate("""
        timerDuration = 3;
        timerRemaining = 3;
        updateTimerDisplay();
    """)
    
    # Verify timer shows 00:03
    timer_display = page.locator("#timer-display")
    expect(timer_display).to_have_text("00:03")
    
    # Start the timer
    start_button = page.locator("#start-btn")
    start_button.click()
    
    # Wait for the timer to complete (3 seconds + buffer)
    page.wait_for_timeout(4000)
    
    # Verify session counter has incremented
    final_count = int(sessions_completed.text_content())
    assert final_count == initial_count + 1
    
    # Verify focus time has been updated
    focus_time = page.locator("#focus-time")
    focus_time_text = focus_time.text_content()
    assert "min" in focus_time_text
    
    # Verify timer has reset to initial duration
    timer_display_after = page.locator("#timer-display")
    expect(timer_display_after).to_have_text("00:03")


def test_progress_persists_in_local_storage(page: Page, flask_app):
    """Test that progress is saved to localStorage and persists across page reloads."""
    page.goto("http://localhost:5000")
    
    # Set a test session with specific values
    page.evaluate("""
        sessionsCompleted = 5;
        focusTime = 7500; // 125 minutes
        updateProgressStats();
        saveProgressToLocalStorage();
    """)
    
    # Verify the values are displayed
    sessions_completed = page.locator("#sessions-completed")
    expect(sessions_completed).to_have_text("5")
    
    focus_time = page.locator("#focus-time")
    focus_time_text = focus_time.text_content()
    assert "hr" in focus_time_text or "min" in focus_time_text
    
    # Reload the page
    page.reload()
    
    # Verify the values persist after reload
    expect(sessions_completed).to_have_text("5")
    
    # Clean up localStorage
    page.evaluate("""
        localStorage.removeItem('pomodoro_sessionsCompleted');
        localStorage.removeItem('pomodoro_focusTime');
    """)


def test_progress_bar_updates(page: Page, flask_app):
    """Test that the circular progress bar updates as the timer counts down."""
    page.goto("http://localhost:5000")
    
    # Override the timer duration for faster testing
    page.evaluate("""
        timerDuration = 5;
        timerRemaining = 5;
        updateTimerDisplay();
        updateProgressBar();
    """)
    
    # Get initial progress bar state
    progress_bar = page.locator("#progress-bar")
    initial_background = progress_bar.evaluate("el => getComputedStyle(el).background")
    
    # Start the timer
    start_button = page.locator("#start-btn")
    start_button.click()
    
    # Wait for timer to count down
    page.wait_for_timeout(2000)
    
    # Get updated progress bar state
    updated_background = progress_bar.evaluate("el => getComputedStyle(el).background")
    
    # Verify progress bar has changed
    assert initial_background != updated_background
