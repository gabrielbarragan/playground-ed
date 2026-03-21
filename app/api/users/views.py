from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from app.core.auth import get_current_user, UserContext
from app.api.users.handler import UserHandler
from app.api.users import process
from app.api.users.serializer import (
    RegisterInSerializer,
    UpdateProfileSerializer,
    SetBadgeSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer,
    ChangeEmailSerializer,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])
users_router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(body: RegisterInSerializer):
    try:
        user = UserHandler.register(
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            password=body.password,
            course_id=body.course_id,
        )
    except ValueError as e:
        code = status.HTTP_409_CONFLICT if "correo" in str(e) else status.HTTP_404_NOT_FOUND
        raise HTTPException(status_code=code, detail=str(e))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=user)


@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """El campo `username` recibe el email (estándar OAuth2 Password Flow)."""
    try:
        token = UserHandler.login(email=form.username, password=form.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@users_router.get("/me")
async def get_me(ctx: UserContext = Depends(get_current_user)):
    user = UserHandler.get_profile(ctx.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return user


@users_router.put("/me")
async def update_me(
    body: UpdateProfileSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    try:
        user = UserHandler.update_profile(ctx.id, body.first_name, body.last_name)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return user


@users_router.put("/me/badge")
async def set_my_badge(
    body: SetBadgeSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    try:
        user = UserHandler.set_badge(ctx.id, body.emoji)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return user


# ── Recuperación de contraseña (público) ───────────────────

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(body: ForgotPasswordSerializer):
    """Siempre retorna 200 — evita email enumeration."""
    await process.forgot_password_process(body.email)
    return {"message": "Si el correo existe, recibirás un link para restablecer tu contraseña."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(body: ResetPasswordSerializer):
    try:
        await process.reset_password_process(body.token, body.new_password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Contraseña actualizada correctamente."}


# ── Cambio de email (requiere JWT del estudiante) ──────────

@users_router.put("/me/email")
async def request_email_change(
    body: ChangeEmailSerializer,
    ctx: UserContext = Depends(get_current_user),
):
    try:
        await process.request_email_change_process(ctx.id, body.new_email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return {"message": "Te enviamos un link de confirmación al nuevo correo."}


@users_router.get("/confirm-email", status_code=status.HTTP_200_OK)
async def confirm_email(token: str = Query(...)):
    try:
        await process.confirm_email_change_process(token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Email actualizado correctamente."}