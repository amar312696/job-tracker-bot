import html
import logging
import time
import requests
from typing import Optional
from trackers.base import Job

logger = logging.getLogger(__name__)


class TelegramNotifier:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage" if self.bot_token else None

    def send_job_alert(self, job: Job, experience_info: str) -> bool:
        """Sends a formatted job notification to Telegram."""
        safe_title = html.escape(job.title)
        safe_company = html.escape(job.company)
        safe_location = html.escape(job.location or "India")
        safe_exp = html.escape(experience_info or "≤ 5 years")
        source = job.extra.get("source", "Official Careers Portal")
        safe_source = html.escape(source)
        safe_url = job.url

        message_html = (
            f"🚨 <b>New Job Alert!</b>\n\n"
            f"🏢 <b>Company:</b> {safe_company}\n"
            f"💼 <b>Role:</b> {safe_title}\n"
            f"📍 <b>Location:</b> {safe_location}\n"
            f"⏳ <b>Experience:</b> {safe_exp}\n"
            f"🌐 <b>Source:</b> {safe_source}\n"
            f"🔗 <a href=\"{safe_url}\"><b>View &amp; Apply Now ➔</b></a>"
        )

        if not self.bot_token or not self.chat_id:
            logger.info(f"[Dry Run / Token Missing] Would notify:\n{job.company} | {job.title} | {job.url} ({safe_source})")
            return True

        payload = {
            "chat_id": self.chat_id,
            "text": message_html,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }

        try:
            resp = requests.post(self.api_url, json=payload, timeout=10)
            if resp.status_code == 200:
                logger.info(f"Successfully notified Telegram for {job.company} - {job.title} ({safe_source})")
                time.sleep(0.5)
                return True
            else:
                logger.error(f"Telegram API error {resp.status_code}: {resp.text}")
                return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False

    def send_test_message(self) -> bool:
        """Sends a verification ping to confirm bot configuration."""
        if not self.bot_token or not self.chat_id:
            logger.warning("Telegram Bot Token or Chat ID is not configured.")
            return False

        payload = {
            "chat_id": self.chat_id,
            "text": (
                "🤖 <b>Job Alert Bot Connected!</b>\n\n"
                "Your job notification system is now active.\n\n"
                "🎯 <b>Tracking:</b> Amazon, Flipkart, Swiggy, Razorpay, Myntra, Smallcase\n"
                "🌐 <b>Sources:</b> Career Portals + LinkedIn Jobs + Instahyre\n"
                "💼 <b>Roles:</b> SDE-1, SDE-2, Backend (≤ 5 YOE)\n\n"
                "You will receive instant alerts the moment new jobs appear!"
            ),
            "parse_mode": "HTML"
        }
        try:
            resp = requests.post(self.api_url, json=payload, timeout=10)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Failed to send test message: {e}")
            return False
