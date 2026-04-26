from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List


@dataclass(frozen=True)
class ResumeTemplate:
    id: str
    name: str
    family: str
    layout: str
    header_style: str
    sidebar: str
    skill_style: str
    timeline_style: str
    project_style: str
    photo_style: str
    image_placement: str
    ornament: str
    scale: str
    accent: str
    muted: str
    font: str
    density: str
    section_style: str


FAMILIES = [
    ("classic", "Classic Professional"),
    ("modern", "Modern Two Column"),
    ("executive", "Executive Boardroom"),
    ("technical", "Technical Systems"),
    ("academic", "Academic Clean"),
    ("compact", "Compact ATS"),
    ("consulting", "Consulting Case"),
    ("product", "Product Leader"),
    ("minimal", "Minimal Editorial"),
    ("hybrid", "Hybrid Portfolio"),
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

MUTED_BACKGROUNDS = [
    "#f8fafc",
    "#eff6ff",
    "#ecfdf5",
    "#fff7ed",
    "#f5f3ff",
    "#fff1f2",
    "#f0fdfa",
    "#eef2ff",
    "#f3f4f6",
    "#f1f5f9",
    "#f0f9ff",
    "#f7fee7",
]

FONTS = [
    "Arial, Helvetica, sans-serif",
    "Calibri, Arial, sans-serif",
    "Georgia, serif",
    "Verdana, Geneva, sans-serif",
]

DENSITIES = ["roomy", "balanced", "compact"]
SECTION_STYLES = ["rule", "caps", "boxed", "plain", "numbered", "bracket"]
LAYOUTS = ["single", "sidebar-left", "sidebar-right", "split", "timeline", "compact-grid"]
HEADERS = ["stacked", "banner", "identity", "masthead", "split", "compact"]
SIDEBARS = ["none", "contact", "skills", "profile", "credentials"]
SKILL_STYLES = ["tags", "bars", "pills", "columns", "inline"]
TIMELINES = ["plain", "rail", "dots", "cards"]
PROJECT_STYLES = ["list", "cards", "highlights"]
PHOTO_STYLES = ["none", "circle", "rounded", "square"]
IMAGE_PLACEMENTS = ["none", "header-left", "header-right", "sidebar-top", "identity-card", "watermark"]
ORNAMENTS = ["none", "left-rule", "top-band", "corner-block", "section-rail", "soft-panel", "boxed-header", "folio"]
SCALES = ["standard", "wide-header", "narrow-sidebar", "dense-editorial", "portfolio"]


def build_templates() -> List[ResumeTemplate]:
    templates: List[ResumeTemplate] = []
    for family_index, (family_key, family_name) in enumerate(FAMILIES):
        for variant in range(12):
            global_index = family_index * 12 + variant
            templates.append(
                ResumeTemplate(
                    id=f"{family_key}-{variant + 1:03d}",
                    name=f"{family_name} {variant + 1:02d}",
                    family=family_key,
                    layout=LAYOUTS[global_index % len(LAYOUTS)],
                    header_style=HEADERS[(global_index // len(LAYOUTS) + variant) % len(HEADERS)],
                    sidebar=SIDEBARS[(global_index // 2 + family_index) % len(SIDEBARS)],
                    skill_style=SKILL_STYLES[(global_index // 3 + variant) % len(SKILL_STYLES)],
                    timeline_style=TIMELINES[(global_index // 4 + family_index) % len(TIMELINES)],
                    project_style=PROJECT_STYLES[(global_index // 5 + variant) % len(PROJECT_STYLES)],
                    photo_style=PHOTO_STYLES[(global_index // 6 + variant) % len(PHOTO_STYLES)],
                    image_placement=IMAGE_PLACEMENTS[(global_index + family_index) % len(IMAGE_PLACEMENTS)],
                    ornament=ORNAMENTS[(global_index // 2 + variant) % len(ORNAMENTS)],
                    scale=SCALES[(global_index // 3 + family_index) % len(SCALES)],
                    accent=ACCENTS[(variant + len(templates)) % len(ACCENTS)],
                    muted=MUTED_BACKGROUNDS[(variant + len(templates)) % len(MUTED_BACKGROUNDS)],
                    font=FONTS[variant % len(FONTS)],
                    density=DENSITIES[variant % len(DENSITIES)],
                    section_style=SECTION_STYLES[variant % len(SECTION_STYLES)],
                )
            )
    return templates


TEMPLATES = build_templates()
TEMPLATE_BY_ID: Dict[str, ResumeTemplate] = {template.id: template for template in TEMPLATES}


def get_template(template_id: str) -> ResumeTemplate:
    return TEMPLATE_BY_ID.get(template_id, TEMPLATES[0])
