/**
 * Viewed History & Video Analytics Controller
 */

let historyAnalyticsChart = null;

async function loadHistoryPage(statusFilter = null, courseId = null) {
  let url = '/api/student/viewed-history?';
  if (statusFilter) url += `status=${statusFilter}&`;
  if (courseId) url += `course_id=${courseId}&`;

  try {
    const historyItems = await App.api(url);
    renderHistoryCards(historyItems);

    const analytics = await App.api('/api/youtube/analytics');
    renderHistoryAnalytics(analytics);
  } catch (err) {
    console.error('Failed to load history:', err);
  }
}

function renderHistoryCards(items) {
  const container = document.getElementById('historyItemsGrid');
  if (!container) return;
  container.innerHTML = '';

  if (!items || items.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1/-1; text-align:center; padding:3rem; color:var(--text-muted);">
        No viewed history found matching these filters. Watch videos in the course to build your history!
      </div>
    `;
    return;
  }

  items.forEach(item => {
    const card = document.createElement('div');
    card.className = 'media-card';
    card.innerHTML = `
      <img src="${item.thumbnail_url || 'https://img.youtube.com/vi/' + item.youtube_video_id + '/hqdefault.jpg'}" class="media-thumb" alt="${item.video_title}" />
      <div class="media-body">
        <div class="media-title">${item.video_title}</div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">
          ${item.course_name} • ${item.concept_name || 'Concept'}
        </div>
        <div class="progress-bar-container" style="height:6px;">
          <div class="progress-bar-fill ${item.completed ? 'success' : ''}" style="width:${item.progress_percentage}%"></div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin:0.4rem 0 0.8rem 0;">
          <span class="badge ${item.completed ? 'badge-mastered' : 'badge-learning'}">
            ${item.completed ? '✓ Completed' : `${Math.round(item.progress_percentage)}% In Progress`}
          </span>
          <span style="color:var(--text-subtle);">⏱ ${Math.round((item.watch_time_seconds || 0) / 60)} mins</span>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.75rem; color:var(--text-subtle); margin-bottom:0.75rem;">
          <span>Replays: ${item.replay_count || 0}</span>
          <span>Last: ${item.last_watched_at ? item.last_watched_at.split(' ')[0] : 'Today'}</span>
        </div>
        <a href="/videos?video_id=${item.video_id}&playlist_id=${item.playlist_id}" class="btn btn-secondary btn-sm" style="margin-top:auto;">
          ▶ ${item.completed ? 'Watch Again' : 'Continue Watching'}
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderHistoryAnalytics(analytics) {
  const sum = analytics.summary || {};
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('statTotalWatched', sum.total_views || 0);
  setEl('statCompleted', sum.completed_count || 0);
  setEl('statInProgress', sum.in_progress_count || 0);
  setEl('statTotalMinutes', `${Math.round((sum.total_watch_seconds || 0) / 60)}m`);
  setEl('statReplays', sum.total_replays || 0);

  if (!window.Chart) return;

  const ctx = document.getElementById('historyMasteryChart');
  if (ctx) {
    if (historyAnalyticsChart) historyAnalyticsChart.destroy();
    const deltas = analytics.mastery_delta || [];
    const labels = deltas.map(d => d.concept_name);
    const beforeData = deltas.map(d => d.before_mastery);
    const afterData = deltas.map(d => d.current_mastery);

    historyAnalyticsChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Algebra', 'Functions', 'Statistics'],
        datasets: [
          {
            label: 'Initial Diagnostic Mastery (%)',
            data: beforeData.length ? beforeData : [40, 45, 28],
            backgroundColor: 'rgba(100, 116, 139, 0.6)',
            borderRadius: 6
          },
          {
            label: 'Mastery After Video + Practice (%)',
            data: afterData.length ? afterData : [85, 72, 43],
            backgroundColor: '#10b981',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        scales: {
          y: { min: 0, max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
          x: { grid: { display: false }, ticks: { color: '#94a3b8' } }
        },
        plugins: {
          legend: { labels: { color: '#cbd5e1' } }
        }
      }
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  // Filter tabs
  document.querySelectorAll('.tab-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.tab-filter').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      loadHistoryPage(filter === 'all' ? null : filter);
    });
  });

  loadHistoryPage();
});
