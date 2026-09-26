/**
 * Student Dashboard Controller
 */

let videoActivityChart = null;
let masteryBeforeAfterChart = null;

async function loadDashboardData(courseId = null) {
  const url = courseId ? `/api/student/dashboard?course_id=${courseId}` : '/api/student/dashboard';
  try {
    const data = await App.api(url);
    renderDashboard(data);
  } catch (err) {
    console.error('Failed to load dashboard:', err);
  }
}

function renderDashboard(data) {
  const s = data.student || {};
  const plan = data.adaptive_plan || {};
  const currentCourse = data.current_course || {};
  const concept = plan.concept || {};
  const activity = plan.activity || {};

  // 1. Header & Persona Sync
  const nameEl = document.getElementById('studentNameHeader');
  if (nameEl) nameEl.textContent = s.name || 'Learner';

  const select = document.getElementById('globalPersonaSelect');
  if (select && s.user_id) {
    select.value = s.user_id;
  }

  // 2. Metrics Cards
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('metricMastery', `${Math.round(s.overall_mastery || 50)}%`);
  setEl('metricCourse', currentCourse.name || 'Mathematics');
  setEl('metricConcept', concept.name || 'Algebra Fundamentals');
  setEl('metricStreak', `${s.learning_streak || 1} Days 🔥`);
  setEl('metricGoal', s.primary_goal || 'Master concepts');

  // ML State Badge
  const mlBadge = document.getElementById('metricMlState');
  if (mlBadge) {
    const state = plan.ml_learning_state || 'Stable';
    mlBadge.textContent = state;
    mlBadge.className = `badge badge-${state.toLowerCase().replace(' ', '-')}`;
  }

  // 3. Hero Next Best Activity
  setEl('heroActivityTitle', activity.title || 'Next Adaptive Learning Step');
  setEl('heroActivityDesc', activity.description || 'Continuous adaptation based on your performance.');
  setEl('heroRationale', `Adaptive Rationale: ${plan.rationale || 'Tailored to your current mastery.'}`);
  setEl('heroInterest', `Context Applied: ${plan.student_interest || 'Space'} 🚀`);
  setEl('heroDifficulty', `Difficulty: ${activity.difficulty || 'Medium'}`);

  const startBtn = document.getElementById('btnStartActivity');
  if (startBtn) {
    startBtn.onclick = () => {
      window.location.href = `/learning?course_id=${currentCourse.id}&concept_id=${concept.id}&type=${activity.type}`;
    };
  }

  // 4. Render Interactive Knowledge Graph
  renderKnowledgeGraph(data.knowledge_graph);

  // 5. Today's Adaptive Path
  renderAdaptivePath(data.adaptive_path);

  // 6. Enrolled Courses
  renderCourseList(data.enrolled_courses, currentCourse.id);

  // 7. Recommended Playlists
  renderPlaylists(data.recommended_playlists);

  // 8. Continue Watching
  renderContinueWatching(data.continue_watching);

  // 9. AI Coaching Narrative
  const aiCoachEl = document.getElementById('aiCoachText');
  if (aiCoachEl) {
    aiCoachEl.textContent = data.ai_coaching || "Keep practicing consistently to reinforce conceptual memory.";
  }

  // 10. Chart.js Analytics
  renderAnalyticsCharts(data.analytics);
}

