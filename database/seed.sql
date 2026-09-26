-- ======================================================================
-- AdaptiveLearn AI - Comprehensive Seed Data
-- ======================================================================

USE adaptivelearn_db;

-- 1. Schools
INSERT INTO schools (id, name, institution_id, board_curriculum, academic_year, address) VALUES
(1, 'Apex International STEM Academy', 'SCH-APEX-2026', 'CBSE & Advanced STEM', '2026-2027', 'Tech Corridor, Silicon Valley / Bengaluru'),
(2, 'Metro Heights Collegiate School', 'SCH-METRO-102', 'International Baccalaureate (IB)', '2026-2027', 'Academic Park Central');

-- 2. Grades
INSERT INTO grades (id, school_id, name, code) VALUES
(1, 1, 'Grade 8', 'G8'),
(2, 1, 'Grade 9', 'G9'),
(3, 1, 'Grade 10', 'G10'),
(4, 1, 'Grade 11', 'G11'),
(5, 1, 'Grade 12', 'G12'),
(6, 2, 'Grade 10', 'IB-MYP5');

-- 3. Streams
INSERT INTO streams (id, name, description) VALUES
(1, 'Computer Science', 'Computing, algorithms, software engineering, and artificial intelligence'),
(2, 'Mathematics', 'Pure, applied, statistics, discrete mathematics, and analytics'),
(3, 'Science', 'Physics, Chemistry, Biology, and foundational scientific investigation'),
(4, 'Electronics', 'Circuits, embedded systems, microcontrollers, and signal processing'),
(5, 'Mechanical', 'Mechanics, dynamics, thermodynamics, and robotics hardware'),
(6, 'Civil', 'Structural design, geospatial analysis, and materials'),
(7, 'Commerce', 'Economics, business mathematics, accounting, and finance');

-- 4. Interests
INSERT INTO interests (id, name, icon) VALUES
(1, 'Space', 'rocket'),
(2, 'Robotics', 'cpu'),
(3, 'Gaming', 'gamepad'),
(4, 'Sports', 'trophy'),
(5, 'Technology', 'laptop'),
(6, 'Cars', 'car'),
(7, 'Business', 'trending-up'),
(8, 'Environment', 'leaf'),
(9, 'Music', 'music'),
(10, 'Art', 'palette');

-- 5. Courses
INSERT INTO courses (id, school_id, name, code, grade_level, description, icon, color_accent) VALUES
(1, 1, 'Mathematics', 'MATH101', 'Grade 10', 'Foundational and advanced mathematics: Algebra, Functions, Statistics, Probability, and Applied Machine Learning Math.', 'compass', '#6366f1'),
(2, 1, 'Computer Science', 'CS101', 'Grade 10', 'Computational thinking, Python programming, data structures, algorithms, and modular design.', 'terminal', '#06b6d4'),
(3, 1, 'Physics', 'PHYS101', 'Grade 10', 'Classical mechanics, energy, thermodynamics, electromagnetism, and modern physical phenomena.', 'zap', '#f59e0b'),
(4, 1, 'Science', 'SCI101', 'Grade 10', 'Integrated physical, chemical, and environmental sciences with investigative labs.', 'activity', '#10b981'),
(5, 1, 'English', 'ENG101', 'Grade 10', 'Analytical reading, rhetoric, technical communication, and literature exploration.', 'book-open', '#ec4899');

-- 6. Concepts (with hierarchy & prerequisite DAG)
-- Mathematics Concepts
INSERT INTO concepts (id, course_id, name, code, description, difficulty, hierarchy_order, weight) VALUES
(1, 1, 'Algebra Fundamentals', 'MATH-ALG', 'Linear equations, polynomials, inequalities, and algebraic transformations.', 'Easy', 1, 1.0),
(2, 1, 'Functions & Relations', 'MATH-FUNC', 'Function mapping, domain, range, linear, quadratic, and exponential models.', 'Medium', 2, 1.2),
(3, 1, 'Statistics & Distributions', 'MATH-STAT', 'Measures of central tendency, variance, standard deviation, and normal distributions.', 'Medium', 3, 1.3),
(4, 1, 'Probability Theory', 'MATH-PROB', 'Conditional probability, Bayes theorem, independent events, and combinatorics.', 'Hard', 4, 1.5),
(5, 1, 'Machine Learning Math', 'MATH-ML', 'Matrix transformations, gradient descent principles, loss functions, and optimization.', 'Hard', 5, 1.8);

