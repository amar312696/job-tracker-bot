import logging
import re
import urllib.parse
import requests
from typing import List
from bs4 import BeautifulSoup
from .base import BaseTracker, Job

logger = logging.getLogger(__name__)


class LinkedInTracker(BaseTracker):
    """
    Scrapes LinkedIn Jobs public guest search API (no login or API key required).
    Captures jobs posted directly on LinkedIn by recruiters for our target companies,
    sorted by most recent (sortBy=DD).
    """
    SEARCH_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

    TARGET_COMPANIES = [
        "Amazon",
        "Flipkart",
        "Swiggy",
        "Razorpay",
        "Myntra",
        "Smallcase"
    ]

    def __init__(self):
        super().__init__("LinkedIn")

    def fetch_jobs(self) -> List[Job]:
        jobs: List[Job] = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }

        for company in self.TARGET_COMPANIES:
            query = f"{company} Software Engineer Backend"
            params = {
                "keywords": query,
                "location": "India",
                "sortBy": "DD",  # Date posted: most recent first
                "start": 0
            }

            try:
                response = requests.get(self.SEARCH_URL, params=params, headers=headers, timeout=15)
                if response.status_code != 200:
                    logger.warning(f"LinkedIn search for {company} returned status {response.status_code}")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")
                job_cards = soup.find_all("li")

                for card in job_cards:
                    title_elem = card.find("h3", class_=re.compile(r"base-search-card__title|job-card-list__title"))
                    company_elem = card.find("h4", class_=re.compile(r"base-search-card__subtitle"))
                    location_elem = card.find("span", class_=re.compile(r"job-search-card__location"))
                    link_elem = card.find("a", class_=re.compile(r"base-card__full-link|job-card-list__title"))
                    date_elem = card.find("time")

                    if not title_elem or not link_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    company_found = company_elem.get_text(strip=True) if company_elem else company
                    location = location_elem.get_text(strip=True) if location_elem else "India"
                    raw_url = link_elem.get("href", "")
                    
                    # Clean tracking parameters from URL
                    clean_url = raw_url.split("?")[0] if raw_url else ""

                    # Verify that the posting actually belongs to the target company
                    if company.lower() not in company_found.lower():
                        continue

                    # Extract LinkedIn Job ID
                    job_id_match = re.search(r"view/([0-9]+)", clean_url) or re.search(r"jobPosting:([0-9]+)", str(card))
                    if job_id_match:
                        job_id = f"linkedin_{job_id_match.group(1)}"
                    else:
                        job_id = f"linkedin_{urllib.parse.quote(clean_url[-30:])}"

                    posted_date = date_elem.get("datetime") if date_elem else None

                    jobs.append(Job(
                        id=job_id,
                        company=company,
                        title=title,
                        location=location,
                        url=clean_url,
                        experience_text=title,
                        description=f"{title} at {company_found} in {location}",
                        posted_date=posted_date,
                        extra={"source": "LinkedIn"}
                    ))
                logger.info(f"Fetched LinkedIn jobs for {company}: found {len(jobs)} total so far.")
            except Exception as e:
                logger.error(f"Error scraping LinkedIn for {company}: {e}")

        return jobs
