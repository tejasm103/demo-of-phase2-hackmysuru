/**
 * Course Detail & Knowledge Graph Inspector Controller
 */

async function loadCoursePage() {
  const pathParts = window.location.pathname.split('/');
  const courseId = pathParts[pathParts.length - 1] || 1;

  try {
    const data = await App.api(`/api/courses/${courseId}`);
    renderCourseDetails(data);
  } catch (err) {
    console.error('Failed to load course details:', err);
  }
}

function renderCourseDetails(data) {
  const c = data.course || {};
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('courseTitle', c.name || 'Course');
  setEl('courseCode', c.code || '');
  setEl('courseDesc', c.description || '');

  // Render Concept List
  const conceptList = document.getElementById('courseConceptsList');
  if (conceptList) {
    conceptList.innerHTML = '';
    const nodes = (data.knowledge_graph || {}).nodes || [];
    nodes.forEach(n => {
      const item = document.createElement('div');
      item.className = 'path-step-item';
      item.innerHTML = `
        <div style="font-weight:700; color:var(--text-subtle);">${n.hierarchy_order}</div>
        <div style="flex:1;">
          <div style="font-weight:700; color:#fff;">${n.name}</div>
          <div style="font-size:0.8rem; color:var(--text-muted);">${n.description || ''}</div>
          <div class="progress-bar-container" style="height:5px;">
            <div class="progress-bar-fill ${n.mastery >= 70 ? 'success' : ''}" style="width:${n.mastery}%"></div>
          </div>
        </div>
        <div style="display:flex; flex-direction:column; align-items:flex-end; gap:0.3rem;">
          <span class="badge badge-${n.status.toLowerCase().replace(' ', '-')}">${n.status}</span>
          <span style="font-weight:700; font-size:0.85rem;">${Math.round(n.mastery)}%</span>
        </div>
      `;
      conceptList.appendChild(item);
    });
  }

  // Render Knowledge Graph DAG
  if (window.renderKnowledgeGraph && data.knowledge_graph) {
    renderKnowledgeGraph(data.knowledge_graph);
  }

  // Render Recommended Playlists
  const playContainer = document.getElementById('coursePlaylistsGrid');
  if (playContainer && data.recommended_playlists) {
    playContainer.innerHTML = '';
    data.recommended_playlists.forEach(p => {
      const card = document.createElement('div');
      card.className = 'media-card';
      card.innerHTML = `
        <img src="${p.thumbnail_url || 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=600'}" class="media-thumb" alt="${p.title}" />
        <div class="media-body">
          <div class="media-title">${p.title}</div>
          <div class="media-channel">📺 ${p.channel_name || 'Channel'} • ${p.difficulty}</div>
          <div class="recommendation-why">${p.recommendation_reason || 'Course curriculum aligned.'}</div>
          <a href="/videos?playlist_id=${p.id}" class="btn btn-secondary btn-sm" style="margin-top:auto;">
            ▶ Start Playlist
          </a>
        </div>
      `;
      playContainer.appendChild(card);
    });
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadCoursePage();
});
