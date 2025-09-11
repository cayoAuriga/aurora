# Email utilities (optional)
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import settings
from typing import List

def send_email(
    to_emails: List[str],
    subject: str,
    body: str,
    is_html: bool = False
) -> bool:
    """Send email using SMTP"""
    if not settings.SMTP_HOST:
        print("SMTP not configured, skipping email send")
        return False
    
    try:
        msg = MIMEMultipart()
        msg['From'] = settings.SMTP_USERNAME
        msg['To'] = ", ".join(to_emails)
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))
        
        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(settings.SMTP_USERNAME, to_emails, text)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def send_verification_email(email: str, verification_token: str) -> bool:
    """Send email verification"""
    subject = "Verify your email address"
    body = f"""
    Please click the following link to verify your email address:
    http://localhost:8000/verify?token={verification_token}
    """
    return send_email([email], subject, body)

def send_password_reset_email(email: str, reset_token: str) -> bool:
    """Send password reset email"""
    subject = "Reset your password"
    body = f"""
    Please click the following link to reset your password:
    http://localhost:8000/reset-password?token={reset_token}
    """
    return send_email([email], subject, body)