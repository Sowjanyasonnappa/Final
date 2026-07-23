from fastapi_mail import FastMail
from fastapi_mail import MessageSchema
from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="your_email@gmail.com",
    MAIL_PASSWORD="your_app_password",
    MAIL_FROM="your_email@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
)


async def send_email(
    email: str,
    subject: str,
    body: str,
):

    message = MessageSchema(
        subject=subject,
        recipients=[email],
        body=body,
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(message)