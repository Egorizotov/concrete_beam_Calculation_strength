from datetime import datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.beam_mark import BeamMark
from models.like import Like
from models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="templates")

CURRENT_USER_ID = 1


@router.get("/beam-marks")
async def get_beam_mark_tiles(
    request: Request,
    strength_min: float | None = Query(default=None, ge=0),
    strength_max: float | None = Query(default=None, ge=0),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BeamMark).where(BeamMark.beam_mark_status == "опубликован")

    if strength_min is not None:
        stmt = stmt.where(BeamMark.beam_mark_strength >= strength_min)
    if strength_max is not None:
        stmt = stmt.where(BeamMark.beam_mark_strength <= strength_max)

    result = await db.execute(stmt.order_by(BeamMark.beam_mark_strength))
    beam_marks = result.scalars().all()

    likes_stmt = select(Like.like_beam_mark_id, func.count(Like.like_id)).group_by(
        Like.like_beam_mark_id
    )
    likes_result = await db.execute(likes_stmt)
    likes_map = dict(likes_result.all())

    return templates.TemplateResponse(
        request=request,
        name="beam_mark_tiles.html",
        context={
            "beam_marks": beam_marks,
            "likes_map": likes_map,
            "strength_min": "" if strength_min is None else strength_min,
            "strength_max": "" if strength_max is None else strength_max,
        },
    )


@router.get("/beam-marks/draft")
async def get_beam_mark_draft(request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(BeamMark).where(
        BeamMark.beam_mark_status == "черновик",
        BeamMark.beam_mark_creator_id == CURRENT_USER_ID,
    )
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    return templates.TemplateResponse(
        request=request,
        name="beam_mark_draft.html",
        context={"beam_mark": draft},
    )


@router.get("/beam-marks/{beam_mark_id}")
async def get_beam_mark_feed(
    request: Request,
    beam_mark_id: int,
    show_next: bool = Query(default=False, alias="next"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BeamMark).where(
        BeamMark.beam_mark_status == "опубликован"
    ).order_by(BeamMark.beam_mark_id)

    result = await db.execute(stmt)
    visible_marks = result.scalars().all()

    current_index = next(
        (i for i, m in enumerate(visible_marks) if m.beam_mark_id == beam_mark_id),
        None,
    )
    if current_index is None:
        raise HTTPException(status_code=404, detail="Марка балки не найдена")

    if show_next:
        beam_mark = visible_marks[(current_index + 1) % len(visible_marks)]
    else:
        beam_mark = visible_marks[current_index]

    likes_count_result = await db.execute(
        select(func.count(Like.like_id)).where(
            Like.like_beam_mark_id == beam_mark.beam_mark_id
        )
    )
    likes_count = likes_count_result.scalar() or 0

    return templates.TemplateResponse(
        request=request,
        name="beam_mark_feed.html",
        context={"beam_mark": beam_mark, "likes_count": likes_count},
    )


@router.post("/beam-marks/draft")
async def create_beam_mark_draft(
    beam_mark_name: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    existing = await db.execute(
        select(BeamMark).where(
            BeamMark.beam_mark_status == "черновик",
            BeamMark.beam_mark_creator_id == CURRENT_USER_ID,
        )
    )
    draft = existing.scalar_one_or_none()

    if draft is not None:
        return RedirectResponse(url="/beam-marks/draft", status_code=303)

    new_draft = BeamMark(
        beam_mark_name=beam_mark_name,
        beam_mark_description="",
        beam_mark_status="черновик",
        beam_mark_image_url=None,     # 👈 не сохраняем — по методичке
        beam_mark_video_url=None,     # 👈 не сохраняем — по методичке
        beam_mark_creator_id=CURRENT_USER_ID,
        beam_mark_created_at=datetime.utcnow(),
    )
    db.add(new_draft)
    await db.commit()

    return RedirectResponse(url="/beam-marks/draft", status_code=303)


@router.post("/beam-marks/draft/publish")
async def publish_beam_mark(
    beam_mark_description: str = Form(...),
    beam_mark_price: float = Form(...),
    beam_mark_strength: float = Form(...),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BeamMark).where(
        BeamMark.beam_mark_status == "черновик",
        BeamMark.beam_mark_creator_id == CURRENT_USER_ID,
    )
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    if draft is None:
        raise HTTPException(status_code=404, detail="Черновик не найден")

    draft.beam_mark_description = beam_mark_description
    draft.beam_mark_price = beam_mark_price
    draft.beam_mark_strength = beam_mark_strength
    draft.beam_mark_status = "опубликован"
    draft.beam_mark_published_at = datetime.utcnow()

    await db.commit()
    return RedirectResponse(url="/beam-marks", status_code=303)


@router.post("/beam-marks/{beam_mark_id}/delete")
async def delete_beam_mark(
    beam_mark_id: int,
    db: AsyncSession = Depends(get_db),
):
    update_query = """
        UPDATE beam_marks
        SET beam_mark_status = 'удален'
        WHERE beam_mark_id = :id
    """
    await db.execute(text(update_query), {"id": beam_mark_id})
    await db.commit()

    return RedirectResponse(url="/beam-marks", status_code=303)