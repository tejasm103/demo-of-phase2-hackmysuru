from flask import Blueprint, request, jsonify, session
from models.student import Student
from models.mastery import Mastery
from models.intervention import Intervention
from models.course import Course
from ml.predictor import predict_learning_state
from ai.intervention import generate_intervention_strategy
from database.db import query_db, execute_db

facilitator_bp = Blueprint('facilitator', __name__, url_prefix='/api')

@facilitator_bp.route('/facilitator/students', methods=['GET'])
def get_students():
    students = Student.get_all()
    # Annotate with ML prediction state
    for s in students:
        pred = predict_learning_state(s['id'])
        s['ml_state'] = pred['predicted_state']
        s['ml_confidence'] = pred['confidence']
    return jsonify(students), 200

@facilitator_bp.route('/facilitator/student/<int:student_id>', methods=['GET'])
def get_student_detail(student_id):
    student = Student.get_by_id(student_id)
    if not student:
        return jsonify({'error': 'Student not found'}), 404

    interests = Student.get_interests(student_id)
    courses = Student.get_enrolled_courses(student_id)
    
    # Get mastery for primary enrolled course
    primary_course_id = courses[0]['id'] if courses else 1
    mastery = Mastery.get_student_mastery_for_course(student_id, primary_course_id)
    ml_pred = predict_learning_state(student_id)
    
    # Recent attempts
    attempts = query_db("""
        SELECT qa.*, q.narrative_context, c.name as concept_name
        FROM question_attempts qa
        JOIN questions q ON qa.question_id = q.id
        JOIN concepts c ON qa.concept_id = c.id
        WHERE qa.student_id = %s
        ORDER BY qa.created_at DESC LIMIT 10
    """, (student_id,))

    # Video history
    video_history = query_db("""
        SELECT vh.*, v.title as video_title, c.name as course_name
        FROM video_view_history vh
        JOIN youtube_videos v ON vh.video_id = v.id
        JOIN courses c ON vh.course_id = c.id
        WHERE vh.student_id = %s
        ORDER BY vh.last_watched_at DESC LIMIT 6
    """, (student_id,))

    return jsonify({
        'student': student,
        'interests': interests,
        'courses': courses,
        'mastery': mastery,
        'ml_prediction': ml_pred,
        'recent_attempts': attempts,
        'video_history': video_history
    }), 200

@facilitator_bp.route('/interventions', methods=['GET'])
def list_interventions():
    interventions = Intervention.get_needs_attention_list()
    stats = Intervention.get_facilitator_stats()
    return jsonify({
        'stats': stats,
        'interventions': interventions
    }), 200

@facilitator_bp.route('/interventions/assign', methods=['POST'])
def assign_intervention():
    data = request.get_json() or {}
    student_id = data.get('student_id')
    concept_id = data.get('concept_id', 3)
    action_type = data.get('action_type', 'assign_playlist')
    action_notes = data.get('notes', 'Facilitator intervention assigned')
    facilitator_id = session.get('user_id', 1)

    stu = Student.get_by_id(student_id)
    student_name = stu['name'] if stu else 'Student'

    # Generate strategy with AI
    strategy = generate_intervention_strategy(
        student_name=student_name,
        course_name="Mathematics",
        concept_name="Statistics & Distributions",
        mastery=43.0,
        evidence_data="Low assessment (42%), 3 consecutive errors, declining trend",
        ml_state="Needs Support"
    )

    iid = Intervention.create_intervention(
        student_id=student_id,
        concept_id=concept_id,
        evidence_text=action_notes,
        ml_state="Needs Support",
        recommendation=strategy,
        action_type=action_type,
        facilitator_id=facilitator_id
    )

    Intervention.log_action(
        facilitator_id=facilitator_id,
        student_id=student_id,
        action_name=f"Assigned {action_type}",
        details=action_notes,
        intervention_id=iid
    )

    return jsonify({
        'message': 'Intervention successfully assigned and dispatched to student learning loop',
        'intervention_id': iid,
        'strategy': strategy
    }), 201

@facilitator_bp.route('/interventions/<int:intervention_id>/resolve', methods=['POST'])
def resolve_intervention(intervention_id):
    Intervention.update_status(intervention_id, 'resolved')
    return jsonify({'message': 'Intervention marked resolved'}), 200
