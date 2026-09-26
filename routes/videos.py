from flask import Blueprint, request, jsonify, session
from models.video import Video
from models.student import Student
from services.youtube_service import YouTubeService
from database.db import query_db

videos_bp = Blueprint('videos', __name__, url_prefix='/api')

def get_student_id():
    student_id = session.get('student_id')
    if not student_id:
        user_id = session.get('user_id', 1)
        stu = Student.get_by_user_id(user_id)
        student_id = stu['id'] if stu else 1
    return student_id

@videos_bp.route('/youtube/playlists', methods=['GET'])
def get_playlists():
    course_id = request.args.get('course_id', type=int)
    if course_id:
        playlists = Video.get_playlists_by_course(course_id)
    else:
        playlists = query_db("SELECT * FROM youtube_playlists ORDER BY id ASC")
    return jsonify(playlists), 200

@videos_bp.route('/youtube/playlists/<int:playlist_id>', methods=['GET'])
def get_playlist_detail(playlist_id):
    playlist = Video.get_playlist_by_id(playlist_id)
    if not playlist:
        return jsonify({'error': 'Playlist not found'}), 404
    videos = Video.get_playlist_videos(playlist_id)
    return jsonify({
        'playlist': playlist,
        'videos': videos
    }), 200

@videos_bp.route('/youtube/videos/<int:video_id>', methods=['GET'])
def get_video_detail(video_id):
    video = Video.get_video_by_id(video_id)
    if not video:
        return jsonify({'error': 'Video not found'}), 404
    return jsonify(video), 200

@videos_bp.route('/youtube/search', methods=['POST'])
def search_youtube():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    course_id = data.get('course_id')
    if not query:
        return jsonify({'error': 'Search query required'}), 400
    results = YouTubeService.search_playlists(query, course_id)
    return jsonify(results), 200

@videos_bp.route('/student/recommended-playlists', methods=['GET'])
def get_recommended():
    student_id = get_student_id()
    course_id = request.args.get('course_id', 1, type=int)
    playlists = YouTubeService.get_recommended_playlists_for_student(student_id, course_id)
    return jsonify(playlists), 200

@videos_bp.route('/student/viewed-history', methods=['GET'])
def get_viewed_history():
    student_id = get_student_id()
    course_id = request.args.get('course_id', type=int)
    status_filter = request.args.get('status')
    completed_only = True if status_filter == 'completed' else (False if status_filter == 'in_progress' else None)

    history = Video.get_viewed_history(student_id, course_id, completed_only)
    return jsonify(history), 200

@videos_bp.route('/student/recent-videos', methods=['GET'])
def get_recent_videos():
    student_id = get_student_id()
    history = Video.get_viewed_history(student_id, limit=5)
    return jsonify(history), 200

@videos_bp.route('/student/continue-watching', methods=['GET'])
def get_continue_watching():
    student_id = get_student_id()
    cw = Video.get_continue_watching(student_id)
    return jsonify(cw), 200

@videos_bp.route('/youtube/video/start', methods=['POST'])
def video_start():
    data = request.get_json() or {}
    student_id = get_student_id()
    video_id = data.get('video_id', 1)
    playlist_id = data.get('playlist_id', 1)
    course_id = data.get('course_id', 1)
    concept_id = data.get('concept_id', 3)

    hist_id = Video.record_view_start(student_id, video_id, playlist_id, course_id, concept_id)
    return jsonify({'message': 'Video playback started', 'history_id': hist_id}), 200

@videos_bp.route('/youtube/video/progress', methods=['POST'])
def video_progress():
    data = request.get_json() or {}
    student_id = get_student_id()
    video_id = data.get('video_id', 1)
    playlist_id = data.get('playlist_id')
    course_id = data.get('course_id', 1)
    concept_id = data.get('concept_id')
    progress_pct = float(data.get('progress_percentage', 50.0))
    watch_time_sec = int(data.get('watch_time_seconds', 0))
    completed = data.get('completed', False) or (progress_pct >= 95.0)

    Video.update_view_progress(student_id, video_id, playlist_id, course_id, concept_id, progress_pct, watch_time_sec, completed)
    return jsonify({'message': 'Progress recorded', 'progress_percentage': progress_pct, 'completed': completed}), 200

@videos_bp.route('/youtube/video/complete', methods=['POST'])
def video_complete():
    data = request.get_json() or {}
    student_id = get_student_id()
    video_id = data.get('video_id', 1)
    playlist_id = data.get('playlist_id')
    course_id = data.get('course_id', 1)
    concept_id = data.get('concept_id')
    watch_time_sec = int(data.get('watch_time_seconds', 600))

    Video.update_view_progress(student_id, video_id, playlist_id, course_id, concept_id, 100.0, watch_time_sec, completed=True)
    return jsonify({
        'message': 'Video marked completed in viewed history',
        'note': 'Demonstrated academic mastery still requires practice and assessment score verification.'
    }), 200

@videos_bp.route('/youtube/analytics', methods=['GET'])
def get_video_analytics():
    student_id = get_student_id()
    analytics = Video.get_analytics(student_id)
    return jsonify(analytics), 200
