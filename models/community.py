from database.db import query_db, execute_db

class Community:
    @staticmethod
    def get_all(course_id=None):
        if course_id:
            return query_db("""
                SELECT c.*, co.name as course_name, COUNT(DISTINCT cm.user_id) as member_count,
                       COUNT(DISTINCT cp.id) as post_count
                FROM communities c
                JOIN courses co ON c.course_id = co.id
                LEFT JOIN community_members cm ON c.id = cm.community_id
                LEFT JOIN community_posts cp ON c.id = cp.community_id
                WHERE c.course_id = %s
                GROUP BY c.id
                ORDER BY c.id ASC
            """, (course_id,))
        return query_db("""
            SELECT c.*, co.name as course_name, COUNT(DISTINCT cm.user_id) as member_count,
                   COUNT(DISTINCT cp.id) as post_count
            FROM communities c
            JOIN courses co ON c.course_id = co.id
            LEFT JOIN community_members cm ON c.id = cm.community_id
            LEFT JOIN community_posts cp ON c.id = cp.community_id
            GROUP BY c.id
            ORDER BY c.id ASC
        """)

    @staticmethod
    def get_by_id(community_id):
        return query_db("""
            SELECT c.*, co.name as course_name
            FROM communities c
            JOIN courses co ON c.course_id = co.id
            WHERE c.id = %s
        """, (community_id,), one=True)

    @staticmethod
    def get_posts(community_id, post_type=None, limit=30):
        if post_type and post_type != 'all':
            return query_db("""
                SELECT cp.*, u.name as author_name, u.role as author_role,
                       COUNT(DISTINCT cc.id) as comment_count,
                       COUNT(DISTINCT pr.id) as reaction_count
                FROM community_posts cp
                JOIN users u ON cp.user_id = u.id
                LEFT JOIN community_comments cc ON cp.id = cc.post_id
                LEFT JOIN post_reactions pr ON cp.id = pr.post_id
                WHERE cp.community_id = %s AND cp.post_type = %s
                GROUP BY cp.id
                ORDER BY cp.created_at DESC LIMIT %s
            """, (community_id, post_type, limit))
        return query_db("""
            SELECT cp.*, u.name as author_name, u.role as author_role,
                   COUNT(DISTINCT cc.id) as comment_count,
                   COUNT(DISTINCT pr.id) as reaction_count
            FROM community_posts cp
            JOIN users u ON cp.user_id = u.id
            LEFT JOIN community_comments cc ON cp.id = cc.post_id
            LEFT JOIN post_reactions pr ON cp.id = pr.post_id
            WHERE cp.community_id = %s
            GROUP BY cp.id
            ORDER BY cp.created_at DESC LIMIT %s
        """, (community_id, limit))

    @staticmethod
    def get_comments(post_id):
        return query_db("""
            SELECT cc.*, u.name as author_name, u.role as author_role
            FROM community_comments cc
            JOIN users u ON cc.user_id = u.id
            WHERE cc.post_id = %s
            ORDER BY cc.created_at ASC
        """, (post_id,))

    @staticmethod
    def create_post(community_id, user_id, title, content, post_type='discussion'):
        return execute_db("""
            INSERT INTO community_posts (community_id, user_id, title, content, post_type)
            VALUES (%s, %s, %s, %s, %s)
        """, (community_id, user_id, title.strip(), content.strip(), post_type))

    @staticmethod
    def add_comment(post_id, user_id, content, is_ai=False):
        return execute_db("""
            INSERT INTO community_comments (post_id, user_id, content, is_ai_assisted)
            VALUES (%s, %s, %s, %s)
        """, (post_id, user_id, content.strip(), is_ai))

    @staticmethod
    def react_post(post_id, user_id, reaction_type='like'):
        existing = query_db("""
            SELECT id FROM post_reactions WHERE post_id = %s AND user_id = %s AND reaction_type = %s
        """, (post_id, user_id, reaction_type), one=True)
        if existing:
            execute_db("DELETE FROM post_reactions WHERE id = %s", (existing['id'],))
            execute_db("UPDATE community_posts SET upvotes = MAX(0, upvotes - 1) WHERE id = %s", (post_id,))
            return False
        else:
            execute_db("""
                INSERT INTO post_reactions (post_id, user_id, reaction_type)
                VALUES (%s, %s, %s)
            """, (post_id, user_id, reaction_type))
            execute_db("UPDATE community_posts SET upvotes = upvotes + 1 WHERE id = %s", (post_id,))
            return True

    @staticmethod
    def report_post(post_id, reporter_id, reason):
        return execute_db("""
            INSERT INTO post_reports (post_id, reporter_id, reason)
            VALUES (%s, %s, %s)
        """, (post_id, reporter_id, reason.strip()))

    @staticmethod
    def get_study_groups(course_id=None):
        if course_id:
            return query_db("""
                SELECT sg.*, c.name as course_name, u.name as leader_name,
                       COUNT(sgm.id) as current_members
                FROM study_groups sg
                JOIN courses c ON sg.course_id = c.id
                JOIN users u ON sg.created_by = u.id
                LEFT JOIN study_group_members sgm ON sg.id = sgm.group_id
                WHERE sg.course_id = %s
                GROUP BY sg.id
                ORDER BY sg.created_at DESC
            """, (course_id,))
        return query_db("""
            SELECT sg.*, c.name as course_name, u.name as leader_name,
                   COUNT(sgm.id) as current_members
            FROM study_groups sg
            JOIN courses c ON sg.course_id = c.id
            JOIN users u ON sg.created_by = u.id
            LEFT JOIN study_group_members sgm ON sg.id = sgm.group_id
            GROUP BY sg.id
            ORDER BY sg.created_at DESC
        """)

    @staticmethod
    def join_study_group(group_id, user_id):
        existing = query_db("SELECT id FROM study_group_members WHERE group_id = %s AND user_id = %s", (group_id, user_id), one=True)
        if existing:
            return existing['id']
        return execute_db("INSERT INTO study_group_members (group_id, user_id, role) VALUES (%s, %s, 'member')", (group_id, user_id))

    @staticmethod
    def get_projects(course_id=None):
        if course_id:
            return query_db("""
                SELECT p.*, c1.name as course1_name, c2.name as course2_name, u.name as lead_name,
                       COUNT(DISTINCT pm.id) as member_count,
                       COUNT(DISTINCT pt.id) as task_count
                FROM projects p
                LEFT JOIN courses c1 ON p.course_id = c1.id
                LEFT JOIN courses c2 ON p.secondary_course_id = c2.id
                JOIN users u ON p.lead_user_id = u.id
                LEFT JOIN project_members pm ON p.id = pm.project_id
                LEFT JOIN project_tasks pt ON p.id = pt.project_id
                WHERE p.course_id = %s OR p.secondary_course_id = %s
                GROUP BY p.id
                ORDER BY p.created_at DESC
            """, (course_id, course_id))
        return query_db("""
            SELECT p.*, c1.name as course1_name, c2.name as course2_name, u.name as lead_name,
                   COUNT(DISTINCT pm.id) as member_count,
                   COUNT(DISTINCT pt.id) as task_count
            FROM projects p
            LEFT JOIN courses c1 ON p.course_id = c1.id
            LEFT JOIN courses c2 ON p.secondary_course_id = c2.id
            JOIN users u ON p.lead_user_id = u.id
            LEFT JOIN project_members pm ON p.id = pm.project_id
            LEFT JOIN project_tasks pt ON p.id = pt.project_id
            GROUP BY p.id
            ORDER BY p.created_at DESC
        """)

    @staticmethod
    def get_challenges(course_id=None):
        if course_id:
            return query_db("""
                SELECT ch.*, c.name as course_name, conc.name as concept_name,
                       COUNT(cp.id) as participants_count
                FROM challenges ch
                JOIN courses c ON ch.course_id = c.id
                LEFT JOIN concepts conc ON ch.concept_id = conc.id
                LEFT JOIN challenge_participants cp ON ch.id = cp.challenge_id
                WHERE ch.course_id = %s
                GROUP BY ch.id
                ORDER BY ch.deadline ASC
            """, (course_id,))
        return query_db("""
            SELECT ch.*, c.name as course_name, conc.name as concept_name,
                   COUNT(cp.id) as participants_count
            FROM challenges ch
            JOIN courses c ON ch.course_id = c.id
            LEFT JOIN concepts conc ON ch.concept_id = conc.id
            LEFT JOIN challenge_participants cp ON ch.id = cp.challenge_id
            GROUP BY ch.id
            ORDER BY ch.deadline ASC
        """)
