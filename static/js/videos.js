/**
 * YouTube Learning System & Video Player Controller
 */

let currentVideo = null;
let currentPlaylist = null;
let progressInterval = null;
let currentProgress = 0;

async function initVideoPage() {
  const params = new URLSearchParams(window.location.search);
  const playlistId = params.get('playlist_id') || 1;
  const videoId = params.get('video_id');

  try {
    const data = await App.api(`/api/youtube/playlists/${playlistId}`);
    currentPlaylist = data.playlist;
    const videos = data.videos || [];

    renderPlaylistSidebar(videos);

    if (videoId) {
      const match = videos.find(v => v.id == videoId);
      if (match) loadVideo(match);
      else if (videos.length) loadVideo(videos[0]);
    } else if (videos.length) {
      loadVideo(videos[0]);
    }
  } catch (err) {
    console.error('Failed to load playlist:', err);
  }
}

function renderPlaylistSidebar(videos) {
  const container = document.getElementById('playlistVideoList');
  if (!container) return;
  container.innerHTML = '';

  videos.forEach((v, idx) => {
    const item = document.createElement('div');
    item.className = 'path-step-item';
    item.style.cursor = 'pointer';
    item.innerHTML = `
      <div style="font-weight:700; color:var(--text-subtle);">${idx + 1}</div>
      <img src="${v.thumbnail_url}" style="width:65px; height:42px; object-fit:cover; border-radius:4px;" />
      <div style="flex:1;">
        <div style="font-weight:600; font-size:0.85rem; line-height:1.3;">${v.title}</div>
        <div style="font-size:0.75rem; color:var(--text-muted);">⏱ ${v.duration || '12:00'}</div>
      </div>
    `;
    item.addEventListener('click', () => loadVideo(v));
    container.appendChild(item);
  });
}

async function loadVideo(video) {
  currentVideo = video;
  const titleEl = document.getElementById('videoTitle');
  if (titleEl) titleEl.textContent = video.title;

  const descEl = document.getElementById('videoDesc');
  if (descEl) descEl.textContent = video.description || '';

  const channelEl = document.getElementById('videoChannel');
  if (channelEl) channelEl.textContent = `Channel: ${video.channel_name || 'Educational Partner'}`;

  // Embed YouTube player
  const playerFrame = document.getElementById('youtubeIframe');
  if (playerFrame) {
    playerFrame.src = `https://www.youtube.com/embed/${video.youtube_video_id}?autoplay=1&enablejsapi=1`;
  }

  // Record playback start in viewed history
  try {
    await App.api('/api/youtube/video/start', {
      method: 'POST',
      body: {
        video_id: video.id,
        playlist_id: currentPlaylist.id,
        course_id: currentPlaylist.course_id,
        concept_id: 3
      }
    });
  } catch (e) {}

  // Start simulated progress tracker (representing active engagement)
  currentProgress = 20;
  updateProgressUI(currentProgress);
  if (progressInterval) clearInterval(progressInterval);
  progressInterval = setInterval(() => {
    if (currentProgress < 95) {
      currentProgress += 10;
      updateProgressUI(currentProgress);
      syncProgressBackend(currentProgress, false);
    }
  }, 10000);
}

function updateProgressUI(pct) {
  const fill = document.getElementById('videoProgressFill');
  if (fill) fill.style.width = `${pct}%`;
  const text = document.getElementById('videoProgressText');
  if (text) text.textContent = `${Math.min(100, Math.round(pct))}% completed`;
}

async function syncProgressBackend(pct, completed) {
  if (!currentVideo) return;
  try {
    await App.api('/api/youtube/video/progress', {
      method: 'POST',
      body: {
        video_id: currentVideo.id,
        playlist_id: currentPlaylist ? currentPlaylist.id : 1,
        course_id: currentPlaylist ? currentPlaylist.course_id : 1,
        concept_id: 3,
        progress_percentage: pct,
        watch_time_seconds: Math.round(pct * 6),
        completed: completed
      }
    });
  } catch (e) {}
}

async function handleCompleteVideo() {
  if (!currentVideo) return;
  currentProgress = 100;
  updateProgressUI(100);
  if (progressInterval) clearInterval(progressInterval);

  try {
    const res = await App.api('/api/youtube/video/complete', {
      method: 'POST',
      body: {
        video_id: currentVideo.id,
        playlist_id: currentPlaylist ? currentPlaylist.id : 1,
        course_id: currentPlaylist ? currentPlaylist.course_id : 1,
        concept_id: 3,
        watch_time_seconds: 645
      }
    });
    App.toast(res.message, 'success');
    App.toast('⚠️ Reminder: Video watching does not equal mastery! Demonstrated practice required.', 'info');
  } catch (err) {
    App.toast('Failed to record completion: ' + err.message, 'error');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const completeBtn = document.getElementById('btnMarkVideoDone');
  if (completeBtn) {
    completeBtn.addEventListener('click', handleCompleteVideo);
  }
  initVideoPage();
});
