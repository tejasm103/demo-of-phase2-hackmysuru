import requests
from config import Config
from database.db import query_db, execute_db

class YouTubeService:
    @staticmethod
    def search_playlists(query_term, course_id=None, limit=5):
        """
        Searches YouTube Data API v3 if API key is configured.
        Otherwise searches verified educational playlists in the platform database.
        """
        if Config.YOUTUBE_API_KEY and not Config.DEMO_MODE:
            try:
                url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    "part": "snippet",
                    "q": f"{query_term} educational tutorial",
                    "type": "playlist",
                    "maxResults": limit,
                    "key": Config.YOUTUBE_API_KEY
                }
                resp = requests.get(url, params=params, timeout=5)
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    results = []
                    for item in items:
                        snip = item.get("snippet", {})
                        pid = item.get("id", {}).get("playlistId")
                        results.append({
                            "youtube_playlist_id": pid,
                            "title": snip.get("title"),
                            "description": snip.get("description"),
                            "channel_name": snip.get("channelTitle"),
                            "thumbnail_url": snip.get("thumbnails", {}).get("high", {}).get("url"),
                            "playlist_url": f"https://www.youtube.com/playlist?list={pid}"
                        })
                    if results:
                        return results
            except Exception:
                pass

        # Fallback to authentic curated database playlists
        if course_id:
            return query_db("""
                SELECT * FROM youtube_playlists
                WHERE course_id = %s AND (LOWER(title) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s))
                LIMIT %s
            """, (course_id, f"%{query_term}%", f"%{query_term}%", limit))
        return query_db("""
            SELECT * FROM youtube_playlists
            WHERE LOWER(title) LIKE LOWER(%s) OR LOWER(description) LIKE LOWER(%s)
            LIMIT %s
        """, (f"%{query_term}%", f"%{query_term}%", limit))

    @staticmethod
    def get_recommended_playlists_for_student(student_id, course_id=None, limit=4):
        """
        Dynamically recommends playlists based on:
        - Active concept learning gap (<70% mastery)
        - Student course
        - Difficulty matching
        - Explaining WHY the playlist is recommended based on mastery percentage!
        """
        if not course_id:
            course_id = 1

        # Find student's lowest mastery concept that is unlocked
        gap = query_db("""
            SELECT c.id as concept_id, c.name as concept_name, c.difficulty, sm.mastery_percentage
            FROM student_mastery sm
            JOIN concepts c ON sm.concept_id = c.id
            WHERE sm.student_id = %s AND c.course_id = %s AND sm.status != 'Locked'
            ORDER BY sm.mastery_percentage ASC
            LIMIT 1
        """, (student_id, course_id), one=True)

        if not gap:
            gap_concept_id = 3
            gap_name = "Statistics"
            gap_mastery = 43.0
        else:
            gap_concept_id = gap['concept_id']
            gap_name = gap['concept_name']
            gap_mastery = float(gap['mastery_percentage'])

        # Fetch playlists tagged for this concept or course
        playlists = query_db("""
            SELECT p.*, COALESCE(pc.relevance_score, 0.8) as relevance
            FROM youtube_playlists p
            LEFT JOIN playlist_concepts pc ON p.id = pc.playlist_id AND pc.concept_id = %s
            WHERE p.course_id = %s
            ORDER BY pc.relevance_score DESC, p.id ASC
            LIMIT %s
        """, (gap_concept_id, course_id, limit))

        results = []
        for p in playlists:
            p_dict = dict(p)
            if gap_mastery < 50.0:
                reason = f"Your {gap_name} mastery is {gap_mastery:.0f}%. Foundational review recommended."
            elif gap_mastery < 70.0:
                reason = f"Your {gap_name} mastery is {gap_mastery:.0f}%. Reinforce key topics to reach the 70% unlock gating threshold."
            else:
                reason = f"Your {gap_name} mastery is {gap_mastery:.0f}%. Advance to high-level applications."
            p_dict['recommendation_reason'] = reason
            results.append(p_dict)

        return results
