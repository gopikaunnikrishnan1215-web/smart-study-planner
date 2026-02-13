// Shared frontend logic for the Study Planner application.

const apiBase = "";

async function apiRequest(path, options = {}) {
  const finalOptions = {
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  // For GET requests, avoid sending an empty body.
  if (finalOptions.method === "GET" || finalOptions.method === "get") {
    delete finalOptions.body;
  }

  const response = await fetch(apiBase + path, finalOptions);

  if (response.status === 401) {
    // Not authenticated – go back to login.
    window.location.href = "/";
    throw new Error("Unauthorized");
  }

  let data = null;
  try {
    data = await response.json();
  } catch (e) {
    // Ignore JSON parse errors for non-JSON responses.
  }

  if (!response.ok) {
    const message = (data && data.error) || "Request failed";
    throw new Error(message);
  }

  return data;
}

function setMessage(container, text, type = "error") {
  if (!container) return;
  container.textContent = text || "";
  container.classList.remove("hidden", "error", "success");
  if (text) {
    container.classList.add(type === "success" ? "success" : "error");
  } else {
    container.classList.add("hidden");
  }
}

// ---------- Auth page ----------

function initAuthPage() {
  const loginTab = document.getElementById("login-tab");
  const registerTab = document.getElementById("register-tab");
  const loginForm = document.getElementById("login-form");
  const registerForm = document.getElementById("register-form");
  const messages = document.getElementById("auth-messages");

  if (!loginForm || !registerForm) return;

  loginTab.addEventListener("click", () => {
    loginTab.classList.add("active");
    registerTab.classList.remove("active");
    loginForm.classList.remove("hidden");
    registerForm.classList.add("hidden");
    setMessage(messages, "");
  });

  registerTab.addEventListener("click", () => {
    registerTab.classList.add("active");
    loginTab.classList.remove("active");
    registerForm.classList.remove("hidden");
    loginForm.classList.add("hidden");
    setMessage(messages, "");
  });

  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(messages, "");
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value;
    if (!username || !password) {
      setMessage(messages, "Please enter username and password.");
      return;
    }
    try {
      await apiRequest("/api/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      window.location.href = "/home";
    } catch (err) {
      setMessage(messages, err.message || "Login failed");
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(messages, "");
    const username = document
      .getElementById("register-username")
      .value.trim();
    const email = document.getElementById("register-email").value.trim();
    const password = document.getElementById("register-password").value;
    const confirmPassword = document.getElementById(
      "register-confirm-password"
    ).value;

    if (!username || !email || !password || !confirmPassword) {
      setMessage(messages, "All fields are required.");
      return;
    }
    if (password !== confirmPassword) {
      setMessage(messages, "Passwords do not match.");
      return;
    }

    try {
      await apiRequest("/api/register", {
        method: "POST",
        body: JSON.stringify({ username, email, password }),
      });
      setMessage(messages, "Registration successful. You can log in now.", "success");
      loginTab.click();
    } catch (err) {
      setMessage(messages, err.message || "Registration failed");
    }
  });
}

// ---------- Dashboard ----------

let cachedSubjects = [];
let cachedProgress = {};

function initHomePage() {
  const logoutBtn = document.getElementById("logout-button");
  if (!logoutBtn) return;
  logoutBtn.addEventListener("click", async () => {
    try {
      await apiRequest("/api/logout", { method: "POST" });
    } catch (e) {
      // Ignore errors; still redirect to login.
    } finally {
      window.location.href = "/";
    }
  });
}

function initDashboard() {
  const logoutBtn = document.getElementById("logout-button");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", async () => {
      try {
        await apiRequest("/api/logout", { method: "POST" });
      } catch (e) {
        // ignore
      } finally {
        window.location.href = "/";
      }
    });
  }

  initSubjectForm();
  initProgressForm();
  initScheduleToggle();
  initSettingsForm();
  maybeShowDashboardTour();
  refreshDashboardData();
}

