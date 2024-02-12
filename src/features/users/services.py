from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from passlib.context import CryptContext
from sqlalchemy import select

from src.core.container import Container
from src.database.session import Session

from .exceptions import InvalidCredentials, UserAlreadyExists, UserNotFound
from .models import User
from .schemas import UserCredentials


class UsersService:
    @inject
    def __init__(
        self,
        session: Session,
        passlib_context: CryptContext = Depends(Provide[Container.passlib_context]),
    ) -> None:
        self.session = session
        self._passlib_context = passlib_context

    async def get_user_by_id(self, user_id: int) -> User:
        user = await self.session.get(User, user_id)
        if not user:
            raise UserNotFound()
        return user

    async def get_user_by_credentials(self, credentials: UserCredentials) -> User:
        user = await self.session.scalar(
            select(User).where(User.email == credentials.email)
        )
        if not user:
            raise UserNotFound()
        password_is_correct = self._passlib_context.verify(
            credentials.password,
            user.password,
        )
        if not password_is_correct:
            raise InvalidCredentials()
        return user

    async def create_user(self, credentials: UserCredentials) -> User:
        existing_user = await self.session.scalar(
            select(User).where(User.email == credentials.email)
        )
        if existing_user:
            raise UserAlreadyExists()
        hashed_password = self._passlib_context.hash(credentials.password)
        db_user = User(
            email=credentials.email,
            password=hashed_password,
        )
        self.session.add(db_user)
        await self.session.flush()
        return db_user

    async def delete_user(self, user_id: int) -> None:
        user = await self.get_user_by_id(user_id)
        await self.session.delete(user)
        await self.session.flush()
