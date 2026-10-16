from .amazon import AmazonTracker
from .smallcase import SmallcaseTracker
from .razorpay import RazorpayTracker
from .swiggy import SwiggyTracker
from .flipkart import FlipkartTracker
from .myntra import MyntraTracker
from .linkedin import LinkedInTracker
from .instahyre import InstahyreTracker

ALL_TRACKERS = [
    # Primary ATS / Career Portals (Instant origin of posts)
    AmazonTracker,
    SmallcaseTracker,
    RazorpayTracker,
    SwiggyTracker,
    FlipkartTracker,
    MyntraTracker,
    
    # External Job Boards & Aggregators (Where recruiters cross-post)
    LinkedInTracker,
    InstahyreTracker,
]

__all__ = [
    "AmazonTracker",
    "SmallcaseTracker",
    "RazorpayTracker",
    "SwiggyTracker",
    "FlipkartTracker",
    "MyntraTracker",
    "LinkedInTracker",
    "InstahyreTracker",
    "ALL_TRACKERS",
]
