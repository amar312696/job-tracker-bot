import logging
import requests
from typing import List
from .base import BaseTracker, Job

logger = logging.getLogger(__name__)


class AmazonTracker(BaseTracker):
    SEARCH_URL = "https://www.amazon.jobs/en/search.json"

    def __init__(self):
        super().__init__("Amazon")

    def fetch_jobs(self) -> List[Job]:
        jobs: List[Job] = []
        params = {
            "category[]": "software-development",
            "country": "IND",
            "result_limit": 100,
            "sort": "recent"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json"
        }

        try:
            response = requests.get(self.SEARCH_URL, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()

            for item in data.get("jobs", []):
                job_id = f"amazon_{item.get('id_icims') or item.get('id')}"
                title = item.get("title", "").strip()
                location = item.get("normalized_location") or item.get("location", "India")
                job_path = item.get("job_path", "")
                url = f"https://www.amazon.jobs{job_path}" if job_path else "https://www.amazon.jobs"
                
                # Basic qualifications often detail required years of experience
                basic_qual = item.get("basic_qualifications", "")
                desc = item.get("description", "")
                full_desc = f"{basic_qual}\n{desc}"
                posted_date = item.get("posted_date")

                jobs.append(Job(
                    id=job_id,
                    company=self.company_name,
                    title=title,
                    location=location,
                    url=url,
                    experience_text=basic_qual,
                    description=full_desc,
                    posted_date=posted_date
                ))
            logger.info(f"Fetched {len(jobs)} jobs from Amazon.")
        except Exception as e:
            logger.error(f"Error fetching jobs from Amazon: {e}")

        return jobs
