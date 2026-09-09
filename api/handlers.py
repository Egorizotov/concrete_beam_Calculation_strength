from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.templating import Jinja2Templates

from data.collections import concrete_mixes, with_media_urls

router = APIRouter()
templates = Jinja2Templates(directory="templates")


def published_concrete_mixes():
    """Возвращает только опубликованные бетонные смеси."""
    return [
        with_media_urls(concrete_mix)
        for concrete_mix in concrete_mixes
        if concrete_mix["concrete_mix_status"] == "опубликован"
    ]


@router.get("/concrete-mixes")
def get_concrete_mix_tiles(
    request: Request,
    concrete_mix_strength: float | None = Query(
        default=None,
        ge=0,
        description="Фильтрация по прочности бетона, МПа",
    ),
):
    """
    GET №1: список опубликованных бетонных смесей.
    Если concrete_mix_strength не задан — выводятся все.
    """
    visible_mixes = published_concrete_mixes()

    if concrete_mix_strength is not None:
        visible_mixes = [
            concrete_mix
            for concrete_mix in visible_mixes
            if concrete_mix["concrete_mix_strength"] == concrete_mix_strength
        ]

    return templates.TemplateResponse(
        request=request,
        name="concrete_mix_tiles.html",
        context={
            "concrete_mixes": visible_mixes,
            "concrete_mix_strength": (
                "" if concrete_mix_strength is None else concrete_mix_strength
            ),
        },
    )


@router.get("/concrete-mixes/draft")
def get_concrete_mix_draft(request: Request):
    """
    GET №2: получение единственного черновика.
    Страница позволяет заполнять форму, но ничего не сохраняет.
    """
    draft = next(
        (
            with_media_urls(concrete_mix)
            for concrete_mix in concrete_mixes
            if concrete_mix["concrete_mix_status"] == "черновик"
        ),
        None,
    )

    if draft is None:
        raise HTTPException(status_code=404, detail="Черновик не найден")

    return templates.TemplateResponse(
        request=request,
        name="concrete_mix_draft.html",
        context={"concrete_mix": draft},
    )


@router.get("/concrete-mixes/{concrete_mix_id}")
def get_concrete_mix_feed(
    request: Request,
    concrete_mix_id: int,
    show_next: bool = Query(default=False, alias="next"),
):
    """
    GET №3: лента по ID.
    При ?next=true открывается следующая опубликованная смесь.
    """
    visible_mixes = published_concrete_mixes()
    current_index = next(
        (
            index
            for index, concrete_mix in enumerate(visible_mixes)
            if concrete_mix["concrete_mix_id"] == concrete_mix_id
        ),
        None,
    )

    if current_index is None:
        raise HTTPException(status_code=404, detail="Бетонная смесь не найдена")

    if show_next:
        concrete_mix = visible_mixes[(current_index + 1) % len(visible_mixes)]
    else:
        concrete_mix = visible_mixes[current_index]

    return templates.TemplateResponse(
        request=request,
        name="concrete_mix_feed.html",
        context={"concrete_mix": concrete_mix},
    )
