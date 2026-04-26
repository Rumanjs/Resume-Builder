# AI Resume Builder

A FastAPI and JavaScript resume builder with 120 selectable templates, live preview, ATS scoring hints, and dependency-light PDF generation.

## Run

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Features

- Collects personal details, education, skills, experience, projects, and certifications.
- Provides 120 ATS-safe template variants.
- Renders a real-time browser preview.
- Generates a downloadable PDF using clean, parser-friendly text layout.
- Keeps templates data-driven so more styles or AI suggestions can be added later.

