import json
from database.db import query_db

def extract_student_features(student_id, concept_id=None):
    """
    Extracts 8 educational features for ML learning-state classification:
    1. assessment_score (0-100)
    2. practice_score (0-100)
    3. attempt_count (int)
    4. incorrect_count (int)
    5. previous_mastery (0-100)
    6. recent_trend_slope (-1.0 to 1.0)
    7. video_engagement (0-100)
    8. time_between_attempts_hours (float, normalized)
    """
    # 1 & 2 & 3 & 4. Question attempts
    if concept_id:
        attempts = query_db("""
            SELECT is_correct, score_earned, attempt_time_seconds, created_at
            FROM question_attempts
            WHERE student_id = %s AND concept_id = %s
            ORDER BY created_at DESC LIMIT 10
        """, (student_id, concept_id))
    else:
        attempts = query_db("""
            SELECT is_correct, score_earned, attempt_time_seconds, created_at
            FROM question_attempts
            WHERE student_id = %s
            ORDER BY created_at DESC LIMIT 10
        """, (student_id,))

    attempt_count = len(attempts)
    if attempt_count > 0:
        scores = [float(a['score_earned']) for a in attempts]
        assessment_score = sum(scores) / len(scores)
        incorrect_count = sum(1 for a in attempts if not a['is_correct'])
        # practice score is average of last 3 attempts
        practice_score = sum(scores[:3]) / len(scores[:3]) if len(scores) >= 3 else assessment_score
        # trend: compare first half to second half
        if len(scores) >= 4:
            recent_avg = sum(scores[:2]) / 2
            older_avg = sum(scores[2:4]) / 2
            trend_slope = (recent_avg - older_avg) / 100.0
        else:
            trend_slope = 0.0
    else:
        assessment_score = 50.0
        practice_score = 50.0
        incorrect_count = 0
        trend_slope = 0.0

    # 5. Mastery
    if concept_id:
        mastery_row = query_db(
            "SELECT mastery_percentage FROM student_mastery WHERE student_id = %s AND concept_id = %s",
            (student_id, concept_id), one=True
        )
        previous_mastery = float(mastery_row['mastery_percentage']) if mastery_row else 40.0
    else:
        mastery_row = query_db(
            "SELECT AVG(mastery_percentage) as avg_m FROM student_mastery WHERE student_id = %s",
            (student_id,), one=True
        )
        previous_mastery = float(mastery_row['avg_m']) if mastery_row and mastery_row['avg_m'] else 50.0

    # 7. Video engagement
    vid_prog = query_db("""
        SELECT AVG(progress_percentage) as avg_p FROM video_view_history WHERE student_id = %s
    """, (student_id,), one=True)
    video_engagement = float(vid_prog['avg_p']) if vid_prog and vid_prog['avg_p'] is not None else 50.0

    # 8. Normalized time between attempts (default ~2.5 hours)
    time_between_attempts_hours = 2.5

    feature_vector = [
        round(assessment_score, 1),
        round(practice_score, 1),
        int(attempt_count),
        int(incorrect_count),
        round(previous_mastery, 1),
        round(trend_slope, 2),
        round(video_engagement, 1),
        round(time_between_attempts_hours, 1)
    ]

    metadata = {
        'assessment_score': feature_vector[0],
        'practice_score': feature_vector[1],
        'attempt_count': feature_vector[2],
        'incorrect_count': feature_vector[3],
        'previous_mastery': feature_vector[4],
        'trend_slope': feature_vector[5],
        'video_engagement': feature_vector[6],
        'time_between_attempts_hours': feature_vector[7]
    }

    return feature_vector, metadata
