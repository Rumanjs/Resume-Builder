from __future__ import annotations

import io
import textwrap
from typing import Iterable, List

from app.models import ResumeData


PAGE_WIDTH = 612
PAGE_HEIGHT = 792
LEFT = 54
TOP = 742
LINE = 13


def _clean(value: str | None) -> str:
    return " ".join((value or "").replace("\r", " ").replace("\n", " ").split())


def _pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _wrap(value: str, width: int = 92) -> List[str]:
    return textwrap.wrap(_clean(value), width=width) or []


def _date_range(start: str | None, end: str | None) -> str:
    start_value = _clean(start)
    end_value = _clean(end)
    if start_value and end_value:
        return f"{start_value} - {end_value}"
    return start_value or end_value


def resume_lines(resume: ResumeData) -> List[tuple[str, str]]:
    lines: List[tuple[str, str]] = []
    personal = resume.personal

    lines.append(("title", _clean(personal.full_name).upper()))
    if personal.title:
        lines.append(("normal", _clean(personal.title)))

    contact = " | ".join(
        item
        for item in [
            _clean(personal.email),
            _clean(personal.phone),
            _clean(personal.location),
            _clean(personal.linkedin),
            _clean(personal.portfolio),
        ]
        if item
    )
    if contact:
        lines.append(("small", contact))

    if personal.summary:
        lines.extend(_section("SUMMARY"))
        for line in _wrap(personal.summary):
            lines.append(("normal", line))

    if resume.skills:
        lines.extend(_section("SKILLS"))
        for line in _wrap(", ".join(_clean(skill) for skill in resume.skills if _clean(skill))):
            lines.append(("normal", line))

    if resume.experience:
        lines.extend(_section("EXPERIENCE"))
        for item in resume.experience:
            heading = f"{_clean(item.role)} | {_clean(item.company)}"
            date = _date_range(item.start, item.end)
            if date:
                heading = f"{heading} | {date}"
            if item.location:
                heading = f"{heading} | {_clean(item.location)}"
            lines.append(("bold", heading))
            for bullet in item.bullets:
                for wrapped in _wrap(bullet, 88):
                    lines.append(("normal", f"- {wrapped}"))

    if resume.projects:
        lines.extend(_section("PROJECTS"))
        for item in resume.projects:
            heading = _clean(item.name)
            if item.link:
                heading = f"{heading} | {_clean(item.link)}"
            lines.append(("bold", heading))
            if item.description:
                for line in _wrap(item.description):
                    lines.append(("normal", line))
            for bullet in item.bullets:
                for wrapped in _wrap(bullet, 88):
                    lines.append(("normal", f"- {wrapped}"))

    if resume.education:
        lines.extend(_section("EDUCATION"))
        for item in resume.education:
            heading = f"{_clean(item.degree)} | {_clean(item.school)}"
            date = _date_range(item.start, item.end)
            if date:
                heading = f"{heading} | {date}"
            if item.location:
                heading = f"{heading} | {_clean(item.location)}"
            lines.append(("bold", heading))
            for detail in item.details:
                for wrapped in _wrap(detail, 88):
                    lines.append(("normal", f"- {wrapped}"))

    if resume.certifications:
        lines.extend(_section("CERTIFICATIONS"))
        for item in resume.certifications:
            parts = [_clean(item.name), _clean(item.issuer), _clean(item.date)]
            lines.append(("normal", " | ".join(part for part in parts if part)))

    return lines


def _section(title: str) -> List[tuple[str, str]]:
    return [("space", ""), ("heading", title)]


def generate_pdf(resume: ResumeData) -> bytes:
    pages: List[List[str]] = [[]]
    y = TOP

    for style, text in resume_lines(resume):
        if style == "space":
            y -= 6
            continue
        if y < 54:
            pages.append([])
            y = TOP
        font = "/F1"
        size = 10
        if style == "title":
            font, size = "/F2", 17
        elif style in {"bold", "heading"}:
            font, size = "/F2", 10
        elif style == "small":
            size = 9
        pages[-1].append(f"BT {font} {size} Tf {LEFT} {y} Td ({_pdf_escape(text)}) Tj ET")
        y -= LINE if style != "title" else 18

    return _build_pdf(pages)


def _build_pdf(pages: Iterable[List[str]]) -> bytes:
    page_list = list(pages)
    objects: List[bytes] = []

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{4 + index * 2} 0 R" for index in range(len(page_list)))
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_list)} >>".encode())
    objects.append(
        b"<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> "
        b"/F2 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >> >> >>"
    )

    for index, commands in enumerate(page_list):
        content_id = 5 + index * 2
        page = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] "
            f"/Resources 3 0 R /Contents {content_id} 0 R >>"
        )
        stream = "\n".join(commands).encode("latin-1", errors="replace")
        objects.append(page.encode())
        objects.append(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")

    buffer = io.BytesIO()
    buffer.write(b"%PDF-1.4\n")
    offsets = [0]
    for number, body in enumerate(objects, start=1):
        offsets.append(buffer.tell())
        buffer.write(f"{number} 0 obj\n".encode())
        buffer.write(body)
        buffer.write(b"\nendobj\n")

    xref_at = buffer.tell()
    buffer.write(f"xref\n0 {len(objects) + 1}\n".encode())
    buffer.write(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buffer.write(f"{offset:010d} 00000 n \n".encode())
    buffer.write(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode()
    )
    return buffer.getvalue()

