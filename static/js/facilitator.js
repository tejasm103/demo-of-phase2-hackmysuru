/**
 * Facilitator Intervention & Monitoring Dashboard Controller
 */

async function loadFacilitatorDashboard() {
  try {
    const data = await App.api('/api/interventions');
    renderFacilitatorStats(data.stats);
    renderNeedsAttentionTable(data.interventions);

    const students = await App.api('/api/facilitator/students');
    renderStudentsRoster(students);
  } catch (err) {
    console.error('Failed to load facilitator dashboard:', err);
  }
}

function renderFacilitatorStats(stats) {
  const s = stats || {};
  const setEl = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
  };

  setEl('statTotalStudents', s.total_students || 5);
  setEl('statActiveLearners', s.active_learners || 5);
  setEl('statImproving', s.improving || 2);
  setEl('statNeedsSupport', s.needs_support || 1);
  setEl('statActiveInterventions', s.active_interventions || 1);
  setEl('statMasteryImprovements', `${s.mastery_improvements || 12} ↗`);
}

function renderNeedsAttentionTable(interventions) {
  const tbody = document.getElementById('needsAttentionTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';

  if (!interventions || interventions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:2rem; color:var(--text-muted);">No active student alerts right now. All learners on track!</td></tr>`;
    return;
  }

  interventions.forEach(item => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid rgba(255,255,255,0.06)';
    const mlState = item.current_ml_state || 'Needs Support';
    const mlClass = mlState.toLowerCase().replace(' ', '-');

    tr.innerHTML = `
      <td style="padding:1rem; font-weight:700; color:#fff;">
        ${item.student_name}
        <div style="font-size:0.75rem; color:var(--text-subtle);">${item.student_email}</div>
      </td>
      <td style="padding:1rem;">${item.course_name}</td>
      <td style="padding:1rem; font-weight:600; color:#cbd5e1;">${item.concept_name}</td>
      <td style="padding:1rem;">
        <span style="font-weight:700; color:#f59e0b;">${Math.round(item.mastery_percentage || 43)}%</span>
      </td>
      <td style="padding:1rem; font-size:0.8rem; color:var(--text-muted); max-width:240px;">
        ${item.evidence_text}
      </td>
      <td style="padding:1rem;">
        <span class="badge badge-${mlClass}">${mlState}</span>
      </td>
      <td style="padding:1rem; font-size:0.8rem; color:#a5b4fc; max-width:260px;">
        ${item.recommendation_text}
      </td>
      <td style="padding:1rem;">
        <div style="display:flex; flex-direction:column; gap:0.4rem;">
          <button class="btn btn-primary btn-sm" onclick="openAssignModal(${item.student_id}, ${item.concept_id}, '${item.student_name}')">
            ⚡ Action Intervention
          </button>
          <button class="btn btn-secondary btn-sm" onclick="resolveIntervention(${item.id})">
            ✓ Mark Resolved
          </button>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderStudentsRoster(students) {
  const container = document.getElementById('studentRosterTableBody');
  if (!container) return;
  container.innerHTML = '';

  (students || []).forEach(st => {
    const tr = document.createElement('tr');
    tr.style.borderBottom = '1px solid rgba(255,255,255,0.04)';
    const state = st.ml_state || 'Stable';
    tr.innerHTML = `
      <td style="padding:0.85rem; font-weight:600; color:#fff;">${st.name}</td>
      <td style="padding:0.85rem;">${st.school_name || 'Apex Academy'}</td>
      <td style="padding:0.85rem;">${st.grade_name || 'Grade 10'}</td>
      <td style="padding:0.85rem;">${st.stream_name || 'Mathematics'}</td>
      <td style="padding:0.85rem; font-weight:700;">${Math.round(st.overall_mastery || 50)}%</td>
      <td style="padding:0.85rem;">
        <span class="badge badge-${state.toLowerCase().replace(' ', '-')}">${state}</span>
      </td>
      <td style="padding:0.85rem;">
        <button class="btn btn-secondary btn-sm" onclick="viewStudentFullProfile(${st.id})">
          Inspect Path
        </button>
      </td>
    `;
    container.appendChild(tr);
  });
}

let activeModalStudent = null;
function openAssignModal(studentId, conceptId, studentName) {
  activeModalStudent = { studentId, conceptId };
  const modal = document.getElementById('interventionModal');
  const modalTitle = document.getElementById('modalStudentName');
  if (modalTitle) modalTitle.textContent = `Assign Intervention to ${studentName}`;
  if (modal) modal.style.display = 'flex';
}

function closeAssignModal() {
  const modal = document.getElementById('interventionModal');
  if (modal) modal.style.display = 'none';
}

async function submitIntervention() {
  if (!activeModalStudent) return;
  const actionType = document.getElementById('actionTypeSelect').value;
  const notes = document.getElementById('actionNotesInput').value;

  try {
    const res = await App.api('/api/interventions/assign', {
      method: 'POST',
      body: {
        student_id: activeModalStudent.studentId,
        concept_id: activeModalStudent.conceptId,
        action_type: actionType,
        notes: notes || 'Targeted remediation assigned by Dr. Sharma'
      }
    });
    App.toast(res.message, 'success');
    closeAssignModal();
    loadFacilitatorDashboard();
  } catch (err) {
    App.toast('Failed to assign: ' + err.message, 'error');
  }
}

async function resolveIntervention(iid) {
  try {
    const res = await App.api(`/api/interventions/${iid}/resolve`, { method: 'POST' });
    App.toast(res.message, 'success');
    loadFacilitatorDashboard();
  } catch (err) {
    // handled
  }
}

async function viewStudentFullProfile(studentId) {
  try {
    const res = await App.api(`/api/facilitator/student/${studentId}`);
    alert(`Student Profile: ${res.student.name}\nGoal: ${res.student.primary_goal}\nML Learning State: ${res.ml_prediction.predicted_state} (Confidence: ${res.ml_prediction.confidence})\nRecent Attempts: ${res.recent_attempts.length}`);
  } catch (e) {}
}

document.addEventListener('DOMContentLoaded', () => {
  const submitBtn = document.getElementById('btnSubmitIntervention');
  if (submitBtn) submitBtn.addEventListener('click', submitIntervention);
  const cancelBtn = document.getElementById('btnCancelIntervention');
  if (cancelBtn) cancelBtn.addEventListener('click', closeAssignModal);

  loadFacilitatorDashboard();
});
