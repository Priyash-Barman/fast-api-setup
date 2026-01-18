import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional, Dict

from config import EMAIL_ID, EMAIL_PASSWORD
from fast_app.utils.logger import logger
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[3]  
# adjust parents[n] based on file depth

TEMPLATE_DIR = (
    BASE_DIR
    / "fast-app"
    / "fast_app"
    / "modules"
    / "common"
    / "templates"
    / "emails"
)

async def send_mail(
    receiver: str,
    subject: str,
    body: Optional[str] = None,
    *,
    is_html: bool = False,
    template_name: Optional[str] = None,
    context: Optional[Dict[str, str]] = None,
) -> bool:
    """
    Generic email sending function.

    - body: plain text or raw HTML
    - template_name: html file name (e.g. reset_password.html)
    - context: variables for template replacement
    """

    try:
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ID
        msg["To"] = receiver
        msg["Subject"] = subject

        # Load template if provided
        if template_name:
            template_path = TEMPLATE_DIR / template_name

            if not template_path.exists():
                raise FileNotFoundError(f"Email template not found: {template_path}")

            html_content = template_path.read_text(encoding="utf-8")

            # Replace template variables
            if context:
                for key, value in context.items():
                    html_content = html_content.replace(f"{{{{{key}}}}}", value)

            msg.attach(MIMEText(html_content, "html"))

        else:
            msg.attach(MIMEText(body or "", "html" if is_html else "plain"))

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(EMAIL_ID, EMAIL_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent successfully to {receiver}")
        return True

    except Exception as e:
        logger.error(f"Email sending failed to {receiver}: {e}")
        return False
