from models.mastery import Mastery
from config import Config

class AdaptiveMasteryManager:
    @staticmethod
    def evaluate_gating(student_id, concept_id):
        """
        Evaluates whether a student can access concept_id based on prerequisite mastery.
        Returns (can_access, unmet_prerequisites).
        """
        concept_data = Mastery.get_student_mastery_for_course(student_id, None)
        # Search for this concept
        for c in concept_data:
            if c['id'] == concept_id:
                return c['status'] != 'Locked', c.get('unmet_prerequisites', [])
        return True, []

    @staticmethod
    def record_assessment_impact(student_id, concept_id, score, is_correct):
        """Updates mastery and checks if any dependent concepts were unlocked."""
        impact = Mastery.update_from_performance(student_id, concept_id, score, is_correct)
        return impact
