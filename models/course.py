from database.db import query_db, execute_db

class Course:
    @staticmethod
    def get_all():
        return query_db("SELECT * FROM courses ORDER BY id ASC")

    @staticmethod
    def get_by_id(course_id):
        return query_db("SELECT * FROM courses WHERE id = %s", (course_id,), one=True)

    @staticmethod
    def get_by_code(code):
        return query_db("SELECT * FROM courses WHERE UPPER(code) = UPPER(%s)", (code,), one=True)

    @staticmethod
    def create(name, code, grade_level="Grade 10", description="", icon="book-open", color_accent="#4f46e5", school_id=None):
        return execute_db(
            "INSERT INTO courses (name, code, grade_level, description, icon, color_accent, school_id) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (name, code, grade_level, description, icon, color_accent, school_id)
        )

    @staticmethod
    def get_enrolled_students(course_id):
        return query_db("""
            SELECT s.id, u.name, u.email, e.course_mastery, e.enrolled_at, s.overall_mastery
            FROM enrollments e
            JOIN students s ON e.student_id = s.id
            JOIN users u ON s.user_id = u.id
            WHERE e.course_id = %s
            ORDER BY e.course_mastery ASC
        """, (course_id,))
