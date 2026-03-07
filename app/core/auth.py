from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.constants import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
oauth2_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


class UserContext(BaseModel):
    """
    DTO del usuario autenticado. Es lo único que circula fuera de auth.py —
    ninguna capa por encima ve el Document de mongoengine.
    """
    id: str
    email: str
    first_name: str
    last_name: str
    course_id: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


def _doc_to_context(user) -> UserContext:
    return UserContext(
        id=str(user.id),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        course_id=str(user.course.id) if user.course else "",
    )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserContext:
    from app.models.user import User

    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = User.objects(id=user_id, is_active=True).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
        )
    return _doc_to_context(user)


async def get_optional_user(
    token: Optional[str] = Depends(oauth2_optional),
) -> Optional[UserContext]:
    if not token:
        return None
    from app.models.user import User

    user_id = decode_token(token)
    if not user_id:
        return None
    user = User.objects(id=user_id, is_active=True).first()
    return _doc_to_context(user) if user else None