function maybeShowDashboardTour() {
  try {
    const seen = window.localStorage.getItem("sp_dashboard_tour_seen");
    if (seen === "1") return;
  } catch (e) {
    // If localStorage is unavailable, fail silently.
  }

  const root = document.getElementById("dashboard-root");
  if (!root) return;

  const overlay = document.createElement("div");
  overlay.className = "tour-overlay";

  overlay.innerHTML = `
    <div class="tour-card">
      <h2 class="tour-title">Quick tour</h2>
      <p class="tour-text">
        Add your subjects, see today's schedule, and log progress in one place.
      </p>
      <ol class="tour-steps">
        <li><strong>Add Subject</strong> – create subjects with exam dates and topics.</li>
        <li><strong>Today's Schedule</strong> – view how many hours to spend on each subject today.</li>
        <li><strong>Statistics</strong> – track total hours and topics completed.</li>
        <li><strong>Update Progress</strong> – log hours and tick off topics as you study.</li>
      </ol>
      <button type="button" class="primary-button" id="tour-got-it-button">
        Got it, let's study
      </button>
    </div>
  `;

  document.body.appendChild(overlay);

  const close = () => {
    overlay.classList.add("tour-overlay-hide");
    window.setTimeout(() => overlay.remove(), 180);
    try {
      window.localStorage.setItem("sp_dashboard_tour_seen", "1");
    } catch (e) {
      // ignore
    }
  };

  overlay.addEventListener("click", (evt) => {
    if (evt.target === overlay) {
      close();
    }
  });

  const btn = document.getElementById("tour-got-it-button");
  if (btn) {
    btn.addEventListener("click", () => {
      close();
    });
  }
}

async function refreshDashboardData() {
  try {
    const [subjectsRes, progressRes, scheduleRes, statsRes, historyRes] =
      await Promise.all([
      apiRequest("/api/subjects", { method: "GET" }),
      apiRequest("/api/progress", { method: "GET" }),
      apiRequest("/api/daily-schedule", { method: "GET" }),
      apiRequest("/api/stats", { method: "GET" }),
      apiRequest("/api/history", { method: "GET" }),
    ]);

    cachedSubjects = subjectsRes.subjects || [];
    cachedProgress = progressRes.progress_by_subject || {};

    renderSchedule(scheduleRes);
    renderStats(statsRes.stats || {});
    renderInsights(historyRes);
    renderSubjects(cachedSubjects, cachedProgress);
    populateProgressSubjectSelect();
    checkAndShowReminder(historyRes);
  } catch (err) {
    const msgEl = document.getElementById("subject-form-messages");
    setMessage(msgEl, err.message || "Failed to load dashboard data");
  }
}

function checkAndShowReminder(history) {
  const reminderCard = document.getElementById("reminder-card");
  if (!reminderCard) return;

  const daily = history.daily_totals || [];
  if (!daily.length) {
    reminderCard.classList.remove("hidden");
    reminderCard.innerHTML = `
      <img src="/static/assets/empty-progress.svg" alt="Welcome" style="width: 48px; height: 48px;" />
      <div class="reminder-card-text">
        <strong>Welcome!</strong> Start tracking your study progress to see insights and stay on schedule.
      </div>
    `;
    return;
  }

  const today = new Date().toISOString().split("T")[0];
  const hasToday = daily.some((d) => d.date === today);
  const lastEntry = daily[daily.length - 1];
  const lastDate = lastEntry ? new Date(lastEntry.date) : null;

  if (!hasToday && lastDate) {
    const daysSince = Math.floor((new Date() - lastDate) / (1000 * 60 * 60 * 24));
    if (daysSince >= 2) {
      reminderCard.classList.remove("hidden");
      reminderCard.innerHTML = `
        <img src="/static/assets/empty-progress.svg" alt="Reminder" style="width: 48px; height: 48px;" />
        <div class="reminder-card-text">
          <strong>Welcome back!</strong> It's been ${daysSince} day${daysSince > 1 ? "s" : ""} since your last progress update. Let's plan today's study session.
        </div>
      `;
      return;
    }
  }

  reminderCard.classList.add("hidden");
}

// ---- Subjects / schedule / stats rendering ----

let scheduleViewMode = "today";

