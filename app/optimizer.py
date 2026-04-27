from __future__ import annotations

import re
from statistics import mean

from app.ats import ats_report, extract_keywords, normalize_term
from app.models import ResumeData


ACTION_VERBS = [
    "Built",
    "Led",
    "Improved",
    "Reduced",
    "Automated",
    "Designed",
    "Delivered",
    "Optimized",
    "Launched",
    "Implemented",
]

WEAK_VERBS = {
    "worked",
    "helped",
    "assisted",
    "responsible",
    "handled",
    "did",
    "made",
    "used",
    "involved",
}

ROLE_SKILLS = {
    "frontend": ["React", "JavaScript", "TypeScript", "HTML", "CSS", "Accessibility", "Performance", "Testing"],
    "backend": ["Python", "FastAPI", "REST APIs", "SQL", "PostgreSQL", "Docker", "Caching", "Testing"],
    "full stack": ["Python", "FastAPI", "React", "SQL", "REST APIs", "Docker", "CI/CD", "Testing"],
    "data": ["Python", "SQL", "Pandas", "Dashboards", "ETL", "Data Modeling", "Analytics", "Visualization"],
    "product": ["Roadmapping", "User Research", "A/B Testing", "Analytics", "Prioritization", "Stakeholder Management"],
    "designer": ["UX Design", "Figma", "Design Systems", "Prototyping", "Accessibility", "User Research"],
    "devops": ["Docker", "Kubernetes", "CI/CD", "Cloud", "Monitoring", "Terraform", "Linux", "Security"],
}


def _text(resume: ResumeData) -> str:
    parts = [
        resume.personal.summary or "",
        resume.target_role or "",
        " ".join(resume.skills),
        resume.job_description or "",
    ]
    for exp in resume.experience:
        parts.extend([exp.role, exp.company, " ".join(exp.bullets)])
    for project in resume.projects:
        parts.extend([project.name, project.description or "", " ".join(project.bullets)])
    return normalize_term(" ".join(parts))


def _role_key(resume: ResumeData) -> str:
    target = normalize_term(resume.target_role or resume.personal.title or "")
    for key in ROLE_SKILLS:
        if key in target:
            return key
    return "full stack"


def _has_metric(value: str) -> bool:
    return bool(re.search(r"\d|%|\b(k|m|million|thousand|users|revenue|hours|days|minutes)\b", value.lower()))


def _starts_with_action(value: str) -> bool:
    first = re.sub(r"[^A-Za-z]", "", value.strip().split(" ")[0]).lower() if value.strip() else ""
    return first in {verb.lower() for verb in ACTION_VERBS}


def _weak_reason(bullet: str) -> str | None:
    normalized = bullet.lower()
    if len(bullet.split()) < 8:
        return "Too short; add scope, tool, and outcome."
    if not _starts_with_action(bullet):
        return "Start with a strong action verb."
    if any(weak in normalized for weak in WEAK_VERBS):
        return "Uses weak or passive phrasing."
    if not _has_metric(bullet):
        return "Missing measurable impact."
    return None


def rewrite_bullet(bullet: str, role: str, keywords: list[str]) -> str:
    clean = bullet.strip().rstrip(".")
    clean = re.sub(
        r"^(worked on|worked with|helped with|helped|assisted with|assisted|responsible for|handled|did|made|used)\s+",
        "",
        clean,
        flags=re.IGNORECASE,
    )
    verb = next((item for item in ACTION_VERBS if item.lower() in clean.lower()), ACTION_VERBS[0])
    if _starts_with_action(clean):
        improved = clean
    else:
        phrase = clean if clean[:2].isupper() else clean[:1].lower() + clean[1:]
        improved = f"{verb} {phrase}"

    keyword = next((item for item in keywords if item.lower() not in improved.lower()), "")
    if keyword:
        improved = f"{improved} using {keyword}"
    if not _has_metric(improved):
        improved = f"{improved}, improving efficiency by 20%"
    if role and role.lower() not in improved.lower() and len(improved) < 135:
        improved = f"{improved} for {role} workflows"
    return improved[:180].rstrip(" ,") + "."


