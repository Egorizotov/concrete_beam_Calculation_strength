# ЮГ БЕТОН — REST API (Лабораторная №3)

## Таблицы БД

### beam_marks
| Поле | Тип | Описание |
|---|---|---|
| beam_mark_id | SERIAL PK | ID |
| beam_mark_name | VARCHAR(100) | Название |
| beam_mark_description | VARCHAR(1000) | Описание |
| beam_mark_status | VARCHAR(20) | черновик/опубликован/удален |
| beam_mark_image_url | VARCHAR(500) | URL из MinIO |
| beam_mark_video_url | VARCHAR(500) | URL из MinIO |
| beam_mark_price | FLOAT | Цена |
| beam_mark_strength | FLOAT | Прочность |
| beam_mark_created_at | TIMESTAMP | Дата создания |
| beam_mark_published_at | TIMESTAMP | Дата публикации |
| beam_mark_creator_id | INT FK → users | Создатель |

### users
| Поле | Тип | Описание |
|---|---|---|
| user_id | SERIAL PK | ID |
| user_username | VARCHAR(50) UNIQUE | Логин |
| user_email | VARCHAR(100) UNIQUE | Email |
| user_password | VARCHAR(100) | Пароль |

### likes
| Поле | Тип | Описание |
|---|---|---|
| like_id | SERIAL PK | ID |
| like_user_id | INT FK → users | Кто лайкнул |
| like_beam_mark_id | INT FK → beam_marks | Что лайкнул |

## Методы API

| Метод | URL | Описание |
|---|---|---|
| GET | /api/beam-marks | Список с фильтром (только опубликованные) |
| GET | /api/beam-marks/feed | Лента с флагом is_liked |
| GET | /api/beam-marks/draft | Черновик текущего пользователя |
| POST | /api/beam-marks | Создать + загрузить файлы |
| PUT | /api/beam-marks/{id}/publish | Опубликовать |
| DELETE | /api/beam-marks/{id} | Soft delete |
| POST | /api/beam-marks/{id}/like | Лайк (0/1) |
| POST | /api/users/register | Регистрация |
| POST | /api/users/login | Логин |
| POST | /api/users/logout | Выход |