function renderKnowledgeGraph(graph) {
  const container = document.getElementById('knowledgeGraphNodes');
  if (!container) return;
  container.innerHTML = '';

  const nodes = graph.nodes || [];
  nodes.forEach((node, idx) => {
    const nodeDiv = document.createElement('div');
    const statusClass = node.status.toLowerCase().replace(' ', '-');
    nodeDiv.className = `dag-node ${statusClass}`;
    nodeDiv.innerHTML = `
      <div style="font-size:0.75rem; color:var(--text-subtle); margin-bottom:0.25rem;">${node.code}</div>
      <div style="font-weight:700; font-size:0.95rem; margin-bottom:0.4rem;">${node.name}</div>
      <div class="progress-bar-container" style="height:6px;">
        <div class="progress-bar-fill ${node.mastery >= 70 ? 'success' : ''}" style="width:${node.mastery}%"></div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin-top:0.4rem;">
        <span class="badge badge-${statusClass}">${node.status}</span>
        <span style="font-weight:700;">${Math.round(node.mastery)}%</span>
      </div>
    `;

    nodeDiv.addEventListener('click', () => {
      if (node.status === 'Locked') {
        const unmet = node.unmet_prerequisites.map(u => `${u.name} (Requires ${u.required}%, Currently ${u.current}%)`).join(', ');
        App.toast(`🔒 Concept Locked! Prerequisite review required: ${unmet || 'Prior concepts need >=70%'}`, 'info');
      } else {
        App.toast(`Opening practice for ${node.name} (Current Mastery: ${node.mastery}%)`, 'info');
        window.location.href = `/learning?course_id=${graph.course_id}&concept_id=${node.id}`;
      }
    });

    container.appendChild(nodeDiv);

    if (idx < nodes.length - 1) {
      const arrow = document.createElement('div');
      arrow.className = 'dag-arrow';
      arrow.textContent = '→';
      container.appendChild(arrow);
    }
  });
}

function renderAdaptivePath(path) {
  const container = document.getElementById('adaptivePathList');
  if (!container) return;
  container.innerHTML = '';

  (path || []).forEach(step => {
    const item = document.createElement('div');
    item.className = `path-step-item ${step.completed ? 'completed' : ''}`;
    item.innerHTML = `
      <div class="path-step-num">${step.completed ? '✓' : step.step}</div>
      <div style="flex:1;">
        <div style="font-weight:600; font-size:0.9rem;">${step.title}</div>
      </div>
      <div>
        ${step.completed ? '<span class="badge badge-mastered">Done</span>' : '<span class="badge badge-learning">Next</span>'}
      </div>
    `;
    container.appendChild(item);
  });
}

function renderCourseList(courses, activeId) {
  const container = document.getElementById('enrolledCoursesList');
  if (!container) return;
  container.innerHTML = '';

  (courses || []).forEach(c => {
    const div = document.createElement('div');
    div.className = `path-step-item ${c.id === activeId ? 'active' : ''}`;
    div.style.cursor = 'pointer';
    div.innerHTML = `
      <div style="font-size:1.25rem;">📚</div>
      <div style="flex:1;">
        <div style="font-weight:700; font-size:0.95rem;">${c.name}</div>
        <div class="progress-bar-container" style="height:5px;">
          <div class="progress-bar-fill" style="width:${c.course_mastery}%"></div>
        </div>
      </div>
      <span style="font-weight:700; font-size:0.85rem; color:#a5b4fc;">${Math.round(c.course_mastery || 0)}%</span>
    `;
    div.onclick = () => loadDashboardData(c.id);
    container.appendChild(div);
  });
}

function renderPlaylists(playlists) {
  const container = document.getElementById('recommendedPlaylistsGrid');
  if (!container) return;
  container.innerHTML = '';

  (playlists || []).forEach(p => {
    const card = document.createElement('div');
    card.className = 'media-card';
    card.innerHTML = `
      <img src="${p.thumbnail_url || 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600'}" class="media-thumb" alt="${p.title}" />
      <div class="media-body">
        <div class="media-title">${p.title}</div>
        <div class="media-channel">📺 ${p.channel_name || 'Educational Channel'} • ${p.difficulty}</div>
        <div class="recommendation-why">💡 ${p.recommendation_reason || 'Matched to your learning gap.'}</div>
        <a href="/videos?playlist_id=${p.id}" class="btn btn-secondary btn-sm" style="margin-top:auto;">
          ▶ Watch Course Playlist
        </a>
      </div>
    `;
    container.appendChild(card);
  });
}

