import os
from flask import Flask, render_template, session, redirect, url_for, request, jsonify
from config import Config
from database.db import init_db
from ml.model import load_or_train_model

# Import Blueprints
from routes.auth import auth_bp
from routes.student import student_bp
from routes.school import school_bp
from routes.courses import courses_bp
from routes.learning import learning_bp
from routes.videos import videos_bp
from routes.facilitator import facilitator_bp
from routes.community import community_bp
from routes.assessment import assessment_bp

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(school_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(videos_bp)
    app.register_blueprint(facilitator_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(assessment_bp)

    # Context processor for templates
    @app.context_processor
    def inject_globals():
        return {
            'current_user': {
                'id': session.get('user_id'),
                'name': session.get('name', 'Guest'),
                'role': session.get('role', 'guest'),
                'student_id': session.get('student_id')
            },
            'demo_mode': Config.DEMO_MODE,
            'mastery_threshold': Config.MASTERY_THRESHOLD
        }

    # -------------------------------------------------------------
    # HTML View Page Routes
    # -------------------------------------------------------------
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/register')
    def register_page():
        return render_template('register.html')

    @app.route('/onboarding')
    def onboarding_page():
        return render_template('onboarding.html')

    @app.route('/dashboard')
    def dashboard_page():
        return render_template('dashboard.html')

    @app.route('/course/<int:course_id>')
    @app.route('/course')
    @app.route('/courses')
    def course_page(course_id=1):
        return render_template('course.html', course_id=course_id)

    @app.route('/assessment')
    def assessment_page():
        return render_template('assessment.html')

    @app.route('/learning')
    def learning_page():
        return render_template('learning.html')

    @app.route('/videos')
    def videos_page():
        return render_template('videos.html')

    @app.route('/history')
    def history_page():
        return render_template('history.html')

    @app.route('/community')
    def community_page():
        return render_template('community.html')

    @app.route('/study-groups')
    def study_groups_page():
        return render_template('study-groups.html')

    @app.route('/projects')
    def projects_page():
        return render_template('projects.html')

    @app.route('/facilitator')
    @app.route('/admin')
    def facilitator_page():
        return render_template('facilitator.html')

    # Error handling
    @app.errorhandler(404)
    def page_not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Endpoint not found', 'status': 404}), 404
        return render_template('index.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error occurred', 'status': 500}), 500
        return render_template('index.html'), 500

    return app

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 ADAPTIVELEARN AI — Starting Adaptive Learning Platform")
    print("“One platform. Shared knowledge. Personalized learning. Connected learners.”")
    print("=" * 70)

    # 1. Initialize DB and load schema / seeds
    init_db()

    # 2. Pre-load / train scikit-learn ML model
    print("[*] Checking Machine Learning engine...")
    load_or_train_model()

    app = create_app()
    print(f"[+] Server starting on http://127.0.0.1:{Config.PORT}")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