function initScheduleToggle() {
  const todayBtn = document.getElementById("schedule-today-btn");
  const weekBtn = document.getElementById("schedule-week-btn");
  if (!todayBtn || !weekBtn) return;

  todayBtn.addEventListener("click", () => {
    scheduleViewMode = "today";
    todayBtn.classList.add("active");
    weekBtn.classList.remove("active");
    document.getElementById("schedule-list").classList.remove("hidden");
    document.getElementById("week-view-container").classList.add("hidden");
    refreshDashboardData();
  });

  weekBtn.addEventListener("click", () => {
    scheduleViewMode = "week";
    weekBtn.classList.add("active");
    todayBtn.classList.remove("active");
    document.getElementById("schedule-list").classList.add("hidden");
    document.getElementById("week-view-container").classList.remove("hidden");
    loadWeekView();
  });
}

async function loadWeekView() {
  const container = document.getElementById("week-view-container");
  if (!container) return;

  try {
    const res = await apiRequest("/api/week-view?start=" + new Date().toISOString().split("T")[0]);
    const week = res.week || [];
    container.innerHTML = "";

    if (!week.length) {
      container.innerHTML = "<p>No subjects yet.</p>";
      return;
    }

    week.forEach((day) => {
      const dayCard = document.createElement("div");
      dayCard.className = "week-day-card";
      const dateObj = new Date(day.date);
      const dayName = dateObj.toLocaleDateString("en-US", { weekday: "short" });
      const dayNum = dateObj.getDate();

      dayCard.innerHTML = `
        <div class="week-day-header">
          <strong>${dayName} ${dayNum}</strong>
          <span class="week-day-total">${day.total_hours.toFixed(1)}h</span>
        </div>
        <ul class="week-day-subjects">
          ${day.subjects.map((s) => `<li>${s.name}: ${s.hours_per_day.toFixed(1)}h</li>`).join("")}
        </ul>
      `;
      container.appendChild(dayCard);
    });
  } catch (err) {
    container.innerHTML = `<p class="error">Failed to load week view.</p>`;
  }
}

function renderSchedule(scheduleData) {
  const list = document.getElementById("schedule-list");
  const warning = document.getElementById("overload-warning");
  if (!list) return;

  list.innerHTML = "";
  if (warning) {
    warning.classList.add("hidden");
    warning.textContent = "";
  }

  const schedule = scheduleData.schedule || [];
  if (!schedule.length) {
    list.innerHTML = "<li>No subjects yet. Add one above.</li>";
    return;
  }

  if (scheduleData.is_overloaded && warning) {
    warning.classList.remove("hidden");
    warning.textContent = `⚠️ Daily total (${scheduleData.total_daily_hours.toFixed(1)}h) exceeds recommended 8h. Consider adjusting your plan.`;
  }

  schedule.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = `${item.name}: ${item.hours_per_day.toFixed(
      2
    )} hr/day (exam ${item.exam_date})`;
    list.appendChild(li);
  });
}

function renderStats(stats) {
  const container = document.getElementById("stats-cards");
  if (!container) return;
  container.innerHTML = "";

  // Display motivational message
  const motivationContainer = document.getElementById("motivation-message");
  if (motivationContainer && stats.overall_progress_percent !== undefined) {
    motivationContainer.classList.remove("hidden");
    const message = generateMotivationalMessage(stats.overall_progress_percent);
    motivationContainer.textContent = message;
  }

  const items = [
    {
      label: "Total hours studied",
      value: stats.total_hours_studied ?? 0,
    },
    {
      label: "Hours remaining",
      value: stats.hours_remaining ?? 0,
    },
    {
      label: "Topics completed",
      value: stats.total_topics_completed ?? 0,
    },
    {
      label: "Topics remaining",
      value: stats.total_topics_remaining ?? 0,
    },
  ];

  items.forEach((item) => {
    const card = document.createElement("div");
    card.className = "stat-card";
    const label = document.createElement("div");
    label.className = "stat-label";
    label.textContent = item.label;
    const value = document.createElement("div");
    value.className = "stat-value";
    value.textContent = item.value;
    card.appendChild(label);
    card.appendChild(value);
    container.appendChild(card);
  });
}

