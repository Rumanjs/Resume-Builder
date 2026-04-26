from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from app.ats import ats_report
from app.models import RenderRequest
from app.pdf import generate_pdf
from app.template_catalog import TEMPLATES, get_template

app = FastAPI(title="AI Resume Builder", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "templates": TEMPLATES,
        },
    )


@app.get("/api/templates")
def list_templates() -> dict:
    return {"templates": [template.__dict__ for template in TEMPLATES]}


@app.post("/api/preview", response_class=HTMLResponse)
def preview(payload: RenderRequest) -> HTMLResponse:
    template = get_template(payload.template_id)
    html = templates.get_template("resume.html").render(
        resume=payload.resume,
        template=template,
        ats=ats_report(payload.resume),
    )
    return HTMLResponse(html)


@app.post("/api/ats")
def score_resume(payload: RenderRequest) -> dict:
    return ats_report(payload.resume)


@app.post("/api/pdf")
def download_pdf(payload: RenderRequest) -> Response:
    if not payload.resume.personal.full_name.strip():
        raise HTTPException(status_code=422, detail="Full name is required.")
    pdf = generate_pdf(payload.resume)
    filename = payload.resume.personal.full_name.lower().replace(" ", "-") or "resume"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}-resume.pdf"'},
    )

