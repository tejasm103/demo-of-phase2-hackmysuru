/**
 * Diagnostic Assessment Engine
 */

let diagnosticQuestions = [];
let diagnosticIndex = 0;
let diagnosticAnswers = [];

async function initDiagnostic() {
  try {
    const params = new URLSearchParams(window.location.search);
    const courseId = params.get('course_id') || 1;

    const data = await App.api(`/api/assessment?course_id=${courseId}&diagnostic=true`);
    diagnosticQuestions = data.questions || [];
    diagnosticIndex = 0;
    diagnosticAnswers = [];

    if (diagnosticQuestions.length > 0) {
      renderDiagnosticQuestion();
    }
  } catch (err) {
    console.error('Failed to init diagnostic assessment:', err);
  }
}

function renderDiagnosticQuestion() {
  const q = diagnosticQuestions[diagnosticIndex];
  if (!q) return;

  const countEl = document.getElementById('diagCounter');
  if (countEl) countEl.textContent = `Diagnostic ${diagnosticIndex + 1} of ${diagnosticQuestions.length}`;

  const promptEl = document.getElementById('diagPrompt');
  if (promptEl) promptEl.textContent = q.narrative_context;

  const optionsContainer = document.getElementById('diagOptions');
  if (!optionsContainer) return;
  optionsContainer.innerHTML = '';

  (q.options || []).forEach(opt => {
    const optDiv = document.createElement('div');
    optDiv.className = 'option-item';
    optDiv.innerHTML = `
      <div class="option-radio"></div>
      <div style="flex:1;">${opt}</div>
    `;
    optDiv.addEventListener('click', () => {
      document.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
      optDiv.classList.add('selected');
      diagnosticAnswers[diagnosticIndex] = {
        question_id: q.id,
        student_answer: opt,
        time_seconds: 20
      };
      document.getElementById('btnNextDiag').disabled = false;
    });
    optionsContainer.appendChild(optDiv);
  });

  const nextBtn = document.getElementById('btnNextDiag');
  if (nextBtn) {
    nextBtn.disabled = !diagnosticAnswers[diagnosticIndex];
    nextBtn.textContent = (diagnosticIndex === diagnosticQuestions.length - 1) ? 'Complete Diagnostic Assessment' : 'Next Question →';
  }
}

async function handleDiagnosticNext() {
  if (diagnosticIndex < diagnosticQuestions.length - 1) {
    diagnosticIndex++;
    renderDiagnosticQuestion();
  } else {
    // Submit diagnostic assessment
    try {
      const btn = document.getElementById('btnNextDiag');
      if (btn) btn.disabled = true;

      const res = await App.api('/api/assessment/submit', {
        method: 'POST',
        body: { answers: diagnosticAnswers, is_diagnostic: true }
      });

      const container = document.getElementById('diagContainer');
      if (container) {
        container.innerHTML = `
          <div class="card mastery-feedback-card">
            <div class="mastery-score-circle">
              <div class="score-num">${res.accuracy_percentage}%</div>
              <div class="score-label">Baseline Score</div>
            </div>
            <h2>Diagnostic Complete! Knowledge Graph Initialized</h2>
            <p style="color:var(--text-muted); margin-bottom:1.5rem;">
              Your prerequisite mastery levels have been calculated and your adaptive sequence has been generated.
            </p>
            <div style="margin-bottom:2rem;">
              <a href="/dashboard" class="btn btn-primary">Go to Personalized Dashboard →</a>
            </div>
          </div>
        `;
      }
    } catch (err) {
      App.toast('Diagnostic submission failed: ' + err.message, 'error');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const nextBtn = document.getElementById('btnNextDiag');
  if (nextBtn) nextBtn.addEventListener('click', handleDiagnosticNext);
  initDiagnostic();
});
