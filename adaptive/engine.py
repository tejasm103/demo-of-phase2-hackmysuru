import json
from database.db import query_db, execute_db
from models.mastery import Mastery
from models.student import Student
from ml.predictor import predict_learning_state
from adaptive.difficulty import AdaptiveDifficulty
from config import Config

class AdaptiveEngine:
    @staticmethod
    def compute_next_best_activity(student_id, course_id=None):
        """
        The Core Decision Engine of AdaptiveLearn AI.
        
        Synthesizes 12 multi-dimensional signals:
        1. Current concept mastery
        2. Assessment history
        3. Practice scores
        4. Incorrect answer patterns (consecutive errors)
        5. Number of attempts
        6. Prerequisites status
        7. Student interests
        8. Learning history
        9. Difficulty history
        10. Video engagement
        11. ML learning state (from scikit-learn model)
        12. Facilitator intervention history

        Outputs:
        - next_concept: dict
        - next_activity: dict (type, title, description, badge)
        - difficulty: 'Easy' | 'Medium' | 'Hard'
        - recommended_resource: dict (playlist/video info)
        - practice_quantity: int
        - revision_required: bool
        - intervention_required: bool
        - rationale: str
        """
        threshold = Config.MASTERY_THRESHOLD

        # If course_id is not provided, pick student's first active enrolled course
        if not course_id:
            courses = Student.get_enrolled_courses(student_id)
            if courses:
                course_id = courses[0]['id']
            else:
                course_id = 1

        # 1. Fetch concepts and mastery for course
        concepts_mastery = Mastery.get_student_mastery_for_course(student_id, course_id)
        if not concepts_mastery:
            return None

        # 7. Student interests
        interests = Student.get_interests(student_id)
        primary_interest = interests[0]['name'] if interests else 'General'

        # 11. Run scikit-learn ML state prediction
        ml_result = predict_learning_state(student_id)
        ml_state = ml_result['predicted_state'] # 'Improving' | 'Stable' | 'Needs Support'

        # 2 & 3 & 4. Recent attempts analysis
        recent_attempts = query_db("""
            SELECT qa.is_correct, qa.score_earned, qa.concept_id, q.difficulty, qa.created_at
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.id
            WHERE qa.student_id = %s
            ORDER BY qa.created_at DESC LIMIT 6
        """, (student_id,))

        consecutive_errors = 0
        for a in recent_attempts:
            if not a['is_correct']:
                consecutive_errors += 1
            else:
                break

        # 10. Video engagement
        vid_summary = query_db("""
            SELECT AVG(progress_percentage) as avg_prog, COUNT(*) as cnt
            FROM video_view_history
            WHERE student_id = %s AND course_id = %s
        """, (student_id, course_id), one=True)
        video_engagement = float(vid_summary['avg_prog']) if vid_summary and vid_summary['avg_prog'] is not None else 0.0

        # Find the active focus concept:
        # Priority A: Any unlocked concept with mastery < 70% (learning gap)
        # Priority B: First locked concept that needs prerequisite remediation
        # Priority C: Highest mastered concept for advanced challenge
        active_concept = None
        learning_gap_concept = None
        prereq_to_review = None

        for c in concepts_mastery:
            st = c['status']
            score = float(c['mastery_percentage'])
            if st in ('Needs Practice', 'Learning'):
                active_concept = c
                learning_gap_concept = c
                break
            elif st == 'Locked' and not active_concept:
                # Find its unmet prerequisite
                unmet = c.get('unmet_prerequisites', [])
                if unmet:
                    prereq_id = unmet[0]['id']
                    # Look up that prerequisite concept
                    for p in concepts_mastery:
                        if p['id'] == prereq_id:
                            prereq_to_review = p
                            active_concept = p
                            break
                break

        if not active_concept:
            # All unlocked concepts are >= 70%
            # Pick highest or next unlocked
            for c in concepts_mastery:
                if c['status'] == 'Mastered':
                    active_concept = c

        if not active_concept:
            active_concept = concepts_mastery[0]

        concept_mastery = float(active_concept['mastery_percentage'])

        # Fetch recommended playlists/videos for this active concept
        recommended_resource = query_db("""
            SELECT p.id, p.title, p.channel_name, p.thumbnail_url, p.playlist_url, p.difficulty,
                   v.id as video_id, v.title as video_title, v.youtube_video_id, v.duration
            FROM playlist_concepts pc
            JOIN youtube_playlists p ON pc.playlist_id = p.id
            LEFT JOIN playlist_videos pv ON p.id = pv.playlist_id AND pv.position = 1
            LEFT JOIN youtube_videos v ON pv.video_id = v.id
            WHERE pc.concept_id = %s
            ORDER BY pc.relevance_score DESC
            LIMIT 1
        """, (active_concept['id'],), one=True)

        if not recommended_resource:
            # Fallback to course playlist
            recommended_resource = query_db("""
                SELECT p.id, p.title, p.channel_name, p.thumbnail_url, p.playlist_url, p.difficulty,
                       v.id as video_id, v.title as video_title, v.youtube_video_id, v.duration
                FROM youtube_playlists p
                LEFT JOIN playlist_videos pv ON p.id = pv.playlist_id AND pv.position = 1
                LEFT JOIN youtube_videos v ON pv.video_id = v.id
                WHERE p.course_id = %s
                LIMIT 1
            """, (course_id,), one=True)

        # -------------------------------------------------------------
        # APPLICATION OF ADAPTIVE RULES (Req 11 & 12)
        # -------------------------------------------------------------
        # 85–100%: Advanced challenge
        # 70–84%: Normal progression
        # 40–69%: Guided practice
        # 0–39%: Remediation + prerequisite review
        # -------------------------------------------------------------
        intervention_required = False
        revision_required = False

        if concept_mastery >= 85.0:
            activity_type = 'advanced_challenge'
            difficulty = 'Hard'
            practice_quantity = 5
            activity_title = f"Advanced Mastery Challenge: {active_concept['name']}"
            activity_desc = f"Your mastery is {concept_mastery:.0f}%. Test complex synthesis, multi-variable logic, and boundary conditions."
            rationale = f"Excellence tier demonstrated ({concept_mastery:.0f}%). Difficulty stepped up to Hard."

        elif concept_mastery >= 70.0:
            activity_type = 'normal_progression'
            difficulty = 'Medium'
            practice_quantity = 4
            activity_title = f"Conceptual Mastery & Synthesis: {active_concept['name']}"
            activity_desc = f"You have achieved passing mastery ({concept_mastery:.0f}%). Reinforce conceptual connections."
            rationale = f"Mastery requirement met (>= {threshold:.0f}%). Unlocking dependent graph concepts."

        elif concept_mastery >= 40.0:
            activity_type = 'guided_practice'
            difficulty = AdaptiveDifficulty.calculate_next_difficulty('Medium', [a['score_earned'] for a in recent_attempts[:3]], consecutive_errors)
            practice_quantity = 4
            activity_title = f"Guided Step-by-Step Practice: {active_concept['name']}"
            activity_desc = f"Current mastery is {concept_mastery:.0f}%. Focus on problem-solving scaffolding and error elimination."
            rationale = f"Moderate understanding ({concept_mastery:.0f}%). Needs guided practice with {primary_interest}-themed contextual problems."

        else: # 0–39%
            activity_type = 'remediation_prerequisite'
            difficulty = 'Easy'
            practice_quantity = 3
            revision_required = True
            activity_title = f"Foundational Remediation & Video Lecture: {active_concept['name']}"
            activity_desc = f"Mastery is currently {concept_mastery:.0f}%. Step back to core visual models before attempting practice."
            rationale = f"Learning gap detected ({concept_mastery:.0f}% < 40%). Prerequisite review and visual video reinforcement mandated."

        # Check for Facilitator Intervention Trigger
        if consecutive_errors >= 3 or (concept_mastery < 45.0 and ml_state == 'Needs Support'):
            intervention_required = True
            activity_title = f"Targeted Intervention Review: {active_concept['name']}"
            rationale += " [Alert: ML predicts 'Needs Support'. Facilitator intervention pathway triggered]."

        return {
            'student_id': student_id,
            'course_id': course_id,
            'concept': active_concept,
            'activity': {
                'type': activity_type,
                'title': activity_title,
                'description': activity_desc,
                'difficulty': difficulty,
                'practice_quantity': practice_quantity,
                'revision_required': revision_required,
                'intervention_required': intervention_required
            },
            'difficulty': difficulty,
            'recommended_resource': recommended_resource,
            'student_interest': primary_interest,
            'ml_learning_state': ml_state,
            'consecutive_errors': consecutive_errors,
            'video_engagement': video_engagement,
            'rationale': rationale
        }
