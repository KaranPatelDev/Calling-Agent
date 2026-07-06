from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.script import ScriptCreate, ScriptUpdate, ScriptResponse, ScriptImportRow, ScriptBulkImport
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.script_service import script_service
from app.services.audio_upload_service import audio_upload_service
from app.utils.file_parser import parse_script_excel, parse_pdf_text
from pathlib import Path

router = APIRouter(prefix="/scripts", tags=["scripts"])


@router.get("", response_model=PaginatedResponse)
async def list_scripts(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await script_service.list_scripts(db, current_user.id, page, limit)
    return PaginatedResponse(
        items=[ScriptResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@router.post("", response_model=ScriptResponse, status_code=status.HTTP_201_CREATED)
async def create_script(
    body: ScriptCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.create(db, current_user.id, **body.model_dump())
    return script


@router.post("/upload-preview")
async def upload_script_preview(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()

    if file.filename.endswith((".xlsx", ".xls")):
        rows = parse_script_excel(content)
        if not rows:
            raise HTTPException(status_code=400, detail="No scripts found in file. Ensure columns: name, content, language.")
        return {"scripts": rows, "source": "excel", "count": len(rows)}

    elif file.filename.endswith(".pdf"):
        text = parse_pdf_text(content)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text content found in PDF.")
        script_name = Path(file.filename).stem.replace("_", " ").replace("-", " ").title()
        return {
            "scripts": [{"name": script_name, "content": text, "language": "hi-IN"}],
            "source": "pdf",
            "count": 1,
        }

    else:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use XLSX, XLS, or PDF.")


@router.post("/import", response_model=list[ScriptResponse], status_code=status.HTTP_201_CREATED)
async def bulk_import_scripts(
    body: ScriptBulkImport,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    created = []
    for row in body.scripts:
        script = await script_service.create(
            db, current_user.id,
            name=row.name,
            content=row.content,
            language=row.language,
        )
        created.append(script)
    return created


@router.get("/{script_id}", response_model=ScriptResponse)
async def get_script(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    return script


@router.put("/{script_id}", response_model=ScriptResponse)
async def update_script(
    script_id: str,
    body: ScriptUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    updated = await script_service.update(db, script, **body.model_dump(exclude_unset=True))
    return updated


@router.delete("/{script_id}", response_model=MessageResponse)
async def delete_script(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    if script.is_active:
        raise HTTPException(status_code=400, detail="Cannot delete active script. Deactivate first.")
    await script_service.delete(db, script)
    return MessageResponse(message="Script deleted")


@router.post("/{script_id}/activate", response_model=MessageResponse)
async def activate_script(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    await script_service.set_active(db, script, current_user.id)
    return MessageResponse(message="Script activated")


@router.post("/{script_id}/audio", response_model=ScriptResponse)
async def upload_audio(
    script_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")

    if script.audio_file_path:
        audio_upload_service.delete(script.audio_file_path)

    file_path, file_size, mime_type = await audio_upload_service.upload(file, current_user.id)
    updated = await script_service.update(
        db, script,
        audio_type="uploaded",
        audio_file_path=file_path,
        audio_file_size=file_size,
        audio_mime_type=mime_type,
    )
    return updated


@router.delete("/{script_id}/audio", response_model=ScriptResponse)
async def remove_audio(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    if script.audio_file_path:
        audio_upload_service.delete(script.audio_file_path)
    updated = await script_service.update(
        db, script,
        audio_type="tts",
        audio_file_path=None,
        audio_file_size=None,
        audio_mime_type=None,
    )
    return updated


@router.get("/{script_id}/audio/preview")
async def preview_audio(
    script_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from fastapi.responses import FileResponse
    script = await script_service.get_by_id(db, script_id, current_user.id)
    if not script or not script.audio_file_path:
        raise HTTPException(status_code=404, detail="No audio file found")

    file_path = Path(script.audio_file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found on disk")

    ext = file_path.suffix.lstrip(".")
    media_type = f"audio/{ext}" if ext != "mp3" else "audio/mpeg"
    return FileResponse(path=file_path, media_type=media_type, filename=file_path.name)
