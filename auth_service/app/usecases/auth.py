from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest, TokenResponse


class AuthUseCase:
    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def register(self, payload: RegisterRequest) -> User:
        existing = await self.users_repo.get_by_email(payload.email)
        if existing:
            raise UserAlreadyExistsError()
        password_hash = hash_password(payload.password)
        return await self.users_repo.create(email=payload.email, password_hash=password_hash)

    async def login(self, username: str, password: str) -> TokenResponse:
        user = await self.users_repo.get_by_email(username)
        if not user or not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        token = create_access_token(sub=str(user.id), role=user.role)
        return TokenResponse(access_token=token)

    async def me(self, user_id: int) -> User:
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()
        return user
