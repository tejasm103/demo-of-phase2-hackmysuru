from config import Config

def generate_student_recommendation(student_name, course_name, concept_name, mastery, ml_state, interest):
    """Generates personalized student dashboard coaching narratives."""
    if Config.GEMINI_API_KEY and not Config.DEMO_MODE:
        try:
            from google import genai
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
            prompt = f"Student: {student_name}, Course: {course_name}, Concept: {concept_name}, Mastery: {mastery}%, ML: {ml_state}, Interest: {interest}. Provide a concise 2-sentence encouraging, actionable pedagogical recommendation."
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return resp.text.strip()
        except Exception:
            pass

    if mastery < 50.0:
        return f"We've detected a learning gap in {concept_name} ({mastery:.0f}% mastery). Before taking advanced practice, watch the foundational playlist and complete the guided {interest}-themed problems to build confidence."
    elif mastery < 70.0:
        return f"You're making solid progress in {concept_name} ({mastery:.0f}% mastery). Complete 3 more practice problems to cross the 70% threshold and unlock your next course concept!"
    else:
        return f"Outstanding mastery in {concept_name} ({mastery:.0f}%)! You're ready for advanced synthesis challenges or collaborative peer mentoring in the community."
