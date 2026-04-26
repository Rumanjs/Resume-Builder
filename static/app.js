const state = {
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

function cardTemplate(type, item, index) {
  const commonDates = `
    <div class="grid two">
      <input data-field="start" placeholder="Start" value="${item.start || ""}">
      <input data-field="end" placeholder="End" value="${item.end || ""}">
    </div>`;

  if (type === "experience") {
    return `
      <div class="item-card" data-type="${type}" data-index="${index}">
        <div class="grid two">
          <input data-field="role" placeholder="Role" value="${item.role || ""}">
          <input data-field="company" placeholder="Company" value="${item.company || ""}">
        </div>
        <input data-field="location" placeholder="Location" value="${item.location || ""}">
        ${commonDates}
        <textarea data-field="bullets" rows="4" placeholder="One bullet per line">${item.bullets || ""}</textarea>
        <button class="danger-btn" type="button" data-remove>Remove</button>
      </div>`;
  }

  if (type === "project") {
    return `
      <div class="item-card" data-type="${type}" data-index="${index}">
        <div class="grid two">
          <input data-field="name" placeholder="Project name" value="${item.name || ""}">
          <input data-field="link" placeholder="Link" value="${item.link || ""}">
        </div>
        <textarea data-field="description" rows="2" placeholder="Description">${item.description || ""}</textarea>
        <textarea data-field="bullets" rows="3" placeholder="One bullet per line">${item.bullets || ""}</textarea>
        <button class="danger-btn" type="button" data-remove>Remove</button>
      </div>`;
  }

  if (type === "education") {
    return `
      <div class="item-card" data-type="${type}" data-index="${index}">
        <div class="grid two">
          <input data-field="degree" placeholder="Degree" value="${item.degree || ""}">
          <input data-field="school" placeholder="School" value="${item.school || ""}">
        </div>
        <input data-field="location" placeholder="Location" value="${item.location || ""}">
        ${commonDates}
        <textarea data-field="details" rows="3" placeholder="One detail per line">${item.details || ""}</textarea>
        <button class="danger-btn" type="button" data-remove>Remove</button>
      </div>`;
  }

  return `
    <div class="item-card" data-type="${type}" data-index="${index}">
      <input data-field="name" placeholder="Certification" value="${item.name || ""}">
      <div class="grid two">
        <input data-field="issuer" placeholder="Issuer" value="${item.issuer || ""}">
        <input data-field="date" placeholder="Date" value="${item.date || ""}">
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

function syncCard(event) {
  const card = event.target.closest(".item-card");
  if (!card) return;
  const collection = card.dataset.type === "project" ? "projects" : `${card.dataset.type}s`;
  const item = state[collection][Number(card.dataset.index)];
  if (event.target.matches("[data-field]")) {
    item[event.target.dataset.field] = event.target.value;
    schedulePreview();
  }
  if (event.target.matches("[data-remove]")) {
    state[collection].splice(Number(card.dataset.index), 1);
    renderCards();
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
  const collection = type === "project" ? "projects" : `${type}s`;
  state[collection].push(empty[type]);
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
        portfolio: "",
        summary: field("summary")
      },
      target_role: field("targetRole"),
      keywords: splitComma(field("keywords")),
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
  previewTimer = setTimeout(updatePreview, 180);
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
  }
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
  anchor.download = "resume.pdf";
  anchor.click();
  URL.revokeObjectURL(url);
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
  if (event.target.closest(".item-card")) syncCard(event);
});

$("#templateSelect").addEventListener("change", schedulePreview);
$("#downloadBtn").addEventListener("click", downloadPdf);

renderCards();
updatePreview();