function generateMotivationalMessage(progressPercent) {
  if (progressPercent <= 40) {
    const messages = [
      "Every small step counts! Keep pushing forward and you'll make great progress.",
      "You're just getting started. Consistency will help you reach your goals.",
      "Remember, slow progress is still progress. Keep going!",
      "Don't worry about how much is left. Focus on what you can do today.",
      "You've got this! Break it into smaller parts and tackle them one by one.",
    ];
    // Deterministic selection based on progress
    const idx = Math.floor(progressPercent) % messages.length;
    return messages[idx];
  } else {
    const messages = [
      "Great work! You're doing really well. Keep up the momentum!",
      "You're more than halfway there! Your hard work is paying off.",
      "Impressive progress! Stay consistent and you'll reach your goal soon.",
      "You're crushing it! Keep this pace and you'll finish strong.",
      "Well done! Your dedication is showing. Keep it up!",
    ];
    // Deterministic selection based on progress
    const idx = Math.floor(progressPercent) % messages.length;
    return messages[idx];
  }
}

function renderInsights(history) {
  const container = document.getElementById("insights");
  if (!container) return;

  container.innerHTML = "";

  const daily = history.daily_totals || [];
  const bySubject = history.by_subject || [];

  if (!daily.length && !bySubject.length) {
    container.innerHTML = "<p class=\"empty-state-text\">Start logging progress to see insights.</p>";
    return;
  }

  if (daily.length) {
    const section = document.createElement("div");
    section.className = "insights-section";
    section.innerHTML = '<h3 class="insights-title">Last 7 days</h3>';

    const bars = document.createElement("div");
    bars.className = "insights-bars";

    const recent = daily.slice(-7);
    const maxHours = Math.max(...recent.map((d) => d.hours), 1);

    recent.forEach((d) => {
      const row = document.createElement("div");
      row.className = "insights-bar-row";

      const dateObj = new Date(d.date);
      const label = document.createElement("div");
      label.className = "insights-bar-label";
      label.textContent = dateObj.toLocaleDateString("en-US", {
        weekday: "short",
      });

      const bar = document.createElement("div");
      bar.className = "insights-bar";
      const inner = document.createElement("div");
      inner.className = "insights-bar-inner";
      inner.style.width = `${(d.hours / maxHours) * 100}%`;
      bar.appendChild(inner);

      row.appendChild(label);
      row.appendChild(bar);
      bars.appendChild(row);
    });

    section.appendChild(bars);
    container.appendChild(section);
  }

  if (bySubject.length) {
    const section = document.createElement("div");
    section.className = "insights-section";
    section.innerHTML = '<h3 class="insights-title">Hours by subject</h3>';

    const list = document.createElement("ul");
    list.className = "simple-list";
    bySubject.forEach((s) => {
      const li = document.createElement("li");
      li.textContent = `${s.name}: ${s.total_hours.toFixed(1)}h`;
      list.appendChild(li);
    });
    section.appendChild(list);
    container.appendChild(section);
  }
}

