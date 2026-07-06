from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.script import Script


class ScriptService:
    async def get_by_id(self, db: AsyncSession, script_id: str, user_id: str) -> Script | None:
        result = await db.execute(
            select(Script).where(Script.id == script_id, Script.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_scripts(self, db: AsyncSession, user_id: str, page: int = 1, limit: int = 20) -> tuple[list[Script], int]:
        count_q = select(func.count()).select_from(Script).where(Script.user_id == user_id)
        total = (await db.execute(count_q)).scalar() or 0

        q = (
            select(Script)
            .where(Script.user_id == user_id)
            .order_by(Script.updated_at.desc())
            .offset((page - 1) * limit)
            .limit(limit)
        )
        result = await db.execute(q)
        return list(result.scalars().all()), total

    async def create(self, db: AsyncSession, user_id: str, **kwargs) -> Script:
        script = Script(user_id=user_id, **kwargs)
        db.add(script)
        await db.flush()
        return script

    async def update(self, db: AsyncSession, script: Script, **kwargs) -> Script:
        for key, value in kwargs.items():
            if value is not None and hasattr(script, key):
                setattr(script, key, value)
        script.version += 1
        await db.flush()
        return script

    async def delete(self, db: AsyncSession, script: Script) -> None:
        await db.delete(script)
        await db.flush()

    async def set_active(self, db: AsyncSession, script: Script, user_id: str) -> None:
        result = await db.execute(
            select(Script).where(Script.user_id == user_id, Script.is_active == True)
        )
        for s in result.scalars().all():
            s.is_active = False
        script.is_active = True
        await db.flush()

    async def get_active(self, db: AsyncSession, user_id: str) -> Script | None:
        result = await db.execute(
            select(Script).where(Script.user_id == user_id, Script.is_active == True)
        )
        return result.scalar_one_or_none()


script_service = ScriptService()
