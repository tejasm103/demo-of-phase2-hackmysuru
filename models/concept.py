from database.db import query_db, execute_db

class Concept:
    @staticmethod
    def get_by_id(concept_id):
        return query_db("SELECT * FROM concepts WHERE id = %s", (concept_id,), one=True)

    @staticmethod
    def get_by_course(course_id):
        return query_db("SELECT * FROM concepts WHERE course_id = %s ORDER BY hierarchy_order ASC", (course_id,))

    @staticmethod
    def get_prerequisites(concept_id):
        return query_db("""
            SELECT cp.id, cp.concept_id, cp.prerequisite_id, cp.min_mastery_required,
                   c.name as prerequisite_name, c.code as prerequisite_code, c.difficulty
            FROM concept_prerequisites cp
            JOIN concepts c ON cp.prerequisite_id = c.id
            WHERE cp.concept_id = %s
        """, (concept_id,))

    @staticmethod
    def get_dependents(concept_id):
        """Returns concepts that require this concept as a prerequisite."""
        return query_db("""
            SELECT cp.id, cp.concept_id, cp.prerequisite_id, cp.min_mastery_required,
                   c.name as dependent_name, c.code as dependent_code, c.course_id
            FROM concept_prerequisites cp
            JOIN concepts c ON cp.concept_id = c.id
            WHERE cp.prerequisite_id = %s
        """, (concept_id,))

    @staticmethod
    def add_prerequisite(concept_id, prerequisite_id, min_mastery=70.0):
        return execute_db(
            "INSERT INTO concept_prerequisites (concept_id, prerequisite_id, min_mastery_required) VALUES (%s, %s, %s)",
            (concept_id, prerequisite_id, min_mastery)
        )
