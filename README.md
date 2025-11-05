# README

## About

We are using this repository for Github Copilot workshop 2025.

## History

This repo was forked from: [2025-Github-Copilot-Workshop-Python](https://github.com/moulongzhang/2025-Github-Copilot-Workshop-Python)

That repo is for the workshop material below:
ワークショップの手順：https://moulongzhang.github.io/2025-Github-Copilot-Workshop/github-copilot-workshop/#0

## How to Use the Pomodoro Timer App

### Installation (Recommended: venv + uv)

1. **Create a virtual environment:**
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Install uv (fast Python package manager):**
   ```sh
   pip install uv
   ```
3. **Install dependencies with uv:**
   ```sh
   uv pip install flask flask-session pytest
   ```

### Running the App

1. **Activate your virtual environment (if not already):**
   ```sh
   source .venv/bin/activate
   ```
2. **Start the Flask server:**
   ```sh
   python app.py
   ```
3. **Open your browser and go to:**
   [http://localhost:5000](http://localhost:5000)

### Features
- Start and reset a 25-minute Pomodoro timer
- Animated circular progress bar
- Track sessions completed and total focus time
- Progress is saved in your browser (localStorage) and can be optionally synced to the server

### Testing
Run backend tests with:
```sh
pytest tests/test_timer.py
```

### File Structure
- `app.py`: Flask backend
- `templates/index.html`: Main UI
- `static/css/style.css`: Stylesheet
- `static/js/timer.js`: Timer logic
- `tests/test_timer.py`: Backend tests

### Customization
- Change timer duration in `static/js/timer.js` (`timerDuration`)
- Extend backend for user authentication or analytics as needed

---

Enjoy your productive Pomodoro sessions!
