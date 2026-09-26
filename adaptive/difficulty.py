class AdaptiveDifficulty:
    DIFFICULTIES = ['Easy', 'Medium', 'Hard']

    @staticmethod
    def calculate_next_difficulty(current_difficulty, recent_scores, consecutive_errors=0):
        """
        Dynamically adjusts difficulty based on demonstrated performance:
        - If recent performance is high (>=80%) and no consecutive errors: step up difficulty.
        - If consecutive errors >= 2 or recent performance low (<50%): step down difficulty.
        - Otherwise, maintain current level.
        """
        idx = AdaptiveDifficulty.DIFFICULTIES.index(current_difficulty) if current_difficulty in AdaptiveDifficulty.DIFFICULTIES else 1

        if consecutive_errors >= 2:
            return AdaptiveDifficulty.DIFFICULTIES[max(0, idx - 1)]

        if not recent_scores:
            return current_difficulty

        avg_score = sum(recent_scores) / len(recent_scores)

        if avg_score >= 80.0:
            return AdaptiveDifficulty.DIFFICULTIES[min(len(AdaptiveDifficulty.DIFFICULTIES) - 1, idx + 1)]
        elif avg_score < 50.0:
            return AdaptiveDifficulty.DIFFICULTIES[max(0, idx - 1)]
        else:
            return AdaptiveDifficulty.DIFFICULTIES[idx]

    @staticmethod
    def get_remediation_ladder_step(consecutive_errors, current_mastery):
        """
        If repeated errors occur, ladder progression:
        0 -> Easy Practice
        1 -> Guided Example
        2 -> Prerequisite Review
        >=3 -> Remediation + Facilitator Intervention Alert
        """
        if consecutive_errors >= 3 or current_mastery < 40.0:
            return 'remediation_prerequisite_review'
        elif consecutive_errors == 2:
            return 'guided_example'
        elif consecutive_errors == 1:
            return 'easy_practice'
        return 'standard_practice'
