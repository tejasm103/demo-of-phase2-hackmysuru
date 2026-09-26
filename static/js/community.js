/**
 * Community, Study Groups & Projects Controller
 */

async function loadCommunityFeed() {
  try {
    const posts = await App.api('/api/community/1');
    renderPosts(posts.posts);

    const groups = await App.api('/api/study-groups');
    renderStudyGroups(groups);

    const projects = await App.api('/api/projects');
    renderProjects(projects);

    const challenges = await App.api('/api/challenges');
    renderChallenges(challenges);
  } catch (err) {
    console.error('Failed to load community feed:', err);
  }
}

function renderPosts(posts) {
  const container = document.getElementById('communityPostsList');
  if (!container) return;
  container.innerHTML = '';

  (posts || []).forEach(post => {
    const card = document.createElement('div');
    card.className = 'post-card';
    card.innerHTML = `
      <div class="post-meta">
        <span style="font-weight:700; color:#fff;">👤 ${post.author_name}</span>
        <span>•</span>
        <span class="badge ${post.author_role === 'facilitator' ? 'badge-mastered' : 'badge-stable'}">${post.author_role}</span>
        <span>•</span>
        <span>${post.created_at ? post.created_at.split(' ')[0] : 'Today'}</span>
      </div>
      <div class="post-title">${post.title}</div>
      <div class="post-content">${post.content}</div>
      <div class="post-footer">
        <div class="post-actions-group">
          <button class="action-btn" onclick="reactPost(${post.id})">
            👍 <span>${post.upvotes || 0}</span> Upvotes
          </button>
          <button class="action-btn" onclick="toggleComments(${post.id})">
            💬 <span>${post.comment_count || 0}</span> Comments
          </button>
          <button class="action-btn" onclick="askAiAssist(${post.id}, '${escapeQuote(post.title)}', '${escapeQuote(post.content)}')">
            🤖 Ask AI Assistant
          </button>
        </div>
        <button class="action-btn" style="color:var(--text-subtle);" onclick="reportPost(${post.id})">
          ⚠️ Report
        </button>
      </div>
      <div id="commentsThread-${post.id}" class="comment-thread" style="display:none;"></div>
    `;
    container.appendChild(card);
  });
}

