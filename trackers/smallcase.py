import logging
import requests
from typing import List
from bs4 import BeautifulSoup
from .base import BaseTracker, Job

logger = logging.getLogger(__name__)


class SmallcaseTracker(BaseTracker):
    LEVER_URL = "https://api.lever.co/v0/postings/smallcase?mode=json"

    def __init__(self):
        super().__init__("Smallcase")

    def fetch_jobs(self) -> List[Job]:
        jobs: List[Job] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        try:
            response = requests.get(self.LEVER_URL, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data:
                job_id = f"smallcase_{item.get('id')}"
                title = item.get("text", "").strip()
                categories = item.get("categories", {})
                location = categories.get("location", "Bangalore / Remote")
                url = item.get("hostedUrl", "")
                
                # Parse description and requirements
                desc_html = item.get("description", "")
                lists_content = []
                for lst in item.get("lists", []):
                    lists_content.append(f"{lst.get('text', '')}: {lst.get('content', '')}")
                
                combined_desc = f"{desc_html} " + " ".join(lists_content)
                soup = BeautifulSoup(combined_desc, "html.parser")
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
            logger.info(f"Fetched {len(jobs)} jobs from Smallcase.")
        except Exception as e:
            logger.error(f"Error fetching jobs from Smallcase: {e}")

        return jobs