def _readability_score(resume: ResumeData) -> int:
    bullets = [bullet for exp in resume.experience for bullet in exp.bullets] + [
        bullet for project in resume.projects for bullet in project.bullets
    ]
    if not bullets:
        return 55
    lengths = [len(bullet.split()) for bullet in bullets if bullet.strip()]
    if not lengths:
        return 55
    avg = mean(lengths)
    score = 100
    if avg < 8:
        score -= 25
    if avg > 28:
        score -= 20
    if any(len(bullet) > 190 for bullet in bullets):
        score -= 15
    return max(45, min(100, round(score)))


def _impact_score(resume: ResumeData) -> int:
    bullets = [bullet for exp in resume.experience for bullet in exp.bullets]
    bullets += [bullet for project in resume.projects for bullet in project.bullets]
    if not bullets:
        return 40
    metric_count = sum(_has_metric(bullet) for bullet in bullets)
    action_count = sum(_starts_with_action(bullet) for bullet in bullets)
    return round(((metric_count / len(bullets)) * 55) + ((action_count / len(bullets)) * 45))


def _formatting_score(resume: ResumeData) -> int:
    score = 100
    if len(resume.personal.summary or "") > 650:
        score -= 15
    if len(resume.skills) < 6:
        score -= 15
    if not resume.section_order:
        score -= 10
    if any(len(exp.bullets) > 6 for exp in resume.experience):
        score -= 10
    return max(50, score)


def optimize_resume(resume: ResumeData) -> dict:
    ats = ats_report(resume)
    role = resume.target_role or resume.personal.title or "target role"
    role_key = _role_key(resume)
    jd_keywords = extract_keywords(resume.job_description or "")
    keyword_pool = list(dict.fromkeys([*resume.keywords, *jd_keywords, *ROLE_SKILLS[role_key]]))

    weak_bullets = []
    rewrites = []
    for exp_index, exp in enumerate(resume.experience):
        for bullet_index, bullet in enumerate(exp.bullets):
            reason = _weak_reason(bullet)
            if reason:
                weak_bullets.append(
                    {
                        "section": "experience",
                        "item": exp.role or exp.company,
                        "index": bullet_index,
                        "original": bullet,
                        "reason": reason,
                    }
                )
            rewrites.append(
                {
                    "section": "experience",
                    "item": exp.role or exp.company,
                    "index": bullet_index,
                    "original": bullet,
                    "improved": rewrite_bullet(bullet, role, keyword_pool),
                }
            )

    project_improvements = []
    for project in resume.projects:
        base = project.description or f"{project.name} project"
        keyword = next((item for item in keyword_pool if item.lower() not in base.lower()), role)
        project_improvements.append(
            {
                "project": project.name,
                "improved_description": (
                    f"{base.rstrip('.')}. Highlights {keyword} through measurable delivery, clear ownership, "
                    "and ATS-friendly technical outcomes."
                ),
            }
        )

    existing_skills = {skill.lower() for skill in resume.skills}
    recommended_skills = [skill for skill in ROLE_SKILLS[role_key] if skill.lower() not in existing_skills]
    missing_keywords = ats["missing_keywords"][:8]
    summary = (
        f"{role} with experience delivering {', '.join((resume.skills or ROLE_SKILLS[role_key])[:4])}. "
        f"Known for building reliable solutions, improving measurable outcomes, and collaborating across teams."
    )

    readability = _readability_score(resume)
    formatting = _formatting_score(resume)
    impact = _impact_score(resume)
    keyword = ats["keyword_score"]
    overall = round((keyword * 0.35) + (readability * 0.2) + (formatting * 0.2) + (impact * 0.25))

    return {
        "score": overall,
        "breakdown": {
            "keyword_match": keyword,
            "readability": readability,
            "formatting": formatting,
            "impact": impact,
        },
        "weak_bullets": weak_bullets[:8],
        "rewrites": rewrites[:10],
        "summary": summary,
        "recommended_skills": recommended_skills[:10],
        "project_improvements": project_improvements[:6],
        "missing_keywords": missing_keywords,
        "keyword_suggestions": [
            {
                "keyword": keyword,
                "where": "experience bullet" if index % 2 == 0 else "skills or project description",
                "how": f"Use '{keyword}' in a truthful result-focused sentence tied to tools, scope, or impact.",
            }
            for index, keyword in enumerate(missing_keywords)
        ],
        "role_recommendations": [
            f"Tailor the summary toward {role} outcomes.",
            "Prioritize bullets with action verb + tool + measurable result.",
            "Keep each bullet under two lines for readability.",
        ],
    }