function renderSubjects(subjects, progressBySubject) {
  const container = document.getElementById("subjects-container");
  if (!container) return;
  container.innerHTML = "";
  if (!subjects.length) {
    container.innerHTML = `
      <div class="empty-state">
        <img src="/static/assets/empty-subjects.svg" alt="No subjects yet" class="empty-state-image" loading="lazy" />
        <p class="empty-state-text">No subjects yet. Add your first subject above to get started!</p>
      </div>
    `;
    return;
  }

  subjects.forEach((subj) => {
    const card = document.createElement("div");
    card.className = "subject-card";

    const title = document.createElement("h3");
    title.textContent = subj.name;

    const meta = document.createElement("p");
    meta.className = "subject-meta";
    meta.textContent = `Exam: ${subj.exam_date} • ${subj.hours_per_day.toFixed(
      2
    )} hr/day • Total: ${subj.total_hours_needed} hrs`;

    const progressInfo = progressBySubject[subj.id] || {};
    const percent = progressInfo.progress_percent || 0;
    const hoursStudied = progressInfo.total_hours_studied || 0;

    const progressBarWrapper = document.createElement("div");
    progressBarWrapper.className = "progress-bar-wrapper";
    progressBarWrapper.setAttribute("role", "progressbar");
    progressBarWrapper.setAttribute("aria-valuenow", Math.min(percent, 100).toFixed(1));
    progressBarWrapper.setAttribute("aria-valuemin", "0");
    progressBarWrapper.setAttribute("aria-valuemax", "100");
    progressBarWrapper.setAttribute("aria-label", `Progress for ${subj.name}: ${percent.toFixed(1)}%`);
    const progressBar = document.createElement("div");
    progressBar.className = "progress-bar";
    progressBar.style.width = `${Math.min(percent, 100)}%`;
    progressBarWrapper.appendChild(progressBar);

    const progressText = document.createElement("p");
    progressText.className = "subject-progress-text";
    progressText.textContent = `${hoursStudied}/${subj.total_hours_needed} hrs (${percent.toFixed(
      1
    )}%)`;

    const topicsInfo = document.createElement("p");
    topicsInfo.className = "subject-topics-text";
    const totalTopics = (subj.topics || []).length;
    const completedTopics = (progressInfo.topics_completed || []).length;
    topicsInfo.textContent = `Topics: ${completedTopics}/${totalTopics} completed`;

    card.appendChild(title);
    card.appendChild(meta);
    card.appendChild(progressBarWrapper);
    card.appendChild(progressText);
    card.appendChild(topicsInfo);

    container.appendChild(card);
  });
}

// ---------- Subject creation ----------

let newSubjectTopics = [];

function initSubjectForm() {
  const form = document.getElementById("subject-form");
  if (!form) return;

  const addTopicBtn = document.getElementById("add-topic-btn");
  const topicInput = document.getElementById("new-topic-input");
  const topicsList = document.getElementById("topics-list");
  const messages = document.getElementById("subject-form-messages");

  function renderTopicTags() {
    topicsList.innerHTML = "";
    newSubjectTopics.forEach((topic, index) => {
      const tag = document.createElement("span");
      tag.className = "topic-tag";
      tag.textContent = topic;
      tag.addEventListener("click", () => {
        newSubjectTopics.splice(index, 1);
        renderTopicTags();
      });
      topicsList.appendChild(tag);
    });
  }

  addTopicBtn.addEventListener("click", () => {
    const value = topicInput.value.trim();
    if (!value) return;
    newSubjectTopics.push(value);
    topicInput.value = "";
    renderTopicTags();
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(messages, "");
    const name = document.getElementById("subject-name").value.trim();
    const examDate = document.getElementById("subject-exam-date").value;
    const totalHoursStr = document
      .getElementById("subject-total-hours")
      .value.trim();

    if (!name || !examDate || !totalHoursStr) {
      setMessage(messages, "Please fill in all required fields.");
      return;
    }

    const totalHours = parseFloat(totalHoursStr);
    if (Number.isNaN(totalHours) || totalHours <= 0) {
      setMessage(messages, "Total hours must be a positive number.");
      return;
    }

    try {
      await apiRequest("/api/subjects", {
        method: "POST",
        body: JSON.stringify({
          name,
          exam_date: examDate,
          total_hours_needed: totalHours,
          topics: newSubjectTopics,
        }),
      });
      setMessage(messages, "Subject added.", "success");
      // Reset form and topics state.
      form.reset();
      newSubjectTopics = [];
      renderTopicTags();
      refreshDashboardData();
    } catch (err) {
      setMessage(messages, err.message || "Failed to add subject");
    }
  });
}

// ---------- Progress form ----------

