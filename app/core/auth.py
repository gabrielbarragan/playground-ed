from datetime import datetime, timedelta
from typing import Optional

import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.constants import JWT_SECRET, JWT_ALGORITHM, JWT_EXPIRE_MINUTES

_ITERATIONS = 260_000
_ALGORITHM  = "sha256"

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
    is_admin: bool = False


def hash_password(password: str) -> str:
    salt = secrets.token_hex(32)
    key = hashlib.pbkdf2_hmac(_ALGORITHM, password.encode(), salt.encode(), _ITERATIONS)
    return f"pbkdf2:{_ALGORITHM}:{_ITERATIONS}${salt}${key.hex()}"


def verify_password(plain: str, hashed: str) -> bool:
    try:
        method, salt, stored_key = hashed.split("$")
        _, algorithm, iterations = method.split(":")
        new_key = hashlib.pbkdf2_hmac(algorithm, plain.encode(), salt.encode(), int(iterations))
        return hmac.compare_digest(new_key.hex(), stored_key)
    except Exception:
        return False


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
        is_admin=user.is_admin,
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


async def get_current_admin(token: str = Depends(oauth2_scheme)) -> UserContext:
    ctx = await get_current_user(token)
    if not ctx.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso restringido a administradores",
        )
    return ctx


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