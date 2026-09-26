from config import Config

def assist_community_discussion(post_title, post_content, user_query=None):
    """
    AI Community Assistant:
    Provides pedagogical guidance, conceptual hints, discussion summaries,
    and practice suggestions without spoiling final homework answers.
    """
    if Config.GEMINI_API_KEY and not Config.DEMO_MODE:
        try:
            from google import genai
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
            prompt = f"""You are the AdaptiveLearn AI Community Assistant.
Discussion Post: "{post_title}"
Content: "{post_content}"
User Query / Follow-up: "{user_query or 'How can I understand this?'}"

Guidelines:
1. Do NOT just give away the raw answer.
2. Structure your response:
   - 💡 Guided Conceptual Hint
   - 🔍 Clear Explanation of the underlying rule/principle
   - 🧩 Relatable Analogy or small simplified example
   - 🎯 Recommended next practice step
Keep it supportive, academically rigorous, and engaging."""
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            return resp.text.strip()
        except Exception:
            pass

    return f"""### 🤖 Adaptive Community Assistant

* **💡 Conceptual Hint**: When working with sample statistics, remember that your sample represents only a portion of the entire population. Ask yourself: does a small sample typically capture rare extremes?
* **🔍 Core Principle**: Bessel's Correction uses $(n - 1)$ degrees of freedom in the denominator to ensure the sample variance is an unbiased estimator of true population variance $\\\\sigma^2$.
* **🧩 Simplified Analogy**: If you sample 4 temperatures in a city over one morning, you probably missed the coldest midnight and hottest noon. Dividing by $3$ ($n-1$) slightly expands the calculated spread to compensate for what the sample missed!
* **🎯 Recommended Next Step**: Try calculating variance on a 3-element set $[2, 4, 6]$ using both $n$ and $n-1$, and note the variance difference!
"""
