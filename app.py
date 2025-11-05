from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'pomodoro_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress', methods=['GET', 'POST'])
def progress():
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

if __name__ == '__main__':
    app.run(debug=True)
