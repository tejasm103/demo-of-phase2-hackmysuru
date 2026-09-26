from flask import Blueprint, request, jsonify, session
from models.community import Community
from models.user import User
from database.db import query_db, execute_db

community_bp = Blueprint('community', __name__, url_prefix='/api')

def get_current_user_id():
    return session.get('user_id', 1)

@community_bp.route('/community', methods=['GET'])
def list_communities():
    course_id = request.args.get('course_id', type=int)
    communities = Community.get_all(course_id)
    return jsonify(communities), 200

@community_bp.route('/community/<int:community_id>', methods=['GET'])
def get_community(community_id):
    comm = Community.get_by_id(community_id)
    if not comm:
        return jsonify({'error': 'Community not found'}), 404
    post_type = request.args.get('type')
    posts = Community.get_posts(community_id, post_type)
    return jsonify({
        'community': comm,
        'posts': posts
    }), 200

@community_bp.route('/community/posts', methods=['POST'])
def create_post():
    data = request.get_json() or {}
    user_id = get_current_user_id()
    community_id = data.get('community_id', 1)
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    post_type = data.get('post_type', 'discussion')

    if not title or not content:
        return jsonify({'error': 'Title and content are required'}), 400

    pid = Community.create_post(community_id, user_id, title, content, post_type)
    return jsonify({'message': 'Post created', 'post_id': pid}), 201

@community_bp.route('/community/posts/<int:post_id>/comments', methods=['GET'])
def get_comments(post_id):
    comments = Community.get_comments(post_id)
    return jsonify(comments), 200

@community_bp.route('/community/posts/<int:post_id>/comments', methods=['POST'])
def add_comment(post_id):
    data = request.get_json() or {}
    user_id = get_current_user_id()
    content = data.get('content', '').strip()
    is_ai = data.get('is_ai_assisted', False)

    if not content:
        return jsonify({'error': 'Comment content required'}), 400

    cid = Community.add_comment(post_id, user_id, content, is_ai)
    return jsonify({'message': 'Comment added', 'comment_id': cid}), 201

@community_bp.route('/community/posts/<int:post_id>/reactions', methods=['POST'])
def react_post(post_id):
    data = request.get_json() or {}
    user_id = get_current_user_id()
    rtype = data.get('reaction_type', 'like')

    liked = Community.react_post(post_id, user_id, rtype)
    return jsonify({'liked': liked}), 200

@community_bp.route('/community/posts/<int:post_id>/report', methods=['POST'])
def report_post(post_id):
    data = request.get_json() or {}
    reporter_id = get_current_user_id()
    reason = data.get('reason', 'Inappropriate or spam').strip()

    rid = Community.report_post(post_id, reporter_id, reason)
    return jsonify({'message': 'Report submitted for review', 'report_id': rid}), 201

# ================= Study Groups =================

@community_bp.route('/study-groups', methods=['GET'])
def list_study_groups():
    course_id = request.args.get('course_id', type=int)
    groups = Community.get_study_groups(course_id)
    return jsonify(groups), 200

@community_bp.route('/study-groups', methods=['POST'])
def create_study_group():
    data = request.get_json() or {}
    user_id = get_current_user_id()
    course_id = data.get('course_id', 1)
    name = data.get('name', '').strip()
    topic = data.get('topic', '').strip()
    grade = data.get('grade_level', 'Grade 10')
    desc = data.get('description', '')

    if not name or not topic:
        return jsonify({'error': 'Group name and topic are required'}), 400

    gid = execute_db("""
        INSERT INTO study_groups (course_id, name, topic, grade_level, created_by, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (course_id, name, topic, grade, user_id, desc))

    Community.join_study_group(gid, user_id)
    return jsonify({'message': 'Study group created', 'group_id': gid}), 201

@community_bp.route('/study-groups/<int:group_id>/join', methods=['POST'])
def join_group(group_id):
    user_id = get_current_user_id()
    mid = Community.join_study_group(group_id, user_id)
    return jsonify({'message': 'Joined study group successfully', 'member_id': mid}), 200

# ================= Projects =================

@community_bp.route('/projects', methods=['GET'])
def list_projects():
    course_id = request.args.get('course_id', type=int)
    projects = Community.get_projects(course_id)
    return jsonify(projects), 200

@community_bp.route('/projects/<int:project_id>', methods=['GET'])
def get_project_detail(project_id):
    proj = query_db("""
        SELECT p.*, c1.name as course1_name, c2.name as course2_name, u.name as lead_name
        FROM projects p
        LEFT JOIN courses c1 ON p.course_id = c1.id
        LEFT JOIN courses c2 ON p.secondary_course_id = c2.id
        JOIN users u ON p.lead_user_id = u.id
        WHERE p.id = %s
    """, (project_id,), one=True)
    if not proj:
        return jsonify({'error': 'Project not found'}), 404

    members = query_db("""
        SELECT pm.*, u.name, u.email
        FROM project_members pm
        JOIN users u ON pm.user_id = u.id
        WHERE pm.project_id = %s
    """, (project_id,))

    tasks = query_db("""
        SELECT pt.*, u.name as assigned_name
        FROM project_tasks pt
        LEFT JOIN users u ON pt.assigned_to = u.id
        WHERE pt.project_id = %s
    """, (project_id,))

    return jsonify({
        'project': proj,
        'members': members,
        'tasks': tasks
    }), 200

@community_bp.route('/projects', methods=['POST'])
def create_project():
    data = request.get_json() or {}
    user_id = get_current_user_id()
    title = data.get('title', '').strip()
    description = data.get('description', '')
    course_id = data.get('course_id', 1)
    sec_course_id = data.get('secondary_course_id')

    if not title:
        return jsonify({'error': 'Project title is required'}), 400

    pid = execute_db("""
        INSERT INTO projects (title, description, course_id, secondary_course_id, lead_user_id)
        VALUES (%s, %s, %s, %s, %s)
    """, (title, description, course_id, sec_course_id, user_id))

    execute_db("INSERT INTO project_members (project_id, user_id, role) VALUES (%s, %s, 'Project Lead')", (pid, user_id))
    return jsonify({'message': 'Project created', 'project_id': pid}), 201

# ================= Challenges =================

@community_bp.route('/challenges', methods=['GET'])
def list_challenges():
    course_id = request.args.get('course_id', type=int)
    challenges = Community.get_challenges(course_id)
    return jsonify(challenges), 200

@community_bp.route('/challenges/<int:challenge_id>/join', methods=['POST'])
def join_challenge(challenge_id):
    student_id = session.get('student_id', 1)
    existing = query_db("SELECT id FROM challenge_participants WHERE challenge_id = %s AND student_id = %s", (challenge_id, student_id), one=True)
    if existing:
        return jsonify({'message': 'Already joined challenge'}), 200

    cid = execute_db("""
        INSERT INTO challenge_participants (challenge_id, student_id, status)
        VALUES (%s, %s, 'joined')
    """, (challenge_id, student_id))
    return jsonify({'message': 'Joined challenge successfully', 'participant_id': cid}), 200
