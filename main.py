import argparse
import logging
import os
import sys
from dotenv import load_dotenv

from trackers import ALL_TRACKERS
from filter import JobFilter
from database import JobDatabase
from notifier import TelegramNotifier

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("JobAlertRunner")


def run(init_mode: bool = False, dry_run: bool = False, test_mode: bool = False):
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    notifier = TelegramNotifier(bot_token=bot_token, chat_id=chat_id)

    if test_mode:
        logger.info("Sending test notification to Telegram...")
        success = notifier.send_test_message()
        if success:
            logger.info("Test message sent successfully!")
        else:
            logger.error("Failed to send test message. Please verify your TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.")
        return

    db = JobDatabase("seen_jobs.json")
    total_found = 0
    total_matched = 0
    total_new = 0

    logger.info("Starting scan across target companies: Amazon, Smallcase, Razorpay, Swiggy, Flipkart, Myntra...")

    for tracker_cls in ALL_TRACKERS:
        tracker = tracker_cls()
        logger.info(f"--- Scanning {tracker.company_name} ---")
        try:
            jobs = tracker.fetch_jobs()
            total_found += len(jobs)

            for job in jobs:
                # 1. Filter: Check role and experience constraints (SDE-1/2, Backend, <= 5 YOE)
                is_eligible, exp_info = JobFilter.is_eligible(job)
                if not is_eligible:
                    continue

                total_matched += 1

                # 2. Check if already seen
                if db.is_seen(job.id):
                    continue

                total_new += 1
                logger.info(f"[NEW MATCH] {job.company} | {job.title} | {exp_info} | {job.url}")

                if init_mode:
                    # On initialization, seed the database without notifying
                    db.mark_seen(job.id)
                elif dry_run:
                    logger.info(f"[DRY RUN] Would notify for {job.id}")
                else:
                    sent = notifier.send_job_alert(job, exp_info)
                    if sent or not bot_token:
                        db.mark_seen(job.id)

        except Exception as e:
            logger.error(f"Unexpected error in {tracker.company_name} tracker: {e}")

    if not dry_run and not test_mode:
        db.save()

    logger.info("================ Summary ================")
    logger.info(f"Total jobs scraped: {total_found}")
    logger.info(f"Eligible SDE-1/2 / Backend jobs (<= 5 YOE): {total_matched}")
    logger.info(f"New alerts processed: {total_new}")
    logger.info("=========================================")


def main():
    parser = argparse.ArgumentParser(description="Real-Time Job Notification System")
    parser.add_argument("--test", action="store_true", help="Send a test notification to Telegram")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and filter jobs without notifying or updating seen_jobs.json")
    parser.add_argument("--init", action="store_true", help="Mark all existing jobs as seen without sending notifications (first-time setup)")
    args = parser.parse_args()

    run(init_mode=args.init, dry_run=args.dry_run, test_mode=args.test)


if __name__ == "__main__":
    main()
