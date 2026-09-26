from database.db import query_db, execute_db

class Student:
    @staticmethod
    def get_by_id(student_id):
        return query_db("""
            SELECT s.*, u.name, u.email, sch.name as school_name, g.name as grade_name, st.name as stream_name
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN schools sch ON s.school_id = sch.id
            LEFT JOIN grades g ON s.grade_id = g.id
            LEFT JOIN streams st ON s.stream_id = st.id
            WHERE s.id = %s
        """, (student_id,), one=True)

    @staticmethod
    def get_by_user_id(user_id):
        return query_db("""
            SELECT s.*, u.name, u.email, sch.name as school_name, g.name as grade_name, st.name as stream_name
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN schools sch ON s.school_id = sch.id
            LEFT JOIN grades g ON s.grade_id = g.id
            LEFT JOIN streams st ON s.stream_id = st.id
            WHERE s.user_id = %s
        """, (user_id,), one=True)

    @staticmethod
    def get_all():
        return query_db("""
            SELECT s.*, u.name, u.email, sch.name as school_name, g.name as grade_name, st.name as stream_name
            FROM students s
            JOIN users u ON s.user_id = u.id
            LEFT JOIN schools sch ON s.school_id = sch.id
            LEFT JOIN grades g ON s.grade_id = g.id
            LEFT JOIN streams st ON s.stream_id = st.id
            ORDER BY s.id ASC
        """)

    @staticmethod
    def create(user_id, school_id=None, grade_id=None, stream_id=None, academic_level='Grade 10', preferred_learning_style='Visual & Guided Practice', current_skill_level='Intermediate', primary_goal='Master concepts'):
        return execute_db("""
            INSERT INTO students (user_id, school_id, grade_id, stream_id, academic_level, preferred_learning_style, current_skill_level, primary_goal)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, school_id, grade_id, stream_id, academic_level, preferred_learning_style, current_skill_level, primary_goal))

    @staticmethod
    def get_interests(student_id):
        return query_db("""
            SELECT i.id, i.name, i.icon, si.is_primary
            FROM student_interests si
            JOIN interests i ON si.interest_id = i.id
            WHERE si.student_id = %s
            ORDER BY si.is_primary DESC, i.name ASC
        """, (student_id,))

    @staticmethod
    def set_interests(student_id, interest_names):
        # Clear existing
        execute_db("DELETE FROM student_interests WHERE student_id = %s", (student_id,))
        for idx, name in enumerate(interest_names):
            interest = query_db("SELECT id FROM interests WHERE LOWER(name) = LOWER(%s)", (name.strip(),), one=True)
            if not interest:
                # Insert dynamic interest if not in catalog
                iid = execute_db("INSERT INTO interests (name, icon) VALUES (%s, 'sparkles')", (name.strip(),))
            else:
                iid = interest['id']
            is_prim = (idx == 0)
            execute_db("INSERT INTO student_interests (student_id, interest_id, is_primary) VALUES (%s, %s, %s)", (student_id, iid, is_prim))

    @staticmethod
    def get_enrolled_courses(student_id):
        return query_db("""
            SELECT c.*, e.course_mastery, e.enrolled_at, e.status as enrollment_status
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = %s
            ORDER BY e.enrolled_at ASC
        """, (student_id,))

    @staticmethod
    def enroll_in_course(student_id, course_id):
        existing = query_db("SELECT id FROM enrollments WHERE student_id = %s AND course_id = %s", (student_id, course_id), one=True)
        if existing:
            return existing['id']
        return execute_db("""
            INSERT INTO enrollments (student_id, course_id, course_mastery, status)
            VALUES (%s, %s, 0.0, 'active')
        """, (student_id, course_id))