function initProgressForm() {
  const form = document.getElementById("progress-form");
  if (!form) return;
  const messages = document.getElementById("progress-form-messages");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(messages, "");

    const select = document.getElementById("progress-subject-select");
    const hoursStr = document.getElementById("progress-hours").value.trim();
    const checkContainer = document.getElementById(
      "progress-topics-checkboxes"
    );

    const subjectId = parseInt(select.value, 10);
    if (!subjectId) {
      setMessage(messages, "Please choose a subject.");
      return;
    }

    const hours = parseFloat(hoursStr);
    if (Number.isNaN(hours) || hours < 0) {
      setMessage(messages, "Hours must be a non-negative number.");
      return;
    }

    const topicsCompleted = [];
    if (checkContainer) {
      checkContainer
        .querySelectorAll("input[type='checkbox']")
        .forEach((cb) => {
          if (cb.checked) {
            topicsCompleted.push(cb.value);
          }
        });
    }

    try {
      await apiRequest("/api/progress", {
        method: "POST",
        body: JSON.stringify({
          subject_id: subjectId,
          hours_studied: hours,
          topics_completed: topicsCompleted,
        }),
      });
      setMessage(messages, "Progress updated.", "success");
      form.reset();
      refreshDashboardData();
    } catch (err) {
      setMessage(messages, err.message || "Failed to update progress");
    }
  });
}

function initSettingsForm() {
  const form = document.getElementById("settings-form");
  if (!form) return;

  const maxHoursInput = document.getElementById("settings-max-hours");
  const showTourCheckbox = document.getElementById("settings-show-tour");
  const messages = document.getElementById("settings-messages");

  const applyTourSettingToLocalStorage = (showTour) => {
    try {
      if (showTour) {
        window.localStorage.removeItem("sp_dashboard_tour_seen");
      } else {
        window.localStorage.setItem("sp_dashboard_tour_seen", "1");
      }
    } catch (e) {
      // ignore
    }
  };

  (async () => {
    try {
      const res = await apiRequest("/api/settings", { method: "GET" });
      const settings = res.settings || {};
      if (maxHoursInput) {
        maxHoursInput.value = settings.max_daily_hours ?? 8;
      }
      if (showTourCheckbox) {
        showTourCheckbox.checked = settings.show_dashboard_tour !== false;
      }
    } catch (err) {
      setMessage(messages, err.message || "Failed to load settings");
    }
  })();

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    setMessage(messages, "");

    const valueStr = maxHoursInput.value.trim();
    const showTour = showTourCheckbox.checked;
    const value = parseFloat(valueStr);

    if (Number.isNaN(value) || value <= 0) {
      setMessage(messages, "Daily maximum hours must be a positive number.");
      return;
    }

    try {
      const res = await apiRequest("/api/settings", {
        method: "PUT",
        body: JSON.stringify({
          max_daily_hours: value,
          show_dashboard_tour: showTour,
        }),
      });
      const settings = res.settings || {};
      applyTourSettingToLocalStorage(settings.show_dashboard_tour !== false);
      setMessage(messages, "Settings saved.", "success");
      // Refresh schedule to reflect new max_daily_hours threshold.
      refreshDashboardData();
    } catch (err) {
      setMessage(messages, err.message || "Failed to save settings");
    }
  });
}

function populateProgressSubjectSelect() {
  const select = document.getElementById("progress-subject-select");
  const container = document.getElementById("progress-topics-checkboxes");
  if (!select || !container) return;

  select.innerHTML = "";
  if (!cachedSubjects.length) {
    const opt = document.createElement("option");
    opt.value = "";
    opt.textContent = "No subjects yet";
    select.appendChild(opt);
    container.innerHTML = "<p>Add a subject to track topics.</p>";
    return;
  }

  cachedSubjects.forEach((subj) => {
    const opt = document.createElement("option");
    opt.value = subj.id;
    opt.textContent = subj.name;
    select.appendChild(opt);
  });

  select.addEventListener("change", () => {
    renderProgressTopicsCheckboxes();
  });

  renderProgressTopicsCheckboxes();
}

