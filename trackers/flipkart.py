import logging
import requests
from typing import List
from bs4 import BeautifulSoup
from .base import BaseTracker, Job

logger = logging.getLogger(__name__)


class FlipkartTracker(BaseTracker):
    EIGHTFOLD_URL = "https://flipkart.eightfold.ai/api/apply/v2/jobs"
    GREENHOUSE_URL = "https://boards-api.greenhouse.io/v1/boards/flipkart/jobs?content=true"

    def __init__(self):
        super().__init__("Flipkart")

    def fetch_jobs(self) -> List[Job]:
        jobs: List[Job] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        # 1. Eightfold API
        try:
            params = {
                "domain": "flipkart.com",
                "start": 0,
                "num": 50,
                "sort_by": "relevance"
            }
            response = requests.get(self.EIGHTFOLD_URL, params=params, headers=headers, timeout=15)
            if response.status_code == 200:
                data = response.json()
                for pos in data.get("positions", []):
                    job_id = f"flipkart_ef_{pos.get('id')}"
                    title = pos.get("name", "").strip()
                    locations = pos.get("locations", [])
                    location = ", ".join(locations) if locations else "Bengaluru, India"
                    url = pos.get("canonicalPositionUrl") or f"https://flipkartcareers.com/#!/job-details/{pos.get('id')}"
                    desc = pos.get("job_description", "")
                    soup = BeautifulSoup(desc, "html.parser")
                    clean_desc = soup.get_text(separator=" ").strip()

                    jobs.append(Job(
                        id=job_id,
                        company=self.company_name,
                        title=title,
                        location=location,
                        url=url,
                        experience_text=clean_desc,
                        description=clean_desc,
                        posted_date=pos.get("posted_at")
                    ))
        except Exception as e:
            logger.warning(f"Eightfold API fetch failed for Flipkart: {e}")

        # 2. Greenhouse Fallback if Eightfold returns nothing
        if not jobs:
            try:
                response = requests.get(self.GREENHOUSE_URL, headers=headers, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("jobs", []):
                        job_id = f"flipkart_gh_{item.get('id')}"
                        title = item.get("title", "").strip()
                        loc_obj = item.get("location", {})
                        location = loc_obj.get("name", "Bengaluru, India") if isinstance(loc_obj, dict) else str(loc_obj)
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
                logger.warning(f"Greenhouse fallback fetch failed for Flipkart: {e}")

        logger.info(f"Fetched {len(jobs)} jobs from Flipkart.")
        return jobs
