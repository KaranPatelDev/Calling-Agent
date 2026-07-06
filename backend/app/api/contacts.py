from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.schemas.contact_list import (
    ContactListCreate, ContactListResponse, ContactCreate,
    ContactResponse, BulkUploadResponse,
)
from app.schemas.contact import ContactImportRow
from app.schemas.common import PaginatedResponse
from app.services.contact_service import contact_service

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/lists", response_model=PaginatedResponse)
async def list_contact_lists(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    items, total = await contact_service.list_lists(db, current_user.id, page, limit)
    return PaginatedResponse(
        items=[ContactListResponse.model_validate(i) for i in items],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@router.post("/lists", response_model=ContactListResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_list(
    body: ContactListCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cl = await contact_service.create_list(db, current_user.id, body.name, body.description)
    return cl


@router.get("/lists/{list_id}", response_model=PaginatedResponse)
async def get_contact_list(
    list_id: str,
    page: int = 1,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cl = await contact_service.get_list_by_id(db, list_id, current_user.id)
    if not cl:
        raise HTTPException(status_code=404, detail="Contact list not found")
    contacts, total = await contact_service.list_contacts(db, list_id, page, limit)
    return PaginatedResponse(
        items=[ContactResponse.model_validate(c) for c in contacts],
        total=total,
        page=page,
        pages=(total + limit - 1) // limit,
    )


@router.delete("/lists/{list_id}")
async def delete_contact_list(
    list_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cl = await contact_service.get_list_by_id(db, list_id, current_user.id)
    if not cl:
        raise HTTPException(status_code=404, detail="Contact list not found")
    await contact_service.delete_list(db, cl)
    return {"message": "Contact list deleted"}


@router.post("/lists/{list_id}/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def add_contact(
    list_id: str,
    body: ContactCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cl = await contact_service.get_list_by_id(db, list_id, current_user.id)
    if not cl:
        raise HTTPException(status_code=404, detail="Contact list not found")
    contact = await contact_service.add_contact(db, list_id, body.phone, body.name, body.email, body.company)
    return contact


@router.post("/upload", response_model=BulkUploadResponse)
async def bulk_upload(
    list_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cl = await contact_service.get_list_by_id(db, list_id, current_user.id)
    if not cl:
        raise HTTPException(status_code=404, detail="Contact list not found")

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    try:
        valid_rows, errors = await contact_service.validate_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    imported = await contact_service.import_contacts(db, list_id, valid_rows)

    return BulkUploadResponse(
        total_rows=len(valid_rows) + len(errors),
        valid_rows=len(valid_rows),
        invalid_rows=len(errors),
        duplicates_skipped=len(valid_rows) - imported,
        list_id=list_id,
        errors=errors,
    )


@router.get("/upload/validate")
async def validate_upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    try:
        valid_rows, errors = await contact_service.validate_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "total_rows": len(valid_rows) + len(errors),
        "valid_rows": len(valid_rows),
        "invalid_rows": len(errors),
        "errors": errors,
    }


@router.post("/upload-preview")
async def upload_contact_preview(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    content = await file.read()
    try:
        valid_rows, errors = await contact_service.validate_upload(content, file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    all_rows = []
    for r in valid_rows:
        all_rows.append({"phone": r["phone"], "name": r.get("name", ""), "email": r.get("email", ""), "company": r.get("company", ""), "_valid": True, "_errors": []})
    for e in errors:
        all_rows.append({"phone": e.get("phone", ""), "name": "", "email": "", "company": "", "_valid": False, "_errors": e.get("errors", [])})

    return {
        "rows": all_rows,
        "total": len(all_rows),
        "valid": len(valid_rows),
        "invalid": len(errors),
    }


@router.post("/lists/{list_id}/import", response_model=BulkUploadResponse)
async def bulk_import_contacts(
    list_id: str,
    contacts: list[ContactImportRow],
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cl = await contact_service.get_list_by_id(db, list_id, current_user.id)
    if not cl:
        raise HTTPException(status_code=404, detail="Contact list not found")

    valid_rows = [{"phone": c.phone, "name": c.name or "", "email": c.email or "", "company": c.company or ""} for c in contacts]
    imported = await contact_service.import_contacts(db, list_id, valid_rows)

    return BulkUploadResponse(
        total_rows=len(valid_rows),
        valid_rows=len(valid_rows),
        invalid_rows=0,
        duplicates_skipped=len(valid_rows) - imported,
        list_id=list_id,
        errors=[],
    )
