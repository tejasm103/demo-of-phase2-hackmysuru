from database.db import query_db
from models.mastery import Mastery
from config import Config

class KnowledgeGraph:
    @staticmethod
    def get_graph_data(student_id, course_id):
        """
        Builds graph structure:
        - Nodes: All concepts with student mastery status (Mastered, Learning, Needs Practice, Locked)
        - Edges: Directed prerequisite dependencies
        - Summary metrics: total_nodes, mastered_count, learning_count, locked_count
        """
        concepts_mastery = Mastery.get_student_mastery_for_course(student_id, course_id)
        
        edges = query_db("""
            SELECT cp.concept_id, cp.prerequisite_id, cp.min_mastery_required
            FROM concept_prerequisites cp
            JOIN concepts c ON cp.concept_id = c.id
            WHERE c.course_id = %s
        """, (course_id,))

        nodes = []
        mastered_count = 0
        learning_count = 0
        needs_practice_count = 0
        locked_count = 0

        for c in concepts_mastery:
            st = c['status']
            if st == 'Mastered':
                mastered_count += 1
                color = '#10b981' # Green
                icon = 'check-circle'
            elif st == 'Learning':
                learning_count += 1
                color = '#3b82f6' # Blue
                icon = 'play-circle'
            elif st == 'Needs Practice':
                needs_practice_count += 1
                color = '#f59e0b' # Yellow
                icon = 'alert-circle'
            else: # Locked
                locked_count += 1
                color = '#64748b' # Gray
                icon = 'lock'

            nodes.append({
                'id': c['id'],
                'name': c['name'],
                'code': c['code'],
                'description': c['description'],
                'difficulty': c['difficulty'],
                'hierarchy_order': c['hierarchy_order'],
                'mastery': round(float(c['mastery_percentage']), 1),
                'status': st,
                'color': color,
                'icon': icon,
                'unmet_prerequisites': c.get('unmet_prerequisites', [])
            })

        formatted_edges = []
        for e in edges:
            formatted_edges.append({
                'from': e['prerequisite_id'],
                'to': e['concept_id'],
                'min_mastery': float(e['min_mastery_required'])
            })

        return {
            'course_id': course_id,
            'student_id': student_id,
            'gating_threshold': Config.MASTERY_THRESHOLD,
            'nodes': nodes,
            'edges': formatted_edges,
            'stats': {
                'total_nodes': len(nodes),
                'mastered_count': mastered_count,
                'learning_count': learning_count,
                'needs_practice_count': needs_practice_count,
                'locked_count': locked_count
            }
        }