function renderContinueWatching(items) {
  const container = document.getElementById('continueWatchingList');
  if (!container) return;
  container.innerHTML = '';

  if (!items || items.length === 0) {
    container.innerHTML = `<div style="color:var(--text-subtle); padding:1rem; font-size:0.9rem;">No videos currently in progress. Start an adaptive video above!</div>`;
    return;
  }

  items.forEach(v => {
    const card = document.createElement('div');
    card.className = 'media-card';
    card.innerHTML = `
      <img src="${v.thumbnail_url || 'https://img.youtube.com/vi/' + v.youtube_video_id + '/hqdefault.jpg'}" class="media-thumb" alt="${v.video_title}" />
      <div class="media-body">
        <div class="media-title">${v.video_title}</div>
        <div style="font-size:0.8rem; color:var(--text-muted); margin-bottom:0.5rem;">${v.course_name} • ${v.concept_name || 'Topic'}</div>
        <div class="progress-bar-container" style="height:6px;">
          <div class="progress-bar-fill" style="width:${v.progress_percentage}%"></div>
        </div>
        <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin:0.4rem 0 0.8rem 0;">
          <span style="color:var(--text-muted);">${Math.round(v.progress_percentage)}% watched</span>
          <span style="color:var(--text-subtle);">⏱ ${v.duration || '12:00'}</span>
        </div>
        <div style="display:flex; gap:0.5rem; margin-top:auto;">
          <a href="/videos?video_id=${v.video_id}&playlist_id=${v.playlist_id}" class="btn btn-primary btn-sm" style="flex:1;">
            Continue
          </a>
          <button class="btn btn-secondary btn-sm" onclick="markVideoComplete(${v.video_id}, ${v.playlist_id}, ${v.course_id})">
            ✓ Done
          </button>
        </div>
      </div>
    `;
    container.appendChild(card);
  });
}

async function markVideoComplete(videoId, playlistId, courseId) {
  try {
    const res = await App.api('/api/youtube/video/complete', {
      method: 'POST',
      body: { video_id: videoId, playlist_id: playlistId, course_id: courseId }
    });
    App.toast(res.message, 'success');
    loadDashboardData();
  } catch (err) {
    // handled
  }
}

function renderAnalyticsCharts(analytics) {
  if (!window.Chart || !analytics) return;

  // Chart 1: Course Viewing Distribution
  const ctxCourse = document.getElementById('chartCourseViews');
  if (ctxCourse) {
    if (videoActivityChart) videoActivityChart.destroy();
    const courseLabels = (analytics.course_views || []).map(c => c.course_name);
    const courseData = (analytics.course_views || []).map(c => Math.round((c.total_seconds || 600) / 60));

    videoActivityChart = new Chart(ctxCourse, {
      type: 'doughnut',
      data: {
        labels: courseLabels.length ? courseLabels : ['Mathematics', 'Computer Science'],
        datasets: [{
          data: courseData.length ? courseData : [45, 25],
          backgroundColor: ['#6366f1', '#06b6d4', '#10b981', '#f59e0b', '#ec4899'],
          borderColor: '#0f172a',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom', labels: { color: '#94a3b8' } }
        }
      }
    });
  }

  // Chart 2: Mastery Before vs After Learning Activity
  const ctxMastery = document.getElementById('chartMasteryDelta');
  if (ctxMastery) {
    if (masteryBeforeAfterChart) masteryBeforeAfterChart.destroy();
    const deltas = analytics.mastery_delta || [];
    const labels = deltas.map(d => d.concept_name);
    const beforeData = deltas.map(d => d.before_mastery);
    const currentData = deltas.map(d => d.current_mastery);

    masteryBeforeAfterChart = new Chart(ctxMastery, {
      type: 'bar',
      data: {
        labels: labels.length ? labels : ['Algebra', 'Functions', 'Statistics'],
        datasets: [
          {
            label: 'Before Activity (%)',
            data: beforeData.length ? beforeData : [40, 45, 28],
            backgroundColor: 'rgba(100, 116, 139, 0.6)',
            borderRadius: 4
          },
          {
            label: 'Demonstrated Mastery (%)',
            data: currentData.length ? currentData : [85, 72, 43],
            backgroundColor: '#6366f1',
            borderRadius: 4
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
  loadDashboardData();
});
