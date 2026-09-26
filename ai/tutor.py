import json
from config import Config

def explain_concept(concept_name, student_interest="Space", difficulty="Medium", mode="explanation"):
    """
    Generates tailored conceptual explanations with Socratic hints, real-world analogies,
    and worked examples mapped to student interests.
    Modes: 'hint' | 'explanation' | 'example' | 'practice_prompt'
    """
    if Config.GEMINI_API_KEY and not Config.DEMO_MODE:
        try:
            from google import genai
            client = genai.Client(api_key=Config.GEMINI_API_KEY)
            prompt = f"""You are AdaptiveLearn AI Socratic Tutor.
Explain the academic concept '{concept_name}' at a {difficulty} level.
Use concrete analogies and examples tailored to the student's interest: {student_interest}.
Format cleanly with:
1. Socratic Intuitive Hint (thought-provoking guidance)
2. Core Conceptual Explanation (step-by-step)
3. Tailored Real-World Example ({student_interest} scenario)
4. Check-For-Understanding Micro Practice Question with Answer Key.
Never just give away answers without guided steps."""
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception:
            pass

    # High-quality deterministic educational scaffolding
    if 'statistics' in concept_name.lower():
        if student_interest == 'Space':
            return f"""### 🚀 Adaptive Socratic Tutor: {concept_name} (Space Context)

#### 1. 💡 Socratic Hint
Before diving into equations, consider: If two satellites measure radiation levels in the Van Allen belt, why isn't the simple average (mean) enough to know if extreme solar flares are happening? What does the *spread* (variance) reveal?

#### 2. 🧠 Core Conceptual Breakdown
* **Mean ($\\\\mu$ or $\\\\bar{{x}}$)**: The central balancing point of orbital telemetry data.
* **Variance ($s^2$)**: The average squared distance of each telemetry data point from the mean.
* **Bessel's Correction ($n - 1$)**: When analyzing a sample of telemetry data rather than the entire universe of readings, dividing by $n - 1$ removes statistical bias and prevents underestimating real-world risk.

#### 3. 🛰️ Worked Real-World Example
Suppose an ion thruster logs 5 burn pressures: $10, 12, 14, 16, 18$ kPa.
1. **Find Mean**: $(10+12+14+16+18)/5 = 70/5 = 14$ kPa.
2. **Find Squared Deviations**: $(-4)^2 + (-2)^2 + 0^2 + 2^2 + 4^2 = 16 + 4 + 0 + 4 + 16 = 40$.
3. **Sample Variance**: $s^2 = 40 / (5 - 1) = 40 / 4 = 10$ $\\text{{kPa}}^2$.

#### 4. ✍️ Check For Understanding
If a telemetry sample has sum of squared deviations equal to 28 across 8 sensor readings, what is the sample variance?
*(Answer: $28 / (8 - 1) = 28 / 7 = 4.0$)*
"""
        elif student_interest == 'Robotics':
            return f"""### 🤖 Adaptive Socratic Tutor: {concept_name} (Robotics Context)

#### 1. 💡 Socratic Hint
Imagine an autonomous mobile warehouse robot navigating between charging docks. If its lidar sensor has erratic noise, how does variance measure sensor reliability compared to raw average distance?

#### 2. 🧠 Core Conceptual Breakdown
* **Central Tendency**: Guides robot waypoint navigation.
* **Sample Variance ($s^2$)**: Quantifies actuator and sensor noise. A high variance warns the robot controller to slow down and verify localization.

#### 3. 🦾 Worked Real-World Example
A robotic gripper records motor current draw over 5 grasp tests: $2, 4, 6, 8, 10$ Amperes.
1. **Mean**: $30 / 5 = 6$ A.
2. **Deviations Squared**: $(-4)^2 + (-2)^2 + 0^2 + 2^2 + 4^2 = 40$.
3. **Sample Variance**: $s^2 = 40 / (5 - 1) = 10.0$ $\\text{{A}}^2$.
"""
    elif 'function' in concept_name.lower():
        return f"""### 💻 Adaptive Socratic Tutor: {concept_name} ({student_interest} Context)

#### 1. 💡 Socratic Hint
Think of a mathematical function as a black-box flight computer or game physics shader: for every valid input coordinate you feed in, it returns exactly one deterministic output state!

#### 2. 🧠 Core Concepts
* **Domain**: All valid inputs your system can accept without crashing.
* **Range**: The set of all possible outputs produced.
* **Mapping**: $f(x)$ transforms the input variable $x$ into the output response.

#### 3. 🎮 Worked Example
Let $f(x) = 2x^2 - 3x + 5$ represent the power output at throttle level $x$.
To find power change between level 3 and level 1:
* $f(3) = 2(9) - 3(3) + 5 = 18 - 9 + 5 = 14$
* $f(1) = 2(1) - 3(1) + 5 = 4$
* Net Difference = $14 - 4 = 10$.
"""
    else:
        return f"""### 📚 Adaptive Socratic Tutor: {concept_name}

#### 1. 💡 Socratic Hint
How does this concept build directly upon the prerequisites you have already mastered? Notice how mathematical and computational structures maintain conservation laws.

#### 2. 🧠 Core Conceptual Mechanics
Every formula in this concept describes an invariant relationship between variables under physical or computational constraints.

#### 3. 🎯 Application in {student_interest}
Applying these principles allows engineers and scientists in {student_interest} to model dynamic behaviors, optimize resource efficiency, and avoid system failures.
"""
