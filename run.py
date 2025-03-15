from app import create_app
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler

app = create_app()
CORS(app, supports_credentials=True)
scheduler = BackgroundScheduler(daemon=True)
scheduler.start()

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)
