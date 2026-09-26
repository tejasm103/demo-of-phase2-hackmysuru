from werkzeug.security import generate_password_hash, check_password_hash
from database.db import query_db, execute_db

class User:
    @staticmethod
    def get_by_id(user_id):
        return query_db("SELECT id, name, email, role, status, created_at FROM users WHERE id = %s", (user_id,), one=True)

    @staticmethod
    def get_by_email(email):
        return query_db("SELECT * FROM users WHERE LOWER(email) = LOWER(%s)", (email.strip(),), one=True)

    @staticmethod
    def create(name, email, password, role="student"):
        password_hash = generate_password_hash(password)
        user_id = execute_db(
            "INSERT INTO users (name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (name.strip(), email.strip().lower(), password_hash, role)
        )
        return user_id

    @staticmethod
    def authenticate(email, password):
        user = User.get_by_email(email)
        if not user:
            return None
        if check_password_hash(user['password_hash'], password):
            return {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role']
            }
        return None

    @staticmethod
    def list_all():
        return query_db("SELECT id, name, email, role, status, created_at FROM users ORDER BY id ASC")