-- Computer Science Concepts
INSERT INTO concepts (id, course_id, name, code, description, difficulty, hierarchy_order, weight) VALUES
(6, 2, 'Programming Basics', 'CS-BASICS', 'Syntax, data types, standard input/output, and algorithmic execution.', 'Easy', 1, 1.0),
(7, 2, 'Variables & Control Flow', 'CS-VARS', 'Conditionals, nested logic, while/for loops, and execution branching.', 'Medium', 2, 1.2),
(8, 2, 'Functions & Modularity', 'CS-FUNC', 'Function definitions, parameters, return values, scope, recursion, and docstrings.', 'Medium', 3, 1.4),
(9, 2, 'Data Structures', 'CS-DS', 'Lists, dictionaries, sets, tuples, stacks, queues, and complexity analysis.', 'Hard', 4, 1.6),
(10, 2, 'Algorithms & Optimization', 'CS-ALGO', 'Searching, sorting, recursion trees, dynamic programming, and Big O notation.', 'Hard', 5, 1.8);

-- Physics Concepts
INSERT INTO concepts (id, course_id, name, code, description, difficulty, hierarchy_order, weight) VALUES
(11, 3, 'Classical Mechanics', 'PHYS-MECH', 'Kinematics, Newton laws of motion, friction, and momentum conservation.', 'Easy', 1, 1.0),
(12, 3, 'Work, Energy & Thermodynamics', 'PHYS-THERM', 'Work-energy theorem, conservation of energy, thermal expansion, and heat cycles.', 'Medium', 2, 1.3),
(13, 3, 'Electromagnetism', 'PHYS-EM', 'Electric fields, Coulomb law, magnetic flux, induction, and Maxwell foundations.', 'Hard', 3, 1.5),
(14, 3, 'Modern Physics', 'PHYS-MOD', 'Photoelectric effect, wave-particle duality, atomic models, and relativity basics.', 'Hard', 4, 1.7);

-- 7. Concept Prerequisites (Gating Threshold = 70.0%)
INSERT INTO concept_prerequisites (id, concept_id, prerequisite_id, min_mastery_required) VALUES
(1, 2, 1, 70.0), -- Functions requires Algebra
(2, 3, 2, 70.0), -- Statistics requires Functions
(3, 4, 3, 70.0), -- Probability requires Statistics
(4, 5, 4, 70.0), -- ML Math requires Probability
(5, 7, 6, 70.0), -- Variables requires Programming Basics
(6, 8, 7, 70.0), -- Functions requires Variables & Control Flow
(7, 9, 8, 70.0), -- Data Structures requires Functions
(8, 10, 9, 70.0), -- Algorithms requires Data Structures
(9, 12, 11, 70.0), -- Thermodynamics requires Mechanics
(10, 13, 12, 70.0), -- Electromagnetism requires Thermodynamics
(11, 14, 13, 70.0); -- Modern Physics requires Electromagnetism

