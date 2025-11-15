import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
import logging

logger = logging.getLogger(__name__)


async def send_magic_link_email(email: str, token: str):
    """Send magic link email to user"""
    
    # Create magic link URL
    magic_link = f"http://localhost:3000/auth/verify?token={token}"
    
    # В режиме разработки просто выводим ссылку в лог
    if settings.DEBUG:
        logger.info("=" * 80)
        logger.info("🔑 MAGIC LINK FOR DEVELOPMENT")
        logger.info(f"📧 Email: {email}")
        logger.info(f"🔗 Link: {magic_link}")
        logger.info(f"🎫 Token: {token}")
        logger.info("=" * 80)
        print("\n" + "=" * 80)
        print("🔑 MAGIC LINK (Copy this link to browser)")
        print(f"📧 Email: {email}")
        print(f"🔗 Link: {magic_link}")
        print("=" * 80 + "\n")
        return  # Не отправляем email в dev режиме
    
    # Create message
    message = MIMEMultipart("alternative")
    message["Subject"] = "Your Alfa Copilot Magic Link"
    message["From"] = settings.SMTP_FROM
    message["To"] = email
    
    # Create HTML body
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #0f0f10; color: #ffffff; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #1a1b1e; border-radius: 20px; padding: 40px;">
          <h1 style="color: #ef3124;">Welcome to Alfa Copilot!</h1>
          <p>Click the button below to sign in to your account:</p>
          <a href="{magic_link}" 
             style="display: inline-block; background-color: #ef3124; color: white; padding: 12px 24px; 
                    text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold;">
            Sign In
          </a>
          <p style="color: #a3a3a3; font-size: 14px;">
            This link will expire in 15 minutes. If you didn't request this email, you can safely ignore it.
          </p>
          <p style="color: #a3a3a3; font-size: 14px;">
            Or copy and paste this link into your browser:<br>
            <code style="background-color: #2a2b30; padding: 4px 8px; border-radius: 4px;">{magic_link}</code>
          </p>
        </div>
      </body>
    </html>
    """
    
    part = MIMEText(html, "html")
    message.attach(part)
    
    # Send email
    try:
        await aiosmtplib.send(
            message,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USER,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info(f"✅ Magic link email sent successfully to {email}")
    except aiosmtplib.SMTPAuthenticationError as e:
        logger.error(f"❌ SMTP Authentication failed. Check SMTP_USER and SMTP_PASSWORD in .env file.")
        logger.error(f"For Gmail: Make sure you're using App Password (not regular password)")
        logger.error(f"Create one here: https://myaccount.google.com/apppasswords")
        raise
    except aiosmtplib.SMTPConnectError as e:
        logger.error(f"❌ Cannot connect to SMTP server. Check SMTP_HOST and SMTP_PORT in .env file.")
        logger.error(f"Current: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
        raise
    except Exception as e:
        logger.error(f"❌ Failed to send magic link email to {email}: {str(e)}")
        logger.error(f"SMTP Config: {settings.SMTP_HOST}:{settings.SMTP_PORT} (user: {settings.SMTP_USER})")
        raise
