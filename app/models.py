from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class PersonalDetails(BaseModel):
    full_name: str = Field(..., min_length=1, max_length=120)
    title: Optional[str] = Field(default="", max_length=160)
    email: str = Field(..., min_length=3, max_length=160)
    phone: str = Field(..., min_length=6, max_length=40)
    location: Optional[str] = Field(default="", max_length=120)
    linkedin: Optional[str] = Field(default="", max_length=200)
    portfolio: Optional[str] = Field(default="", max_length=200)
    summary: Optional[str] = Field(default="", max_length=900)


class EducationItem(BaseModel):
    school: str = Field(..., min_length=1, max_length=160)
    degree: str = Field(..., min_length=1, max_length=160)
    location: Optional[str] = Field(default="", max_length=120)
    start: Optional[str] = Field(default="", max_length=40)
    end: Optional[str] = Field(default="", max_length=40)
    details: List[str] = Field(default_factory=list)


class ExperienceItem(BaseModel):
    company: str = Field(..., min_length=1, max_length=160)
    role: str = Field(..., min_length=1, max_length=160)
    location: Optional[str] = Field(default="", max_length=120)
    start: Optional[str] = Field(default="", max_length=40)
    end: Optional[str] = Field(default="", max_length=40)
    bullets: List[str] = Field(default_factory=list)


class ProjectItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=160)
    link: Optional[str] = Field(default="", max_length=200)
    description: Optional[str] = Field(default="", max_length=600)
    bullets: List[str] = Field(default_factory=list)


class CertificationItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=180)
    issuer: Optional[str] = Field(default="", max_length=160)
    date: Optional[str] = Field(default="", max_length=40)


class ResumeData(BaseModel):
    personal: PersonalDetails
    skills: List[str] = Field(default_factory=list)
    education: List[EducationItem] = Field(default_factory=list)
    experience: List[ExperienceItem] = Field(default_factory=list)
    projects: List[ProjectItem] = Field(default_factory=list)
    certifications: List[CertificationItem] = Field(default_factory=list)
    target_role: Optional[str] = Field(default="", max_length=160)
    keywords: List[str] = Field(default_factory=list)


class RenderRequest(BaseModel):
    template_id: str = Field(default="classic-001")
    resume: ResumeData
