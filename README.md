# 🤖 LinkedIn Easy Apply Bot

Automatically applies to LinkedIn Easy Apply jobs from any search URL.

- **AI cover letters & tailored resumes** — powered by Ollama (free, runs locally)
- **Saves all docs** — every cover letter and resume stored in your Job Applications folder
- **Skips non-Easy-Apply** jobs automatically
- **Session cookies** — log in once, runs headlessly from then on
- **Optional: [Vibecraft](https://github.com/your-handle/vibecraft) integration** — watch the bot work in a live 3D visualization

---

## ✅ Setup Checklist

Work through these steps in order. Each one has a checkbox — check them off as you go.

---

### Step 1 — Install Python

- [ ] Download Python 3.10 or newer from [python.org](https://www.python.org/downloads/)
- [ ] Run the installer — **check "Add Python to PATH"** during install
- [ ] Verify install: open Terminal and run:
  ```bash
  python3 --version
  ```
  You should see `Python 3.10.x` or higher.

---

### Step 2 — Download the Bot

**Option A — Clone with Git (recommended):**
```bash
git clone https://github.com/your-handle/linkedin-bot.git
cd linkedin-bot
```

**Option B — Download ZIP:**
- Click the green **Code** button on GitHub → **Download ZIP**
- Unzip the folder, open Terminal, and `cd` into it

---

### Step 3 — Install Python Dependencies

In Terminal, from inside the `linkedin-bot` folder:

```bash
pip install -r requirements.txt
```

This installs:
- `playwright` — controls the browser
- `openai` — talks to Ollama for AI writing

- [ ] Run the command above
- [ ] Install Playwright's browser (Chromium):
  ```bash
  playwright install chromium
  ```

---

### Step 4 — Install Ollama (AI Cover Letters)

Ollama runs the AI locally on your machine — free, private, no API key needed.

- [ ] Download Ollama from [ollama.com](https://ollama.com)
- [ ] Install it (drag to Applications on Mac, or run the installer on Windows)
- [ ] Pull the AI model — open Terminal and run:
  ```bash
  ollama pull llama3.2
  ```
  This downloads ~2GB. Wait for it to finish.
- [ ] Verify Ollama is running:
  ```bash
  ollama list
  ```
  You should see `llama3.2` in the list.

> **Skip this step?** The bot still works — it just uses a generic cover letter instead of an AI-tailored one.

---

### Step 5 — Fill In Your Info

Open `linkedin_bot.py` in any text editor (VS Code, TextEdit, Notepad, etc.)

#### 5a — Personal Info

Find the `PERSONAL_INFO` block near the top and fill it in:

- [ ] `first_name` — your first name
- [ ] `last_name` — your last name
- [ ] `full_name` — your full legal name
- [ ] `email` — your email address
- [ ] `phone` — digits only, no dashes (e.g. `5551234567`)
- [ ] `city` and `state` — your city and 2-letter state code
- [ ] `location` — `"City, ST"` format (e.g. `"Austin, TX"`)
- [ ] `zip` — your ZIP code
- [ ] `linkedin` — your full LinkedIn profile URL
- [ ] `years_experience` — number as a string (e.g. `"5"`)
- [ ] `salary` — your target salary, numbers only (e.g. `"100000"`)
- [ ] `gender`, `veteran`, `disability`, `ethnicity` — fill these in or leave the defaults

#### 5b — Resume

Find the `BASE_RESUME` block and replace the placeholder text with your actual resume:

- [ ] Delete the placeholder text between the triple quotes `"""`
- [ ] Paste in your resume as plain text
- [ ] Include: summary/headline, work experience (with bullet points), education, skills
- [ ] **Use real numbers** — the AI will reference them in your cover letters (e.g. "increased revenue 40%", "managed 12 accounts")

Good resume format example:
```
Jane Doe
jane.doe@email.com | Austin, TX | linkedin.com/in/janedoe

SUMMARY
Results-driven sales professional with 5 years closing enterprise SaaS deals.
Grew territory revenue 60% YoY and consistently ranked top 10% of org.

WORK EXPERIENCE

Acme Corp — Account Executive (Jan 2022 - Present) | Austin, TX
- Closed $2.4M in new ARR in 2023, top performer in a team of 18
- Expanded average deal size from $45K to $120K through solution selling
- Built outbound pipeline from scratch, 200+ meetings booked in first year

Previous Co — SDR (Jun 2020 - Dec 2021) | Houston, TX
- Generated 180% of quota for 6 consecutive quarters
- Sourced largest deal in team history: $380K enterprise contract

EDUCATION
University of Texas — B.S. Business Administration (2020)

SKILLS
- Enterprise sales, SaaS, full-cycle AE
- Salesforce, Outreach, LinkedIn Sales Navigator
- Negotiation, discovery, demo delivery
```

#### 5c — Cover Letter Examples

Find the `COVER_LETTER_EXAMPLES` block and replace the placeholders:

- [ ] Write 1-2 of your strongest cover letter opening sentences
- [ ] Make them punchy, specific, and include a real number if possible
- [ ] The AI will study your examples and match your voice

Example:
```
EXAMPLE 1:
"I don't wait for pipeline — I build it. In my last role I sourced and closed $2.4M in new ARR
and I'm ready to bring that same energy to Acme."

EXAMPLE 2:
"The moment I saw Acme's 400% growth trajectory, I stopped reading and started writing this letter."
```

#### 5d — Personality Blurb

Find the `YOUR_PERSONALITY` block:

- [ ] Write 3-4 sentences describing your professional brand
- [ ] Include your biggest achievements and what you're known for

---

### Step 6 — Log In to LinkedIn

The bot saves your login session so you only have to do this once.

- [ ] Run the bot (no URL needed for first login):
  ```bash
  python3 linkedin_bot.py
  ```
- [ ] A browser window will open on the LinkedIn login page
- [ ] Log in with your LinkedIn credentials
- [ ] Complete any 2-factor authentication if prompted
- [ ] Once you see your LinkedIn feed, come back to Terminal and press **ENTER**
- [ ] The bot saves your session to `linkedin_cookies.json` in your home folder

> **Cookies expired?** If you see `❌ Redirected to login`, delete `~/linkedin_cookies.json` and rerun to log in again.

---

### Step 7 — Get a LinkedIn Search URL

- [ ] Go to LinkedIn and search for jobs (use filters: location, remote, job type, etc.)
- [ ] Copy the URL from your browser address bar
- [ ] It should look like:
  ```
  https://www.linkedin.com/jobs/search/?keywords=account+executive&geoId=104472865&distance=25
  ```

> **Tip:** Apply Easy Apply filters on LinkedIn first to see only Easy Apply jobs, then copy the URL.

---

### Step 8 — Run the Bot

```bash
python3 linkedin_bot.py
```

Paste your LinkedIn search URL when prompted, set your max number of jobs, and watch it go.

Or pass the URL directly:
```bash
python3 linkedin_bot.py "https://www.linkedin.com/jobs/search/?keywords=account+executive&location=Austin%2C+TX" 30
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

  ...

📊 RESULTS SUMMARY
  ✅ Applied:         12
  ⏭️  Skipped:         8
  🔄 Already applied: 2
  ❌ Errors:          2
  📁 Log: ~/Job Applications/applied_20260314_103000.json
```

---

## 📁 Output Files

After each run you'll find:

| Location | Contents |
|----------|----------|
| `~/Job Applications/YYYYMMDD - Company - Title/resume.txt` | AI-tailored resume |
| `~/Job Applications/YYYYMMDD - Company - Title/cover_letter.txt` | AI cover letter |
| `~/Job Applications/applied_TIMESTAMP.json` | Full log of all results |

---

## ⚙️ Configuration

| Setting | Where | What it does |
|---------|-------|-------------|
| `COOKIES_PATH` | `linkedin_bot.py` | Where session cookies are saved |
| `OUTPUT_DIR` | `linkedin_bot.py` | Where docs are saved |
| `OLLAMA_MODEL` | `linkedin_bot.py` | Which Ollama model to use (`llama3.2` default) |
| `max_jobs` | CLI arg or prompt | Max jobs to attempt per run |

---

## 🎮 Vibecraft Integration (Optional)

If you use [Vibecraft](https://github.com/your-handle/vibecraft), the bot automatically shows up as a live worker in the 3D visualization when it runs. No extra setup needed — just have Vibecraft running on `localhost:4003`.

---

## ❓ Troubleshooting

**"No job cards found"**
The LinkedIn search URL you pasted is showing a single job view. Make sure the URL contains `/jobs/search/` (not `/jobs/search-results/`). The bot strips this automatically but double-check your URL.

**"Redirected to login"**
Your cookies expired. Delete `~/linkedin_cookies.json` and rerun — you'll be prompted to log in again.

**"playwright: command not found"**
Run `pip install playwright && playwright install chromium`

**"openai: No module named 'openai'"**
Run `pip install openai`

**Ollama not responding**
Make sure Ollama is running: open the Ollama app (Mac) or run `ollama serve` in a terminal. The bot will still work without it — just uses generic text.

**The bot gets stuck on a form step**
The bot has automatic stuck detection (3 strikes) and will skip to the next job. Some complex multi-page forms will get skipped. That's expected.

---

## ⚠️ Disclaimer

This bot is for personal use. Use responsibly:
- Respect LinkedIn's Terms of Service
- Don't run at extremely high volume
- Review applications before they go out — the AI is good but not perfect
- You are responsible for what gets submitted in your name

---

## License

MIT — use freely, modify as needed, attribution appreciated.
