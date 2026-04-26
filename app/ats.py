from __future__ import annotations

import re
from collections import Counter

from app.models import ResumeData


STOP_WORDS = {
    "about",
    "after",
    "also",
    "and",
    "are",
    "but",
    "can",
    "for",
    "from",
    "has",
    "have",
    "into",
    "our",
    "that",
    "the",
    "this",
    "with",
    "will",
    "need",
    "needs",
    "must",
    "should",
    "we",
    "you",
    "your",
    "their",
    "they",
    "role",
    "team",
    "work",
    "years",
    "using",
    "experience",
    "skills",
}


def normalize_term(value: str) -> str:
    return " ".join(value.lower().strip().split())


def extract_keywords(job_description: str, limit: int = 18) -> list[str]:
    words = re.findall(r"[A-Za-z][A-Za-z0-9+#.-]{2,}", job_description.lower())
    candidates = [word.strip(".,;:()[]{}") for word in words if word not in STOP_WORDS]
    weighted = Counter(candidates)

    phrases = re.findall(r"\b[A-Za-z][A-Za-z0-9+#.-]+(?:\s+[A-Za-z][A-Za-z0-9+#.-]+){1,2}\b", job_description)
    for phrase in phrases:
        normalized = normalize_term(phrase)
        if not any(part in STOP_WORDS for part in normalized.split()):
            weighted[normalized] += 2

    return [term for term, _ in weighted.most_common(limit)]


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
    jd_keywords = extract_keywords(resume.job_description or "")
    requested = [normalize_term(keyword) for keyword in [*resume.keywords, *jd_keywords] if keyword.strip()]
    requested = list(dict.fromkeys(requested))
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
    if resume.job_description and not resume.keywords:
        suggestions.append("Review extracted job keywords and add the most relevant ones to the resume.")
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
        "extracted_keywords": jd_keywords,
        "suggestions": suggestions,
    }