function renderProgressTopicsCheckboxes() {
  const select = document.getElementById("progress-subject-select");
  const container = document.getElementById("progress-topics-checkboxes");
  if (!select || !container) return;

  const subjectId = parseInt(select.value, 10);
  const subject = cachedSubjects.find((s) => s.id === subjectId);
  const progress = cachedProgress[subjectId] || {};

  container.innerHTML = "";
  if (!subject || !subject.topics || !subject.topics.length) {
    container.innerHTML = "<p>No topics defined for this subject.</p>";
    return;
  }

  const completedSet = new Set(progress.topics_completed || []);
  subject.topics.forEach((topic) => {
    const label = document.createElement("label");
    label.className = "topic-checkbox";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.value = topic;
    cb.checked = completedSet.has(topic);
    const span = document.createElement("span");
    span.textContent = topic;
    if (completedSet.has(topic)) {
      span.classList.add("topic-completed");
    }
    label.appendChild(cb);
    label.appendChild(span);
    container.appendChild(label);
  });
}

// ---------- Bootstrap ----------

// ---------- Chatbot ----------

function initChatbot() {
  const toggleBtn = document.getElementById("chatbot-toggle-btn");
  const chatbotWidget = document.getElementById("chatbot-widget");
  const closeBtn = document.getElementById("chatbot-close-btn");
  const chatbotForm = document.getElementById("chatbot-form");
  const chatbotInput = document.getElementById("chatbot-input");
  const chatbotMessages = document.getElementById("chatbot-messages");
  const defaultQuestions = document.getElementById("default-questions");

  if (!toggleBtn || !chatbotWidget) return;

  // Handle default question buttons
  const defaultQuestionBtns = document.querySelectorAll(".default-question-btn");
  defaultQuestionBtns.forEach((btn) => {
    btn.addEventListener("click", () => {
      const question = btn.getAttribute("data-question");
      chatbotInput.value = question;
      submitChatMessage(question);
    });
  });

  // Toggle chatbot visibility
  toggleBtn.addEventListener("click", () => {
    chatbotWidget.classList.toggle("hidden");
    if (!chatbotWidget.classList.contains("hidden")) {
      chatbotInput.focus();
    }
  });

  closeBtn.addEventListener("click", () => {
    chatbotWidget.classList.add("hidden");
  });

  // Send message
  chatbotForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatbotInput.value.trim();
    if (!message) return;
    submitChatMessage(message);
  });

  async function submitChatMessage(message) {
    // Remove default questions on first user input
    if (defaultQuestions && !defaultQuestions.classList.contains("hidden")) {
      defaultQuestions.classList.add("hidden");
    }

    // Add user message
    addChatbotMessage(message, "user");
    chatbotInput.value = "";

    try {
      // Get bot response
      const response = await apiRequest("/api/chatbot", {
        method: "POST",
        body: JSON.stringify({ message }),
      });
      const botReply = response.reply || "I'm here to help! Can you rephrase your question?";
      addChatbotMessage(botReply, "bot");
    } catch (err) {
      addChatbotMessage("Sorry, I couldn't process that. Please try again.", "bot");
    }
  }

  function addChatbotMessage(text, sender) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `chatbot-message ${sender}`;
    
    // Format the message with line breaks and structure
    const formattedText = formatChatbotResponse(text);
    messageDiv.innerHTML = `<div class="chatbot-message-content">${formattedText}</div>`;
    chatbotMessages.appendChild(messageDiv);
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
  }

  function formatChatbotResponse(text) {
    // Escape HTML
    const div = document.createElement("div");
    div.textContent = text;
    let html = div.innerHTML;

    // Convert numbered lists
    html = html.replace(/(\d+\.\s+[^\n]+)/g, (match) => {
      return `<div style="margin: 0.3rem 0; padding-left: 0.5rem;">• ${match}</div>`;
    });

    // Convert bullet points
    html = html.replace(/([•\-]\s+[^\n]+)/g, (match) => {
      return `<div style="margin: 0.3rem 0; padding-left: 0.5rem;">${match}</div>`;
    });

    // Convert section headers (text followed by colon at line start)
    html = html.replace(/^([A-Za-z\s]+):\s*$/gm, (match) => {
      return `<div style="font-weight: 500; margin-top: 0.4rem; margin-bottom: 0.2rem;">${match}</div>`;
    });

    return html;
  }
}


document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("auth-messages")) {
    initAuthPage();
  }
  if (document.getElementById("home-page")) {
    initHomePage();
  }
  if (document.getElementById("dashboard-root")) {
    initDashboard();
    initChatbot();
  }
});


