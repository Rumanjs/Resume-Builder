const state = {
  profileImage:
    "data:image/svg+xml;utf8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%20120%20120'%3E%3Crect%20width='120'%20height='120'%20fill='%23e2e8f0'/%3E%3Ccircle%20cx='60'%20cy='45'%20r='24'%20fill='%2364758b'/%3E%3Cpath%20d='M22%20108c8-28%2028-42%2038-42s30%2014%2038%2042'%20fill='%23334155'/%3E%3C/svg%3E",
  sectionOrder: ["summary", "skills", "experience", "projects", "education", "certifications"],
  experience: [
    {
      company: "Northstar Labs",
      role: "Full Stack Developer",
      location: "Remote",
      start: "2021",
      end: "Present",
      bullets:
        "Built FastAPI services and JavaScript interfaces used by 40,000+ monthly users.\nReduced API response times by 32% through query tuning and caching.\nImproved release quality by adding automated tests and CI checks."
    }
  ],
  projects: [
    {
      name: "Resume Intelligence Platform",
      link: "github.com/alex/resume-platform",
      description: "ATS-focused resume builder with template rendering and PDF export.",
      bullets: "Designed clean PDF layouts for parser compatibility.\nAdded keyword scoring for target job descriptions."
    }
  ],
  education: [
    {
      school: "State University",
      degree: "B.S. Computer Science",
      location: "Austin, TX",
      start: "2016",
      end: "2020",
      details: "Coursework: Data Structures, Databases, Web Engineering"
    }
  ],
  certifications: [
    {
      name: "AWS Certified Cloud Practitioner",
      issuer: "Amazon Web Services",
      date: "2024"
    }
  ]
};

const $ = (selector) => document.querySelector(selector);
const STORAGE_KEY = "advanced-resume-builder-state";

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function splitLines(value) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitComma(value) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function field(id) {
  return document.getElementById(id).value.trim();
}

function selectTemplate(templateId) {
  $("#templateSelect").value = templateId;
  document.querySelectorAll(".template-card").forEach((card) => {
    card.classList.toggle("active", card.dataset.templateId === templateId);
  });
  schedulePreview();
}

function setValue(id, value) {
  const element = document.getElementById(id);
  if (element) element.value = value || "";
}

function input(fieldName, placeholder, value = "") {
  return `<input data-field="${fieldName}" placeholder="${placeholder}" value="${escapeHtml(value)}">`;
}

function textarea(fieldName, rows, placeholder, value = "") {
  return `<textarea data-field="${fieldName}" rows="${rows}" placeholder="${placeholder}">${escapeHtml(value)}</textarea>`;
}

function cardTemplate(type, item, index) {
  const commonDates = `
    <div class="grid two">
      ${input("start", "Start", item.start)}
      ${input("end", "End", item.end)}
    </div>`;

  if (type === "experience") {
    return `
      <div class="item-card" data-type="${type}" data-index="${index}">
        <div class="grid two">
          ${input("role", "Role", item.role)}
          ${input("company", "Company", item.company)}
        </div>
        ${input("location", "Location", item.location)}
        ${commonDates}
        ${textarea("bullets", 4, "One measurable result per line", item.bullets)}
        <button class="danger-btn" type="button" data-remove>Remove</button>
      </div>`;
  }

  if (type === "project") {
    return `
      <div class="item-card" data-type="${type}" data-index="${index}">
        <div class="grid two">
          ${input("name", "Project name", item.name)}
          ${input("link", "Link", item.link)}
        </div>
        ${textarea("description", 2, "Short project summary", item.description)}
        ${textarea("bullets", 3, "One highlight per line", item.bullets)}
        <button class="danger-btn" type="button" data-remove>Remove</button>
      </div>`;
  }

  if (type === "education") {
    return `
      <div class="item-card" data-type="${type}" data-index="${index}">
        <div class="grid two">
          ${input("degree", "Degree", item.degree)}
          ${input("school", "School", item.school)}
        </div>
        ${input("location", "Location", item.location)}
        ${commonDates}
        ${textarea("details", 3, "One detail per line", item.details)}
        <button class="danger-btn" type="button" data-remove>Remove</button>
      </div>`;
  }

  return `
    <div class="item-card" data-type="${type}" data-index="${index}">
      ${input("name", "Certification", item.name)}
      <div class="grid two">
        ${input("issuer", "Issuer", item.issuer)}
        ${input("date", "Date", item.date)}
      </div>
      <button class="danger-btn" type="button" data-remove>Remove</button>
    </div>`;
}

