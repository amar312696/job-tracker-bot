# 🚀 Real-Time Job Alert Bot (SDE-1 / SDE-2 Backend ≤ 5 YOE)

An automated, 100% free notification system that scans both **Official Career Portals** and **External Job Boards (LinkedIn Jobs, Instahyre)** for **Myntra, Swiggy, Razorpay, Amazon, Flipkart, and Smallcase**, filters for **SDE-1, SDE-2, and Backend roles (≤ 5 years of experience)**, and immediately sends instant push notifications to your phone via **Telegram**.

Runs **24/7 on GitHub Actions** without keeping your laptop open or paying for servers.

---

## 📌 Features & Coverage

- **Target Companies**: Myntra, Swiggy, Razorpay, Amazon, Flipkart, Smallcase.
- **Data Sources**:
  1. **Direct ATS & Career Portals**: Greenhouse, Lever, Eightfold, Amazon.jobs (first place jobs get published before syndication).
  2. **External Job Boards**:
     - **LinkedIn Jobs**: Public guest search API sorted by newest (`sortBy=DD`) for direct recruiter posts.
     - **Instahyre**: Fast-track tech hiring portal heavily used by Swiggy, Razorpay, Smallcase, Flipkart, Myntra.
- **Role Filtering**: SDE-1, SDE-2, Backend Engineers, Software Development Engineers.
- **Experience Filter**: Identifies postings requiring $\le 5$ years of experience (0–2 yrs, 2–4 yrs, 3–5 yrs, etc.) and ignores senior/lead roles.
- **De-duplication**: Tracks `seen_jobs.json` so you never get notified for the same job twice.
- **Zero Cost**: 100% free using GitHub Actions + Telegram Bot API.

---

## ⚡ 1. Set Up Your Free Telegram Bot (Takes 2 Minutes)

1. **Create the Bot**:
   - Open Telegram and search for `@BotFather`.
   - Send `/newbot` and follow the prompts to choose a name and username (e.g. `my_job_tracker_bot`).
   - Copy the **HTTP API Token** (e.g., `7123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`).

2. **Get Your Telegram Chat ID**:
   - In Telegram, search for `@userinfobot` and click **Start**.
   - It will reply with your `Id` (e.g. `123456789`). Copy this number.
   - Also, open your newly created bot in Telegram and click **Start** (or send `/start`) so the bot has permission to message you.

---

## 💻 2. Local Testing (Optional)

1. Create a `.env` file in the root directory:
   ```bash
   cp .env.example .env
   ```
2. Put your token and chat ID in `.env`:
   ```env
   TELEGRAM_BOT_TOKEN=your_token_from_botfather
   TELEGRAM_CHAT_ID=your_chat_id_from_userinfobot
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Test connectivity with Telegram:
   ```bash
   python3 main.py --test
   ```
5. Run a dry run to see matching jobs right now:
   ```bash
   python3 main.py --dry-run
   ```

---

## ☁️ 3. Deploy 24/7 on GitHub Actions (Runs Forever for Free)

1. **Push this code to a GitHub repository** (can be Private or Public):
   ```bash
   git init
   git add .
   git commit -m "feat: initial job alert system"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo-name>.git
   git push -u origin main
   ```

2. **Add Secrets to GitHub**:
   - On GitHub, go to your repository: **Settings** ➔ **Secrets and variables** ➔ **Actions**.
   - Click **New repository secret** and add:
     - `TELEGRAM_BOT_TOKEN`: Your bot token from `@BotFather`.
     - `TELEGRAM_CHAT_ID`: Your chat ID from `@userinfobot`.

3. **Enable GitHub Actions Permissions**:
   - Go to **Settings** ➔ **Actions** ➔ **General**.
   - Under **Workflow permissions**, select **Read and write permissions** (this allows the bot to commit `seen_jobs.json` after finding new jobs).
   - Click **Save**.

4. **Done!**
   - The workflow (`.github/workflows/track_jobs.yml`) will automatically run every **20 minutes**.
   - You can also manually trigger a run anytime under the **Actions** tab by selecting **Job Alert Tracker** ➔ **Run workflow**.

---

## 📁 Project Architecture

```
.
├── .github/
│   └── workflows/
│       └── track_jobs.yml     # 24/7 cloud cron scheduler
├── trackers/
│   ├── base.py               # Abstract Base Tracker & Job model
│   ├── amazon.py             # Amazon.jobs scraper
│   ├── smallcase.py          # Smallcase (Lever API) scraper
│   ├── razorpay.py           # Razorpay (Greenhouse/Lever) scraper
│   ├── swiggy.py             # Swiggy scraper
│   ├── flipkart.py           # Flipkart (Eightfold/Greenhouse) scraper
│   ├── myntra.py             # Myntra (Eightfold/Greenhouse) scraper
│   ├── linkedin.py           # LinkedIn Jobs guest search scraper
│   ├── instahyre.py          # Instahyre tech jobs scraper
│   └── __init__.py
├── filter.py                 # Filters SDE-1, SDE-2, Backend & <= 5 YOE
├── notifier.py               # Telegram bot alert dispatcher (with source tags)
├── database.py               # Stores seen jobs to prevent duplicates
├── main.py                   # Main orchestrator
├── seen_jobs.json            # State file
└── requirements.txt
```
