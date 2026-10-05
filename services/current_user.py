from models.user import User


class _CurrentUser:
    """Singleton — фиксированный текущий пользователь (заглушка до Лаб.4)."""

    def __init__(self) -> None:
        self._user_id: int = 1  # 👈 константа
        self._user: User | None = None

    @property
    def user_id(self) -> int:
        return self._user_id

    def set_user(self, user: User) -> None:
        """Позже вызовется из auth-middleware."""
        self._user = user
        self._user_id = user.user_id

    @property
    def user(self) -> User | None:
        return self._user


current_user = _CurrentUser()