from config import Config

def generate_intervention_strategy(student_name, course_name, concept_name, mastery, evidence_data, ml_state):
    """
    Generates actionable intervention recommendations for teachers/facilitators.
    """
    if Config.GEMINI_API_KEY and not Config.DEMO_MODE:
        try:
            from google import genai
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
            prompt = f"""Generate an actionable educational intervention plan for facilitator:
Student: {student_name}
Course: {course_name}
Struggling Concept: {concept_name} (Mastery: {mastery}%)
Evidence: {evidence_data}
ML Classifier State: {ml_state}
Output 3-4 concrete pedagogical steps: prerequisite review, curated media, scaffolding, and reassessment."""
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return resp.text.strip()
        except Exception:
            pass

    return f"""1. Review foundational prerequisite principles with {student_name} during 1-on-1 office hours.
2. Assign the curated beginner video playlist on {concept_name} with guided notes.
3. Provide 3 scaffolding practice questions with immediate feedback.
4. Schedule a targeted 5-question micro-reassessment once mastery crosses 65%."""
