from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ResumeTemplate:
    id: str
    name: str
    family: str
    accent: str
    font: str
    density: str
    section_style: str


FAMILIES = [
    ("classic", "Classic"),
    ("modern", "Modern"),
    ("executive", "Executive"),
    ("technical", "Technical"),
    ("academic", "Academic"),
    ("compact", "Compact"),
    ("consulting", "Consulting"),
    ("product", "Product"),
    ("minimal", "Minimal"),
    ("hybrid", "Hybrid"),
]

ACCENTS = [
    "#1f2937",
    "#2563eb",
    "#047857",
    "#b45309",
    "#7c3aed",
    "#be123c",
    "#0f766e",
    "#4338ca",
    "#374151",
    "#0f172a",
    "#0369a1",
    "#4d7c0f",
]

FONTS = [
    "Arial, Helvetica, sans-serif",
    "Calibri, Arial, sans-serif",
    "Georgia, serif",
    "Verdana, Geneva, sans-serif",
]

DENSITIES = ["roomy", "balanced", "compact"]
SECTION_STYLES = ["rule", "caps", "boxed", "plain"]


def build_templates() -> List[ResumeTemplate]:
    templates: List[ResumeTemplate] = []
    index = 1
    for family_key, family_name in FAMILIES:
        for variant in range(12):
            templates.append(
                ResumeTemplate(
                    id=f"{family_key}-{variant + 1:03d}",
                    name=f"{family_name} {variant + 1:02d}",
                    family=family_key,
                    accent=ACCENTS[(variant + len(templates)) % len(ACCENTS)],
                    font=FONTS[variant % len(FONTS)],
                    density=DENSITIES[variant % len(DENSITIES)],
                    section_style=SECTION_STYLES[variant % len(SECTION_STYLES)],
                )
            )
            index += 1
    return templates


TEMPLATES = build_templates()
TEMPLATE_BY_ID: Dict[str, ResumeTemplate] = {template.id: template for template in TEMPLATES}


def get_template(template_id: str) -> ResumeTemplate:
    return TEMPLATE_BY_ID.get(template_id, TEMPLATES[0])

