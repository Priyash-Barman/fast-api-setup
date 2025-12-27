import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_ID, EMAIL_PASSWORD
from fast_app.utils.logger import logger



async def send_mail(receiver: str, subject: str, body: str, is_html: bool = False) -> bool:
    """Generic email sending function"""
    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        smtp_username = EMAIL_ID
        smtp_password = EMAIL_PASSWORD
        from_email = EMAIL_ID
        
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = receiver
        msg['Subject'] = subject

        if is_html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        logger.info(f"Email send successfully to {receiver}")
        return True
    except Exception as e:
        logger.error(f"Email sending failed to {receiver}: {e}")
        return False