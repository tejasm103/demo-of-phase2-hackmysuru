import json
from flask import Blueprint, request, jsonify, session
from models.assessment import Assessment
from models.mastery import Mastery
from models.student import Student
from models.concept import Concept
from ai.retheme import retheme_question
from ml.predictor import predict_learning_state
from adaptive.engine import AdaptiveEngine

assessment_bp = Blueprint('assessment', __name__, url_prefix='/api/assessment')

def get_student_id():
    student_id = session.get('student_id')
    if not student_id:
        user_id = session.get('user_id', 1)
        stu = Student.get_by_user_id(user_id)
        student_id = stu['id'] if stu else 1
    return student_id

@assessment_bp.route('', methods=['GET'])
def get_assessment():
    """
    Returns questions for diagnostic assessment or targeted practice.
    Re-themes questions in real-time according to student's interest!
    """
    student_id = get_student_id()
    course_id = request.args.get('course_id', 1, type=int)
    concept_id = request.args.get('concept_id', type=int)
    is_diagnostic = request.args.get('diagnostic', 'false').lower() in ('true', '1')

    # Get student's primary interest
    interests = Student.get_interests(student_id)
    primary_interest = interests[0]['name'] if interests else 'Space'

    if is_diagnostic:
        raw_questions = Assessment.get_diagnostic_questions(course_id, limit=5)
    elif concept_id:
        raw_questions = Assessment.get_questions_by_concept(concept_id, limit=4)
    else:
        # Get active gap concept from adaptive engine
        adaptive = AdaptiveEngine.compute_next_best_activity(student_id, course_id)
        active_cid = adaptive['concept']['id'] if adaptive and adaptive.get('concept') else 3
        raw_questions = Assessment.get_questions_by_concept(active_cid, limit=4)

    # Contextually re-theme each question to the student's interest
    formatted_questions = []
    for q in raw_questions:
        try:
            options = json.loads(q['options_json']) if q.get('options_json') else []
        except Exception:
            options = ["Option A", "Option B", "Option C", "Option D"]

        rethemed = retheme_question(
            q['narrative_context'],
            options=options,
            correct_answer=q['correct_answer'],
            interest=primary_interest
        )

        formatted_questions.append({
            'id': q['id'],
            'course_id': q['course_id'],
            'concept_id': q['concept_id'],
            'difficulty': q['difficulty'],
            'question_type': q['question_type'],
            'original_narrative': q['narrative_context'],
            'narrative_context': rethemed['transformed_question'],
            'options': options,
            'explanation': q.get('explanation', ''),
            'interest_applied': primary_interest
        })

    return jsonify({
        'student_id': student_id,
        'course_id': course_id,
        'interest': primary_interest,
        'questions_count': len(formatted_questions),
        'questions': formatted_questions
    }), 200

@assessment_bp.route('/submit', methods=['POST'])
def submit_assessment():
    """
    The Core Adaptive Feedback Loop in Action:
    1. Score submitted answers
    2. Update concept mastery
    3. Evaluate prerequisite gating (unlock dependent concepts)
    4. Re-run scikit-learn ML learning-state analysis
    5. Trigger AdaptiveEngine for next best activity!
    """
    data = request.get_json() or {}
    student_id = get_student_id()
    answers = data.get('answers', []) # list of {question_id: int, student_answer: str, time_seconds: int}
    is_diagnostic = data.get('is_diagnostic', False)

    if not answers:
        return jsonify({'error': 'No answers submitted'}), 400

    interests = Student.get_interests(student_id)
    interest_name = interests[0]['name'] if interests else 'General'

    results = []
    concept_scores = {} # concept_id -> list of float scores
    total_correct = 0

    for item in answers:
        qid = item.get('question_id')
        user_ans = str(item.get('student_answer', '')).strip()
        time_spent = int(item.get('time_seconds', 30))

        q = Assessment.get_question_by_id(qid)
        if not q:
            continue

        cid = q['concept_id']
        correct_ans = str(q['correct_answer']).strip()
        is_correct = (user_ans.lower() == correct_ans.lower())
        score_earned = 100.0 if is_correct else 0.0

        if is_correct:
            total_correct += 1

        # Record attempt
        Assessment.record_attempt(
            student_id=student_id,
            question_id=qid,
            concept_id=cid,
            student_answer=user_ans,
            is_correct=is_correct,
            score_earned=score_earned,
            time_seconds=time_spent,
            is_diagnostic=is_diagnostic,
            interest=interest_name
        )

        concept_scores.setdefault(cid, []).append((score_earned, is_correct))
        results.append({
            'question_id': qid,
            'concept_id': cid,
            'is_correct': is_correct,
            'student_answer': user_ans,
            'correct_answer': correct_ans,
            'explanation': q.get('explanation')
        })

    # Update mastery for each affected concept
    mastery_updates = []
    for cid, scores_list in concept_scores.items():
        avg_score = sum(s[0] for s in scores_list) / len(scores_list)
        any_correct = any(s[1] for s in scores_list)
        update_info = Mastery.update_from_performance(student_id, cid, avg_score, any_correct)
        conc = Concept.get_by_id(cid)
        update_info['concept_id'] = cid
        update_info['concept_name'] = conc['name'] if conc else f"Concept {cid}"
        update_info['new_mastery_percentage'] = update_info['new_mastery']
        update_info['unlocked'] = update_info['unlocked_dependent']
        mastery_updates.append(update_info)

    # Re-run real scikit-learn ML state prediction
    ml_reanalysis = predict_learning_state(student_id)

    # Compute updated next best activity
    first_cid = list(concept_scores.keys())[0] if concept_scores else 1
    conc_obj = Concept.get_by_id(first_cid)
    course_id = conc_obj['course_id'] if conc_obj else 1
    next_adaptive_plan = AdaptiveEngine.compute_next_best_activity(student_id, course_id)

    pct_score = round((total_correct / len(answers)) * 100.0, 1)

    return jsonify({
        'message': 'Assessment processed and mastery updated',
        'student_id': student_id,
        'total_questions': len(answers),
        'correct_count': total_correct,
        'accuracy_percentage': pct_score,
        'score_percentage': pct_score,
        'mastery_updates': mastery_updates,
        'mastery_update': mastery_updates[0] if mastery_updates else {},
        'ml_learning_state': ml_reanalysis,
        'next_adaptive_plan': next_adaptive_plan,
        'question_results': results
    }), 200
