from datetime import datetime

from fastapi import (
    APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
)
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from models.beam_mark import BeamMark
from models.like import Like
from models.user import User
from schemas.beam_mark import (
    BeamMarkCreate, BeamMarkPublish, BeamMarkResponse, LikeRequest,
)
from schemas.user import UserLogin, UserRegister, UserResponse
from services.current_user import current_user
from services.minio_service import minio_service

router = APIRouter(prefix="/api")


# ==========================================================
#   ДОМЕН УСЛУГИ (beam_mark)
# ==========================================================

# ---------- GET список с фильтрацией ----------
@router.get("/beam-marks", response_model=list[BeamMarkResponse])
async def list_beam_marks(
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
    marks = result.scalars().all()

    return [
        BeamMarkResponse.model_validate(m).model_copy(
            update={"is_mine": m.beam_mark_creator_id == current_user.user_id}
        )
        for m in marks
    ]


# ---------- GET лента ----------
@router.get("/beam-marks/feed", response_model=list[BeamMarkResponse])
async def feed_beam_marks(db: AsyncSession = Depends(get_db)):
    stmt = select(BeamMark).where(BeamMark.beam_mark_status == "опубликован")
    result = await db.execute(stmt.order_by(BeamMark.beam_mark_id))
    marks = result.scalars().all()

    # ID лайкнутых текущим юзером
    likes_result = await db.execute(
        select(Like.like_beam_mark_id).where(Like.like_user_id == current_user.user_id)
    )
    liked_ids = {row[0] for row in likes_result.all()}

    return [
        BeamMarkResponse.model_validate(m).model_copy(
            update={
                "is_mine": m.beam_mark_creator_id == current_user.user_id,
                "is_liked": m.beam_mark_id in liked_ids,
            }
        )
        for m in marks
    ]


# ---------- GET черновик ----------
@router.get("/beam-marks/draft", response_model=BeamMarkResponse | None)
async def get_draft(db: AsyncSession = Depends(get_db)):
    stmt = select(BeamMark).where(
        BeamMark.beam_mark_status == "черновик",
        BeamMark.beam_mark_creator_id == current_user.user_id,
    )
    result = await db.execute(stmt)
    draft = result.scalar_one_or_none()

    if draft is None:
        return None

    return BeamMarkResponse.model_validate(draft)


# ---------- POST создание + загрузка файлов ----------
@router.post("/beam-marks", response_model=BeamMarkResponse, status_code=201)
async def create_beam_mark(
    beam_mark_name: str = Form(...),
    beam_mark_description: str = Form(default=""),
    beam_mark_price: float = Form(...),
    beam_mark_strength: float = Form(...),
    image: UploadFile | None = File(default=None),
    video: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
):
    # Проверяем, что нет второго черновика
    existing = await db.execute(
        select(BeamMark).where(
            BeamMark.beam_mark_status == "черновик",
            BeamMark.beam_mark_creator_id == current_user.user_id,
        )
    )
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(400, "У пользователя уже есть черновик")

    # Сначала создаём запись, чтобы получить ID (для имени файла)
    new_mark = BeamMark(
        beam_mark_name=beam_mark_name,
        beam_mark_description=beam_mark_description,
        beam_mark_status="черновик",
        beam_mark_price=beam_mark_price,
        beam_mark_strength=beam_mark_strength,
        beam_mark_creator_id=current_user.user_id,
        beam_mark_created_at=datetime.utcnow(),
    )
    db.add(new_mark)
    await db.flush()  # получаем beam_mark_id без commit

    # Загружаем файлы (имена на латинице!)
    if image and image.filename:
        ext = image.filename.rsplit(".", 1)[-1].lower()
        filename = f"beam-mark-{new_mark.beam_mark_id}-image.{ext}"
        content = await image.read()
        new_mark.beam_mark_image_url = minio_service.upload(
            content, filename, image.content_type or "image/jpeg"
        )

    if video and video.filename:
        ext = video.filename.rsplit(".", 1)[-1].lower()
        filename = f"beam-mark-{new_mark.beam_mark_id}-video.{ext}"
        content = await video.read()
        new_mark.beam_mark_video_url = minio_service.upload(
            content, filename, video.content_type or "video/mp4"
        )

    await db.commit()
    await db.refresh(new_mark)

    return BeamMarkResponse.model_validate(new_mark)


# ---------- PUT публикация ----------
@router.put("/beam-marks/{beam_mark_id}/publish", response_model=BeamMarkResponse)
async def publish_beam_mark(
    beam_mark_id: int,
    payload: BeamMarkPublish,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BeamMark).where(BeamMark.beam_mark_id == beam_mark_id)
    result = await db.execute(stmt)
    mark = result.scalar_one_or_none()

    if mark is None:
        raise HTTPException(404, "Марка не найдена")

    if mark.beam_mark_creator_id != current_user.user_id:
        raise HTTPException(403, "Это не ваша марка")

    if mark.beam_mark_status == "удален":
        raise HTTPException(400, "Удалённую нельзя публиковать")

    if mark.beam_mark_status == "опубликован":
        raise HTTPException(400, "Уже опубликована")

    # Обновляем поля и меняем статус
    mark.beam_mark_description = payload.beam_mark_description
    mark.beam_mark_price = payload.beam_mark_price
    mark.beam_mark_strength = payload.beam_mark_strength
    mark.beam_mark_status = "опубликован"
    mark.beam_mark_published_at = datetime.utcnow()

    await db.commit()
    await db.refresh(mark)

    return BeamMarkResponse.model_validate(mark)


# ---------- DELETE soft delete ----------
@router.delete("/beam-marks/{beam_mark_id}", status_code=200)
async def delete_beam_mark(
    beam_mark_id: int,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(BeamMark).where(BeamMark.beam_mark_id == beam_mark_id)
    result = await db.execute(stmt)
    mark = result.scalar_one_or_none()

    if mark is None:
        raise HTTPException(404, "Марка не найдена")

    if mark.beam_mark_creator_id != current_user.user_id:
        raise HTTPException(403, "Это не ваша марка")

    # Требование: удаление через raw SQL (без ORM)
    await db.execute(
        text("UPDATE beam_marks SET beam_mark_status = 'удален' WHERE beam_mark_id = :id"),
        {"id": beam_mark_id},
    )
    await db.commit()

    return {"status": "success", "message": f"Марка {beam_mark_id} удалена"}


# ---------- POST like (toggle 0/1) ----------
@router.post("/beam-marks/{beam_mark_id}/like")
async def toggle_like(
    beam_mark_id: int,
    payload: LikeRequest,
    db: AsyncSession = Depends(get_db),
):
    # Проверяем, что марка существует и опубликована
    stmt = select(BeamMark).where(
        BeamMark.beam_mark_id == beam_mark_id,
        BeamMark.beam_mark_status == "опубликован",
    )
    result = await db.execute(stmt)
    mark = result.scalar_one_or_none()
    if mark is None:
        raise HTTPException(404, "Марка не найдена")

    # Ищем существующий лайк
    like_stmt = select(Like).where(
        Like.like_user_id == current_user.user_id,
        Like.like_beam_mark_id == beam_mark_id,
    )
    like_result = await db.execute(like_stmt)
    existing_like = like_result.scalar_one_or_none()

    if payload.value == 1:
        if existing_like is None:
            db.add(Like(
                like_user_id=current_user.user_id,
                like_beam_mark_id=beam_mark_id,
            ))
    else:  # value == 0
        if existing_like is not None:
            await db.delete(existing_like)

    await db.commit()

    # Считаем актуальное количество лайков
    count_result = await db.execute(
        select(func.count(Like.like_id)).where(Like.like_beam_mark_id == beam_mark_id)
    )
    total = count_result.scalar() or 0

    return {"status": "success", "likes_count": total, "is_liked": payload.value == 1}


# ==========================================================
#   ДОМЕН ПОЛЬЗОВАТЕЛЯ
# ==========================================================

@router.post("/users/register", response_model=UserResponse, status_code=201)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    # Проверка на дубликат
    existing = await db.execute(
        select(User).where(User.user_username == payload.user_username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Логин уже занят")

    user = User(
        user_username=payload.user_username,
        user_email=payload.user_email,
        # ВНИМАНИЕ: в реальном проекте пароль надо хешировать!
        user_password=payload.user_password,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/users/login", response_model=UserResponse)
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Заглушка для Лаб.4 — просто проверяем логин/пароль."""
    result = await db.execute(
        select(User).where(User.user_username == payload.user_username)
    )
    user = result.scalar_one_or_none()

    if user is None or user.user_password != payload.user_password:
        raise HTTPException(401, "Неверный логин или пароль")

    # Устанавливаем текущего пользователя в singleton
    current_user.set_user(user)

    return UserResponse.model_validate(user)


@router.post("/users/logout")
async def logout_user():
    """Заглушка для Лаб.4 — сбрасываем singleton на дефолт."""
    return {"status": "success", "message": "Вы вышли из системы"}