from flask import Blueprint, request, jsonify, session
from models.student import Student
from models.course import Course
from models.mastery import Mastery
from models.video import Video
from adaptive.engine import AdaptiveEngine
from adaptive.knowledge_graph import KnowledgeGraph
from services.youtube_service import YouTubeService
from ai.recommendations import generate_student_recommendation
from database.db import query_db, execute_db

student_bp = Blueprint('student', __name__, url_prefix='/api')

def get_current_student_id():
    student_id = session.get('student_id')
    if not student_id:
        user_id = session.get('user_id', 1)
        stu = Student.get_by_user_id(user_id)
        if stu:
            student_id = stu['id']
            session['student_id'] = student_id
        else:
            student_id = 1
    return student_id

@student_bp.route('/onboarding', methods=['POST'])
def complete_onboarding():
    data = request.get_json() or {}
    student_id = get_current_student_id()

    school_id = data.get('school_id', 1)
    grade_id = data.get('grade_id', 3)
    stream_id = data.get('stream_id', 1)
    course_id = data.get('course_id', 1)
    interests = data.get('interests', ['Space', 'Technology'])
    goals = data.get('primary_goal', 'Master fundamentals and complete course')
    learning_style = data.get('preferred_learning_style', 'Visual & Guided Practice')
    skill_level = data.get('current_skill_level', 'Intermediate')

    # Update student profile
    execute_db("""
        UPDATE students
        SET school_id = %s, grade_id = %s, stream_id = %s, primary_goal = %s,
            preferred_learning_style = %s, current_skill_level = %s,
            diagnostic_completed = TRUE
        WHERE id = %s
    """, (school_id, grade_id, stream_id, goals, learning_style, skill_level, student_id))

    # Set interests
    if isinstance(interests, list):
        Student.set_interests(student_id, interests)

    # Enroll in selected course
    Student.enroll_in_course(student_id, course_id)

    return jsonify({
        'message': 'Onboarding completed successfully',
        'student_id': student_id,
        'course_id': course_id
    }), 200

@student_bp.route('/student/profile', methods=['GET'])
def get_profile():
    student_id = get_current_student_id()
    profile = Student.get_by_id(student_id)
    interests = Student.get_interests(student_id)
    courses = Student.get_enrolled_courses(student_id)
    return jsonify({
        'profile': profile,
        'interests': interests,
        'courses': courses
    }), 200

@student_bp.route('/student/courses', methods=['GET'])
def get_student_courses():
    student_id = get_current_student_id()
    courses = Student.get_enrolled_courses(student_id)
    return jsonify(courses), 200

@student_bp.route('/student/dashboard', methods=['GET'])
def get_dashboard():
    student_id = get_current_student_id()
    course_id = request.args.get('course_id', type=int)

    profile = Student.get_by_id(student_id)
    if not profile:
        profile = {'name': 'Student', 'overall_mastery': 50.0, 'learning_streak': 3}

    enrolled_courses = Student.get_enrolled_courses(student_id)
    if not course_id:
        course_id = enrolled_courses[0]['id'] if enrolled_courses else 1

    current_course = Course.get_by_id(course_id) or {'id': 1, 'name': 'Mathematics'}

    # 1. Adaptive Engine Next Best Activity
    adaptive_plan = AdaptiveEngine.compute_next_best_activity(student_id, course_id)

    # 2. Knowledge Graph
    knowledge_graph = KnowledgeGraph.get_graph_data(student_id, course_id)

    # 3. YouTube Recommendations
    recommended_playlists = YouTubeService.get_recommended_playlists_for_student(student_id, course_id, limit=3)

    # 4. Continue Watching
    continue_watching = Video.get_continue_watching(student_id, limit=3)

    # 5. AI Personalized Recommendation Narrative
    current_concept_name = adaptive_plan['concept']['name'] if adaptive_plan and adaptive_plan.get('concept') else 'General Concepts'
    current_mastery = float(adaptive_plan['concept'].get('mastery_percentage', adaptive_plan['concept'].get('mastery', 50.0))) if adaptive_plan and adaptive_plan.get('concept') else 50.0
    ml_state = adaptive_plan['ml_learning_state'] if adaptive_plan else 'Stable'
    primary_interest = adaptive_plan['student_interest'] if adaptive_plan else 'Space'

    ai_coaching = generate_student_recommendation(
        profile.get('name', 'Student'),
        current_course.get('name', 'Course'),
        current_concept_name,
        current_mastery,
        ml_state,
        primary_interest
    )

    # 6. Today's Adaptive Path (step sequence)
    rec_res_title = (adaptive_plan.get('recommended_resource') or {}).get('title', 'Concept Tutorial') if adaptive_plan else 'Concept Tutorial'
    practice_qty = (adaptive_plan.get('activity') or {}).get('practice_quantity', 3) if adaptive_plan else 3
    adaptive_path = [
        {"step": 1, "title": f"Review {current_concept_name} Key Principles", "type": "review", "completed": current_mastery >= 40.0},
        {"step": 2, "title": f"Watch {rec_res_title}", "type": "video", "completed": len(continue_watching) > 0 and continue_watching[0].get('completed') == 1},
        {"step": 3, "title": f"Guided {primary_interest}-Themed Practice ({practice_qty} Problems)", "type": "practice", "completed": False},
        {"step": 4, "title": "Mini-Assessment & Mastery Gating Evaluation", "type": "assessment", "completed": False}
    ]

    # 7. Video Analytics Summary for Chart.js
    analytics = Video.get_analytics(student_id)

    return jsonify({
        'student': profile,
        'current_course': current_course,
        'enrolled_courses': enrolled_courses,
        'adaptive_plan': adaptive_plan,
        'knowledge_graph': knowledge_graph,
        'recommended_playlists': recommended_playlists,
        'continue_watching': continue_watching,
        'ai_coaching': ai_coaching,
        'ai_coaching_narrative': ai_coaching,
        'adaptive_path': adaptive_path,
        'analytics': analytics
    }), 200
