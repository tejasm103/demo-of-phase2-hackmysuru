import json
from database.db import query_db, execute_db

class Assessment:
    @staticmethod
    def get_questions_by_concept(concept_id, difficulty=None, limit=5):
        if difficulty:
            return query_db("""
                SELECT * FROM questions
                WHERE concept_id = %s AND difficulty = %s
                ORDER BY id ASC LIMIT %s
            """, (concept_id, difficulty, limit))
        return query_db("""
            SELECT * FROM questions
            WHERE concept_id = %s
            ORDER BY id ASC LIMIT %s
        """, (concept_id, limit))

    @staticmethod
    def get_diagnostic_questions(course_id, limit=5):
        """Fetches representative diagnostic questions across prerequisite and foundational concepts."""
        return query_db("""
            SELECT q.*, c.name as concept_name, c.code as concept_code
            FROM questions q
            JOIN concepts c ON q.concept_id = c.id
            WHERE q.course_id = %s
            ORDER BY c.hierarchy_order ASC, q.difficulty ASC
            LIMIT %s
        """, (course_id, limit))

    @staticmethod
    def get_question_by_id(question_id):
        return query_db("SELECT * FROM questions WHERE id = %s", (question_id,), one=True)

    @staticmethod
    def record_attempt(student_id, question_id, concept_id, student_answer, is_correct, score_earned, time_seconds=30, is_diagnostic=False, interest="General"):
        return execute_db("""
            INSERT INTO question_attempts (student_id, question_id, concept_id, is_diagnostic, student_answer, is_correct, score_earned, attempt_time_seconds, context_interest)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (student_id, question_id, concept_id, is_diagnostic, student_answer, is_correct, score_earned, time_seconds, interest))

    @staticmethod
    def get_student_attempts(student_id, concept_id=None, limit=20):
        if concept_id:
            return query_db("""
                SELECT qa.*, q.narrative_context, q.correct_answer, c.name as concept_name
                FROM question_attempts qa
                JOIN questions q ON qa.question_id = q.id
                JOIN concepts c ON qa.concept_id = c.id
                WHERE qa.student_id = %s AND qa.concept_id = %s
                ORDER BY qa.created_at DESC LIMIT %s
            """, (student_id, concept_id, limit))
        return query_db("""
            SELECT qa.*, q.narrative_context, q.correct_answer, c.name as concept_name
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.id
            JOIN concepts c ON qa.concept_id = c.id
            WHERE qa.student_id = %s
            ORDER BY qa.created_at DESC LIMIT %s
        """, (student_id, limit))
