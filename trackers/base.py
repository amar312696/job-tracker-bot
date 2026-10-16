from dataclasses import dataclass, field
from typing import Optional, List
from abc import ABC, abstractmethod


@dataclass
class Job:
    id: str
    company: str
    title: str
    location: str
    url: str
    experience_text: Optional[str] = None
    description: str = ""
    posted_date: Optional[str] = None
    extra: dict = field(default_factory=dict)


class BaseTracker(ABC):
    def __init__(self, company_name: str):
        self.company_name = company_name

    @abstractmethod
    def fetch_jobs(self) -> List[Job]:
        """Fetch all relevant open job postings for this company."""
        pass
