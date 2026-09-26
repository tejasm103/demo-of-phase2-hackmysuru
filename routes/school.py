from flask import Blueprint, request, jsonify, session
from models.school import School
from database.db import query_db, execute_db

school_bp = Blueprint('school', __name__, url_prefix='/api/schools')

@school_bp.route('', methods=['GET'])
def list_schools():
    schools = School.get_all()
    return jsonify(schools), 200

@school_bp.route('/<int:school_id>', methods=['GET'])
def get_school(school_id):
    school = School.get_by_id(school_id)
    if not school:
        return jsonify({'error': 'School not found'}), 404
    grades = School.get_grades(school_id)
    return jsonify({
        'school': school,
        'grades': grades
    }), 200

@school_bp.route('/<int:school_id>/grades', methods=['GET'])
def get_school_grades(school_id):
    grades = School.get_grades(school_id)
    return jsonify(grades), 200

@school_bp.route('/streams', methods=['GET'])
def list_streams():
    streams = School.get_all_streams()
    return jsonify(streams), 200

@school_bp.route('', methods=['POST'])
def create_school():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    institution_id = data.get('institution_id', '').strip()
    board = data.get('board_curriculum', 'CBSE')
    academic_year = data.get('academic_year', '2026-2027')
    address = data.get('address', '')

    if not name or not institution_id:
        return jsonify({'error': 'School name and institution ID are required'}), 400

    try:
        sid = School.create(name, institution_id, board, academic_year, address)
        return jsonify({'message': 'School created', 'school_id': sid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
