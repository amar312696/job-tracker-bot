import logging
import requests
from typing import List
from bs4 import BeautifulSoup
from .base import BaseTracker, Job

logger = logging.getLogger(__name__)


class RazorpayTracker(BaseTracker):
    GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/razorpay/jobs?content=true"
    LEVER_URL = "https://api.lever.co/v0/postings/razorpay?mode=json"

    def __init__(self):
        super().__init__("Razorpay")

    def fetch_jobs(self) -> List[Job]:
        jobs: List[Job] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        # 1. Try Greenhouse API
        try:
            response = requests.get(self.GREENHOUSE_URL, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for item in data.get("jobs", []):
                    job_id = f"razorpay_gh_{item.get('id')}"
                    title = item.get("title", "").strip()
                    loc_obj = item.get("location", {})
                    location = loc_obj.get("name", "Bangalore, India") if isinstance(loc_obj, dict) else str(loc_obj)
                    url = item.get("absolute_url", "")
                    content_html = item.get("content", "")
                    soup = BeautifulSoup(content_html, "html.parser")
                    clean_content = soup.get_text(separator=" ").strip()

                    jobs.append(Job(
                        id=job_id,
                        company=self.company_name,
                        title=title,
                        location=location,
                        url=url,
                        experience_text=clean_content,
                        description=clean_content,
                        posted_date=item.get("updated_at")
                    ))
        except Exception as e:
            logger.warning(f"Greenhouse fetch failed for Razorpay: {e}")

        # 2. Try Lever API if Greenhouse returned empty or as supplement
        if not jobs:
            try:
                response = requests.get(self.LEVER_URL, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for item in data:
                        job_id = f"razorpay_lever_{item.get('id')}"
                        title = item.get("text", "").strip()
                        categories = item.get("categories", {})
                        location = categories.get("location", "Bangalore, India")
                        url = item.get("hostedUrl", "")
                        
                        desc_html = item.get("description", "")
                        soup = BeautifulSoup(desc_html, "html.parser")
                        clean_desc = soup.get_text(separator=" ").strip()

                        jobs.append(Job(
                            id=job_id,
                            company=self.company_name,
                            title=title,
                            location=location,
                            url=url,
                            experience_text=clean_desc,
                            description=clean_desc,
                            posted_date=str(item.get("createdAt", ""))
                        ))
            except Exception as e:
                logger.warning(f"Lever fetch failed for Razorpay: {e}")

        logger.info(f"Fetched {len(jobs)} jobs from Razorpay.")
        return jobs
