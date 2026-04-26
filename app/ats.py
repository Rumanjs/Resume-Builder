from __future__ import annotations

from app.models import ResumeData


def normalize_term(value: str) -> str:
    return " ".join(value.lower().strip().split())


def ats_report(resume: ResumeData) -> dict:
    text_parts = [
        resume.personal.summary or "",
        resume.target_role or "",
        " ".join(resume.skills),
        " ".join(resume.keywords),
    ]
    for item in resume.experience:
        text_parts.extend([item.role, item.company, " ".join(item.bullets)])
    for item in resume.projects:
        text_parts.extend([item.name, item.description or "", " ".join(item.bullets)])

    haystack = normalize_term(" ".join(text_parts))
    requested = [normalize_term(keyword) for keyword in resume.keywords if keyword.strip()]
    matched = [keyword for keyword in requested if keyword in haystack]
    missing = [keyword for keyword in requested if keyword not in matched]

    essentials = 0
    essentials += bool(resume.personal.full_name)
    essentials += bool(resume.personal.email)
    essentials += bool(resume.personal.phone)
    essentials += bool(resume.skills)
    essentials += bool(resume.experience or resume.projects)
    essentials += bool(resume.education)

    keyword_score = 100 if not requested else round((len(matched) / len(requested)) * 100)
    completeness_score = round((essentials / 6) * 100)
    score = round((keyword_score * 0.45) + (completeness_score * 0.55))

    suggestions = []
    if missing:
        suggestions.append("Add missing target keywords naturally in experience or project bullets.")
    if not resume.personal.summary:
        suggestions.append("Add a concise professional summary tailored to the target role.")
    if len(resume.skills) < 8:
        suggestions.append("Add more role-specific hard skills.")
    if not any(any(char.isdigit() for char in bullet) for exp in resume.experience for bullet in exp.bullets):
        suggestions.append("Add measurable outcomes, such as percentages, revenue, users, time saved, or scale.")

    return {
        "score": score,
        "keyword_score": keyword_score,
        "completeness_score": completeness_score,
        "matched_keywords": matched,
        "missing_keywords": missing,
        "suggestions": suggestions,
    }

