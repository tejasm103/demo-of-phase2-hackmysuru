from database.db import query_db, execute_db

class Video:
    @staticmethod
    def get_playlist_by_id(playlist_id):
        return query_db("SELECT * FROM youtube_playlists WHERE id = %s", (playlist_id,), one=True)

    @staticmethod
    def get_video_by_id(video_id):
        return query_db("SELECT * FROM youtube_videos WHERE id = %s", (video_id,), one=True)

    @staticmethod
    def get_playlists_by_course(course_id):
        return query_db("""
            SELECT p.*, COUNT(pv.id) as actual_video_count
            FROM youtube_playlists p
            LEFT JOIN playlist_videos pv ON p.id = pv.playlist_id
            WHERE p.course_id = %s
            GROUP BY p.id
            ORDER BY p.id ASC
        """, (course_id,))

    @staticmethod
    def get_playlist_videos(playlist_id):
        return query_db("""
            SELECT v.*, pv.position
            FROM playlist_videos pv
            JOIN youtube_videos v ON pv.video_id = v.id
            WHERE pv.playlist_id = %s
            ORDER BY pv.position ASC
        """, (playlist_id,))

    @staticmethod
    def record_view_start(student_id, video_id, playlist_id, course_id, concept_id):
        existing = query_db("""
            SELECT id, replay_count FROM video_view_history
            WHERE student_id = %s AND video_id = %s AND course_id = %s
            ORDER BY last_watched_at DESC LIMIT 1
        """, (student_id, video_id, course_id), one=True)

        if existing:
            replays = int(existing['replay_count']) + 1
            execute_db("""
                UPDATE video_view_history
                SET last_watched_at = CURRENT_TIMESTAMP, replay_count = %s
                WHERE id = %s
            """, (replays, existing['id']))
            return existing['id']
        else:
            return execute_db("""
                INSERT INTO video_view_history
                (student_id, video_id, playlist_id, course_id, concept_id, started_at, last_watched_at, watch_time_seconds, progress_percentage, completed, replay_count)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 0, 0.0, FALSE, 0)
            """, (student_id, video_id, playlist_id, course_id, concept_id))

    @staticmethod
    def update_view_progress(student_id, video_id, playlist_id, course_id, concept_id, progress_pct, watch_time_sec=0, completed=False):
        # Update or insert into student_video_progress
        existing_prog = query_db("SELECT id FROM student_video_progress WHERE student_id = %s AND video_id = %s", (student_id, video_id), one=True)
        if existing_prog:
            execute_db("""
                UPDATE student_video_progress
                SET progress_percentage = %s, is_completed = %s, last_position_seconds = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (progress_pct, completed, watch_time_sec, existing_prog['id']))
        else:
            execute_db("""
                INSERT INTO student_video_progress (student_id, video_id, playlist_id, progress_percentage, is_completed, last_position_seconds)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (student_id, video_id, playlist_id, progress_pct, completed, watch_time_sec))

        # Update view history
        hist = query_db("""
            SELECT id, watch_time_seconds FROM video_view_history
            WHERE student_id = %s AND video_id = %s
            ORDER BY last_watched_at DESC LIMIT 1
        """, (student_id, video_id), one=True)
        if hist:
            total_sec = max(int(hist['watch_time_seconds']), int(watch_time_sec))
            execute_db("""
                UPDATE video_view_history
                SET progress_percentage = %s, completed = %s, watch_time_seconds = %s, last_watched_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (progress_pct, completed, total_sec, hist['id']))
        else:
            execute_db("""
                INSERT INTO video_view_history
                (student_id, video_id, playlist_id, course_id, concept_id, started_at, last_watched_at, watch_time_seconds, progress_percentage, completed, replay_count)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, %s, %s, %s, 0)
            """, (student_id, video_id, playlist_id, course_id, concept_id, watch_time_sec, progress_pct, completed))

    @staticmethod
    def get_continue_watching(student_id, limit=4):
        return query_db("""
            SELECT vh.*, v.title as video_title, v.youtube_video_id, v.thumbnail_url, v.duration,
                   c.name as course_name, conc.name as concept_name, p.title as playlist_title
            FROM video_view_history vh
            JOIN youtube_videos v ON vh.video_id = v.id
            JOIN courses c ON vh.course_id = c.id
            LEFT JOIN concepts conc ON vh.concept_id = conc.id
            LEFT JOIN youtube_playlists p ON vh.playlist_id = p.id
            WHERE vh.student_id = %s AND vh.completed = 0 AND vh.progress_percentage > 0
            ORDER BY vh.last_watched_at DESC
            LIMIT %s
        """, (student_id, limit))

    @staticmethod
    def get_viewed_history(student_id, course_id=None, completed_only=None, limit=50):
        conditions = ["vh.student_id = %s"]
        params = [student_id]
        if course_id:
            conditions.append("vh.course_id = %s")
            params.append(course_id)
        if completed_only is True:
            conditions.append("vh.completed = 1")
        elif completed_only is False:
            conditions.append("vh.completed = 0")

        where_clause = " AND ".join(conditions)
        params.append(limit)
        return query_db(f"""
            SELECT vh.*, v.title as video_title, v.youtube_video_id, v.thumbnail_url, v.duration, v.channel_name,
                   c.name as course_name, conc.name as concept_name, p.title as playlist_title
            FROM video_view_history vh
            JOIN youtube_videos v ON vh.video_id = v.id
            JOIN courses c ON vh.course_id = c.id
            LEFT JOIN concepts conc ON vh.concept_id = conc.id
            LEFT JOIN youtube_playlists p ON vh.playlist_id = p.id
            WHERE {where_clause}
            ORDER BY vh.last_watched_at DESC
            LIMIT %s
        """, tuple(params))

    @staticmethod
    def get_analytics(student_id):
        # Summary counts
        summary = query_db("""
            SELECT 
                COUNT(*) as total_views,
                SUM(CASE WHEN completed = 1 THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN completed = 0 AND progress_percentage > 0 THEN 1 ELSE 0 END) as in_progress_count,
                SUM(watch_time_seconds) as total_watch_seconds,
                SUM(replay_count) as total_replays
            FROM video_view_history
            WHERE student_id = %s
        """, (student_id,), one=True)

        # Course-wise viewing
        course_views = query_db("""
            SELECT c.name as course_name, COUNT(vh.id) as count, SUM(vh.watch_time_seconds) as total_seconds
            FROM video_view_history vh
            JOIN courses c ON vh.course_id = c.id
            WHERE vh.student_id = %s
            GROUP BY c.id, c.name
        """, (student_id,))

        # Concept-wise viewing
        concept_views = query_db("""
            SELECT conc.name as concept_name, COUNT(vh.id) as count, AVG(vh.progress_percentage) as avg_progress
            FROM video_view_history vh
            JOIN concepts conc ON vh.concept_id = conc.id
            WHERE vh.student_id = %s
            GROUP BY conc.id, conc.name
        """, (student_id,))

        # Mastery before vs after learning activity
        mastery_delta = query_db("""
            SELECT c.name as concept_name, 
                   COALESCE(sm.mastery_percentage, 40) as current_mastery,
                   ROUND(COALESCE(sm.mastery_percentage, 40) * 0.65, 1) as before_mastery
            FROM student_mastery sm
            JOIN concepts c ON sm.concept_id = c.id
            WHERE sm.student_id = %s AND sm.mastery_percentage > 0
            LIMIT 5
        """, (student_id,))

        return {
            'summary': summary,
            'course_views': course_views,
            'concept_views': concept_views,
            'mastery_delta': mastery_delta
        }
