// file: script.js

document.addEventListener('DOMContentLoaded', () => {
  let currentRecommendations = [];
  let currentPreferences = {};

  const form = document.getElementById('preferences-form');
  const resultsArea = document.getElementById('results-area');
  const submitBtn = document.getElementById('submit-btn');
  const clearBtn = document.getElementById('clear-btn');
  const formStatus = document.getElementById('form-status');
  const normalizeToggle = document.getElementById('normalize-toggle');
  const accentSelect = document.getElementById('accent-select');
  const sidebarWidthSlider = document.getElementById('sidebar-width');
  const resumeUploadBtn = document.getElementById('resume-upload-btn');
  const resumeUploadInput = document.getElementById('resume-upload-input');
  const resumeStatus = document.getElementById('resume-status');

  const getSliders = () => Array.from(document.querySelectorAll('input[type="range"][data-weight-key]'));
  const getEnabledSliders = () => getSliders().filter(s => !s.disabled);
  const escapeHtml = (s) => String(s || '').replace(/[&<>"']/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[ch]));

  const safeArrayFill = (inputId, arr, maxItems = 50) => {
    const input = document.getElementById(inputId);
    if (!input) return false;
    if (!Array.isArray(arr)) {
      input.value = '';
      return false;
    }
    const filtered = arr
      .map(x => (typeof x === 'string' ? x.trim() : ''))
      .filter(x => x.length > 0 && x.length <= 100)
      .slice(0, maxItems);

    if (filtered.length === 0) {
      input.value = '';
      return false;
    }
    input.value = filtered.join(', ');
    return true;
  };

  const syncDisplays = () => {
    getSliders().forEach(slider => {
      const display = slider.parentElement.querySelector('.weight-value');
      if (display) display.textContent = `${Math.round(Number(slider.value))}%`;
      slider.closest('.weight-row').classList.toggle('disabled', slider.disabled);
    });
  };

  const applyAccent = (name) => {
    const root = document.documentElement.style;
    const accents = {
      gold: ['#D4AF37', '#ffd572', '#5b61ff'],
      rose: ['#e29aa6', '#f6c6cc', '#b85aa8'],
      midnight: ['#7dd3fc', '#60a5fa', '#0f172a'],
    };
    const [c1, c2, c3] = accents[name] || accents.gold;
    root.setProperty('--accent-1', c1);
    root.setProperty('--accent-2', c2);
    root.setProperty('--accent-3', c3);
  };

  const applySidebarWidth = (px) => {
    document.documentElement.style.setProperty('--sidebar-width', `${px}px`);
  };

  const normalizeAndApply = () => {
    const enabled = getEnabledSliders();
    if (enabled.length === 0) return;

    const totalRaw = enabled.reduce((sum, s) => sum + Number(s.value), 0);
    if (totalRaw === 0) {
      const equalShare = 100 / enabled.length;
      enabled.forEach(s => s.value = equalShare);
    } else {
      const scaleFactor = 100 / totalRaw;
      enabled.forEach(s => s.value = Number(s.value) * scaleFactor);
    }

    let currentSum = enabled.reduce((sum, s) => sum + Math.round(Number(s.value)), 0);
    if (currentSum !== 100 && enabled.length > 0) {
      const diff = 100 - currentSum;
      const lastSlider = enabled[enabled.length - 1];
      lastSlider.value = Number(lastSlider.value) + diff;
    }

    syncDisplays();
  };

  const replaceIcons = () => {
    if (window.feather) {
      window.feather.replace();
    }
  };
  const handleClearForm = () => {
    const confirmClear = confirm('Are you sure you want to clear all form fields?');
    if (!confirmClear) return;
    const originalHTML = clearBtn.innerHTML;
    clearBtn.disabled = true;
    clearBtn.innerHTML = '<i data-feather="loader" class="spin"></i> Clearing...';
    replaceIcons();
    setTimeout(() => {

      document.getElementById('skills').value = '';
      document.getElementById('titles').value = '';
      document.getElementById('locations').value = '';
      document.getElementById('industries').value = '';

      document.getElementById('min_salary').value = '170000';

      resumeUploadInput.value = '';
      resumeStatus.textContent = '';

      document.getElementById('w_skills').value = 30;
      document.getElementById('w_title').value = 20;
      document.getElementById('w_location').value = 15;
      document.getElementById('w_salary').value = 10;
      document.getElementById('w_industry').value = 10;

      document.querySelectorAll('.weight-enable-chk').forEach(checkbox => {
        checkbox.checked = true;
        const targetId = checkbox.dataset.target;
        const slider = document.getElementById(targetId);
        if (slider) slider.disabled = false;
      });

      normalizeToggle.checked = false;
      syncDisplays();

      resultsArea.innerHTML = `
        <div class="placeholder">
          <i data-feather="briefcase"></i>
          <p>Your personalized job recommendations will appear here.</p>
          <small>Upload a resume or complete your profile to begin.</small>
        </div>
      `;
      currentRecommendations = [];
      currentPreferences = {};

      clearBtn.disabled = false;
      clearBtn.innerHTML = originalHTML;

      if (formStatus) {
        formStatus.textContent = '✓ Form cleared successfully';
        formStatus.style.color = 'var(--accent-3)';
        setTimeout(() => { formStatus.textContent = ''; }, 3000);
      }

      const sidebar = document.querySelector('.sidebar');
      if (sidebar) {
        sidebar.scrollTo({ top: 0, behavior: 'smooth' });
      }
      window.scrollTo({ top: 0, behavior: 'smooth' });

      replaceIcons();

      console.log('✓ Form cleared successfully');
    }, 300);
  };

  const init = () => {
    document.querySelectorAll('.weight-enable-chk').forEach(chk => {
      const slider = document.getElementById(chk.dataset.target);
      if (!slider) return;
      slider.disabled = !chk.checked;
      chk.addEventListener('change', () => {
        slider.disabled = !chk.checked;
        if (normalizeToggle.checked) normalizeAndApply();
        syncDisplays();
      });
    });

    getSliders().forEach(s => s.addEventListener('input', () => {
      if (normalizeToggle.checked) normalizeAndApply();
      else syncDisplays();
    }));

    normalizeToggle.addEventListener('change', () => {
      if (normalizeToggle.checked) normalizeAndApply();
    });

    accentSelect.addEventListener('change', (e) => applyAccent(e.target.value));
    sidebarWidthSlider.addEventListener('input', (e) => applySidebarWidth(e.target.value));

    resumeUploadBtn.addEventListener('click', () => resumeUploadInput.click());
    resumeUploadInput.addEventListener('change', handleResumeUpload);

    // Add Clear Button Event Listener
    if (clearBtn) {
      clearBtn.addEventListener('click', handleClearForm);
    }

    applyAccent(accentSelect.value);
    applySidebarWidth(sidebarWidthSlider.value);
    syncDisplays();
    replaceIcons();
    initCookieConsent();
  };

  const initCookieConsent = () => {
    const popup = document.getElementById('cookie-consent-popup');
    const acceptBtn = document.getElementById('cookie-accept-btn');
    const rejectBtn = document.getElementById('cookie-reject-btn');

    if (!popup || !acceptBtn || !rejectBtn) return;

    const consent = localStorage.getItem('cookieConsent');

    if (!consent) {
      popup.classList.remove('hidden');
    }

    acceptBtn.addEventListener('click', () => {
      localStorage.setItem('cookieConsent', 'accepted');
      popup.classList.add('hidden');
    });

    rejectBtn.addEventListener('click', () => {
      localStorage.setItem('cookieConsent', 'rejected');
      popup.classList.add('hidden');
    });
  };

  init();

  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      if (clearBtn && !clearBtn.disabled) {
        clearBtn.click();
      }
    }
  });

  async function handleResumeUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    resumeStatus.innerHTML = '<i data-feather="loader" class="spin"></i> Parsing...';
    replaceIcons();
    resumeUploadBtn.disabled = true;

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const res = await fetch('/parse_resume', {
        method: 'POST',
        body: formData,
      });

      const responseText = await res.text();
      if (!res.ok) {
        let parsedError;
        try { parsedError = JSON.parse(responseText); }
        catch (e) { parsedError = null; }
        const message = parsedError && parsedError.error ? parsedError.error : responseText || `HTTP ${res.status}`;
        throw new Error(message);
      }

      const parsedData = JSON.parse(responseText);
      if (parsedData.error) {
        throw new Error(parsedData.error);
      }

      const anySkills = safeArrayFill('skills', parsedData.skills);
      const anyTitles = safeArrayFill('titles', parsedData.titles);
      safeArrayFill('locations', parsedData.locations);
      safeArrayFill('industries', parsedData.industries);

      if (!anySkills && !anyTitles) {
        throw new Error("Could not extract key skills or titles from the resume.");
      }

      resumeStatus.textContent = `Successfully parsed: ${file.name}`;

    } catch (err) {
      console.error(err);
      resumeStatus.textContent = `Error: ${err.message}`;
    } finally {
      resumeUploadBtn.disabled = false;
      resumeUploadInput.value = '';
      replaceIcons();
    }
  };

  form.addEventListener('submit', async (ev) => {
    ev.preventDefault();
    submitBtn.disabled = true;
    const oldHtml = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i data-feather="loader" class="spin"></i> Analyzing...';
    replaceIcons();

    resultsArea.innerHTML = '';

    const getArrayFromInput = (id) => (document.getElementById(id)?.value || '').split(',').map(s => s.trim()).filter(Boolean);

    currentPreferences = {
      skills: getArrayFromInput('skills'),
      titles: getArrayFromInput('titles'),
      locations: getArrayFromInput('locations'),
      min_salary: parseInt(document.getElementById('min_salary')?.value, 10) || 0,
      industries: getArrayFromInput('industries'),
    };

    const weights = {};
    getEnabledSliders().forEach(s => {
      weights[s.dataset.weightKey] = Number(s.value);
    });

    try {
      const res = await fetch('/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preferences: currentPreferences, weights })
      });

      const text = await res.text();

      if (!res.ok) {
        let parsed;
        try { parsed = JSON.parse(text); }
        catch (e) { parsed = null; }
        const message = parsed && parsed.error ? parsed.error : text || `HTTP ${res.status}`;
        throw new Error(message);
      }

      let data;
      try { data = JSON.parse(text); }
      catch (e) { throw new Error('Invalid JSON returned from server: ' + text); }

      currentRecommendations = data;
      renderJobs(currentRecommendations);

    } catch (err) {
      resultsArea.innerHTML = `<div class="placeholder"><i data-feather="alert-triangle"></i><p>Unable to fetch recommendations</p><small>${escapeHtml(err.message)}</small></div>`;
      replaceIcons();
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = oldHtml;
      replaceIcons();
    }
  });

  const renderBreakdown = (b) => {
    if (!b || typeof b !== 'object') return '<li><em>No breakdown available</em></li>';
    return Object.entries(b).map(([k, v]) => `<li><strong>${escapeHtml(k)}:</strong> ${escapeHtml(v)}%</li>`).join('');
  };

  const renderJobs = (jobs) => {
    if (!jobs || jobs.length === 0) {
      resultsArea.innerHTML = '<div class="placeholder"><i data-feather="alert-circle"></i><p>No matching jobs found.</p><small>Try broadening your search criteria.</small></div>';
      replaceIcons();
      return;
    }
    const cardsHtml = jobs.map((job, index) => {
      const score = Number(job.match_score) || 0;
      return `
        <article class="job-card" style="animation-delay: ${index * 100}ms;" data-job-id="${escapeHtml(job.job_id)}">
          <div class="card-header">
            <div>
              <h3>${escapeHtml(job.job_title)}</h3>
              <h4 class="muted">${escapeHtml(job.company)} - ${escapeHtml(job.location)}</h4>
            </div>
            <div class="match-score" style="--score:${score}"><span>${score}%</span></div>
          </div>
          <div class="match-story"><p>${escapeHtml(job.story)}</p></div>
          <div class="card-actions">
            <details class="score-breakdown"><summary>View Score Breakdown</summary><ul>${renderBreakdown(job.breakdown)}</ul></details>
            <button class="validate-btn"><i data-feather="check-square"></i> Validate</button>
          </div>
          <div class="validation-view" style="display: none;"></div>
        </article>`;
    }).join('');
    resultsArea.innerHTML = cardsHtml;
    replaceIcons();
    addValidationListeners();
  };

  function addValidationListeners() {
    document.querySelectorAll('.validate-btn').forEach(button => {
      button.addEventListener('click', e => {
        const card = e.currentTarget.closest('.job-card');
        const jobId = card.dataset.jobId;
        const validationView = card.querySelector('.validation-view');
        const jobData = currentRecommendations.find(j => j.job_id === jobId);

        if (validationView.style.display === 'none') {
          validationView.innerHTML = createValidationTable(jobData);
          validationView.style.display = 'block';
          e.currentTarget.innerHTML = '<i data-feather="x-square"></i> Hide Validation';
        } else {
          validationView.style.display = 'none';
          validationView.innerHTML = '';
          e.currentTarget.innerHTML = '<i data-feather="check-square"></i> Validate';
        }
        replaceIcons();
      });
    });
  }

  function createValidationTable(jobData) {
    const { validation_details } = jobData;
    const prefMap = {
      'Skills': currentPreferences.skills,
      'Title': currentPreferences.titles,
      'Location': currentPreferences.locations,
      'Industry': currentPreferences.industries,
      'Salary': currentPreferences.min_salary > 0 ? `Min: ₹${currentPreferences.min_salary.toLocaleString('en-IN')}` : ''
    };

    let tableHTML = '<h5>Preference vs. Job Data</h5><table class="validation-table">';
    tableHTML += '<tr><th>Attribute</th><th>Your Preference</th><th>Job Requirement</th></tr>';

    for (const key in prefMap) {
      const userPref = Array.isArray(prefMap[key]) ? prefMap[key].join(', ') : prefMap[key];

      let jobReqHTML = '';
      if (Array.isArray(validation_details[key])) {
        jobReqHTML = validation_details[key].map(item => {
          if (item.type === 'direct') {
            return `<span class="match-highlight direct">${escapeHtml(item.skill)}</span>`;
          } else if (item.type === 'semantic') {
            return `<span class="match-highlight semantic">${escapeHtml(item.skill)}</span>`;
          }
          return escapeHtml(item.skill);
        }).join(', ');
      } else {
        jobReqHTML = escapeHtml(validation_details[key]) || '<i>Not specified</i>';
      }

      tableHTML += `<tr><td><strong>${key}</strong></td><td>${userPref || '<i>Not specified</i>'}</td><td>${jobReqHTML}</td></tr>`;
    }

    tableHTML += '</table>';
    return tableHTML;
  }
});


