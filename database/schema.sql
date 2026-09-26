-- ======================================================================
-- AdaptiveLearn AI - Complete MySQL Schema
-- “One platform. Shared knowledge. Personalized learning. Connected learners.”
-- ======================================================================

CREATE DATABASE IF NOT EXISTS adaptivelearn_db;
USE adaptivelearn_db;

-- 1. Core Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    email VARCHAR(160) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('student', 'facilitator', 'admin') NOT NULL DEFAULT 'student',
    status VARCHAR(30) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_email (email),
    INDEX idx_user_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 2. Schools / Institutions
CREATE TABLE IF NOT EXISTS schools (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    institution_id VARCHAR(80) NOT NULL UNIQUE,
    board_curriculum VARCHAR(100) NOT NULL, -- CBSE, ICSE, IB, State Board, etc.
    academic_year VARCHAR(30) NOT NULL,    -- 2026-2027
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3. Grades / Classes
CREATE TABLE IF NOT EXISTS grades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,             -- Grade 8, Grade 9, Grade 10, Grade 11, etc.
    code VARCHAR(30),
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4. Academic Streams
CREATE TABLE IF NOT EXISTS streams (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,       -- Computer Science, Electronics, Mechanical, Civil, Mathematics, Science, Commerce
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5. Courses Table
CREATE TABLE IF NOT EXISTS courses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT DEFAULT NULL,            -- NULL for global shared courses
    name VARCHAR(120) NOT NULL,            -- Mathematics, Computer Science, Science, Physics, Chemistry, Biology, Commerce, etc.
    code VARCHAR(40) NOT NULL UNIQUE,
    grade_level VARCHAR(30),
    description TEXT,
    icon VARCHAR(60) DEFAULT 'book-open',
    color_accent VARCHAR(30) DEFAULT '#4f46e5',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6. Students Profile
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    school_id INT,
    grade_id INT,
    stream_id INT,
    academic_level VARCHAR(50) DEFAULT 'High School',
    preferred_learning_style VARCHAR(50) DEFAULT 'Visual & Practice',
    current_skill_level VARCHAR(50) DEFAULT 'Intermediate',
    primary_goal VARCHAR(120) DEFAULT 'Improve fundamentals & Master concepts',
    diagnostic_completed BOOLEAN DEFAULT FALSE,
    overall_mastery FLOAT DEFAULT 0.0,
    learning_streak INT DEFAULT 1,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL,
    FOREIGN KEY (grade_id) REFERENCES grades(id) ON DELETE SET NULL,
    FOREIGN KEY (stream_id) REFERENCES streams(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7. Facilitators Profile
CREATE TABLE IF NOT EXISTS facilitators (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    school_id INT,
    department VARCHAR(100),
    title VARCHAR(100) DEFAULT 'Senior Educator',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8. Course Enrollments
CREATE TABLE IF NOT EXISTS enrollments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    course_mastery FLOAT DEFAULT 0.0,
    status VARCHAR(30) DEFAULT 'active',
    UNIQUE KEY uq_student_course (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9. Interests Catalog
CREATE TABLE IF NOT EXISTS interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(80) NOT NULL UNIQUE,       -- Space, Robotics, Gaming, Sports, Technology, Cars, Business, Environment, Music, Art
    icon VARCHAR(40) DEFAULT 'sparkles'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10. Student Interests Junction
CREATE TABLE IF NOT EXISTS student_interests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    interest_id INT NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE,
    UNIQUE KEY uq_student_interest (student_id, interest_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (interest_id) REFERENCES interests(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11. Concepts Table
CREATE TABLE IF NOT EXISTS concepts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50) NOT NULL,
    description TEXT,
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    hierarchy_order INT DEFAULT 1,
    weight FLOAT DEFAULT 1.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    INDEX idx_concept_course (course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12. Concept Prerequisites (Knowledge Graph DAG)
CREATE TABLE IF NOT EXISTS concept_prerequisites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    concept_id INT NOT NULL,               -- The target concept
    prerequisite_id INT NOT NULL,          -- Must master this first
    min_mastery_required FLOAT DEFAULT 70.0,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (prerequisite_id) REFERENCES concepts(id) ON DELETE CASCADE,
    UNIQUE KEY uq_concept_prereq (concept_id, prerequisite_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13. Student Mastery (Per Student, Per Concept)
CREATE TABLE IF NOT EXISTS student_mastery (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    concept_id INT NOT NULL,
    mastery_percentage FLOAT DEFAULT 0.0,   -- 0.0 to 100.0
    status ENUM('Mastered', 'Learning', 'Needs Practice', 'Locked') DEFAULT 'Locked',
    total_attempts INT DEFAULT 0,
    successful_attempts INT DEFAULT 0,
    last_evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_concept (student_id, concept_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    INDEX idx_student_mastery (student_id, concept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14. Questions Repository
CREATE TABLE IF NOT EXISTS questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    concept_id INT NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    question_type VARCHAR(40) DEFAULT 'multiple_choice', -- multiple_choice, numeric, short_answer
    narrative_context TEXT NOT NULL,       -- Base question text
    options_json TEXT,                     -- JSON list of options
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    INDEX idx_q_concept (concept_id, difficulty)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 15. Question Attempts History
CREATE TABLE IF NOT EXISTS question_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    question_id INT NOT NULL,
    concept_id INT NOT NULL,
    is_diagnostic BOOLEAN DEFAULT FALSE,
    student_answer TEXT,
    is_correct BOOLEAN NOT NULL,
    score_earned FLOAT DEFAULT 0.0,
    attempt_time_seconds INT DEFAULT 0,
    context_interest VARCHAR(50) DEFAULT 'General',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES questions(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    INDEX idx_attempt_student (student_id, concept_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 16. Learning Activities
CREATE TABLE IF NOT EXISTS learning_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    concept_id INT NOT NULL,
    activity_type VARCHAR(60) NOT NULL,    -- diagnostic, guided_practice, video_lecture, remediation, advanced_challenge, reassessment
    title VARCHAR(180) NOT NULL,
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    status VARCHAR(30) DEFAULT 'assigned', -- assigned, in_progress, completed
    score FLOAT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 17. Facilitator Interventions
CREATE TABLE IF NOT EXISTS interventions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    concept_id INT NOT NULL,
    facilitator_id INT DEFAULT NULL,
    evidence_text TEXT NOT NULL,
    ml_learning_state VARCHAR(50) DEFAULT 'Needs Support',
    recommendation_text TEXT NOT NULL,
    action_type VARCHAR(60) DEFAULT 'prerequisite_review', -- assign_playlist, guided_practice, direct_mentoring, reassess
    status VARCHAR(30) DEFAULT 'pending', -- pending, active, resolved, reassessed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP NULL,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE,
    FOREIGN KEY (facilitator_id) REFERENCES facilitators(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 18. Facilitator Actions Log
CREATE TABLE IF NOT EXISTS facilitator_actions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facilitator_id INT NOT NULL,
    student_id INT NOT NULL,
    intervention_id INT DEFAULT NULL,
    action_name VARCHAR(100) NOT NULL,
    details TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (facilitator_id) REFERENCES facilitators(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (intervention_id) REFERENCES interventions(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 19. Machine Learning Predictions Cache
CREATE TABLE IF NOT EXISTS ml_predictions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    predicted_state ENUM('Improving', 'Stable', 'Needs Support') NOT NULL,
    confidence_score FLOAT DEFAULT 0.0,
    assessment_score FLOAT DEFAULT 0.0,
    practice_score FLOAT DEFAULT 0.0,
    attempt_count INT DEFAULT 0,
    incorrect_count INT DEFAULT 0,
    previous_mastery FLOAT DEFAULT 0.0,
    trend_slope FLOAT DEFAULT 0.0,
    video_engagement FLOAT DEFAULT 0.0,
    features_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    INDEX idx_ml_student (student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 20. YouTube Playlists (Strict Schema Req 20)
CREATE TABLE IF NOT EXISTS youtube_playlists (
    id INT AUTO_INCREMENT PRIMARY KEY,
    youtube_playlist_id VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    channel_name VARCHAR(120),
    channel_id VARCHAR(100),
    thumbnail_url VARCHAR(255),
    playlist_url VARCHAR(255),
    course_id INT NOT NULL,
    difficulty ENUM('Beginner', 'Intermediate', 'Advanced') DEFAULT 'Beginner',
    language VARCHAR(30) DEFAULT 'en',
    video_count INT DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 21. YouTube Videos (Strict Schema Req 20)
CREATE TABLE IF NOT EXISTS youtube_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    youtube_video_id VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    thumbnail_url VARCHAR(255),
    video_url VARCHAR(255),
    channel_name VARCHAR(120),
    duration VARCHAR(40),
    published_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 22. Playlist Videos Junction (Strict Schema Req 20)
CREATE TABLE IF NOT EXISTS playlist_videos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT NOT NULL,
    video_id INT NOT NULL,
    position INT DEFAULT 1,
    FOREIGN KEY (playlist_id) REFERENCES youtube_playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES youtube_videos(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 23. Playlist Concepts Junction (Strict Schema Req 20)
CREATE TABLE IF NOT EXISTS playlist_concepts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    playlist_id INT NOT NULL,
    concept_id INT NOT NULL,
    relevance_score FLOAT DEFAULT 1.0,
    FOREIGN KEY (playlist_id) REFERENCES youtube_playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 24. Student Playlist Recommendations
CREATE TABLE IF NOT EXISTS student_playlist_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    playlist_id INT NOT NULL,
    concept_id INT NOT NULL,
    recommended_reason TEXT,
    match_score FLOAT DEFAULT 0.9,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES youtube_playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 25. Student Video Progress
CREATE TABLE IF NOT EXISTS student_video_progress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    video_id INT NOT NULL,
    playlist_id INT,
    progress_percentage FLOAT DEFAULT 0.0,
    is_completed BOOLEAN DEFAULT FALSE,
    last_position_seconds INT DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_student_video (student_id, video_id),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES youtube_videos(id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES youtube_playlists(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 26. Video View History (Strict Schema Req 20 & 21)
CREATE TABLE IF NOT EXISTS video_view_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    video_id INT NOT NULL,
    playlist_id INT,
    course_id INT NOT NULL,
    concept_id INT,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    watch_time_seconds INT DEFAULT 0,
    progress_percentage FLOAT DEFAULT 0.0,
    completed BOOLEAN DEFAULT FALSE,
    replay_count INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (video_id) REFERENCES youtube_videos(id) ON DELETE CASCADE,
    FOREIGN KEY (playlist_id) REFERENCES youtube_playlists(id) ON DELETE SET NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE SET NULL,
    INDEX idx_view_history (student_id, course_id, last_watched_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 27. Communities Table
CREATE TABLE IF NOT EXISTS communities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    school_id INT DEFAULT NULL,
    course_id INT NOT NULL,
    concept_id INT DEFAULT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT,
    is_course_wide BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 28. Community Members
CREATE TABLE IF NOT EXISTS community_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    community_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(30) DEFAULT 'member',   -- member, moderator, mentor
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_community_user (community_id, user_id),
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 29. Community Posts
CREATE TABLE IF NOT EXISTS community_posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    community_id INT NOT NULL,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    post_type ENUM('question', 'discussion', 'resource', 'announcement') DEFAULT 'discussion',
    upvotes INT DEFAULT 0,
    is_solved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 30. Community Comments
CREATE TABLE IF NOT EXISTS community_comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_ai_assisted BOOLEAN DEFAULT FALSE,
    is_solution BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 31. Post Reactions
CREATE TABLE IF NOT EXISTS post_reactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    user_id INT NOT NULL,
    reaction_type VARCHAR(30) DEFAULT 'like', -- like, helpful, celebrate, insightful
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_post_user_reaction (post_id, user_id, reaction_type),
    FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 32. Post Reports (Moderation & Safety)
CREATE TABLE IF NOT EXISTS post_reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    reporter_id INT NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(30) DEFAULT 'pending', -- pending, reviewed, dismissed, removed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES community_posts(id) ON DELETE CASCADE,
    FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 33. Study Groups
CREATE TABLE IF NOT EXISTS study_groups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    topic VARCHAR(150) NOT NULL,
    grade_level VARCHAR(30),
    max_members INT DEFAULT 20,
    created_by INT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 34. Study Group Members
CREATE TABLE IF NOT EXISTS study_group_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(30) DEFAULT 'member',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_group_user (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES study_groups(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 35. Community Projects (Collaborative Cross-Course)
CREATE TABLE IF NOT EXISTS projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(180) NOT NULL,
    description TEXT,
    course_id INT DEFAULT NULL,
    secondary_course_id INT DEFAULT NULL,
    lead_user_id INT NOT NULL,
    status VARCHAR(30) DEFAULT 'active', -- active, completed, on_hold
    progress_percentage INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE SET NULL,
    FOREIGN KEY (secondary_course_id) REFERENCES courses(id) ON DELETE SET NULL,
    FOREIGN KEY (lead_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 36. Project Members
CREATE TABLE IF NOT EXISTS project_members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    user_id INT NOT NULL,
    role VARCHAR(50) DEFAULT 'contributor',
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_project_user (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 37. Project Tasks
CREATE TABLE IF NOT EXISTS project_tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    assigned_to INT DEFAULT NULL,
    title VARCHAR(180) NOT NULL,
    is_completed BOOLEAN DEFAULT FALSE,
    due_date DATE DEFAULT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 38. Project Milestones
CREATE TABLE IF NOT EXISTS project_milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    target_date DATE DEFAULT NULL,
    is_achieved BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 39. Project Resources
CREATE TABLE IF NOT EXISTS project_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    url VARCHAR(255) NOT NULL,
    resource_type VARCHAR(40) DEFAULT 'document',
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 40. Challenges Table
CREATE TABLE IF NOT EXISTS challenges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    concept_id INT DEFAULT NULL,
    title VARCHAR(180) NOT NULL,
    description TEXT,
    difficulty ENUM('Easy', 'Medium', 'Hard') DEFAULT 'Medium',
    points INT DEFAULT 100,
    deadline TIMESTAMP NULL,
    FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
    FOREIGN KEY (concept_id) REFERENCES concepts(id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 41. Challenge Participants
CREATE TABLE IF NOT EXISTS challenge_participants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    challenge_id INT NOT NULL,
    student_id INT NOT NULL,
    score INT DEFAULT 0,
    status VARCHAR(30) DEFAULT 'joined', -- joined, submitted, completed
    completed_at TIMESTAMP NULL,
    UNIQUE KEY uq_challenge_student (challenge_id, student_id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id) ON DELETE CASCADE,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 42. Community Resources
CREATE TABLE IF NOT EXISTS community_resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    community_id INT NOT NULL,
    shared_by INT NOT NULL,
    title VARCHAR(180) NOT NULL,
    resource_url VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (community_id) REFERENCES communities(id) ON DELETE CASCADE,
    FOREIGN KEY (shared_by) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 43. Community Notifications
CREATE TABLE IF NOT EXISTS community_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    link_url VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
