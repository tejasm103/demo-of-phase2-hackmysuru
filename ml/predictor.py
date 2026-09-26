import json
import numpy as np
from ml.model import load_or_train_model
from ml.features import extract_student_features
from database.db import execute_db, query_db

_cached_model = None

def get_model():
    global _cached_model
    if _cached_model is None:
        _cached_model = load_or_train_model()
    return _cached_model

def predict_learning_state(student_id, concept_id=None, custom_features=None):
    """
    Runs real scikit-learn inference to classify student learning state:
    Outputs: 'Improving' | 'Stable' | 'Needs Support'
    Returns state, probabilities, and supporting features.
    """
    model = get_model()

    if custom_features is not None:
        feature_vector = custom_features
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
    else:
        feature_vector, metadata = extract_student_features(student_id, concept_id)

    X_input = np.array([feature_vector])
    predicted_state = str(model.predict(X_input)[0])

    # Probabilities
    classes = list(model.classes_)
    try:
        probs = model.predict_proba(X_input)[0]
        prob_dict = {cls_name: round(float(probs[i]), 3) for i, cls_name in enumerate(classes)}
        confidence = float(prob_dict.get(predicted_state, 0.85))
    except Exception:
        prob_dict = {predicted_state: 0.85}
        confidence = 0.85

    # Cache into ml_predictions
    try:
        execute_db("""
            INSERT INTO ml_predictions 
            (student_id, predicted_state, confidence_score, assessment_score, practice_score, attempt_count, incorrect_count, previous_mastery, trend_slope, video_engagement, features_json)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            student_id,
            predicted_state,
            confidence,
            metadata['assessment_score'],
            metadata['practice_score'],
            metadata['attempt_count'],
            metadata['incorrect_count'],
            metadata['previous_mastery'],
            metadata['trend_slope'],
            metadata['video_engagement'],
            json.dumps(metadata)
        ))
    except Exception as e:
        pass

    return {
        'student_id': student_id,
        'predicted_state': predicted_state,
        'confidence': confidence,
        'class_probabilities': prob_dict,
        'features': metadata
    }
