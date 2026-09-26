from database.db import query_db, execute_db
from config import Config

class Mastery:
    @staticmethod
    def get_student_mastery_for_course(student_id, course_id):
        """
        Retrieves all concepts for a course, their prerequisite dependencies,
        and computes the student's current mastery percentage and status.
        Status: Mastered (>=70%), Learning (40-69%), Needs Practice (<40%), Locked (prereq not met).
        """
        threshold = Config.MASTERY_THRESHOLD
        concepts = query_db("""
            SELECT c.id, c.name, c.code, c.description, c.difficulty, c.hierarchy_order, c.weight,
                   COALESCE(sm.mastery_percentage, 0.0) as mastery_percentage,
                   COALESCE(sm.status, 'Locked') as raw_status,
                   COALESCE(sm.total_attempts, 0) as total_attempts,
                   COALESCE(sm.successful_attempts, 0) as successful_attempts
            FROM concepts c
            LEFT JOIN student_mastery sm ON sm.concept_id = c.id AND sm.student_id = %s
            WHERE c.course_id = %s
            ORDER BY c.hierarchy_order ASC
        """, (student_id, course_id))

        # Build mastery lookup dictionary
        mastery_map = {c['id']: c for c in concepts}

        # Fetch prerequisites for all concepts in this course
        prereqs = query_db("""
            SELECT cp.concept_id, cp.prerequisite_id, cp.min_mastery_required
            FROM concept_prerequisites cp
            JOIN concepts c ON cp.concept_id = c.id
            WHERE c.course_id = %s
        """, (course_id,))

        prereq_dict = {}
        for p in prereqs:
            prereq_dict.setdefault(p['concept_id'], []).append(p)

        results = []
        for c in concepts:
            cid = c['id']
            current_pct = float(c['mastery_percentage'])
            reqs = prereq_dict.get(cid, [])
            
            # Check if all prerequisites meet the required mastery
            is_unlocked = True
            unmet_prereqs = []
            for r in reqs:
                prereq_id = r['prerequisite_id']
                required_score = float(r.get('min_mastery_required') or threshold)
                prereq_concept = mastery_map.get(prereq_id)
                prereq_score = float(prereq_concept['mastery_percentage']) if prereq_concept else 0.0
                if prereq_score < required_score:
                    is_unlocked = False
                    if prereq_concept:
                        unmet_prereqs.append({
                            'id': prereq_id,
                            'name': prereq_concept['name'],
                            'current': prereq_score,
                            'required': required_score
                        })

            if not is_unlocked:
                status = 'Locked'
            elif current_pct >= threshold:
                status = 'Mastered'
            elif current_pct >= 40.0:
                status = 'Learning'
            else:
                status = 'Needs Practice'

            # Persist status in DB if changed
            if c['raw_status'] != status:
                Mastery.upsert(student_id, cid, current_pct, status)

            c_dict = dict(c)
            c_dict['computed_status'] = status
            c_dict['status'] = status
            c_dict['prerequisites'] = reqs
            c_dict['unmet_prerequisites'] = unmet_prereqs
            results.append(c_dict)

        return results

    @staticmethod
    def upsert(student_id, concept_id, mastery_percentage, status):
        existing = query_db(
            "SELECT id FROM student_mastery WHERE student_id = %s AND concept_id = %s",
            (student_id, concept_id), one=True
        )
        if existing:
            execute_db("""
                UPDATE student_mastery
                SET mastery_percentage = %s, status = %s, last_evaluated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (mastery_percentage, status, existing['id']))
        else:
            execute_db("""
                INSERT INTO student_mastery (student_id, concept_id, mastery_percentage, status, total_attempts, successful_attempts)
                VALUES (%s, %s, %s, %s, 1, 1)
            """, (student_id, concept_id, mastery_percentage, status))

    @staticmethod
    def update_from_performance(student_id, concept_id, score_earned, is_correct):
        """
        Updates student mastery after an assessment or practice attempt.
        Uses adaptive weighted update:
        New Mastery = Previous Mastery * 0.65 + Score Earned * 0.35
        Increments attempts and recalculates status.
        """
        threshold = Config.MASTERY_THRESHOLD
        existing = query_db(
            "SELECT * FROM student_mastery WHERE student_id = %s AND concept_id = %s",
            (student_id, concept_id), one=True
        )

        if existing:
            prev_pct = float(existing['mastery_percentage'])
            total_att = int(existing['total_attempts']) + 1
            succ_att = int(existing['successful_attempts']) + (1 if is_correct else 0)
            
            # Adaptive smoothing formula
            new_pct = round(prev_pct * 0.60 + score_earned * 0.40, 1)
            new_pct = min(100.0, max(0.0, new_pct))
            
            new_status = 'Mastered' if new_pct >= threshold else ('Learning' if new_pct >= 40.0 else 'Needs Practice')

            execute_db("""
                UPDATE student_mastery
                SET mastery_percentage = %s, status = %s, total_attempts = %s, successful_attempts = %s,
                    last_evaluated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_pct, new_status, total_att, succ_att, existing['id']))
        else:
            prev_pct = 0.0
            new_pct = min(100.0, max(0.0, round(float(score_earned), 1)))
            new_status = 'Mastered' if new_pct >= threshold else ('Learning' if new_pct >= 40.0 else 'Needs Practice')
            total_att = 1
            succ_att = 1 if is_correct else 0
            execute_db("""
                INSERT INTO student_mastery (student_id, concept_id, mastery_percentage, status, total_attempts, successful_attempts)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, concept_id, new_pct, new_status, total_att, succ_att))

        # Update overall student course mastery
        concept = query_db("SELECT course_id FROM concepts WHERE id = %s", (concept_id,), one=True)
        if concept:
            course_id = concept['course_id']
            avg_row = query_db("""
                SELECT AVG(sm.mastery_percentage) as avg_mastery
                FROM student_mastery sm
                JOIN concepts c ON sm.concept_id = c.id
                WHERE sm.student_id = %s AND c.course_id = %s
            """, (student_id, course_id), one=True)
            if avg_row and avg_row['avg_mastery'] is not None:
                execute_db(
                    "UPDATE enrollments SET course_mastery = %s WHERE student_id = %s AND course_id = %s",
                    (round(avg_row['avg_mastery'], 1), student_id, course_id)
                )

        return {
            'previous_mastery': prev_pct,
            'new_mastery': new_pct,
            'status': new_status,
            'unlocked_dependent': new_pct >= threshold
        }
