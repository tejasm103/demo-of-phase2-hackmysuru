import os
import joblib
import numpy as np
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from config import Config

MODEL_CLASSES = ['Needs Support', 'Stable', 'Improving']

def generate_educational_training_dataset(n_samples=600):
    """
    Generates a realistic educational synthetic dataset based on cognitive learning curves:
    Features:
    [assessment_score, practice_score, attempt_count, incorrect_count, previous_mastery, trend_slope, video_engagement, time_hours]
    """
    np.random.seed(42)
    X = []
    y = []

    # 1. Needs Support samples
    for _ in range(n_samples // 3):
        score = np.random.uniform(15.0, 52.0)
        practice = np.random.uniform(20.0, 55.0)
        attempts = np.random.randint(5, 18)
        incorrect = np.random.randint(4, attempts + 1)
        prev_mastery = np.random.uniform(10.0, 48.0)
        trend = np.random.uniform(-0.5, 0.05)
        video_eng = np.random.uniform(10.0, 60.0)
        time_h = np.random.uniform(0.5, 48.0)
        X.append([score, practice, attempts, incorrect, prev_mastery, trend, video_eng, time_h])
        y.append('Needs Support')

    # 2. Stable samples
    for _ in range(n_samples // 3):
        score = np.random.uniform(50.0, 76.0)
        practice = np.random.uniform(52.0, 78.0)
        attempts = np.random.randint(4, 14)
        incorrect = np.random.randint(1, max(2, attempts // 2))
        prev_mastery = np.random.uniform(50.0, 74.0)
        trend = np.random.uniform(-0.1, 0.15)
        video_eng = np.random.uniform(50.0, 85.0)
        time_h = np.random.uniform(1.0, 24.0)
        X.append([score, practice, attempts, incorrect, prev_mastery, trend, video_eng, time_h])
        y.append('Stable')

    # 3. Improving samples
    for _ in range(n_samples // 3):
        score = np.random.uniform(75.0, 100.0)
        practice = np.random.uniform(78.0, 100.0)
        attempts = np.random.randint(3, 12)
        incorrect = np.random.randint(0, max(1, attempts // 4))
        prev_mastery = np.random.uniform(70.0, 95.0)
        trend = np.random.uniform(0.1, 0.6)
        video_eng = np.random.uniform(70.0, 100.0)
        time_h = np.random.uniform(0.5, 12.0)
        X.append([score, practice, attempts, incorrect, prev_mastery, trend, video_eng, time_h])
        y.append('Improving')

    return np.array(X), np.array(y)

def train_and_save_model():
    """Trains a DecisionTreeClassifier on educational features and saves model artifact."""
    X, y = generate_educational_training_dataset()
    clf = DecisionTreeClassifier(max_depth=5, min_samples_leaf=4, random_state=42)
    clf.fit(X, y)

    Config.ML_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(clf, Config.ML_MODEL_PATH)
    print(f"[+] Scikit-learn Decision Tree model trained and saved to {Config.ML_MODEL_PATH}")
    return clf

def load_or_train_model():
    if os.path.exists(Config.ML_MODEL_PATH):
        try:
            return joblib.load(Config.ML_MODEL_PATH)
        except Exception:
            return train_and_save_model()
    return train_and_save_model()