function renderCards() {
  $("#experienceList").innerHTML = state.experience.map((item, index) => cardTemplate("experience", item, index)).join("");
  $("#projectList").innerHTML = state.projects.map((item, index) => cardTemplate("project", item, index)).join("");
  $("#educationList").innerHTML = state.education.map((item, index) => cardTemplate("education", item, index)).join("");
  $("#certificationList").innerHTML = state.certifications.map((item, index) => cardTemplate("certification", item, index)).join("");
}

function renderSectionOrder() {
  const labels = {
    summary: "Summary",
    skills: "Skills",
    experience: "Experience",
    projects: "Projects",
    education: "Education",
    certifications: "Certifications"
  };
  $("#sectionOrder").innerHTML = state.sectionOrder
    .map(
      (section, index) => `
        <button type="button" data-section="${section}">
          <span>${index + 1}</span>${labels[section]}
        </button>`
    )
    .join("");
}

function collectionName(type) {
  return type === "project" ? "projects" : `${type}s`;
}

function syncCard(event) {
  const card = event.target.closest(".item-card");
  if (!card) return;
  const collection = collectionName(card.dataset.type);
  const index = Number(card.dataset.index);

  if (event.target.matches("[data-remove]")) {
    state[collection].splice(index, 1);
    renderCards();
    schedulePreview();
    return;
  }

  if (event.target.matches("[data-field]")) {
    state[collection][index][event.target.dataset.field] = event.target.value;
    schedulePreview();
  }
}

function addItem(type) {
  const empty = {
    experience: { company: "", role: "", location: "", start: "", end: "", bullets: "" },
    project: { name: "", link: "", description: "", bullets: "" },
    education: { school: "", degree: "", location: "", start: "", end: "", details: "" },
    certification: { name: "", issuer: "", date: "" }
  };
  state[collectionName(type)].push(empty[type]);
  renderCards();
  schedulePreview();
}

function payload() {
  return {
    template_id: field("templateSelect"),
    resume: {
      personal: {
        full_name: field("fullName"),
        title: field("title"),
        email: field("email") || "user@example.com",
        phone: field("phone"),
        location: field("location"),
        linkedin: field("linkedin"),
        portfolio: field("portfolio"),
        profile_image: state.profileImage,
        summary: field("summary")
      },
      target_role: field("targetRole"),
      keywords: splitComma(field("keywords")),
      job_description: field("jobDescription"),
      section_order: state.sectionOrder,
      skills: splitComma(field("skills")),
      experience: state.experience.map((item) => ({ ...item, bullets: splitLines(item.bullets || "") })),
      projects: state.projects.map((item) => ({ ...item, bullets: splitLines(item.bullets || "") })),
      education: state.education.map((item) => ({ ...item, details: splitLines(item.details || "") })),
      certifications: state.certifications
    }
  };
}

let previewTimer;
function schedulePreview() {
  clearTimeout(previewTimer);
  saveDraft();
  previewTimer = setTimeout(updatePreview, 160);
}

async function updatePreview() {
  const body = JSON.stringify(payload());
  const [previewResponse, atsResponse] = await Promise.all([
    fetch("/api/preview", { method: "POST", headers: { "Content-Type": "application/json" }, body }),
    fetch("/api/ats", { method: "POST", headers: { "Content-Type": "application/json" }, body })
  ]);

  if (previewResponse.ok) {
    $("#preview").innerHTML = await previewResponse.text();
  }
  if (atsResponse.ok) {
    const report = await atsResponse.json();
    $("#atsScore").textContent = `ATS ${report.score}`;
    $("#atsHints").textContent = report.suggestions[0] || "Strong structure. Keep bullets specific and measurable.";
    renderKeywordPanel(report);
  }
}

function renderKeywordPanel(report) {
  const missing = (report.missing_keywords || []).slice(0, 10);
  const extracted = (report.extracted_keywords || []).slice(0, 12);
  if (!missing.length && !extracted.length) {
    $("#keywordPanel").innerHTML = "";
    return;
  }
  $("#keywordPanel").innerHTML = `
    <div>
      <strong>Keyword intelligence</strong>
      <p>${missing.length ? "Missing: " + missing.join(", ") : "Target keywords are covered."}</p>
    </div>
    <div class="keyword-chips">
      ${extracted.map((keyword) => `<button type="button" data-keyword="${escapeHtml(keyword)}">${escapeHtml(keyword)}</button>`).join("")}
    </div>`;
}

