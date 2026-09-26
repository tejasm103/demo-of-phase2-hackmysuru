/**
 * Adaptive Learning & Practice Session Controller
 */

let currentQuestions = [];
let currentQuestionIndex = 0;
let userAnswers = [];
let activeConcept = null;

async function initLearningSession() {
  const params = new URLSearchParams(window.location.search);
  const courseId = params.get('course_id') || 1;
  const conceptId = params.get('concept_id');

  try {
    const url = conceptId 
      ? `/api/assessment?course_id=${courseId}&concept_id=${conceptId}`
      : `/api/assessment?course_id=${courseId}`;
    
    const data = await App.api(url);
    currentQuestions = data.questions || [];
    currentQuestionIndex = 0;
    userAnswers = [];

    const interestBadge = document.getElementById('sessionInterestBadge');
    if (interestBadge) {
      interestBadge.textContent = `Narrative Context: ${data.interest || 'Space'} 🚀`;
    }

    if (currentQuestions.length > 0) {
      renderCurrentQuestion();
    } else {
      document.getElementById('questionContainer').innerHTML = `
        <div style="text-align:center; padding:3rem;">
          <h3>No practice questions available for this concept yet.</h3>
          <a href="/dashboard" class="btn btn-primary" style="margin-top:1rem;">Back to Dashboard</a>
        </div>
      `;
    }
  } catch (err) {
    console.error('Failed to init learning session:', err);
  }
}

function renderCurrentQuestion() {
  const q = currentQuestions[currentQuestionIndex];
  if (!q) return;

  const countEl = document.getElementById('questionCounter');
  if (countEl) countEl.textContent = `Question ${currentQuestionIndex + 1} of ${currentQuestions.length}`;

  const diffBadge = document.getElementById('questionDiffBadge');
  if (diffBadge) {
    diffBadge.textContent = q.difficulty;
    diffBadge.className = `badge badge-${q.difficulty.toLowerCase()}`;
  }

  const promptEl = document.getElementById('questionPrompt');
  if (promptEl) promptEl.textContent = q.narrative_context;

  const optionsContainer = document.getElementById('questionOptions');
  if (!optionsContainer) return;
  optionsContainer.innerHTML = '';

  (q.options || []).forEach((opt, idx) => {
    const optDiv = document.createElement('div');
    optDiv.className = 'option-item';
    optDiv.innerHTML = `
      <div class="option-radio"></div>
      <div style="flex:1;">${opt}</div>
    `;
    optDiv.addEventListener('click', () => {
      document.querySelectorAll('.option-item').forEach(el => el.classList.remove('selected'));
      optDiv.classList.add('selected');
      userAnswers[currentQuestionIndex] = {
        question_id: q.id,
        student_answer: opt,
        time_seconds: 25
      };
      document.getElementById('btnNextQuestion').disabled = false;
    });
    optionsContainer.appendChild(optDiv);
  });

  const nextBtn = document.getElementById('btnNextQuestion');
  if (nextBtn) {
    nextBtn.disabled = !userAnswers[currentQuestionIndex];
    nextBtn.textContent = (currentQuestionIndex === currentQuestions.length - 1) ? 'Submit Assessment' : 'Next Question →';
  }

  // Pre-load tutor explanation
  loadTutorExplanation(q);
}

async function loadTutorExplanation(question) {
  const tutorBox = document.getElementById('tutorContentArea');
  if (!tutorBox) return;

  try {
    const data = await App.api('/api/ai/explain', {
      method: 'POST',
      body: {
        concept_name: 'Statistics & Distributions',
        interest: question.interest_applied || 'Space',
        difficulty: question.difficulty
      }
    });
    tutorBox.innerHTML = markedParse(data.explanation);
  } catch (err) {
    tutorBox.textContent = "Socratic hints available. Think about prerequisite properties and variable invariants.";
  }
}

function markedParse(text) {
  // Simple markdown to HTML formatter for Socratic tutor
  return text
    .replace(/^### (.*$)/gim, '<h3 style="margin-top:0.75rem; color:#fff;">$1</h3>')
    .replace(/^#### (.*$)/gim, '<h4 style="margin-top:0.5rem; color:#a5b4fc;">$1</h4>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br/>');
}

async function handleNextOrSubmit() {
  if (currentQuestionIndex < currentQuestions.length - 1) {
    currentQuestionIndex++;
    renderCurrentQuestion();
  } else {
    // Submit all answers
    try {
      const submitBtn = document.getElementById('btnNextQuestion');
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = 'Evaluating with Adaptive Engine...';
      }

      const res = await App.api('/api/assessment/submit', {
        method: 'POST',
        body: { answers: userAnswers }
      });

      renderAssessmentResults(res);
    } catch (err) {
      App.toast('Submission failed: ' + err.message, 'error');
    }
  }
}

function renderAssessmentResults(res) {
  const container = document.getElementById('questionContainer');
  if (!container) return;

  const updates = res.mastery_updates || [];
  let unlockHtml = '';
  updates.forEach(u => {
    if (u.unlocked_dependent) {
      unlockHtml += `
        <div class="unlock-banner">
          🎉 <strong>PREREQUISITE MASTERY ACHIEVED (${u.new_mastery}%)!</strong>
          Dependent concept is now <strong>UNLOCKED</strong> in your knowledge graph!
        </div>
      `;
    }
  });

  const nextPlan = res.next_adaptive_plan || {};
  const mlState = res.ml_learning_state || {};

  container.innerHTML = `
    <div class="card mastery-feedback-card">
      <div class="mastery-score-circle">
        <div class="score-num">${res.accuracy_percentage}%</div>
        <div class="score-label">Score</div>
      </div>
      <h2>Adaptive Performance Evaluated!</h2>
      <p style="color:var(--text-muted); margin-bottom:1.5rem;">
        Mastery recalculated across demonstrated answers. ML Learning State: 
        <strong style="color:#60a5fa;">${mlState.predicted_state || 'Improving'}</strong>
      </p>

      ${unlockHtml}

      <div style="background:rgba(255,255,255,0.04); border-radius:var(--radius-md); padding:1.25rem; margin-bottom:1.5rem; text-align:left;">
        <h4 style="margin-bottom:0.5rem; color:#fff;">Next Best Adaptive Activity:</h4>
        <div style="font-weight:700; color:#a5b4fc; font-size:1.1rem;">
          ${nextPlan.activity ? nextPlan.activity.title : 'Proceed with next course concept'}
        </div>
        <div style="font-size:0.9rem; color:var(--text-muted); margin-top:0.35rem;">
          ${nextPlan.rationale || 'Tailored to your new mastery level.'}
        </div>
      </div>

      <div style="display:flex; justify-content:center; gap:1rem;">
        <a href="/dashboard" class="btn btn-primary">Return to Dashboard</a>
        <a href="/course" class="btn btn-secondary">View Knowledge Graph</a>
      </div>
    </div>
  `;
}

document.addEventListener('DOMContentLoaded', () => {
  const btnNext = document.getElementById('btnNextQuestion');
  if (btnNext) {
    btnNext.addEventListener('click', handleNextOrSubmit);
  }

  const toggleTutor = document.getElementById('btnToggleTutor');
  if (toggleTutor) {
    toggleTutor.addEventListener('click', () => {
      const drawer = document.getElementById('tutorDrawer');
      if (drawer) {
        drawer.style.display = (drawer.style.display === 'none') ? 'block' : 'none';
      }
    });
  }

  initLearningSession();
});
