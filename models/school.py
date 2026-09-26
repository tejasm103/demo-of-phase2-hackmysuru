from database.db import query_db, execute_db

class School:
    @staticmethod
    def get_all():
        return query_db("SELECT * FROM schools ORDER BY id ASC")

    @staticmethod
    def get_by_id(school_id):
        return query_db("SELECT * FROM schools WHERE id = %s", (school_id,), one=True)

    @staticmethod
    def get_grades(school_id):
        return query_db("SELECT * FROM grades WHERE school_id = %s ORDER BY id ASC", (school_id,))

    @staticmethod
    def create(name, institution_id, board_curriculum, academic_year, address=""):
        return execute_db(
            "INSERT INTO schools (name, institution_id, board_curriculum, academic_year, address) VALUES (%s, %s, %s, %s, %s)",
            (name, institution_id, board_curriculum, academic_year, address)
        )

    @staticmethod
    def add_grade(school_id, name, code=""):
        return execute_db("INSERT INTO grades (school_id, name, code) VALUES (%s, %s, %s)", (school_id, name, code))

    @staticmethod
    def get_all_streams():
        return query_db("SELECT * FROM streams ORDER BY id ASC")