async function downloadPdf() {
  const response = await fetch("/api/pdf", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload())
  });
  if (!response.ok) {
    alert("Please complete the required resume fields before downloading.");
    return;
  }
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = `${field("fullName") || "resume"}.pdf`;
  anchor.click();
  URL.revokeObjectURL(url);
}

function handleImageUpload(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  if (file.size > 700000) {
    alert("Please choose an image under 700 KB for fast preview and PDF requests.");
    event.target.value = "";
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    state.profileImage = String(reader.result || "");
    $("#profileImageName").textContent = file.name;
    schedulePreview();
  };
  reader.readAsDataURL(file);
}

function moveSection(section, event) {
  const index = state.sectionOrder.indexOf(section);
  if (index < 0) return;
  const nextIndex = event.shiftKey ? Math.max(0, index - 1) : Math.min(state.sectionOrder.length - 1, index + 1);
  state.sectionOrder.splice(index, 1);
  state.sectionOrder.splice(nextIndex, 0, section);
  renderSectionOrder();
  schedulePreview();
}

function filterTemplates() {
  const query = field("templateSearch").toLowerCase();
  const layout = field("layoutFilter");
  document.querySelectorAll(".template-card").forEach((card) => {
    const text = card.textContent.toLowerCase();
    const matchesQuery = !query || text.includes(query) || card.dataset.layout.includes(query);
    const matchesLayout = !layout || card.dataset.layout === layout;
    card.hidden = !(matchesQuery && matchesLayout);
  });
}

function addKeyword(keyword) {
  const current = splitComma(field("keywords"));
  if (!current.map((item) => item.toLowerCase()).includes(keyword.toLowerCase())) {
    current.push(keyword);
    setValue("keywords", current.join(", "));
    schedulePreview();
  }
}

async function analyzeKeywords() {
  const response = await fetch("/api/keywords", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload())
  });
  if (!response.ok) return;
  const data = await response.json();
  if (data.keywords?.length) {
    setValue("keywords", data.keywords.slice(0, 12).join(", "));
    schedulePreview();
  }
}

async function optimizeResume() {
  $("#optimizerPanel").innerHTML = `<div class="optimizer-card"><strong>Optimizing...</strong><p>Reviewing bullets, keywords, role fit, and ATS impact.</p></div>`;
  const response = await fetch("/api/optimize", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload())
  });
  if (!response.ok) {
    $("#optimizerPanel").innerHTML = `<div class="optimizer-card"><strong>Optimization failed</strong><p>Complete the required resume fields and try again.</p></div>`;
    return;
  }
  renderOptimizer(await response.json());
}

function copyText(value) {
  navigator.clipboard?.writeText(value);
}

function renderOptimizer(report) {
  const scoreItems = Object.entries(report.breakdown || {})
    .map(([label, value]) => `<span><b>${label.replace("_", " ")}</b>${value}</span>`)
    .join("");
  const rewrites = (report.rewrites || [])
    .slice(0, 5)
    .map(
      (item) => `
        <li>
          <small>${escapeHtml(item.item)}</small>
          <p>${escapeHtml(item.improved)}</p>
          <button type="button" data-copy="${escapeHtml(item.improved)}">Copy</button>
        </li>`
    )
    .join("");
  const weak = (report.weak_bullets || [])
    .slice(0, 5)
    .map((item) => `<li><b>${escapeHtml(item.reason)}</b><span>${escapeHtml(item.original)}</span></li>`)
    .join("");
  const keywords = (report.keyword_suggestions || [])
    .map((item) => `<li><b>${escapeHtml(item.keyword)}</b><span>${escapeHtml(item.where)} - ${escapeHtml(item.how)}</span></li>`)
    .join("");
  const projects = (report.project_improvements || [])
    .map((item) => `<li><b>${escapeHtml(item.project)}</b><span>${escapeHtml(item.improved_description)}</span></li>`)
    .join("");

  $("#optimizerPanel").innerHTML = `
    <div class="optimizer-card">
      <div class="optimizer-head">
        <div>
          <strong>AI Resume Optimizer</strong>
          <p>Overall score: ${report.score}/100</p>
        </div>
        <button type="button" data-copy="${escapeHtml(report.summary || "")}">Copy summary</button>
      </div>
      <div class="score-grid">${scoreItems}</div>
      <section>
        <h3>Professional Summary</h3>
        <p>${escapeHtml(report.summary || "")}</p>
      </section>
      <section>
        <h3>Bullet Rewrites</h3>
        <ul class="optimizer-list">${rewrites || "<li>No rewrites needed.</li>"}</ul>
      </section>
      <section>
        <h3>Weak Bullets</h3>
        <ul class="optimizer-list">${weak || "<li>Bullets look strong. Keep measurable impact visible.</li>"}</ul>
      </section>
      <section>
        <h3>Keyword Placement</h3>
        <ul class="optimizer-list">${keywords || "<li>Keyword coverage is healthy.</li>"}</ul>
      </section>
      <section>
        <h3>Recommended Skills</h3>
        <div class="keyword-chips">${(report.recommended_skills || []).map((skill) => `<button type="button" data-keyword="${escapeHtml(skill)}">${escapeHtml(skill)}</button>`).join("")}</div>
      </section>
      <section>
        <h3>Project Improvements</h3>
        <ul class="optimizer-list">${projects || "<li>Add project outcomes with tools, scope, and measurable results.</li>"}</ul>
      </section>
    </div>`;
}

