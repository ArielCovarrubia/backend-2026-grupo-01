import os
import smtplib
from email.message import EmailMessage


def send_password_reset_email(email: str, token: str) -> None:
    host = os.getenv("SMTP_HOST", "mailpit")
    port = int(os.getenv("SMTP_PORT", "1025"))
    sender = os.getenv("EMAIL_FROM", "no-reply@habitos.local")
    reset_url = os.getenv("PASSWORD_RESET_URL", "http://localhost:8000/reset-password")

    message = EmailMessage()
    message["From"] = sender
    message["To"] = email
    message["Subject"] = "Recuperación de contraseña"
    message.set_content(
        "Has solicitado restablecer tu contraseña.\n\n"
        f"{reset_url}?token={token}\n\n"
        "Si no solicitaste el cambio, ignora este correo."
    )

    with smtplib.SMTP(host, port, timeout=5) as smtp:
        smtp.send_message(message)