function escapeQuote(str) {
  return (str || '').replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

async function reactPost(postId) {
  try {
    const res = await App.api(`/api/community/posts/${postId}/reactions`, { method: 'POST' });
    App.toast(res.liked ? 'Upvoted!' : 'Reaction removed', 'success');
    loadCommunityFeed();
  } catch (e) {}
}

async function toggleComments(postId) {
  const thread = document.getElementById(`commentsThread-${postId}`);
  if (!thread) return;

  if (thread.style.display === 'none') {
    thread.style.display = 'flex';
    try {
      const comments = await App.api(`/api/community/posts/${postId}/comments`);
      renderComments(postId, comments);
    } catch (e) {}
  } else {
    thread.style.display = 'none';
  }
}

function renderComments(postId, comments) {
  const thread = document.getElementById(`commentsThread-${postId}`);
  if (!thread) return;
  thread.innerHTML = '';

  (comments || []).forEach(c => {
    const div = document.createElement('div');
    div.className = `comment-item ${c.is_ai_assisted ? 'ai-assisted' : ''}`;
    div.innerHTML = `
      <div style="display:flex; justify-content:space-between; font-size:0.8rem; margin-bottom:0.25rem;">
        <span style="font-weight:700; color:${c.is_ai_assisted ? '#c084fc' : '#fff'};">
          ${c.is_ai_assisted ? '🤖 Adaptive AI Assistant' : c.author_name}
        </span>
        <span style="color:var(--text-subtle);">${c.created_at ? c.created_at.split(' ')[0] : 'Just now'}</span>
      </div>
      <div style="font-size:0.9rem; color:#cbd5e1;">${c.content.replace(/\n/g, '<br/>')}</div>
    `;
    thread.appendChild(div);
  });

  // Add Comment input
  const inputRow = document.createElement('div');
  inputRow.style.display = 'flex';
  inputRow.style.gap = '0.5rem';
  inputRow.style.marginTop = '0.5rem';
  inputRow.innerHTML = `
    <input type="text" id="newCommentInput-${postId}" placeholder="Write an academic reply or hint..." style="flex:1; background:#0f172a; border:1px solid var(--border-subtle); color:#fff; padding:0.5rem 0.85rem; border-radius:var(--radius-sm); outline:none;" />
    <button class="btn btn-primary btn-sm" onclick="submitComment(${postId})">Reply</button>
  `;
  thread.appendChild(inputRow);
}

async function submitComment(postId) {
  const input = document.getElementById(`newCommentInput-${postId}`);
  if (!input || !input.value.trim()) return;

  try {
    await App.api(`/api/community/posts/${postId}/comments`, {
      method: 'POST',
      body: { content: input.value.trim() }
    });
    App.toast('Reply posted', 'success');
    toggleComments(postId); // refresh
  } catch (e) {}
}

async function askAiAssist(postId, title, content) {
  App.toast('AI Assistant analyzing discussion...', 'info');
  try {
    const res = await App.api('/api/ai/community-assist', {
      method: 'POST',
      body: { title, content }
    });
    // Post as AI comment
    await App.api(`/api/community/posts/${postId}/comments`, {
      method: 'POST',
      body: { content: res.assistance, is_ai_assisted: true }
    });
    App.toast('AI Socratic guidance added to thread!', 'success');
    const thread = document.getElementById(`commentsThread-${postId}`);
    if (thread) {
      thread.style.display = 'flex';
      const comments = await App.api(`/api/community/posts/${postId}/comments`);
      renderComments(postId, comments);
    }
  } catch (err) {
    App.toast('AI Assist error: ' + err.message, 'error');
  }
}

function renderStudyGroups(groups) {
  const container = document.getElementById('studyGroupsGrid');
  if (!container) return;
  container.innerHTML = '';

  (groups || []).forEach(g => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div style="font-size:0.8rem; color:#60a5fa; font-weight:700; margin-bottom:0.4rem;">${g.course_name} • ${g.grade_level}</div>
      <h3 style="font-size:1.15rem; margin-bottom:0.5rem;">${g.name}</h3>
      <div style="font-size:0.85rem; color:#cbd5e1; margin-bottom:1rem;">Topic: <strong>${g.topic}</strong></div>
      <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:1.25rem;">${g.description || 'Weekly peer study circle.'}</p>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto;">
        <span style="font-size:0.8rem; color:var(--text-subtle);">👥 ${g.current_members || 1}/${g.max_members || 20} members</span>
        <button class="btn btn-primary btn-sm" onclick="joinGroup(${g.id})">Join Group</button>
      </div>
    `;
    container.appendChild(card);
  });
}

async function joinGroup(gid) {
  try {
    const res = await App.api(`/api/study-groups/${gid}/join`, { method: 'POST' });
    App.toast(res.message, 'success');
    loadCommunityFeed();
  } catch (e) {}
}

function renderProjects(projects) {
  const container = document.getElementById('projectsGrid');
  if (!container) return;
  container.innerHTML = '';

  (projects || []).forEach(p => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div style="font-size:0.8rem; color:#a855f7; font-weight:700; margin-bottom:0.4rem;">
        ${p.course1_name || 'Physics'} + ${p.course2_name || 'Computer Science'} Cross-Course
      </div>
      <h3 style="font-size:1.15rem; margin-bottom:0.5rem;">${p.title}</h3>
      <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:1rem;">${p.description}</p>
      <div class="progress-bar-container" style="height:6px;">
        <div class="progress-bar-fill" style="width:${p.progress_percentage || 40}%"></div>
      </div>
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; margin:0.4rem 0 1rem 0;">
        <span style="color:var(--text-muted);">${p.progress_percentage || 40}% Complete</span>
        <span style="color:var(--text-subtle);">Lead: ${p.lead_name}</span>
      </div>
      <a href="/projects?project_id=${p.id}" class="btn btn-secondary btn-sm" style="width:100%;">
        View Tasks & Milestones
      </a>
    `;
    container.appendChild(card);
  });
}

function renderChallenges(challenges) {
  const container = document.getElementById('challengesGrid');
  if (!container) return;
  container.innerHTML = '';

  (challenges || []).forEach(ch => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5rem;">
        <span class="badge badge-warning">${ch.difficulty}</span>
        <span style="font-weight:700; color:#f59e0b;">⭐ ${ch.points} Points</span>
      </div>
      <h3 style="font-size:1.1rem; margin-bottom:0.5rem;">${ch.title}</h3>
      <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:1rem;">${ch.description}</p>
      <div style="display:flex; justify-content:space-between; align-items:center; margin-top:auto;">
        <span style="font-size:0.8rem; color:var(--text-subtle);">👥 ${ch.participants_count || 1} Participated</span>
        <button class="btn btn-primary btn-sm" onclick="joinChallenge(${ch.id})">Take Challenge</button>
      </div>
    `;
    container.appendChild(card);
  });
}

async function joinChallenge(cid) {
  try {
    const res = await App.api(`/api/challenges/${cid}/join`, { method: 'POST' });
    App.toast(res.message, 'success');
  } catch (e) {}
}

async function reportPost(postId) {
  const reason = prompt("Please provide reason for reporting this post:");
  if (!reason) return;
  try {
    const res = await App.api(`/api/community/posts/${postId}/report`, {
      method: 'POST',
      body: { reason }
    });
    App.toast(res.message, 'success');
  } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
  const postForm = document.getElementById('newPostForm');
  if (postForm) {
    postForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const title = document.getElementById('postTitleInput').value;
      const content = document.getElementById('postContentInput').value;
      const postType = document.getElementById('postTypeSelect').value;

      try {
        const res = await App.api('/api/community/posts', {
          method: 'POST',
          body: { title, content, post_type: postType, community_id: 1 }
        });
        App.toast('Post published to community!', 'success');
        postForm.reset();
        loadCommunityFeed();
      } catch (err) {
        // handled
      }
    });
  }

  loadCommunityFeed();
});
