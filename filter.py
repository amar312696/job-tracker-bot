import re
from typing import Tuple, Optional
from trackers.base import Job


class JobFilter:
    # Explicit positive keywords for backend / SDE 1 / SDE 2
    BACKEND_KEYWORDS = [
        r"\bbackend\b",
        r"\bback-end\b",
        r"\bback end\b",
        r"\bserver-side\b",
        r"\bapi\b",
        r"\bdistributed systems\b",
        r"\bjava\b",
        r"\bgolang\b",
        r"\bgo developer\b",
        r"\bpython developer\b",
        r"\bnode(?:\.js)?\b",
    ]

    SDE_LEVEL_KEYWORDS = [
        r"\bsde[-\s]?1\b",
        r"\bsde[-\s]?i\b",
        r"\bsde[-\s]?2\b",
        r"\bsde[-\s]?ii\b",
        r"\bsoftware development engineer[-\s]?(?:1|2|i|ii)?\b",
        r"\bsoftware engineer[-\s]?(?:1|2|i|ii)?\b",
        r"\bmts[-\s]?(?:1|2|i|ii)\b",
        r"\bassociate software engineer\b",
        r"\bmember technical staff[-\s]?(?:1|2|i|ii)?\b",
    ]

    # Explicit exclusions (roles not relevant to SDE-1 / SDE-2 Backend)
    EXCLUDE_KEYWORDS = [
        r"\bfrontend\b",
        r"\bfront-end\b",
        r"\bui\b",
        r"\bux\b",
        r"\bandroid\b",
        r"\bios\b",
        r"\bmobile engineer\b",
        r"\bdevops\b",
        r"\bsre\b",
        r"\bsite reliability\b",
        r"\bsdet\b",
        r"\bqa\b",
        r"\bquality assurance\b",
        r"\btest engineer\b",
        r"\bdata scientist\b",
        r"\bdata engineer\b",
        r"\bproduct manager\b",
        r"\bengineering manager\b",
        r"\bprincipal\b",
        r"\bstaff engineer\b",
        r"\bdirector\b",
        r"\barchitect\b",
        r"\bvp\b",
        r"\bintern\b",
        r"\binternship\b",
    ]

    @classmethod
    def matches_role(cls, title: str, description: str = "") -> bool:
        """Check whether the title and description match SDE-1, SDE-2, or Backend engineering."""
        title_lower = title.lower()
        desc_lower = description.lower()

        # Reject if clearly an excluded title (Frontend, iOS, QA, Staff, Principal, etc.)
        for pattern in cls.EXCLUDE_KEYWORDS:
            if re.search(pattern, title_lower):
                return False

        # If title specifically mentions SDE-1 / SDE-I / SDE-2 / SDE-II, accept!
        for pattern in cls.SDE_LEVEL_KEYWORDS:
            if re.search(pattern, title_lower):
                return True

        # If title mentions Backend
        for pattern in cls.BACKEND_KEYWORDS:
            if re.search(pattern, title_lower):
                return True

        # Generic "Software Engineer" / "Software Development Engineer" if description has backend keywords
        if "software engineer" in title_lower or "software development engineer" in title_lower or "developer" in title_lower:
            for pattern in cls.BACKEND_KEYWORDS:
                if re.search(pattern, desc_lower):
                    return True

        return False

    @classmethod
    def parse_experience(cls, text: str) -> Tuple[bool, Optional[str]]:
        """
        Parses required years of experience from text.
        Returns: (is_eligible_under_or_equal_5_yoe, extracted_experience_snippet)
        """
        if not text:
            return True, None

        text_lower = text.lower()

        # Look for explicit range: e.g. "2-4 years", "2 to 5 yrs", "3 - 5 yoe"
        range_match = re.search(
            r"([0-9]+)\s*(?:-|to)\s*([0-9]+)\s*(?:\+)?\s*(?:years?|yrs?|yoe)",
            text_lower
        )
        if range_match:
            min_y = int(range_match.group(1))
            max_y = int(range_match.group(2))
            snippet = f"{min_y}-{max_y} years"
            # Eligible if min experience is <= 5 years
            if min_y <= 5:
                return True, snippet
            else:
                return False, snippet

        # Look for single bound: e.g. "3+ years", "2 years", "at least 4 years"
        single_match = re.search(
            r"(?:at least|minimum of|min\.?)?\s*([0-9]+)\s*(?:\+)?\s*(?:years?|yrs?|yoe)",
            text_lower
        )
        if single_match:
            years = int(single_match.group(1))
            snippet = f"{years}+ years"
            if years <= 5:
                return True, snippet
            else:
                return False, snippet

        # Look for phrases like "fresher" or "entry level"
        if re.search(r"\b(?:fresher|entry level|0-1 years?|0-2 years?)\b", text_lower):
            return True, "0-2 years (Entry Level)"

        # No explicit YOE pattern found
        return True, None

    @classmethod
    def is_eligible(cls, job: Job) -> Tuple[bool, str]:
        """
        Evaluates a Job against role and experience constraints.
        Returns: (is_accepted, reason_or_experience_snippet)
        """
        if not cls.matches_role(job.title, job.description):
            return False, "Role does not match SDE-1 / SDE-2 Backend criteria"

        eligible_exp, exp_snippet = cls.parse_experience(job.experience_text or job.description)
        if not eligible_exp:
            return False, f"Requires >5 YOE ({exp_snippet})"

        # If title specifically indicates SDE-1 or SDE-2, tag it
        title_lower = job.title.lower()
        if re.search(r"\bsde[-\s]?(?:1|i)\b|\bsoftware engineer[-\s]?(?:1|i)\b", title_lower):
            level = "SDE-1 (0-3 YOE)"
        elif re.search(r"\bsde[-\s]?(?:2|ii)\b|\bsoftware engineer[-\s]?(?:2|ii)\b", title_lower):
            level = "SDE-2 (2-5 YOE)"
        else:
            level = "Backend / SDE (≤ 5 YOE)"

        final_exp = exp_snippet or level
        return True, final_exp
