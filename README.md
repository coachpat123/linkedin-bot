# 🤖 LinkedIn Easy Apply Bot

Automatically applies to LinkedIn Easy Apply jobs from any search URL.

- **AI cover letters & tailored resumes** — powered by Ollama (free, runs locally, no API key)
- **Saves all docs** — every cover letter and resume stored in a local folder
- **Skips non-Easy-Apply** jobs automatically
- **Log in once** — saves your session so it runs hands-free after that

**Optional:** [Vibecraft](https://github.com/coachpat123/vibecraft) integration — watch the bot work in a live 3D visualization

---

## System Requirements

Before starting, make sure your machine can handle this:

| Requirement | Minimum |
|-------------|---------|
| RAM | **8 GB** (Ollama needs this — the AI won't load with less) |
| Disk space | **5 GB free** (Ollama ~2 GB + Chromium ~400 MB + model ~2 GB) |
| Internet | Required for LinkedIn and for the initial Ollama model download |
| OS | macOS 11+, Windows 10+, or Ubuntu 20.04+ |

---

## ✅ Setup Checklist

Work through these steps in order. Each one has a checkbox — check them off as you go.

---

### Step 1 — Open a Terminal

You'll type commands into a terminal throughout this setup.

- **Mac:** Press `Cmd + Space`, type `Terminal`, press Enter
- **Windows:** Press `Win + X`, click **Windows PowerShell** (or **Terminal** on Windows 11)
- **Linux:** Press `Ctrl + Alt + T`

Leave it open — you'll use it in every step below.

---

### Step 2 — Install Python

- [ ] Go to [python.org/downloads](https://www.python.org/downloads/) and download Python **3.10 or newer**
- [ ] Run the installer
  - **Windows:** Check **"Add Python to PATH"** at the bottom of the first screen — this is critical
  - **Mac/Linux:** Default options are fine
- [ ] **Close and reopen your terminal** (required on Windows for PATH to take effect)
- [ ] Verify it worked:
  ```bash
  python3 --version
  ```
  - **Windows**, if that doesn't work, try: `python --version`
  - You should see `Python 3.10.x` or higher

---

### Step 3 — Download This Bot

**Option A — Git (recommended):**
```bash
git clone https://github.com/coachpat123/linkedin-bot.git
cd linkedin-bot
```

**Option B — Download ZIP:**
- Click the green **Code** button at the top of this page → **Download ZIP**
- Unzip it, then in your terminal navigate into the folder:
  ```bash
  # Mac/Linux:
  cd ~/Downloads/linkedin-bot-main

  # Windows PowerShell:
  cd $HOME\Downloads\linkedin-bot-main
  ```

---

### Step 4 — Create a Virtual Environment

This keeps the bot's packages isolated from the rest of your system.

```bash
python3 -m venv venv
```

Then activate it:
- **Mac/Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows PowerShell:**
  ```powershell
  venv\Scripts\Activate.ps1
  ```
  If you get a permissions error on Windows, run this first:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

You'll see `(venv)` at the start of your terminal prompt. **You need to activate this every time you open a new terminal to run the bot.**

---

### Step 5 — Install Python Dependencies

With the virtual environment active:

```bash
pip install -r requirements.txt
```

Then install the browser Playwright uses (downloads ~400 MB, may take a few minutes):
```bash
playwright install chromium
```

- [ ] Both commands finished without errors

**Linux only** — if Playwright fails, install these system packages first:
```bash
sudo apt-get install -y libglib2.0-0 libx11-6 libxext6 libxrender1 libxtst6 libxi6
```

---

### Step 6 — Install Ollama (AI Cover Letters)

Ollama runs the AI locally — free, private, no account needed.

- [ ] Go to [ollama.com](https://ollama.com) and download for your OS
  - **Mac:** Drag Ollama to your Applications folder, then open it (look for the llama icon in your menu bar)
  - **Windows:** Run the `.exe` installer, then open Ollama from the Start menu
  - **Linux:**
    ```bash
    curl -fsSL https://ollama.com/install.sh | sh
    ```
- [ ] Pull the AI model (downloads ~2 GB — this takes a few minutes):
  ```bash
  ollama pull llama3.2
  ```
- [ ] Verify it worked:
  ```bash
  ollama list
  ```
  You should see `llama3.2` in the list.

> **Important:** Ollama must be running in the background whenever you run the bot.
> - **Mac:** It runs automatically when open (check menu bar for the llama icon)
> - **Windows:** Open the Ollama app from Start menu before running the bot
> - **Linux:** Run `ollama serve` in a separate terminal

> **Skip Ollama?** The bot still works — it just uses a generic cover letter template instead of a custom one.

---

### Step 7 — Fill In Your Info

Open `linkedin_bot.py` in a text editor:
- **VS Code** (recommended, free): [code.visualstudio.com](https://code.visualstudio.com)
- **Mac:** TextEdit (change to plain text: Format → Make Plain Text)
- **Windows:** Notepad or Notepad++

Find and fill in each section marked with `✏️`:

#### 7a — Personal Info (`PERSONAL_INFO`)

- [ ] `first_name` — your first name
- [ ] `last_name` — your last name
- [ ] `full_name` — your full name as it appears on your resume
- [ ] `email` — your email address
- [ ] `phone` — **digits only, no spaces or dashes** (e.g. `"5551234567"`, not `"555-123-4567"`)
- [ ] `city` and `state` — your city and 2-letter state/province
- [ ] `location` — `"City, ST"` format exactly (e.g. `"Austin, TX"`)
- [ ] `zip` — your ZIP / postal code
- [ ] `linkedin` — your full LinkedIn URL (e.g. `"https://www.linkedin.com/in/yourname/"`)
- [ ] `years_experience` — a number as a string (e.g. `"5"`)
- [ ] `salary` — your target annual salary, **numbers only, no $ or commas** (e.g. `"100000"`)
- [ ] Leave `gender`, `veteran`, `disability`, `ethnicity` as-is unless you want to change them

#### 7b — Resume (`BASE_RESUME`)

- [ ] Delete all the placeholder text between the triple quotes `""" """`
- [ ] Paste your resume as **plain text** (no Word formatting, no PDF text, just raw text)
- [ ] Include: summary, work history with bullet points, education, skills
- [ ] **Include real numbers** — the AI will use them (e.g. "grew revenue 40%", "managed 8 reports")

Good example structure:
```
Your Name
your@email.com | City, ST | linkedin.com/in/yourprofile

SUMMARY
2-3 sentences about your background and biggest achievements.

WORK EXPERIENCE

Company Name — Job Title (Month Year - Present) | City, ST
- Achievement with a number (e.g. grew X by Y% or closed $Xk in revenue)
- Another accomplishment
- Another accomplishment

Previous Company — Job Title (Month Year - Month Year) | City, ST
- Achievement
- Achievement

EDUCATION
University Name — Degree, Major (Year)

SKILLS
- Category: list of skills
- Category: list of skills
```

#### 7c — Cover Letter Style (`COVER_LETTER_EXAMPLES`)

- [ ] Replace the placeholder examples with 1-2 of your strongest opening sentences
- [ ] Make them bold, punchy, and include a real number if you have one
- [ ] The AI will study these and match your voice — better examples = better output

Example:
```
EXAMPLE 1:
"I don't wait for pipeline — I build it. In my last role I sourced and closed $2.4M in
new ARR and I'm ready to bring that same energy to [Company]."

EXAMPLE 2:
"Five years ago I cold-called my way into a $380K deal nobody thought was closable.
I'm ready to do the same for [Company]."
```

#### 7d — Personality Blurb (`YOUR_PERSONALITY`)

- [ ] Write 3-4 sentences about who you are professionally
- [ ] Include: your field, your biggest achievement with a number, what you're known for

Example:
```
Jane is a results-driven sales professional with 5 years closing enterprise SaaS deals.
She grew her territory 60% YoY, ranked top 10% of her org, and built pipeline from scratch.
Known for consultative selling and showing up over-prepared to every meeting.
```

---

### Step 8 — Log In to LinkedIn

The bot saves your login session so you only have to do this once.

- [ ] Make sure your virtual environment is active (you should see `(venv)` in your terminal)
- [ ] Run:
  ```bash
  python3 linkedin_bot.py
  ```
  - **Windows:** use `python linkedin_bot.py` if `python3` doesn't work
- [ ] A browser window opens on the LinkedIn login page
- [ ] Log in with your email and password
- [ ] Complete 2-factor authentication if LinkedIn asks for it
- [ ] Once you see your LinkedIn feed, come back to the terminal and press **Enter**
- [ ] You'll see: `✅ Session saved to ~/linkedin_cookies.json`

> **Cookies expired later?** If you see `❌ Redirected to login`, your session expired.
> Delete the cookies file and rerun to log in again:
> - Mac/Linux: `rm ~/linkedin_cookies.json`
> - Windows: `del %USERPROFILE%\linkedin_cookies.json`

---

### Step 9 — Get a LinkedIn Search URL

- [ ] Go to [linkedin.com/jobs](https://www.linkedin.com/jobs)
- [ ] Search for job titles, add filters (location, remote, experience level, etc.)
- [ ] Copy the full URL from your browser address bar

It should look like:
```
https://www.linkedin.com/jobs/search/?keywords=account+executive&geoId=104472865&distance=25
```

> **Tip:** Set the "Easy Apply" filter on LinkedIn before copying the URL so you only see Easy Apply jobs.

---

### Step 10 — Run the Bot

Make sure:
- [ ] Virtual environment is active (`(venv)` in your terminal prompt)
- [ ] Ollama is running in the background (menu bar icon on Mac, app open on Windows)

Run:
```bash
python3 linkedin_bot.py
```

Paste your LinkedIn search URL when prompted, enter how many jobs to apply to, and watch it go.

Or pass the URL directly:
```bash
python3 linkedin_bot.py "https://www.linkedin.com/jobs/search/?keywords=account+executive&location=Austin" 25
```

**What you'll see:**
```
🔍 Loading search results...
  Found 24 job cards
📋 Will attempt 24 jobs

  → Account Executive @ Acme Corp
     📁 Saved docs: ~/Job Applications/20260314 - Acme Corp - Account Executive
     ✅ Applied!

  → Sales Manager @ TechCo
     ⏭️  No Easy Apply button

📊 RESULTS SUMMARY
  ✅ Applied:         12
  ⏭️  Skipped:         8
  🔄 Already applied: 2
  ❌ Errors:          2
```

---

## 📁 Output Files

After each run:

| Location | Contents |
|----------|----------|
| `~/Job Applications/YYYYMMDD - Company - Title/resume.txt` | AI-tailored resume |
| `~/Job Applications/YYYYMMDD - Company - Title/cover_letter.txt` | AI cover letter |
| `~/Job Applications/applied_TIMESTAMP.json` | Full log of all results |

On Windows, `~` means your user folder: `C:\Users\YourName\`

---

## ❓ Troubleshooting

**`python3: command not found`**
On Windows try `python` instead. If neither works, Python isn't in PATH — reinstall Python and check "Add to PATH".

**`playwright: command not found` or `ModuleNotFoundError: playwright`**
Your virtual environment isn't active. Run `source venv/bin/activate` (Mac/Linux) or `venv\Scripts\Activate.ps1` (Windows) first.

**"No job cards found"**
LinkedIn showed a single-job page instead of search results. The bot strips bad URL params automatically — double check your URL contains `/jobs/search/`.

**"Redirected to login — cookies expired"**
Delete `~/linkedin_cookies.json` (Mac/Linux) or `%USERPROFILE%\linkedin_cookies.json` (Windows) and rerun.

**Ollama not responding / generic cover letters**
Make sure Ollama is running before starting the bot. Mac: check menu bar. Windows: open Ollama app. Linux: run `ollama serve` in a separate terminal.

**Playwright install fails on Linux**
```bash
sudo apt-get install -y libglib2.0-0 libx11-6 libxext6 libxrender1 libxtst6 libxi6
playwright install chromium
```

**"Critical selectors are broken" / LinkedIn updated their HTML**
The bot runs a health check before every batch. If LinkedIn changed their HTML structure you'll see exactly which selector broke and instructions to fix it. To update a selector:
1. Open your LinkedIn job search in Chrome
2. Right-click a job card → **Inspect**
3. Find the `<li>` element that wraps each job listing
4. Copy its selector and update `SELECTORS['job_cards']` near the top of `linkedin_bot.py`
5. Open an issue on this repo so others get the fix too

**The bot gets stuck on a form**
Built-in stuck detection skips after 3 failed attempts and moves to the next job. Some multi-page forms with unusual questions will get skipped — that's expected.

**LinkedIn blocking / CAPTCHA**
Run at moderate volume (20-50 jobs per session). If you hit a CAPTCHA, complete it in the browser window and the bot will continue.

---

## ⚠️ Disclaimer

This bot is for personal use. Use responsibly:
- Respect LinkedIn's Terms of Service
- Don't run at extremely high volume (keep sessions under 50 jobs)
- Review your resume and cover letter templates before the first run
- You are responsible for every application submitted in your name

---

## License

MIT — use freely, modify as needed, attribution appreciated.
