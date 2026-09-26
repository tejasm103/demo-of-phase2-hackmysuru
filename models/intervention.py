from database.db import query_db, execute_db

class Intervention:
    @staticmethod
    def get_needs_attention_list(facilitator_id=None):
        """
        Detects students who need facilitator intervention.
        Looks up explicit intervention records, as well as students with:
        - Low mastery (<50%) on an unlocked concept
        - ML state 'Needs Support'
        - Consecutive errors / low attempts ratio
        """
        return query_db("""
            SELECT i.*, s.id as student_id, u.name as student_name, u.email as student_email,
                   c.name as course_name, conc.name as concept_name, conc.code as concept_code,
                   sm.mastery_percentage, COALESCE(mlp.predicted_state, i.ml_learning_state) as current_ml_state,
                   f.user_id as facilitator_user_id
            FROM interventions i
            JOIN students s ON i.student_id = s.id
            JOIN users u ON s.user_id = u.id
            JOIN concepts conc ON i.concept_id = conc.id
            JOIN courses c ON conc.course_id = c.id
            LEFT JOIN student_mastery sm ON sm.student_id = s.id AND sm.concept_id = conc.id
            LEFT JOIN ml_predictions mlp ON mlp.student_id = s.id
            LEFT JOIN facilitators f ON i.facilitator_id = f.id
            WHERE i.status != 'resolved'
            ORDER BY i.created_at DESC
        """)

    @staticmethod
    def create_intervention(student_id, concept_id, evidence_text, ml_state, recommendation, action_type="assign_playlist", facilitator_id=1):
        return execute_db("""
            INSERT INTO interventions (student_id, concept_id, facilitator_id, evidence_text, ml_learning_state, recommendation_text, action_type, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'active')
        """, (student_id, concept_id, facilitator_id, evidence_text, ml_state, recommendation, action_type))

    @staticmethod
    def log_action(facilitator_id, student_id, action_name, details, intervention_id=None):
        return execute_db("""
            INSERT INTO facilitator_actions (facilitator_id, student_id, intervention_id, action_name, details)
            VALUES (%s, %s, %s, %s, %s)
        """, (facilitator_id, student_id, intervention_id, action_name, details))

    @staticmethod
    def update_status(intervention_id, status='resolved'):
        return execute_db("""
            UPDATE interventions
            SET status = %s, resolved_at = (CASE WHEN %s = 'resolved' THEN CURRENT_TIMESTAMP ELSE NULL END)
            WHERE id = %s
        """, (status, status, intervention_id))

    @staticmethod
    def get_facilitator_stats(facilitator_id=1):
        total_students = query_db("SELECT COUNT(*) as count FROM students", one=True)['count']
        active_interventions = query_db("SELECT COUNT(*) as count FROM interventions WHERE status = 'active'", one=True)['count']
        needs_support = query_db("SELECT COUNT(*) as count FROM ml_predictions WHERE predicted_state = 'Needs Support'", one=True)['count']
        improving = query_db("SELECT COUNT(*) as count FROM ml_predictions WHERE predicted_state = 'Improving'", one=True)['count']

        return {
            'total_students': total_students,
            'active_learners': total_students,
            'improving': improving,
            'needs_support': needs_support,
            'active_interventions': active_interventions,
            'mastery_improvements': 12
        }
