from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
from gamification import GamificationManager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pomodoro_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    """Render the main Pomodoro timer page."""
    return render_template('index.html')


@app.route('/progress', methods=['GET', 'POST'])
def progress():
    """
    Get or update the user's Pomodoro progress.
    On GET: return the number of completed sessions and total focus time.
    On POST: update the number of completed sessions and total focus time.
    """
    if request.method == 'POST':
        data = request.get_json()
        sessions_completed = data.get('sessionsCompleted', 0)
        focus_time = data.get('focusTime', 0)
        # Validate data
        if not isinstance(sessions_completed, int) or not isinstance(focus_time, int):
            return jsonify({'error': 'Invalid data'}), 400
        session['sessions_completed'] = sessions_completed
        session['focus_time'] = focus_time
        return jsonify({'status': 'saved'})
    else:
        sessions_completed = session.get('sessions_completed', 0)
        focus_time = session.get('focus_time', 0)
        return jsonify({
            'sessionsCompleted': sessions_completed,
            'focusTime': focus_time
        })


@app.route('/gamification/complete', methods=['POST'])
def complete_pomodoro():
    """
    Handle Pomodoro completion and update gamification data.
    Awards XP, checks for level ups and achievements.
    """
    data = request.get_json()
    focus_time = data.get('focusTime', 1500)  # Default 25 minutes
    
    # Load gamification manager from session
    gamification_data = session.get('gamification_data', {})
    manager = GamificationManager(gamification_data)
    
    # Process completion
    result = manager.complete_pomodoro(focus_time)
    
    # Save updated data to session
    session['gamification_data'] = manager.to_dict()
    
    return jsonify(result)


@app.route('/gamification/stats', methods=['GET'])
def get_gamification_stats():
    """
    Get current gamification statistics including XP, level, achievements, and streaks.
    """
    gamification_data = session.get('gamification_data', {})
    manager = GamificationManager(gamification_data)
    
    stats = manager.get_stats()
    xp_progress = manager.get_xp_progress()
    
    return jsonify({
        'stats': stats,
        'xp_progress': xp_progress
    })


@app.route('/gamification/charts', methods=['GET'])
def get_chart_data():
    """
    Get chart data for weekly and monthly statistics.
    """
    gamification_data = session.get('gamification_data', {})
    manager = GamificationManager(gamification_data)
    
    weekly_data = manager.get_weekly_chart_data(weeks=4)
    monthly_data = manager.get_monthly_chart_data(months=6)
    
    return jsonify({
        'weekly': weekly_data,
        'monthly': monthly_data
    })


if __name__ == '__main__':
    app.run(debug=True)
