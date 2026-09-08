import os

from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from agent.agent import run_pipeline
from backend.models.schemas import ProjectReport

router = APIRouter()


@router.post("/analyze", response_model=ProjectReport)
async def analyze_screenplay(
    file: UploadFile = File(None),
    text: str = Form(None),
    base_region: str = Form("Kathmandu Valley"),
    project_name: str = Form("Untitled Project"),
):
    api_key = os.environ.get("GOOGLE_MAPS_API_KEY") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="API key not configured. Set GOOGLE_MAPS_API_KEY or GEMINI_API_KEY.",
        )

    pdf_bytes = None
    if file:
        content = await file.read()
        if file.filename and file.filename.lower().endswith(".pdf"):
            pdf_bytes = content
        else:
            text = content.decode("utf-8", errors="ignore")

    if not pdf_bytes and not text:
        raise HTTPException(
            status_code=400,
            detail="Please upload a PDF file or provide screenplay text.",
        )

    try:
        report = await run_pipeline(
            pdf_bytes=pdf_bytes,
            text_input=text,
            base_region=base_region,
            project_name=project_name,
            api_key=api_key,
        )
        return report
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
