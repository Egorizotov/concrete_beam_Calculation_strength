MINIO_PUBLIC_URL = "http://localhost:9000/concrete-media"

concrete_mixes = [
    {
        "concrete_mix_id": 100,
        "concrete_mix_name": "M100",
        "concrete_mix_price": 4200,
        "concrete_mix_strength": 7.5,
        "concrete_mix_description": "Лёгкая бетонная смесь для подготовительных и ненагруженных работ, полезна в строительстве легких и простых конструкций, а также для заливки стяжек и создания фундаментов под небольшие постройки. Подходит для любых видов работ, где не требуется повышенная прочность, обеспечивает удобство укладки и быстрое затвердевание.",
        "concrete_mix_image_key": "m100.jpg",
        "concrete_mix_video_key": "m100.mp4",
        "concrete_mix_status": "опубликован",
        "concrete_mix_likes_user_ids": [1, 4, 7, 12, 19],
    },
    {
        "concrete_mix_id": 150,
        "concrete_mix_name": "M150",
        "concrete_mix_price": 4600,
        "concrete_mix_strength": 11.2,
        "concrete_mix_description": "Универсальная бетонная смесь для стяжек, дорожек и небольших конструкций, полезна в стоительстве дорог и домашних участках",
        "concrete_mix_image_key": "m150.jpg",
        "concrete_mix_video_key": "m150.mp4",
        "concrete_mix_status": "опубликован",
        "concrete_mix_likes_user_ids": [2, 3, 9, 14],
    },
    {
        "concrete_mix_id": 300,
        "concrete_mix_name": "M300",
        "concrete_mix_price": 5900,
        "concrete_mix_strength": 22.5,
        "concrete_mix_description": "Прочный бетон для фундаментов, плит, лестниц и других ответственных работ, обеспечивает высокую несущую способность и долговечность конструкций.",
        "concrete_mix_image_key": "m300.jpg",
        "concrete_mix_video_key": "m300.mp4",
        "concrete_mix_status": "опубликован",
        "concrete_mix_likes_user_ids": [1, 2, 5, 6, 8, 11, 16, 21, 24, 27, 31, 33, 35, 40, 44],
    },
    {
        "concrete_mix_id": 400,
        "concrete_mix_name": "M400",
        "concrete_mix_price": 7200,
        "concrete_mix_strength": 25.0,
        "concrete_mix_description": "Бетон повышенной прочности для мостов, колонн и ответственных железобетонных конструкций, применяется в сложных инженерных объектах.",
        "concrete_mix_image_key": "m400.jpg",
        "concrete_mix_video_key": "m400.mp4",
        "concrete_mix_status": "опубликован",
        "concrete_mix_likes_user_ids": [4, 7, 10, 13, 18, 20, 22, 25, 29, 30, 32, 36, 38, 41, 45, 48, 50, 52, 55, 58],
    },
    {
        "concrete_mix_id": 500,
        "concrete_mix_name": "M500",
        "concrete_mix_price": 8400,
        "concrete_mix_strength": 30.0,
        "concrete_mix_description": "Высокопрочный бетон для особо ответственных промышленных и инженерных конструкций, где предъявляются повышенные требования к прочности и устойчивости.",
        "concrete_mix_image_key": "m500.jpg",
        "concrete_mix_video_key": "m500.mp4",
        "concrete_mix_status": "опубликован",
        "concrete_mix_likes_user_ids": [1, 3, 6, 9, 12, 15, 17, 19, 23, 26, 28, 34, 37, 39, 43, 46, 49, 51, 54, 57, 60, 63, 66, 69, 72, 75, 78],
    },
    {
        "concrete_mix_id": 350,
        "concrete_mix_name": "M350",
        "concrete_mix_price": 6500,
        "concrete_mix_strength": 38.0,
        "concrete_mix_description": "Высокопрочная смесь для монолитных конструкций и повышенных нагрузок, применяется при возведении многоэтажных зданий и ответственных сооружений.",
        "concrete_mix_image_key": "m350.jpg",
        "concrete_mix_video_key": "m350.mp4",
        "concrete_mix_status": "опубликован",
        "concrete_mix_likes_user_ids": [2, 5, 8, 11, 14, 17, 20, 23, 26, 29, 32, 35, 38, 41, 44, 47, 50, 53, 56, 59],
    },
    {
        "concrete_mix_id": 999,
        "concrete_mix_name": "Новая бетонная смесь",
        "concrete_mix_price": 0,
        "concrete_mix_strength": 0.0,
        "concrete_mix_description": "",
        "concrete_mix_image_key": "draft.jpg",
        "concrete_mix_video_key": "draft.mp4",
        "concrete_mix_status": "черновик",
        "concrete_mix_likes_user_ids": [],
    },
    {
        "concrete_mix_id": 998,
        "concrete_mix_name": "Удалённая бетонная смесь",
        "concrete_mix_price": 0,
        "concrete_mix_strength": 0.0,
        "concrete_mix_description": "",
        "concrete_mix_image_key": "deleted.jpg",
        "concrete_mix_video_key": "deleted.mp4",
        "concrete_mix_status": "удален",
        "concrete_mix_likes_user_ids": [],
    },
]


def with_media_urls(concrete_mix: dict) -> dict:
    """Готовит представление записи для Jinja2, не изменяя исходную коллекцию."""
    result = concrete_mix.copy()
    result["concrete_mix_image_url"] = (
        f"{MINIO_PUBLIC_URL}/{concrete_mix['concrete_mix_image_key']}"
    )
    result["concrete_mix_video_url"] = (
        f"{MINIO_PUBLIC_URL}/{concrete_mix['concrete_mix_video_key']}"
    )
    result["concrete_mix_likes_count"] = len(
        concrete_mix["concrete_mix_likes_user_ids"]
    )
    return result