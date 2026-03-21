"""
Envío de emails transaccionales via Gmail + App Password.
Usa aiosmtplib para no bloquear el event loop de FastAPI.
"""
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from app.core.constants import (
    FRONTEND_URL, 
    GMAIL_APP_PASSWORD, 
    GMAIL_USER
)


def _build_message(to: str, subject: str, html: str) -> MIMEMultipart:
    msg = MIMEMultipart("alternative")
    msg["From"] = f"FANAMA Playground <{GMAIL_USER}>"
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))
    return msg


async def _send(to: str, subject: str, html: str) -> None:
    if not GMAIL_USER or not GMAIL_APP_PASSWORD:
        # En dev sin credenciales, solo logueamos
        print(f"[EMAIL MOCK] To={to} | Subject={subject}")
        return
    msg = _build_message(to, subject, html)
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        username=GMAIL_USER,
        password=GMAIL_APP_PASSWORD,
        start_tls=True,
    )


async def send_password_reset_email(to: str, token: str) -> None:
    link = f"{FRONTEND_URL}/reset-password?token={token}"
    html = f"""
    <div style="font-family:monospace;background:#1e1e2e;color:#cdd6f4;padding:2rem;border-radius:12px;max-width:500px">
      <h2 style="color:#cba6f7;margin-bottom:1rem">Recuperación de contraseña</h2>
      <p>Recibiste este email porque solicitaste restablecer tu contraseña en FANAMA Playground.</p>
      <p style="margin:1.5rem 0">
        <a href="{link}"
           style="background:#cba6f7;color:#1e1e2e;padding:0.6rem 1.2rem;border-radius:7px;text-decoration:none;font-weight:700">
          Restablecer contraseña
        </a>
      </p>
      <p style="color:#6c7086;font-size:0.85rem">
        El link expira en <strong>15 minutos</strong>.<br>
        Si no solicitaste esto, ignorá este mensaje.
      </p>
    </div>
    """
    await _send(to, "Recuperación de contraseña — FANAMA Playground", html)


async def send_email_change_confirmation(new_email: str, token: str) -> None:
    link = f"{FRONTEND_URL}/confirm-email?token={token}"
    html = f"""
    <div style="font-family:monospace;background:#1e1e2e;color:#cdd6f4;padding:2rem;border-radius:12px;max-width:500px">
      <h2 style="color:#cba6f7;margin-bottom:1rem">Confirmá tu nuevo correo</h2>
      <p>Alguien solicitó cambiar el correo de su cuenta en FANAMA Playground a esta dirección.</p>
      <p style="margin:1.5rem 0">
        <a href="{link}"
           style="background:#cba6f7;color:#1e1e2e;padding:0.6rem 1.2rem;border-radius:7px;text-decoration:none;font-weight:700">
          Confirmar nuevo email
        </a>
      </p>
      <p style="color:#6c7086;font-size:0.85rem">
        El link expira en <strong>30 minutos</strong>.<br>
        Si no solicitaste esto, ignorá este mensaje — tu email actual no cambiará.
      </p>
    </div>
    """
    await _send(new_email, "Confirmá tu nuevo correo — FANAMA Playground", html)


async def send_email_change_admin_notification(old_email: str, new_email: str) -> None:
    html = f"""
    <div style="font-family:monospace;background:#1e1e2e;color:#cdd6f4;padding:2rem;border-radius:12px;max-width:500px">
      <h2 style="color:#cba6f7;margin-bottom:1rem">Tu correo fue actualizado</h2>
      <p>Un administrador actualizó el correo de tu cuenta en FANAMA Playground.</p>
      <ul style="color:#a6adc8;margin:1rem 0">
        <li>Email anterior: <strong>{old_email}</strong></li>
        <li>Email nuevo: <strong>{new_email}</strong></li>
      </ul>
      <p style="color:#6c7086;font-size:0.85rem">
        Si esto fue un error, contactá a tu docente.
      </p>
    </div>
    """
    await _send(old_email, "Tu correo fue actualizado — FANAMA Playground", html)