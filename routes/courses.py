from flask import Blueprint, request, jsonify, session
from models.course import Course
from models.student import Student
from models.concept import Concept
from models.mastery import Mastery
from models.video import Video
from adaptive.engine import AdaptiveEngine
from adaptive.knowledge_graph import KnowledgeGraph
from services.youtube_service import YouTubeService
from models.community import Community

courses_bp = Blueprint('courses', __name__, url_prefix='/api')

def get_student_id():
    student_id = session.get('student_id')
    if not student_id:
        user_id = session.get('user_id', 1)
        stu = Student.get_by_user_id(user_id)
        student_id = stu['id'] if stu else 1
    return student_id

@courses_bp.route('/courses', methods=['GET'])
def list_courses():
    courses = Course.get_all()
    return jsonify(courses), 200

@courses_bp.route('/courses/<int:course_id>', methods=['GET'])
def get_course_detail(course_id):
    student_id = get_student_id()
    course = Course.get_by_id(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    # Knowledge Graph
    graph_data = KnowledgeGraph.get_graph_data(student_id, course_id)

    # Adaptive plan
    adaptive_plan = AdaptiveEngine.compute_next_best_activity(student_id, course_id)

    # Course concepts
    concepts = Concept.get_by_course(course_id)

    # Recommended YouTube Playlists
    playlists = YouTubeService.get_recommended_playlists_for_student(student_id, course_id, limit=3)

    # Viewed history for this course
    view_history = Video.get_viewed_history(student_id, course_id=course_id, limit=5)

    # Course communities
    communities = Community.get_all(course_id=course_id)

    return jsonify({
        'course': course,
        'knowledge_graph': graph_data,
        'adaptive_plan': adaptive_plan,
        'concepts': concepts,
        'recommended_playlists': playlists,
        'view_history': view_history,
        'communities': communities
    }), 200

@courses_bp.route('/concepts/graph', methods=['GET'])
def get_concept_graph():
    student_id = get_student_id()
    course_id = request.args.get('course_id', 1, type=int)
    graph = KnowledgeGraph.get_graph_data(student_id, course_id)
    return jsonify(graph), 200

@courses_bp.route('/mastery', methods=['GET'])
def get_mastery():
    student_id = get_student_id()
    course_id = request.args.get('course_id', 1, type=int)
    mastery = Mastery.get_student_mastery_for_course(student_id, course_id)
    return jsonify(mastery), 200
