from flask import Blueprint, request, jsonify, session
from models.student import Student
from models.mastery import Mastery
from models.course import Course
from adaptive.engine import AdaptiveEngine
from ai.retheme import retheme_question
from ai.tutor import explain_concept
from ai.community import assist_community_discussion
from ml.predictor import predict_learning_state

learning_bp = Blueprint('learning', __name__, url_prefix='/api')

def get_student_id():
    student_id = session.get('student_id')
    if not student_id:
        user_id = session.get('user_id', 1)
        stu = Student.get_by_user_id(user_id)
        student_id = stu['id'] if stu else 1
    return student_id

@learning_bp.route('/learning/next', methods=['GET'])
def get_next_activity():
    student_id = get_student_id()
    course_id = request.args.get('course_id', type=int)
    plan = AdaptiveEngine.compute_next_best_activity(student_id, course_id)
    return jsonify(plan), 200

@learning_bp.route('/learning/path', methods=['GET'])
def get_learning_path():
    student_id = get_student_id()
    course_id = request.args.get('course_id', 1, type=int)
    mastery_list = Mastery.get_student_mastery_for_course(student_id, course_id)
    plan = AdaptiveEngine.compute_next_best_activity(student_id, course_id)
    return jsonify({
        'student_id': student_id,
        'course_id': course_id,
        'current_concept': plan['concept'] if plan else None,
        'mastery_sequence': mastery_list,
        'adaptive_plan': plan
    }), 200

@learning_bp.route('/learning/complete', methods=['POST'])
def complete_activity():
    data = request.get_json() or {}
    student_id = get_student_id()
    activity_type = data.get('activity_type', 'practice')
    concept_id = data.get('concept_id', 3)
    score = float(data.get('score', 80.0))

    # Update mastery
    res = Mastery.update_from_performance(student_id, concept_id, score, score >= 60.0)

    # Re-predict ML state
    ml_state = predict_learning_state(student_id)

    # Re-compute next best activity
    next_plan = AdaptiveEngine.compute_next_best_activity(student_id)

    return jsonify({
        'message': 'Activity logged and mastery updated',
        'mastery_result': res,
        'ml_learning_state': ml_state,
        'next_plan': next_plan
    }), 200

# ================= AI Endpoints =================

@learning_bp.route('/ai/retheme', methods=['POST'])
def api_retheme():
    data = request.get_json() or {}
    original_text = data.get('question', '')
    options = data.get('options', [])
    correct_answer = data.get('correct_answer', '')
    interest = data.get('interest', 'Space')

    if not original_text:
        return jsonify({'error': 'question text required'}), 400

    result = retheme_question(original_text, options, correct_answer, interest)
    return jsonify(result), 200

@learning_bp.route('/ai/explain', methods=['POST'])
def api_explain():
    data = request.get_json() or {}
    concept_name = data.get('concept_name', 'Statistics & Distributions')
    interest = data.get('interest', 'Space')
    difficulty = data.get('difficulty', 'Medium')

    explanation = explain_concept(concept_name, interest, difficulty)
    return jsonify({
        'concept_name': concept_name,
        'interest': interest,
        'explanation': explanation
    }), 200

@learning_bp.route('/ai/generate-practice', methods=['POST'])
def api_generate_practice():
    data = request.get_json() or {}
    concept_name = data.get('concept_name', 'Statistics')
    interest = data.get('interest', 'Space')

    explanation = explain_concept(concept_name, interest, mode='practice_prompt')
    return jsonify({
        'concept_name': concept_name,
        'interest': interest,
        'practice': explanation
    }), 200

@learning_bp.route('/ai/community-assist', methods=['POST'])
def api_community_assist():
    data = request.get_json() or {}
    title = data.get('title', '')
    content = data.get('content', '')
    query = data.get('query', '')

    assistance = assist_community_discussion(title, content, query)
    return jsonify({
        'assistance': assistance
    }), 200

@learning_bp.route('/ml/status', methods=['GET'])
def get_ml_status():
    student_id = get_student_id()
    pred = predict_learning_state(student_id)
    return jsonify(pred), 200
