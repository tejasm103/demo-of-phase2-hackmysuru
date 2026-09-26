from flask import Blueprint, request, jsonify, session
from models.user import User
from models.student import Student

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', 'student')

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    existing = User.get_by_email(email)
    if existing:
        return jsonify({'error': 'An account with this email already exists'}), 409

    try:
        user_id = User.create(name, email, password, role)
        if role == 'student':
            student_id = Student.create(user_id)
        else:
            student_id = None

        session['user_id'] = user_id
        session['role'] = role
        session['name'] = name
        session['email'] = email
        if student_id:
            session['student_id'] = student_id

        return jsonify({
            'message': 'Registration successful',
            'user': {
                'id': user_id,
                'name': name,
                'email': email,
                'role': role,
                'student_id': student_id
            }
        }), 201
    except Exception as e:
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.authenticate(email, password)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401

    session['user_id'] = user['id']
    session['role'] = user['role']
    session['name'] = user['name']
    session['email'] = user['email']

    student_id = None
    if user['role'] == 'student':
        stu = Student.get_by_user_id(user['id'])
        if stu:
            student_id = stu['id']
            session['student_id'] = student_id

    return jsonify({
        'message': 'Login successful',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'student_id': student_id
        }
    }), 200

@auth_bp.route('/logout', methods=['POST', 'GET'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'authenticated': False}), 200
    user = User.get_by_id(user_id)
    if not user:
        session.clear()
        return jsonify({'authenticated': False}), 200
    
    student_id = session.get('student_id')
    if user['role'] == 'student' and not student_id:
        stu = Student.get_by_user_id(user_id)
        if stu:
            student_id = stu['id']
            session['student_id'] = student_id

    return jsonify({
        'authenticated': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'student_id': student_id
        }
    }), 200

@auth_bp.route('/switch-demo-user', methods=['POST'])
def switch_demo_user():
    """Allows rapid hackathon switching between seeded personas."""
    data = request.get_json() or {}
    user_id = data.get('user_id', 1)
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    session['user_id'] = user['id']
    session['role'] = user['role']
    session['name'] = user['name']
    session['email'] = user['email']

    student_id = None
    if user['role'] == 'student':
        stu = Student.get_by_user_id(user['id'])
        if stu:
            student_id = stu['id']
            session['student_id'] = student_id

    return jsonify({
        'message': f'Switched to {user["name"]}',
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'role': user['role'],
            'student_id': student_id
        }
    }), 200