function draftData() {
  return {
    fields: {
      templateSelect: field("templateSelect"),
      targetRole: field("targetRole"),
      keywords: field("keywords"),
      jobDescription: field("jobDescription"),
      fullName: field("fullName"),
      title: field("title"),
      email: field("email"),
      phone: field("phone"),
      location: field("location"),
      linkedin: field("linkedin"),
      portfolio: field("portfolio"),
      summary: field("summary"),
      skills: field("skills")
    },
    state
  };
}

function saveDraft() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(draftData()));
    $("#saveStatus").textContent = "Autosaved";
  } catch {
    $("#saveStatus").textContent = "Autosave paused";
  }
}

function loadDraft() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return;
  try {
    const draft = JSON.parse(raw);
    Object.entries(draft.fields || {}).forEach(([id, value]) => setValue(id, value));
    Object.assign(state, draft.state || {});
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
}

function exportJson() {
  const blob = new Blob([JSON.stringify(draftData(), null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = "resume-builder-draft.json";
  anchor.click();
  URL.revokeObjectURL(url);
}

function importJson(event) {
  const file = event.target.files?.[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    const draft = JSON.parse(String(reader.result || "{}"));
    Object.entries(draft.fields || {}).forEach(([id, value]) => setValue(id, value));
    Object.assign(state, draft.state || {});
    renderCards();
    renderSectionOrder();
    selectTemplate(field("templateSelect"));
  };
  reader.readAsText(file);
}

document.addEventListener("input", (event) => {
  if (event.target.closest(".item-card")) {
    syncCard(event);
    return;
  }
  schedulePreview();
});

document.addEventListener("click", (event) => {
  if (event.target.matches("[data-add]")) addItem(event.target.dataset.add);
  const templateCard = event.target.closest(".template-card");
  if (templateCard) selectTemplate(templateCard.dataset.templateId);
  const orderButton = event.target.closest("#sectionOrder [data-section]");
  if (orderButton) moveSection(orderButton.dataset.section, event);
  const keywordButton = event.target.closest("[data-keyword]");
  if (keywordButton) addKeyword(keywordButton.dataset.keyword);
  const copyButton = event.target.closest("[data-copy]");
  if (copyButton) copyText(copyButton.dataset.copy);
  if (event.target.closest(".item-card")) syncCard(event);
});

$("#templateSelect").addEventListener("change", (event) => selectTemplate(event.target.value));
$("#templateSearch").addEventListener("input", filterTemplates);
$("#layoutFilter").addEventListener("change", filterTemplates);
$("#downloadBtn").addEventListener("click", downloadPdf);
$("#profileImage").addEventListener("change", handleImageUpload);
$("#analyzeBtn").addEventListener("click", analyzeKeywords);
$("#optimizeBtn").addEventListener("click", optimizeResume);
$("#exportBtn").addEventListener("click", exportJson);
$("#importJson").addEventListener("change", importJson);
$("#previewZoom").addEventListener("input", (event) => {
  $("#preview").style.transform = `scale(${Number(event.target.value) / 100})`;
  $("#preview").style.transformOrigin = "top center";
});

loadDraft();
renderCards();
renderSectionOrder();
selectTemplate(field("templateSelect"));
updatePreview();
