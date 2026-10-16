import logging
import re
import requests
from typing import List
from bs4 import BeautifulSoup
from .base import BaseTracker, Job

logger = logging.getLogger(__name__)


class InstahyreTracker(BaseTracker):
    """
    Scrapes Instahyre public job directory for top Indian tech companies:
    Swiggy, Razorpay, Flipkart, Myntra, Smallcase.
    """
    COMPANY_SLUGS = {
        "Swiggy": "swiggy",
        "Razorpay": "razorpay",
        "Flipkart": "flipkart",
        "Myntra": "myntra",
        "Smallcase": "smallcase",
    }

    def __init__(self):
        super().__init__("Instahyre")

    def fetch_jobs(self) -> List[Job]:
        jobs: List[Job] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }

        for company_name, slug in self.COMPANY_SLUGS.items():
            url = f"https://www.instahyre.com/jobs-at-{slug}/"
            try:
                resp = requests.get(url, headers=headers, timeout=15)
                if resp.status_code != 200:
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")
                # Look for job cards
                job_rows = soup.find_all("div", class_=re.compile(r"employer-job-row|job-card"))
                for row in job_rows:
                    title_elem = row.find(re.compile(r"h2|h3|a"), class_=re.compile(r"job-title|position-title"))
                    if not title_elem:
                        link_cand = row.find("a", href=re.compile(r"/job-\d+"))
                        if link_cand:
                            title_elem = link_cand

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    link = title_elem.get("href") or (row.find("a", href=True) or {}).get("href", "")
                    if link and link.startswith("/"):
                        link = f"https://www.instahyre.com{link}"

                    loc_elem = row.find(class_=re.compile(r"job-locations|location"))
                    location = loc_elem.get_text(strip=True) if loc_elem else "India"

                    exp_elem = row.find(class_=re.compile(r"experience"))
                    exp_text = exp_elem.get_text(strip=True) if exp_elem else ""

                    job_id_match = re.search(r"job-(\d+)", link)
                    job_id = f"instahyre_{job_id_match.group(1)}" if job_id_match else f"instahyre_{slug}_{len(jobs)}"

                    jobs.append(Job(
                        id=job_id,
                        company=company_name,
                        title=title,
                        location=location,
                        url=link,
                        experience_text=exp_text,
                        description=f"{title} at {company_name} - {exp_text}",
                        extra={"source": "Instahyre"}
                    ))
            except Exception as e:
                logger.debug(f"Instahyre check for {company_name} error: {e}")

        logger.info(f"Fetched {len(jobs)} jobs from Instahyre.")
        return jobs
