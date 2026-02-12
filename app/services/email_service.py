from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from app.config import settings


conf = ConnectionConfig(
    MAIL_USERNAME=settings.smtp_user,
    MAIL_PASSWORD=settings.smtp_password,
    MAIL_FROM=settings.smtp_user,
    MAIL_PORT=settings.smtp_port,
    MAIL_SERVER=settings.smtp_host,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False
)


async def send_email(to_email: str, subject: str, message: str) -> bool:
    if not settings.smtp_user or not settings.smtp_password:
        print("SMTP credentials not configured, skipping email send")
        return False

    try:
        message_schema = MessageSchema(
            subject=subject,
            recipients=[to_email],
            body=message,
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message_schema)

        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False


async def send_otp_email(to_email: str, otp: str) -> bool:
    subject = "Verify Your Email - Traffic Accident Analyser"
    message = f"""
    <h2>Welcome to Traffic Accident Analyser!</h2>
    <p>Your One-Time Password (OTP) for email verification is:</p>
    <h1 style="color: #007bff; font-size: 32px; letter-spacing: 5px;">{otp}</h1>
    <p>This OTP will expire in 10 minutes.</p>
    <p>If you didn't request this, please ignore this email.</p>
    <br>
    <p>Best regards,<br>Traffic Accident Analyser Team</p>
    """
    return await send_email(to_email, subject, message)


async def send_alert_email(to_email: str, subject: str, message: str) -> bool:
    return await send_email(to_email, subject, message)


async def send_high_risk_alert(user_email: str, risk_level: str, location: dict) -> bool:
    subject = f"High Risk Alert - {risk_level.upper()}"
    message = f"""
    <h2>Traffic Safety Alert</h2>
    <p>A <strong>{risk_level.upper()}</strong> risk has been detected at:</p>
    <ul>
        <li>Latitude: {location.get('latitude')}</li>
        <li>Longitude: {location.get('longitude')}</li>
    </ul>
    <p>Please exercise caution when traveling in this area.</p>
    """
    return await send_alert_email(user_email, subject, message)
