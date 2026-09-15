const $ = (selector) => document.querySelector(selector);
const stressRange = $('#stressRange');
const stressOutput = $('#stressOutput');
const stressDscr = $('#stressDscr');
const stressStatus = $('#stressStatus');
const stressCopy = $('#stressCopy');
const scoreValue = $('#scoreValue');
const scoreRing = $('#scoreRing');
const scoreLabel = $('#scoreLabel');
const gradeValue = $('#gradeValue');
const pdValue = $('#pdValue');
const dscrValue = $('#dscrValue');

function formatDscr(value) { return `${value.toFixed(2)}x`; }

function updateStress() {
  const decline = Number(stressRange.value);
  const dscr = Math.max(0.65, 1.62 - decline * 0.02);
  const score = Math.max(38, Math.round(78 - decline * 0.72));
  const pd = (1.84 + decline * 0.11).toFixed(2);
  const grade = score >= 75 ? 'A−' : score >= 65 ? 'BBB+' : score >= 55 ? 'BBB' : 'BB+';
  const status = dscr >= 1.35 ? 'Above covenant' : dscr >= 1.15 ? 'Covenant watch' : 'Covenant breach';
  stressOutput.value = `−${decline}%`;
  stressDscr.textContent = formatDscr(dscr);
  stressStatus.textContent = status;
  stressStatus.style.color = dscr >= 1.35 ? '#4f8759' : dscr >= 1.15 ? '#aa713d' : '#bd6554';
  stressCopy.textContent = dscr >= 1.35 ? 'The borrower retains adequate debt-servicing headroom under this contraction.' : dscr >= 1.15 ? 'Headroom narrows materially; trigger enhanced monthly monitoring.' : 'Projected debt service falls below covenant. Escalation and mitigants are required.';
  scoreValue.innerHTML = `${score}<span>/100</span>`;
  scoreRing.style.background = `conic-gradient(var(--teal) ${score}%,#e2e8e1 0)`;
  scoreRing.querySelector('span').textContent = score;
  scoreLabel.textContent = score >= 75 ? 'Strong' : score >= 65 ? 'Satisfactory' : 'Elevated risk';
  gradeValue.textContent = grade;
  pdValue.innerHTML = `${pd}<span>%</span>`;
  dscrValue.innerHTML = `${formatDscr(dscr)}`;
  $('#scenarioName').textContent = decline === 10 ? 'Base case' : `Revenue −${decline}%`;
}
stressRange.addEventListener('input', updateStress);

const dialog = $('#memoDialog');
$('#memoBtn').addEventListener('click', () => dialog.showModal());
$('#reviewBtn').addEventListener('click', () => dialog.showModal());
$('#closeDialog').addEventListener('click', () => dialog.close());
$('#printBtn').addEventListener('click', () => window.print());
$('#exportBtn').addEventListener('click', () => dialog.showModal());
dialog.addEventListener('click', (event) => { if (event.target === dialog) dialog.close(); });
document.querySelectorAll('.nav-link').forEach((link) => link.addEventListener('click', () => {
  document.querySelector('.nav-link.active')?.classList.remove('active'); link.classList.add('active');
}));
