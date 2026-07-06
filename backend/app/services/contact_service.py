from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.contact_list import ContactList
from app.models.contact import Contact
from app.utils.phone_validator import normalize_phone
from app.utils.file_parser import parse_csv, parse_excel, parse_pdf, detect_columns, validate_rows


class ContactService:
    async def list_lists(self, db: AsyncSession, user_id: str, page: int = 1, limit: int = 20) -> tuple[list[ContactList], int]:
        count_q = select(func.count()).select_from(ContactList).where(ContactList.user_id == user_id)
        total = (await db.execute(count_q)).scalar() or 0
        q = (
            select(ContactList)
            .where(ContactList.user_id == user_id)
            .order_by(ContactList.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(q)
        return list(result.scalars().all()), total

    async def get_list_by_id(self, db: AsyncSession, list_id: str, user_id: str) -> ContactList | None:
        result = await db.execute(
            select(ContactList).where(ContactList.id == list_id, ContactList.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_list(self, db: AsyncSession, user_id: str, name: str, description: str | None = None) -> ContactList:
        cl = ContactList(user_id=user_id, name=name, description=description)
        db.add(cl)
        await db.flush()
        return cl

    async def delete_list(self, db: AsyncSession, contact_list: ContactList) -> None:
        await db.delete(contact_list)
        await db.flush()

    async def add_contact(self, db: AsyncSession, list_id: str, phone: str, name: str | None = None, email: str | None = None, company: str | None = None) -> Contact:
        contact = Contact(
            list_id=list_id,
            phone=normalize_phone(phone),
            name=name,
            email=email,
            company=company,
        )
        db.add(contact)
        await db.flush()
        await self._update_count(db, list_id)
        return contact

    async def list_contacts(self, db: AsyncSession, list_id: str, page: int = 1, limit: int = 50) -> tuple[list[Contact], int]:
        count_q = select(func.count()).select_from(Contact).where(Contact.list_id == list_id)
        total = (await db.execute(count_q)).scalar() or 0
        q = (
            select(Contact)
            .where(Contact.list_id == list_id)
            .order_by(Contact.created_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(q)
        return list(result.scalars().all()), total

    async def validate_upload(self, file_content: bytes, filename: str) -> tuple[list[dict], list[dict]]:
        if filename.endswith(".csv"):
            rows = parse_csv(file_content)
        elif filename.endswith((".xlsx", ".xls")):
            rows = parse_excel(file_content)
        elif filename.endswith(".pdf"):
            rows = parse_pdf(file_content)
        else:
            raise ValueError("Unsupported file format. Use CSV, XLSX, or PDF.")

        if not rows:
            return [], [{"row": 1, "phone": "", "errors": ["File is empty"]}]

        headers = list(rows[0].keys())
        column_map = detect_columns(headers)

        if not column_map.get("phone"):
            raise ValueError("No phone number column detected. Ensure your file has a 'phone', 'mobile', or 'number' column.")

        valid, errors = validate_rows(rows, column_map)
        return valid, errors

    async def import_contacts(self, db: AsyncSession, list_id: str, valid_rows: list[dict]) -> int:
        count = 0
        for row in valid_rows:
            existing = await db.execute(
                select(Contact).where(Contact.list_id == list_id, Contact.phone == row["phone"])
            )
            if existing.scalar_one_or_none():
                continue
            contact = Contact(
                list_id=list_id,
                phone=row["phone"],
                name=row.get("name"),
                email=row.get("email"),
                company=row.get("company"),
            )
            db.add(contact)
            count += 1
        await db.flush()
        await self._update_count(db, list_id)
        return count

    async def _update_count(self, db: AsyncSession, list_id: str) -> None:
        count = (await db.execute(
            select(func.count()).select_from(Contact).where(Contact.list_id == list_id)
        )).scalar() or 0
        await db.execute(
            update(ContactList).where(ContactList.id == list_id).values(contact_count=count)
        )


contact_service = ContactService()