-- 8. Users (Password is 'password123' for all demo accounts)
INSERT INTO users (id, name, email, password_hash, role, status) VALUES
(1, 'Rahul Sharma', 'rahul@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'student', 'active'),
(2, 'Priya Patel', 'priya@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'student', 'active'),
(3, 'Arjun Verma', 'arjun@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'student', 'active'),
(4, 'Ananya Iyer', 'ananya@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'student', 'active'),
(5, 'Kiran Rao', 'kiran@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'student', 'active'),
(6, 'Dr. Robert Sharma', 'teacher@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'facilitator', 'active'),
(7, 'Principal Elena Davis', 'admin@school.edu', 'scrypt:32768:8:1$hYyi8RLZlT98Udvk$c02c085e17b50b6320bc4d998e10a8833fa817dc7aea1be842a31e6320eb766a36a36c96cb1b8ee4b187dd5a972a4c7dea6bc3e49dda17bf221db518e0c675d4', 'admin', 'active');

-- 9. Facilitators
INSERT INTO facilitators (id, user_id, school_id, department, title) VALUES
(1, 6, 1, 'Mathematics & Computing', 'Lead Adaptive Learning Facilitator');

-- 10. Students Profiles
INSERT INTO students (id, user_id, school_id, grade_id, stream_id, academic_level, preferred_learning_style, current_skill_level, primary_goal, diagnostic_completed, overall_mastery, learning_streak) VALUES
(1, 1, 1, 3, 2, 'Grade 10 High School', 'Visual & Guided Practice', 'Intermediate', 'Master competitive mathematics & pass with distinction', TRUE, 50.0, 5),
(2, 2, 1, 3, 2, 'Grade 10 High School', 'Interactive Problem Solving', 'Advanced', 'Prepare for Math Olympiad & AI foundations', TRUE, 84.0, 14),
(3, 3, 1, 3, 1, 'Grade 10 High School', 'Project-Based & Practical', 'Intermediate', 'Learn programming & build autonomous game algorithms', TRUE, 77.0, 8),
(4, 4, 1, 4, 3, 'Grade 11 High School', 'Conceptual & Derivations', 'Advanced', 'Excel in Physics & environmental sensor networks', TRUE, 88.0, 12),
(5, 5, 1, 3, 1, 'Grade 10 High School', 'Step-by-Step Guidance', 'Beginner', 'Improve fundamentals & build study habits', FALSE, 0.0, 1);

-- 11. Student Interests
INSERT INTO student_interests (student_id, interest_id, is_primary) VALUES
(1, 1, TRUE),   -- Rahul: Space
(1, 5, FALSE),  -- Rahul: Technology
(2, 2, TRUE),   -- Priya: Robotics
(2, 5, FALSE),  -- Priya: Technology
(3, 3, TRUE),   -- Arjun: Gaming
(3, 1, FALSE),  -- Arjun: Space
(4, 8, TRUE),   -- Ananya: Environment
(4, 2, FALSE),  -- Ananya: Robotics
(5, 5, TRUE);   -- Kiran: Technology

-- 12. Enrollments
INSERT INTO enrollments (student_id, course_id, course_mastery, status) VALUES
(1, 1, 50.0, 'active'), -- Rahul in Math
(1, 2, 45.0, 'active'), -- Rahul in CS
(2, 1, 84.0, 'active'), -- Priya in Math
(2, 2, 90.0, 'active'), -- Priya in CS
(3, 2, 77.0, 'active'), -- Arjun in CS
(3, 1, 65.0, 'active'), -- Arjun in Math
(4, 3, 88.0, 'active'), -- Ananya in Physics
(4, 4, 82.0, 'active'), -- Ananya in Science
(5, 2, 0.0, 'active');  -- Kiran in CS

-- 13. Student Mastery (Demonstrating Individual Adaptation)
-- Rahul: Algebra 85%, Functions 72%, Statistics 43% (NEEDS PRACTICE), Probability 0% (LOCKED)
INSERT INTO student_mastery (student_id, concept_id, mastery_percentage, status, total_attempts, successful_attempts) VALUES
(1, 1, 85.0, 'Mastered', 12, 11),
(1, 2, 72.0, 'Mastered', 10, 7),
(1, 3, 43.0, 'Needs Practice', 14, 6),
(1, 4, 0.0, 'Locked', 0, 0),
(1, 5, 0.0, 'Locked', 0, 0),
-- Priya: Algebra 92%, Functions 88%, Statistics 82%, Probability 74% (LEARNING), ML 0% (LOCKED)
(2, 1, 92.0, 'Mastered', 15, 14),
(2, 2, 88.0, 'Mastered', 12, 11),
(2, 3, 82.0, 'Mastered', 11, 9),
(2, 4, 74.0, 'Learning', 8, 6),
(2, 5, 0.0, 'Locked', 0, 0),
-- Arjun: Basics 88%, Variables 78%, Functions 68% (LEARNING), Data Structures 0% (LOCKED)
(3, 6, 88.0, 'Mastered', 10, 9),
(3, 7, 78.0, 'Mastered', 9, 7),
(3, 8, 68.0, 'Learning', 8, 5),
(3, 9, 0.0, 'Locked', 0, 0),
(3, 10, 0.0, 'Locked', 0, 0),
-- Ananya: Mechanics 90%, Energy 86%, Electromagnetism 88%
(4, 11, 90.0, 'Mastered', 14, 13),
(4, 12, 86.0, 'Mastered', 11, 9),
(4, 13, 88.0, 'Mastered', 12, 11),
(4, 14, 45.0, 'Needs Practice', 5, 2);

-- 14. Real scikit-learn ML Predictions Cache
INSERT INTO ml_predictions (student_id, predicted_state, confidence_score, assessment_score, practice_score, attempt_count, incorrect_count, previous_mastery, trend_slope, video_engagement, features_json) VALUES
(1, 'Needs Support', 0.88, 42.0, 44.0, 14, 8, 48.0, -0.15, 64.0, '{"trend": "declining", "consecutive_errors": 3, "gap": "Statistics"}'),
(2, 'Improving', 0.94, 84.0, 80.0, 15, 2, 78.0, 0.22, 92.0, '{"trend": "accelerating", "consecutive_errors": 0, "gap": "None"}'),
(3, 'Stable', 0.79, 68.0, 70.0, 10, 3, 67.0, 0.02, 75.0, '{"trend": "steady", "consecutive_errors": 1, "gap": "Functions"}'),
(4, 'Improving', 0.91, 88.0, 90.0, 14, 1, 85.0, 0.18, 88.0, '{"trend": "strong", "consecutive_errors": 0, "gap": "None"}');

-- 15. Real YouTube Playlists (Verified Real Educational Channels)
INSERT INTO youtube_playlists (id, youtube_playlist_id, title, description, channel_name, channel_id, thumbnail_url, playlist_url, course_id, difficulty, language, video_count) VALUES
(1, 'PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9', 'Statistics Fundamentals & Distributions', 'Clear, step-by-step intuitive breakdown of statistical distributions, variance, standard deviation, and p-values.', 'StatQuest with Josh Starmer', 'UCtYLUTtgS3k1Fg4y5tAhLbw', 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600&auto=format&fit=crop&q=80', 'https://www.youtube.com/playlist?list=PLblh5JKOoLUK0FLuzwntyYI10UQFUhsY9', 1, 'Beginner', 'en', 12),
(2, 'PL13949EA34DAA4355', 'Probability and Statistics', 'Comprehensive Khan Academy playlist covering fundamental probability rules, independent events, and statistical modeling.', 'Khan Academy', 'UC4a-Gbdw7vOaccHmFo40b9g', 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=600&auto=format&fit=crop&q=80', 'https://www.youtube.com/playlist?list=PL13949EA34DAA4355', 1, 'Beginner', 'en', 25),
(3, 'PLZHQObOWTQDPD3Mnl15PlKeMrLCD6pHBQ', 'Essence of Linear Algebra & Mathematics', 'Geometric intuitions for vectors, matrices, dot products, cross products, and eigenvalues.', '3Blue1Brown', 'UCYO_jab_esuFRV4b17AJtAw', 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=600&auto=format&fit=crop&q=80', 'https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3Mnl15PlKeMrLCD6pHBQ', 1, 'Advanced', 'en', 16),
(4, 'PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB', 'Python Programming for Beginners', 'Complete course on Python syntax, variables, conditionals, functions, and data structures.', 'freeCodeCamp.org', 'UC8butISFwT-Wl7EV0hUK0BQ', 'https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=600&auto=format&fit=crop&q=80', 'https://www.youtube.com/playlist?list=PLWKjhJtqVAbnqBxcdjVGgT3uVR10bzTEB', 2, 'Beginner', 'en', 18),
(5, 'PLhQjrBD2T382_RTW5470yZ8_8k1Fj_2w8', 'CS50: Introduction to Computer Science', 'Harvard university world-renowned introductory curriculum to algorithms, computational concepts, and software architecture.', 'CS50', 'UCcabW7890RKJzL968QWEykA', 'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=600&auto=format&fit=crop&q=80', 'https://www.youtube.com/playlist?list=PLhQjrBD2T382_RTW5470yZ8_8k1Fj_2w8', 2, 'Intermediate', 'en', 24),
(6, 'PL8dPuuaLjXtN0ge7yDk_UA0ldZJdhwkoV', 'Crash Course Physics', 'Entertaining and rigorous exploration of mechanics, Newton laws, thermal energy, and electromagnetism.', 'CrashCourse', 'UCX6b17PVsYBQ0ip5gyeme-Q', 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80', 'https://www.youtube.com/playlist?list=PL8dPuuaLjXtN0ge7yDk_UA0ldZJdhwkoV', 3, 'Beginner', 'en', 46);

-- 16. YouTube Videos (Real Embeddable IDs)
INSERT INTO youtube_videos (id, youtube_video_id, title, description, thumbnail_url, video_url, channel_name, duration, published_at) VALUES
(1, '3d6DsjIBzJ4', 'Statistics Basics: What is Statistics?', 'Introduction to statistics, data collection, central tendency, mean, median, and mode explained simply.', 'https://img.youtube.com/vi/3d6DsjIBzJ4/hqdefault.jpg', 'https://www.youtube.com/watch?v=3d6DsjIBzJ4', 'Khan Academy', '10:45', '2023-01-15 10:00:00'),
(2, 'qBigTkBLU6g', 'Histograms & Probability Distributions Clearly Explained', 'Visual step-by-step intuition for how histograms relate to continuous and discrete probability distributions.', 'https://img.youtube.com/vi/qBigTkBLU6g/hqdefault.jpg', 'https://www.youtube.com/watch?v=qBigTkBLU6g', 'StatQuest with Josh Starmer', '14:20', '2023-04-10 14:30:00'),
(3, 'fNk_zzaMoSs', 'Essence of Calculus & Probability Density', 'Visual exploration of rate of change, areas under curve, and their foundational role in continuous random variables.', 'https://img.youtube.com/vi/fNk_zzaMoSs/hqdefault.jpg', 'https://www.youtube.com/watch?v=fNk_zzaMoSs', '3Blue1Brown', '18:12', '2022-11-20 09:15:00'),
(4, 'rfscVS0vtbw', 'Python Functions Tutorial: Defining, Arguments & Return Values', 'Learn how functions modularize code, handle default arguments, keyword parameters, and return multiple values.', 'https://img.youtube.com/vi/rfscVS0vtbw/hqdefault.jpg', 'https://www.youtube.com/watch?v=rfscVS0vtbw', 'freeCodeCamp.org', '22:40', '2023-05-18 16:00:00'),
(5, 'kjBOesZCoqc', 'CS50 Lecture on Data Structures: Pointers, Lists, Arrays', 'Deep dive into memory organization, lists, linked structures, and computational performance tradeoffs.', 'https://img.youtube.com/vi/kjBOesZCoqc/hqdefault.jpg', 'https://www.youtube.com/watch?v=kjBOesZCoqc', 'CS50', '48:30', '2023-09-02 11:00:00'),
(6, 'k3EG05nmd80', 'Newtonian Mechanics & Motion in One Dimension', 'Position, velocity, acceleration, free-fall motion, and kinematic formulas tested against physical reality.', 'https://img.youtube.com/vi/k3EG05nmd80/hqdefault.jpg', 'https://www.youtube.com/watch?v=k3EG05nmd80', 'CrashCourse', '11:08', '2022-08-14 13:45:00');

-- 17. Playlist Videos Junction
INSERT INTO playlist_videos (id, playlist_id, video_id, position) VALUES
(1, 1, 1, 1),
(2, 1, 2, 2),
(3, 2, 2, 1),
(4, 3, 3, 1),
(5, 4, 4, 1),
(6, 5, 5, 1),
(7, 6, 6, 1);

-- 18. Playlist Concepts Junction
INSERT INTO playlist_concepts (id, playlist_id, concept_id, relevance_score) VALUES
(1, 1, 3, 0.98), -- StatQuest -> Statistics
(2, 2, 3, 0.92), -- Khan Academy -> Statistics
(3, 2, 4, 0.95), -- Khan Academy -> Probability
(4, 3, 5, 0.96), -- 3Blue1Brown -> ML Math
(5, 4, 8, 0.97), -- freeCodeCamp -> Functions
(6, 5, 9, 0.94), -- CS50 -> Data Structures
(7, 6, 11, 0.95); -- CrashCourse -> Mechanics

-- 19. Viewed History (Req 21, 22, 23, 24)
INSERT INTO video_view_history (id, student_id, video_id, playlist_id, course_id, concept_id, started_at, last_watched_at, watch_time_seconds, progress_percentage, completed, replay_count) VALUES
(1, 1, 1, 1, 1, 3, '2026-09-24 14:10:00', '2026-09-24 14:20:45', 645, 100.0, TRUE, 1),
(2, 1, 2, 1, 1, 3, '2026-09-25 10:15:00', '2026-09-25 10:24:10', 550, 64.0, FALSE, 0),
(3, 2, 2, 2, 1, 3, '2026-09-22 09:00:00', '2026-09-22 09:14:20', 860, 100.0, TRUE, 0),
(4, 3, 4, 4, 2, 8, '2026-09-25 16:00:00', '2026-09-25 16:22:40', 1360, 100.0, TRUE, 1);

-- 20. Student Video Progress
INSERT INTO student_video_progress (student_id, video_id, playlist_id, progress_percentage, is_completed, last_position_seconds) VALUES
(1, 1, 1, 100.0, TRUE, 645),
(1, 2, 1, 64.0, FALSE, 550),
(2, 2, 2, 100.0, TRUE, 860),
(3, 4, 4, 100.0, TRUE, 1360);

-- 21. Student Playlist Recommendations (Req 19)
INSERT INTO student_playlist_recommendations (id, student_id, playlist_id, concept_id, recommended_reason, match_score) VALUES
(1, 1, 1, 3, 'Your Statistics mastery is 43%. Review fundamental distributions to unlock Probability.', 0.96),
(2, 1, 2, 3, 'Foundational practice on central tendency and variance recommended by your Facilitator.', 0.91),
(3, 2, 3, 5, 'Your Statistics mastery is 82%. Progressing to Advanced Linear Transformations and Probability.', 0.94),
(4, 3, 4, 8, 'Your Functions mastery is 68%. Solidify parameter passing and return values.', 0.93);

-- 22. Facilitator Interventions (Req 26 & 27)
INSERT INTO interventions (id, student_id, concept_id, facilitator_id, evidence_text, ml_learning_state, recommendation_text, action_type, status) VALUES
(1, 1, 3, 1, 'Diagnostic Score: 42% | Failed Attempts: 3 | Consecutive Errors: 3 | Statistics Mastery: 43% | Trend: Declining', 'Needs Support', '1. Review Statistics fundamentals with StatQuest playlist. 2. Provide guided variance practice. 3. Reassess before unlocking Probability.', 'assign_playlist', 'active');

-- 23. Questions Repository (Rich authentic academic questions with narrative and equations)
INSERT INTO questions (id, course_id, concept_id, difficulty, question_type, narrative_context, options_json, correct_answer, explanation) VALUES
-- Mathematics - Algebra
(1, 1, 1, 'Easy', 'multiple_choice', 'Solve for x: 3x + 12 = 33.', '["x = 5", "x = 7", "x = 9", "x = 11"]', 'x = 7', 'Subtract 12 from both sides to get 3x = 21, then divide by 3 to find x = 7.'),
(2, 1, 1, 'Medium', 'multiple_choice', 'If 2(x - 4) = 3x - 14, what is the value of x^2 - 4?', '["32", "36", "38", "40"]', '32', 'Expanding gives 2x - 8 = 3x - 14. Subtracting 2x yields -8 = x - 14, so x = 6. Then x^2 - 4 = 36 - 4 = 32.'),
-- Mathematics - Functions
(3, 1, 2, 'Medium', 'multiple_choice', 'Given f(x) = 2x^2 - 3x + 5, compute f(3) - f(1).', '["10", "12", "14", "16"]', '10', 'f(3) = 2(9) - 3(3) + 5 = 18 - 9 + 5 = 14. f(1) = 2(1) - 3(1) + 5 = 4. 14 - 4 = 10.'),
-- Mathematics - Statistics
(4, 1, 3, 'Easy', 'multiple_choice', 'Find the mean of the data set: [8, 12, 15, 17, 23].', '["13", "14", "15", "16"]', '15', 'Sum = 8 + 12 + 15 + 17 + 23 = 75. Mean = 75 / 5 = 15.'),
(5, 1, 3, 'Medium', 'multiple_choice', 'A dataset has values [4, 8, 6, 5, 3, 7]. What is the sample variance (s^2)?', '["3.5", "3.0", "2.8", "4.0"]', '3.5', 'Mean = 33/6 = 5.5. Deviations squared sum to 17.5. Dividing by n - 1 (5) yields 3.5.'),
(6, 1, 3, 'Hard', 'multiple_choice', 'In a normal distribution with mean 50 and standard deviation 5, what percentage of values lies between 45 and 55?', '["68.2%", "95.4%", "99.7%", "50.0%"]', '68.2%', 'By the empirical rule, approximately 68.2% of data in a normal distribution falls within ±1 standard deviation of the mean.'),
-- Mathematics - Probability
(7, 1, 4, 'Easy', 'multiple_choice', 'What is the probability of flipping a fair coin twice and getting two heads?', '["1/4", "1/2", "3/4", "1/8"]', '1/4', 'Each flip is independent: P(H and H) = (1/2) * (1/2) = 1/4.'),
(8, 1, 4, 'Medium', 'multiple_choice', 'A box contains 5 red balls and 3 blue balls. If two balls are drawn at random without replacement, what is the probability that both are red?', '["5/14", "25/64", "15/56", "5/8"]', '5/14', 'P(First Red) = 5/8. P(Second Red | First Red) = 4/7. P(Both Red) = (5/8) * (4/7) = 20/56 = 5/14.'),
(9, 1, 4, 'Hard', 'multiple_choice', 'A diagnostic test for a rare condition is 95% accurate. The condition occurs in 1% of the population. Given a positive test, what is the posterior probability via Bayes Theorem?', '["16.1%", "95.0%", "50.0%", "5.0%"]', '16.1%', 'Using Bayes rule: P(Condition|Pos) = (0.95 * 0.01) / (0.95*0.01 + 0.05*0.99) = 0.0095 / 0.0590 ≈ 16.1%.'),
-- Mathematics - Machine Learning Math
(10, 1, 5, 'Easy', 'multiple_choice', 'Given vectors u = [2, 3] and v = [4, -1], compute their dot product u · v.', '["5", "11", "8", "-3"]', '5', 'u · v = (2 * 4) + (3 * -1) = 8 - 3 = 5.'),
(11, 1, 5, 'Medium', 'multiple_choice', 'In gradient descent with learning rate alpha = 0.1, if current weight w = 4.0 and loss derivative dL/dw = 6.0, what is the updated weight w_new?', '["3.4", "4.6", "2.0", "3.6"]', '3.4', 'Weight update formula: w_new = w - alpha * (dL/dw) = 4.0 - 0.1 * 6.0 = 4.0 - 0.6 = 3.4.'),
(12, 1, 5, 'Hard', 'multiple_choice', 'Which loss function is optimal for training a binary neural network classifier?', '["Binary Cross-Entropy", "Mean Squared Error", "Hinge Loss", "L1 Absolute Error"]', 'Binary Cross-Entropy', 'Binary Cross-Entropy directly penalizes probabilistic misclassifications based on log likelihood.'),
-- Computer Science - Basics & Control Flow
(13, 2, 6, 'Easy', 'multiple_choice', 'Which keyword is used in Python to define a function?', '["def", "func", "function", "lambda"]', 'def', 'In Python, functions are defined using the `def` keyword.'),
(14, 2, 7, 'Medium', 'multiple_choice', 'What is the output of the loop: for i in range(1, 6, 2): total += i?', '["9", "15", "6", "10"]', '9', 'The values generated are 1, 3, and 5. Their sum is 1 + 3 + 5 = 9.'),
-- Computer Science - Functions & Structures
(15, 2, 8, 'Medium', 'multiple_choice', 'What does the function return: def calc(n): return n * calc(n-1) if n > 1 else 1 for calc(4)?', '["24", "12", "16", "4"]', '24', 'This is recursive factorial: 4 * 3 * 2 * 1 = 24.'),
(16, 2, 9, 'Hard', 'multiple_choice', 'What is the average time complexity of searching for a key in a Python dictionary (hash map)?', '["O(1)", "O(n)", "O(log n)", "O(n^2)"]', 'O(1)', 'Python dictionaries use hash tables, achieving average O(1) time complexity for lookup.'),
-- Physics - Classical Mechanics & Energy
(17, 3, 11, 'Easy', 'multiple_choice', 'According to Newtons Second Law, what is the net force required to accelerate a 5 kg mass at 4 m/s^2?', '["20 N", "9 N", "1 N", "25 N"]', '20 N', 'F = m * a = 5 kg * 4 m/s^2 = 20 N.'),
(18, 3, 11, 'Medium', 'multiple_choice', 'A projectile is launched with velocity 20 m/s at 30 degrees above the horizontal. What is its initial vertical velocity vy?', '["10 m/s", "17.3 m/s", "20 m/s", "5 m/s"]', '10 m/s', 'vy = v * sin(30°) = 20 * 0.5 = 10 m/s.'),
(19, 3, 12, 'Medium', 'multiple_choice', 'A 2 kg object falls from a height of 10 meters under gravity (g = 9.8 m/s^2). What is its kinetic energy right before impact?', '["196 J", "98 J", "392 J", "49 J"]', '196 J', 'By conservation of energy, KE = PE = m * g * h = 2 * 9.8 * 10 = 196 Joules.');

-- 24. Question Attempts
INSERT INTO question_attempts (student_id, question_id, concept_id, is_diagnostic, student_answer, is_correct, score_earned, attempt_time_seconds, context_interest) VALUES
(1, 4, 3, FALSE, '15', TRUE, 100.0, 35, 'Space'),
(1, 5, 3, FALSE, '4.0', FALSE, 0.0, 80, 'Space'),
(1, 5, 3, FALSE, '3.0', FALSE, 0.0, 72, 'Space'),
(1, 6, 3, FALSE, '95.4%', FALSE, 0.0, 65, 'Space'),
(2, 4, 3, FALSE, '15', TRUE, 100.0, 25, 'Robotics'),
(2, 5, 3, FALSE, '3.5', TRUE, 100.0, 45, 'Robotics'),
(2, 7, 4, FALSE, '5/14', TRUE, 100.0, 40, 'Robotics');

-- 25. Communities
INSERT INTO communities (id, school_id, course_id, concept_id, name, description, is_course_wide) VALUES
(1, 1, 1, 3, 'Mathematics Masters Hub', 'Collaborative peer forum for algebraic transformations, statistics questions, and probability puzzles.', TRUE),
(2, 1, 2, 8, 'Python Coders Guild', 'Algorithm discussions, Python syntax tips, modular programming, and debugging assistance.', TRUE),
(3, 1, 3, 11, 'Physics & Space Dynamics', 'Exploring mechanics, spaceflight trajectories, thermodynamics, and energy systems.', TRUE);

-- 26. Community Members
INSERT INTO community_members (community_id, user_id, role) VALUES
(1, 1, 'member'),
(1, 2, 'mentor'),
(1, 6, 'moderator'),
(2, 3, 'member'),
(2, 2, 'member'),
(3, 4, 'member');

-- 27. Community Posts
INSERT INTO community_posts (id, community_id, user_id, title, content, post_type, upvotes, is_solved) VALUES
(1, 1, 1, 'Need intuition: When do we divide by (n - 1) instead of n in sample variance?', 'Hey everyone! I keep mixing up sample variance vs population variance when calculating deviations. Could someone share an intuitive explanation or analogy?', 'question', 7, TRUE),
(2, 1, 2, 'Bessel Correction Visual Explanation!', 'Think of sample variance as slightly underestimating extreme spreads because your sample rarely captures extreme outliers. Dividing by (n - 1) slightly inflates the result to correct for this bias!', 'discussion', 12, FALSE),
(3, 2, 3, 'Tips for cleanly passing default kwargs in recursive tree algorithms', 'Working on a game state tree generator and noticing mutable default argument bugs in Python. Remember to use `arg=None` and initialize inside!', 'resource', 9, FALSE);

-- 28. Community Comments
INSERT INTO community_comments (id, post_id, user_id, content, is_ai_assisted, is_solution) VALUES
(1, 1, 2, 'Great question Rahul! If you want an analogy: think of estimating the average height of people on Earth using only 5 friends in your room. Your sample is tighter than reality, so Bessel correction (n - 1) compensates.', FALSE, TRUE),
(2, 1, 6, 'Spot on Priya. Also remember, as sample size n grows large (e.g. n=1000), the difference between n and n-1 becomes negligible.', FALSE, FALSE);

-- 29. Study Groups (Req 31)
INSERT INTO study_groups (id, course_id, name, topic, grade_level, max_members, created_by, description) VALUES
(1, 1, 'Probability Beginners Circle', 'Probability Rules & Bayes Intuition', 'Grade 10', 12, 1, 'Weekly collaborative peer problem-solving group dedicated to cracking probability, permutation, and sample space problems.'),
(2, 2, 'Python Algorithm Knights', 'Recursion & Data Structures', 'Grade 10', 15, 3, 'Building and analyzing search and sorting routines, competitive coding practice, and peer code reviews.');

-- 30. Study Group Members
INSERT INTO study_group_members (group_id, user_id, role) VALUES
(1, 1, 'leader'),
(1, 2, 'member'),
(2, 3, 'leader'),
(2, 1, 'member');

-- 31. Community Projects (Req 32: Cross-Course Academic Projects)
INSERT INTO projects (id, title, description, course_id, secondary_course_id, lead_user_id, status, progress_percentage) VALUES
(1, 'Smart Agriculture IoT Sensor Network', 'Design an environmental monitoring station measuring soil moisture, predicting irrigation needs via statistics, and transmitting telemetry via Python microservices.', 3, 2, 4, 'active', 65),
(2, 'School Survey Big Data Analytics', 'Collecting anonymized academic preference data, computing statistical distributions, variance metrics, and rendering interactive dashboards.', 1, 2, 1, 'active', 40),
(3, 'Autonomous Rover Trajectory Simulator', 'Simulating orbital gravitational assists and rover terrain avoidance using Python physics models and vector matrices.', 2, 3, 3, 'active', 80);

-- 32. Project Members
INSERT INTO project_members (project_id, user_id, role) VALUES
(1, 4, 'Project Lead'),
(1, 3, 'Software Engineer'),
(2, 1, 'Lead Data Analyst'),
(2, 2, 'Peer Reviewer'),
(3, 3, 'Algorithm Architect'),
(3, 1, 'Physics Contributor');

-- 33. Project Tasks
INSERT INTO project_tasks (project_id, assigned_to, title, is_completed, due_date) VALUES
(1, 4, 'Calibrate DHT22 sensor readings with baseline physical thermistors', TRUE, '2026-10-05'),
(1, 3, 'Implement Python WebSocket listener for telemetry packet ingestion', FALSE, '2026-10-12'),
(2, 1, 'Calculate standard deviation and mean response times from survey batches', TRUE, '2026-10-02'),
(2, 1, 'Derive normal distribution bell curve overlay for exam score correlations', FALSE, '2026-10-14');

-- 34. Challenges (Req 40 & 41)
INSERT INTO challenges (id, course_id, concept_id, title, description, difficulty, points, deadline) VALUES
(1, 1, 4, 'The Monty Hall Simulation Challenge', 'Write mathematical proofs or empirical simulations explaining why switching doors yields a 2/3 win probability.', 'Medium', 150, '2026-10-20 23:59:59'),
(2, 2, 8, 'Recursion vs Iteration Benchmark Challenge', 'Profile memory and call-stack limits for calculating Fibonacci sequences up to n=100 with memoization.', 'Hard', 200, '2026-10-25 23:59:59');

-- 35. Challenge Participants
INSERT INTO challenge_participants (challenge_id, student_id, score, status) VALUES
(1, 2, 150, 'completed'),
(1, 1, 0, 'joined'),
(2, 3, 185, 'completed');
