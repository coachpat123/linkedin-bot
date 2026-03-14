"""
LinkedIn Easy Apply Bot
=======================
Automatically applies to LinkedIn Easy Apply jobs from a search URL.
- AI-tailored cover letters and resumes via Ollama (local, free)
- Saves application docs to a folder
- Optional: Vibecraft live visualization (https://github.com/your-handle/vibecraft)

Setup: See README.md for the full step-by-step checklist.
"""

import os
import re
import json
import time
import uuid
import urllib.request
import threading
from datetime import datetime
from playwright.sync_api import sync_playwright, Page

# ─────────────────────────────────────────────────────────────────
# ✏️  STEP 1 — FILL IN YOUR PERSONAL INFO
# ─────────────────────────────────────────────────────────────────

PERSONAL_INFO = {
    "first_name":          "Jane",
    "last_name":           "Doe",
    "full_name":           "Jane Doe",
    "email":               "jane.doe@example.com",
    "phone":               "5551234567",            # digits only, no dashes
    "city":                "Austin",
    "state":               "TX",
    "location":            "Austin, TX",
    "zip":                 "78701",
    "linkedin":            "https://www.linkedin.com/in/janedoe/",
    "years_experience":    "5",
    "salary":              "100000",               # desired salary (numbers only)
    "gender":              "Decline to self-identify",
    "veteran":             "I am not a protected veteran",
    "disability":          "I do not have a disability",
    "ethnicity":           "Decline to self-identify",
    "authorized_to_work":  "Yes",
    "require_sponsorship": "No",
}

# ─────────────────────────────────────────────────────────────────
# ✏️  STEP 2 — PASTE YOUR RESUME HERE
#     Plain text is fine. Include work history, skills, education.
#     The AI will tailor this to each job description.
# ─────────────────────────────────────────────────────────────────

BASE_RESUME = """
Jane Doe
jane.doe@example.com | Austin, TX | linkedin.com/in/janedoe

SUMMARY
[Write 2-3 sentences about your background and biggest achievements.]

WORK EXPERIENCE

Company Name — Job Title (Month Year - Present) | City, ST
- [Achievement with a number: grew X by Y%]
- [Another accomplishment]
- [Another accomplishment]

Previous Company — Job Title (Month Year - Month Year) | City, ST
- [Achievement]
- [Achievement]

EDUCATION
University Name — Degree, Major (Year)

SKILLS
- [Skill category]: [list skills]
- [Skill category]: [list skills]
"""

# ─────────────────────────────────────────────────────────────────
# ✏️  STEP 3 — WRITE YOUR COVER LETTER STYLE GUIDE
#     Give 1-2 real examples of strong opening sentences you've written.
#     This is the secret sauce — better examples = better AI output.
# ─────────────────────────────────────────────────────────────────

COVER_LETTER_EXAMPLES = """
EXAMPLE 1:
"[Your best cover letter opening sentence — make it bold and specific]"

EXAMPLE 2:
"[Another strong opening that references a real achievement with a number]"
"""

# ─────────────────────────────────────────────────────────────────
# ✏️  STEP 4 — WRITE YOUR PERSONALITY BLURB
#     3-4 sentences the AI uses to match your voice in AI answers.
# ─────────────────────────────────────────────────────────────────

YOUR_PERSONALITY = """
[Your name] is a [your field] professional known for [your biggest strength].
Key wins: [achievement 1], [achievement 2], [achievement 3].
Excels at [what you do best] and brings a [adjective] mindset to every role.
"""

# ─────────────────────────────────────────────────────────────────
# ⚙️  CONFIG — Paths and settings (change if needed)
# ─────────────────────────────────────────────────────────────────

COOKIES_PATH  = os.path.expanduser("~/linkedin_cookies.json")
OUTPUT_DIR    = os.path.expanduser("~/Job Applications")
OLLAMA_MODEL  = "llama3.2"          # Run: ollama pull llama3.2
OLLAMA_URL    = "http://localhost:11434/v1"

# Vibecraft live visualization (optional — leave as-is if not using)
VIBECRAFT_URL = "http://localhost:4003"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
# LOCAL AI — Ollama
# ─────────────────────────────────────────────────────────────────

try:
    from openai import OpenAI
    ai = OpenAI(base_url=f"{OLLAMA_URL}/v1", api_key="ollama")
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  openai package not installed — AI cover letters disabled. Run: pip install openai")


def write_cover_letter(job_description: str, company: str, title: str) -> str:
    if not AI_AVAILABLE:
        return f"Dear Hiring Team,\n\nI am excited to apply for the {title} role at {company}. My background aligns well with this position and I look forward to discussing further.\n\nBest,\n{PERSONAL_INFO['full_name']}"
    try:
        msg = ai.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": f"""Write a cover letter for {PERSONAL_INFO['full_name']} applying to {company} for {title}.

WRITING STYLE — study these real examples and match the tone exactly:

{COVER_LETTER_EXAMPLES}

STYLE RULES:
- Open with a bold, punchy one-liner specific to THIS company/role
- Never start with "I am writing to express my interest"
- Reference THIS company by name and show you understand what they do
- Use real numbers from the resume
- Write in first person, confident, direct
- 4 paragraphs max, each tight and purposeful
- End with energy and a clear call to action

RESUME:
{BASE_RESUME}

JOB DESCRIPTION:
{job_description}

Return ONLY the cover letter text."""}]
        )
        return msg.choices[0].message.content
    except Exception as e:
        return f"Cover letter generation failed ({e}). Please write manually."


def tailor_resume(job_description: str) -> str:
    if not AI_AVAILABLE:
        return BASE_RESUME
    try:
        msg = ai.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": f"""Tailor this resume to the job description.
Keep all facts 100% accurate. Reorder/adjust language to emphasize the most relevant experience.
Return ONLY the resume text.

JOB DESCRIPTION: {job_description}

BASE RESUME: {BASE_RESUME}"""}]
        )
        return msg.choices[0].message.content
    except Exception:
        return BASE_RESUME


def answer_question(question: str, job_description: str) -> str:
    if not AI_AVAILABLE:
        return "I have strong relevant experience in this area and am excited to contribute to your team."
    try:
        msg = ai.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": f"""Answer this job application question for {PERSONAL_INFO['full_name']}.
Be authentic, specific, and use real facts. Keep it 2-4 sentences.

BACKGROUND: {YOUR_PERSONALITY}
JOB CONTEXT: {job_description[:500]}
QUESTION: {question}

Return ONLY the answer."""}]
        )
        return msg.choices[0].message.content
    except Exception:
        return "I have strong relevant experience and am eager to contribute to your team."


# ─────────────────────────────────────────────────────────────────
# VIBECRAFT INTEGRATION (optional)
# ─────────────────────────────────────────────────────────────────

class VibecraftReporter:
    """Posts live events to Vibecraft 3D visualization. Silently skips if offline."""

    def __init__(self):
        self.session_id = f"job-bot-{uuid.uuid4()}"
        self.cwd = os.path.expanduser("~")
        self._managed_ids: list = []

    def _post(self, event: dict):
        try:
            data = json.dumps(event).encode()
            req = urllib.request.Request(
                f"{VIBECRAFT_URL}/event", data=data,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            urllib.request.urlopen(req, timeout=1)
        except Exception:
            pass

    def _event(self, type: str, **kwargs) -> dict:
        return {
            "id": str(uuid.uuid4()),
            "timestamp": int(time.time() * 1000),
            "type": type,
            "sessionId": self.session_id,
            "cwd": self.cwd,
            **kwargs,
        }

    def register(self, name: str = "Job Bot 🤖"):
        try:
            data = json.dumps({"name": name, "claudeSessionId": self.session_id}).encode()
            req = urllib.request.Request(
                f"{VIBECRAFT_URL}/sessions/register", data=data,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=2)
            body = json.loads(resp.read())
            if body.get("ok") and body.get("session", {}).get("id"):
                self._managed_ids.append(body["session"]["id"])
        except Exception:
            pass

    def register_worker(self, name: str) -> "VibecraftReporter":
        worker = VibecraftReporter()
        try:
            data = json.dumps({"name": name, "claudeSessionId": worker.session_id}).encode()
            req = urllib.request.Request(
                f"{VIBECRAFT_URL}/sessions/register", data=data,
                headers={"Content-Type": "application/json"}, method="POST",
            )
            resp = urllib.request.urlopen(req, timeout=2)
            body = json.loads(resp.read())
            if body.get("ok") and body.get("session", {}).get("id"):
                self._managed_ids.append(body["session"]["id"])
        except Exception:
            pass
        return worker

    def start_run(self, search_url: str):
        self.register()
        self._post(self._event("session_start", source="startup"))
        self._post(self._event("user_prompt_submit", prompt=f"Bulk applying — {search_url}"))

    def tool_start(self, tool: str, label: str = "") -> str:
        tid = str(uuid.uuid4())
        self._post(self._event("pre_tool_use", tool=tool, toolUseId=tid, toolInput={"description": label}))
        return tid

    def tool_done(self, tool: str, tid: str, success: bool = True):
        self._post(self._event("post_tool_use", tool=tool, toolUseId=tid, toolInput={}, toolResponse={}, success=success))

    def notify(self, message: str):
        self._post(self._event("notification", message=message, notificationType="info"))

    def finish(self):
        self._post(self._event("stop", stopHookActive=False))
        for managed_id in self._managed_ids:
            try:
                req = urllib.request.Request(
                    f"{VIBECRAFT_URL}/sessions/{managed_id}",
                    headers={"Content-Type": "application/json"}, method="DELETE",
                )
                urllib.request.urlopen(req, timeout=2)
            except Exception:
                pass
        self._managed_ids.clear()


vc = VibecraftReporter()

# ─────────────────────────────────────────────────────────────────
# BACKGROUND WORKERS (visual flair in Vibecraft — optional)
# ─────────────────────────────────────────────────────────────────

WORKER_SCHEDULES = [
    ("Researcher 🔍", [
        ("WebSearch", "Searching company backgrounds", 6),
        ("Read",      "Reading job descriptions",      5),
        ("Grep",      "Scanning salary data",          4),
        ("WebFetch",  "Checking company LinkedIn",     7),
        ("TodoWrite", "Logging research notes",        3),
    ]),
    ("Cover Letter Writer ✍️", [
        ("Write",  "Drafting cover letter",        8),
        ("Edit",   "Refining opening paragraph",   5),
        ("Edit",   "Tightening closing paragraph", 4),
        ("Write",  "Finalizing cover letter",       6),
        ("Bash",   "Saving to applications folder", 3),
    ]),
]


def _run_worker(worker: VibecraftReporter, name: str, schedule: list):
    worker._post(worker._event("session_start", source="startup"))
    worker._post(worker._event("user_prompt_submit", prompt=f"{name} is on the job"))
    while True:
        for tool, label, sleep_sec in schedule:
            tid = worker.tool_start(tool, label)
            time.sleep(sleep_sec)
            worker.tool_done(tool, tid)
            time.sleep(1)


def start_background_workers():
    for name, schedule in WORKER_SCHEDULES:
        worker = vc.register_worker(name)
        t = threading.Thread(target=_run_worker, args=(worker, name, schedule), daemon=True)
        t.start()


# ─────────────────────────────────────────────────────────────────
# FORM FILLING
# ─────────────────────────────────────────────────────────────────

def fill_easy_apply(page: Page, job_description: str = ""):
    """Fill all fields in an Easy Apply modal — moves forward without stopping."""
    try:
        try:
            modal = page.locator("div[role='dialog']").first
            scope = modal if modal.is_visible() else page
        except Exception:
            scope = page

        # Text inputs
        for inp in scope.locator("input[type='text']:visible, input[type='number']:visible, input[type='tel']:visible, input[type='email']:visible").all():
            try:
                if inp.input_value():
                    continue
                label = ""
                try:
                    el_id = inp.get_attribute("id") or ""
                    if el_id:
                        lbl = page.locator(f"label[for='{el_id}']").first
                        if lbl.is_visible():
                            label = lbl.inner_text().lower()
                    if not label:
                        label = inp.evaluate("el => el.closest('div,li,p')?.innerText || ''").lower()[:200]
                except Exception:
                    pass

                if any(w in label for w in ["first name", "first_name"]):
                    inp.fill(PERSONAL_INFO["first_name"])
                elif any(w in label for w in ["last name", "last_name"]):
                    inp.fill(PERSONAL_INFO["last_name"])
                elif "email" in label:
                    inp.fill(PERSONAL_INFO["email"])
                elif "phone" in label or "mobile" in label:
                    inp.fill(PERSONAL_INFO["phone"])
                elif "linkedin" in label:
                    inp.fill(PERSONAL_INFO["linkedin"])
                elif any(w in label for w in ["city", "location", "where"]):
                    inp.fill(PERSONAL_INFO["location"])
                elif any(w in label for w in ["salary", "compensation", "pay"]):
                    inp.fill(PERSONAL_INFO["salary"])
                elif any(w in label for w in ["year", "experience"]):
                    inp.fill(PERSONAL_INFO["years_experience"])
                elif any(w in label for w in ["zip", "postal"]):
                    inp.fill(PERSONAL_INFO["zip"])
                else:
                    inp.fill("Yes")
                time.sleep(0.1)
            except Exception:
                pass

        # Textareas
        for ta in scope.locator("textarea:visible").all():
            try:
                if ta.input_value():
                    continue
                ta_id = ta.get_attribute("id") or ""
                question = ""
                try:
                    lbl = page.locator(f"label[for='{ta_id}']").first
                    if lbl.is_visible():
                        question = lbl.inner_text()
                except Exception:
                    pass
                if question and len(question) > 10 and "cover" not in question.lower() and job_description:
                    ta.fill(answer_question(question, job_description))
                else:
                    ta.fill(f"I have {PERSONAL_INFO['years_experience']}+ years of relevant experience and am excited to contribute immediately.")
                time.sleep(0.1)
            except Exception:
                pass

        # Dropdowns
        for select in scope.locator("select:visible").all():
            try:
                val = select.input_value()
                if val and val not in ("", "0"):
                    continue
                label = ""
                try:
                    label = select.evaluate("el => el.closest('div,li')?.innerText || ''").lower()[:200]
                except Exception:
                    pass

                if "country" in label:
                    try:
                        select.select_option(label="United States")
                    except Exception:
                        pass
                elif any(w in label for w in ["sponsor", "visa", "previously", "worked for", "ever work"]):
                    try:
                        select.select_option(label="No")
                    except Exception:
                        select.select_option(index=2)
                elif any(w in label for w in ["authorized", "eligible", "legally"]):
                    try:
                        select.select_option(label="Yes")
                    except Exception:
                        select.select_option(index=1)
                elif "veteran" in label:
                    try:
                        select.select_option(label=PERSONAL_INFO["veteran"])
                    except Exception:
                        select.select_option(index=1)
                elif "disability" in label:
                    try:
                        select.select_option(label=PERSONAL_INFO["disability"])
                    except Exception:
                        select.select_option(index=1)
                elif "gender" in label:
                    try:
                        select.select_option(label=PERSONAL_INFO["gender"])
                    except Exception:
                        pass
                elif "ethnicity" in label or "race" in label:
                    try:
                        select.select_option(label=PERSONAL_INFO["ethnicity"])
                    except Exception:
                        pass
                else:
                    try:
                        select.select_option(label="Yes")
                    except Exception:
                        try:
                            select.select_option(index=1)
                        except Exception:
                            pass
                time.sleep(0.1)
            except Exception:
                pass

        # Radio buttons
        for fieldset in scope.locator("fieldset").all():
            try:
                legend = ""
                try:
                    legend = fieldset.locator("legend").first.inner_text().lower()
                except Exception:
                    pass
                if any(w in legend for w in ["sponsor", "visa", "previously", "worked for"]):
                    fieldset.locator("label:has-text('No')").first.click()
                elif any(w in legend for w in ["authorized", "eligible", "legally"]):
                    fieldset.locator("label:has-text('Yes')").first.click()
                elif any(w in legend for w in ["year", "experience", "how long", "how many"]):
                    try:
                        fieldset.locator(f"label:has-text('{PERSONAL_INFO[\"years_experience\"]}')").first.click()
                    except Exception:
                        try:
                            fieldset.locator("label:has-text('Yes')").first.click()
                        except Exception:
                            pass
                elif legend:
                    try:
                        fieldset.locator("label:has-text('Yes')").first.click()
                    except Exception:
                        pass
                time.sleep(0.1)
            except Exception:
                pass

        # Select existing resume if shown
        try:
            resume_radio = scope.locator("input[type='radio']").first
            if resume_radio.is_visible():
                resume_radio.click()
        except Exception:
            pass

    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────
# SAVE DOCS
# ─────────────────────────────────────────────────────────────────

def save_application_docs(company: str, title: str, resume: str, cover_letter: str):
    safe_name = re.sub(r'[^\w\s-]', '', f"{company} - {title}").strip()
    safe_name = re.sub(r'\s+', ' ', safe_name)
    folder_name = f"{datetime.now().strftime('%Y%m%d')} - {safe_name}"
    app_folder = os.path.join(OUTPUT_DIR, folder_name)
    os.makedirs(app_folder, exist_ok=True)
    with open(os.path.join(app_folder, "resume.txt"), "w") as f:
        f.write(resume)
    with open(os.path.join(app_folder, "cover_letter.txt"), "w") as f:
        f.write(cover_letter)
    print(f"     📁 Saved docs: {app_folder}")


# ─────────────────────────────────────────────────────────────────
# APPLY TO ONE JOB
# ─────────────────────────────────────────────────────────────────

def apply_to_job(page: Page, card, search_url: str) -> dict:
    title = ""
    company = ""
    result = {"status": "skipped", "title": "", "company": "", "timestamp": datetime.now().isoformat(), "notes": ""}

    try:
        try:
            title = card.locator(SELECTORS["job_title"]).first.inner_text().strip()
        except Exception:
            pass
        try:
            company = card.locator(SELECTORS["company_name"]).first.inner_text().strip()
        except Exception:
            pass

        result["title"] = title
        result["company"] = company

        # Already applied?
        try:
            if card.locator(SELECTORS["already_applied"]).is_visible():
                result["status"] = "already"
                return result
        except Exception:
            pass

        print(f"\n  → {title} @ {company}")

        card.click()
        time.sleep(1.5)

        job_desc = f"{title} at {company}"
        try:
            job_desc = page.locator(SELECTORS["job_desc"]).inner_text(timeout=5000)
        except Exception:
            pass

        # AI docs
        tid = vc.tool_start("Write", f"Writing cover letter — {company}")
        cover_letter = write_cover_letter(job_desc, company, title)
        vc.tool_done("Write", tid)

        tid = vc.tool_start("Edit", f"Tailoring resume — {title}")
        tailored_resume = tailor_resume(job_desc)
        vc.tool_done("Edit", tid)

        save_application_docs(company, title, tailored_resume, cover_letter)

        # Find Easy Apply button
        easy_apply = None
        try:
            page.wait_for_selector(
                "button.jobs-apply-button:has-text('Easy Apply'), .jobs-s-apply button:has-text('Easy Apply')",
                timeout=2000
            )
            for selector in [
                "button.jobs-apply-button:has-text('Easy Apply')",
                ".jobs-apply-button--top-card button:has-text('Easy Apply')",
                ".jobs-s-apply button:has-text('Easy Apply')",
                ".job-details-jobs-unified-top-card__container--two-pane button:has-text('Easy Apply')",
            ]:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible():
                        easy_apply = btn
                        break
                except Exception:
                    pass
        except Exception:
            pass

        if not easy_apply:
            try:
                for btn in page.locator("button.jobs-apply-button:has-text('Easy Apply')").all():
                    if btn.is_visible():
                        easy_apply = btn
                        break
            except Exception:
                pass

        if not easy_apply:
            print(f"     ⏭️  No Easy Apply button")
            vc.notify(f"⏭️ Skipped {company} — no Easy Apply")
            result["notes"] = "No Easy Apply button"
            return result

        easy_apply.click()
        time.sleep(2)

        try:
            page.wait_for_selector("div[role='dialog']", timeout=2000)
        except Exception:
            print(f"     ⏭️  Modal didn't open")
            result["notes"] = "Modal didn't open"
            return result

        try:
            if not page.locator("div[role='dialog']").first.is_visible():
                return result
        except Exception:
            return result

        # Pre-fill cover letter field
        try:
            cl_field = page.locator("textarea[id*='cover'], textarea[placeholder*='cover']").first
            if cl_field.is_visible() and not cl_field.input_value():
                cl_field.fill(cover_letter)
        except Exception:
            pass

        # Step through form
        prev_btn = ""
        stuck = 0

        for step in range(25):
            time.sleep(0.8)

            tid = vc.tool_start("Bash", f"Filling form step {step+1} — {company}")
            fill_easy_apply(page, job_desc)
            vc.tool_done("Bash", tid)

            submit = page.locator("button:has-text('Submit application')").first
            if submit.is_visible():
                tid = vc.tool_start("Bash", f"Submitting — {title} at {company}")
                submit.click()
                time.sleep(2)
                try:
                    page.locator("button:has-text('Done')").first.click(timeout=2000)
                except Exception:
                    pass
                vc.tool_done("Bash", tid, success=True)
                vc.notify(f"✅ Applied: {title} @ {company}")
                result["status"] = "applied"
                print(f"     ✅ Applied!")
                return result

            review = page.locator("button:has-text('Review')").first
            if review.is_visible():
                review.click()
                time.sleep(1.5)
                fill_easy_apply(page, job_desc)
                submit = page.locator("button:has-text('Submit application')").first
                if submit.is_visible():
                    submit.click()
                    time.sleep(1.5)
                    try:
                        page.locator("button:has-text('Done')").first.click(timeout=1500)
                    except Exception:
                        pass
                    vc.notify(f"✅ Applied: {title} @ {company}")
                    result["status"] = "applied"
                    print(f"     ✅ Applied!")
                    return result
                continue

            next_btn = page.locator("button:has-text('Next'), button:has-text('Continue')").first
            if next_btn.is_visible():
                txt = next_btn.inner_text()
                if txt == prev_btn:
                    stuck += 1
                    if stuck >= 3:
                        try:
                            page.locator("button[aria-label='Dismiss']").first.click(timeout=1500)
                            time.sleep(0.5)
                            page.locator("button:has-text('Discard')").first.click(timeout=1500)
                        except Exception:
                            try:
                                page.keyboard.press("Escape")
                                time.sleep(0.5)
                                page.locator("button:has-text('Discard')").first.click(timeout=1500)
                            except Exception:
                                pass
                        result["notes"] = "Stuck on form"
                        return result
                else:
                    stuck = 0
                    prev_btn = txt
                next_btn.click()
                continue

            stuck += 1
            if stuck >= 2:
                try:
                    page.keyboard.press("Escape")
                    time.sleep(0.5)
                    page.locator("button:has-text('Discard')").first.click(timeout=1500)
                except Exception:
                    pass
                result["notes"] = "No next/submit found"
                return result
            time.sleep(0.8)

    except Exception as e:
        print(f"     ❌ Error: {e}")
        result["status"] = "error"
        result["notes"] = str(e)
        try:
            page.keyboard.press("Escape")
            time.sleep(0.5)
            page.locator("button:has-text('Discard')").first.click(timeout=1500)
        except Exception:
            pass

    return result


# ─────────────────────────────────────────────────────────────────
# SELECTOR HEALTH CHECK
# ─────────────────────────────────────────────────────────────────

# These are the CSS selectors the bot depends on.
# If LinkedIn updates their HTML, these will break first.
# Update them here and the whole bot benefits.
SELECTORS = {
    "job_cards":    "li[data-occludable-job-id]",
    "job_title":    ".job-card-list__title, strong",
    "company_name": ".job-card-container__company-name",
    "easy_apply":   "button.jobs-apply-button:has-text('Easy Apply')",
    "job_desc":     ".jobs-description, .job-details-jobs-unified-top-card__job-insight",
    "already_applied": ".job-card-container__footer-item:has-text('Applied')",
}

def selector_health_check(page) -> bool:
    """
    Verify key LinkedIn selectors still work before running the full batch.
    Prints a pass/fail for each one. Returns False if critical selectors are broken.
    """
    print("\n🔬 Running selector health check...")
    print("   (If LinkedIn updated their HTML, broken selectors will show here)\n")

    critical_ok = True

    # Check job cards — the most critical selector
    card_count = page.locator(SELECTORS["job_cards"]).count()
    if card_count > 0:
        print(f"  ✅ Job cards        ({SELECTORS['job_cards']}) — found {card_count}")
    else:
        print(f"  ❌ Job cards        ({SELECTORS['job_cards']}) — NOT FOUND")
        print(f"     ↳ LinkedIn may have changed their job list HTML.")
        print(f"     ↳ Open browser DevTools on the search page, inspect a job card,")
        print(f"       and find the new selector. Update SELECTORS['job_cards'] in the script.")
        critical_ok = False

    # Check title and company on the first card (non-critical — bot falls back to empty string)
    if card_count > 0:
        first_card = page.locator(SELECTORS["job_cards"]).first
        title_ok = first_card.locator(SELECTORS["job_title"]).count() > 0
        company_ok = first_card.locator(SELECTORS["company_name"]).count() > 0
        print(f"  {'✅' if title_ok   else '⚠️ '} Job title          ({SELECTORS['job_title']})")
        print(f"  {'✅' if company_ok  else '⚠️ '} Company name       ({SELECTORS['company_name']})")
        if not title_ok or not company_ok:
            print(f"     ↳ Title/company parsing broke — applications will still submit")
            print(f"       but folder names and logs will show blank company/title.")

    # Check job description panel (non-critical — AI gets less context)
    desc_ok = page.locator(SELECTORS["job_desc"]).count() > 0
    print(f"  {'✅' if desc_ok else '⚠️ '} Job description    ({SELECTORS['job_desc']})")
    if not desc_ok:
        print(f"     ↳ Can't read job descriptions — AI cover letters will be generic.")

    # Check Easy Apply button (non-critical — checked per-job, skipped if missing)
    # Click first card to trigger the detail pane, then check
    if card_count > 0:
        try:
            page.locator(SELECTORS["job_cards"]).first.click()
            time.sleep(1.5)
            easy_ok = page.locator(SELECTORS["easy_apply"]).count() > 0
            print(f"  {'✅' if easy_ok else '⚠️ '} Easy Apply button  ({SELECTORS['easy_apply']})")
            if not easy_ok:
                print(f"     ↳ First job may not have Easy Apply, or selector changed.")
                print(f"       The bot will still check each job individually.")
        except Exception:
            print(f"  ⚠️  Easy Apply button  — could not check (card click failed)")

    print()

    if not critical_ok:
        print("  ⛔ Critical selectors are broken. The bot cannot find job cards.")
        print("     LinkedIn likely updated their HTML. Steps to fix:")
        print("     1. Open your LinkedIn job search in Chrome")
        print("     2. Right-click a job card → Inspect")
        print("     3. Find the <li> element that wraps each job")
        print("     4. Update SELECTORS['job_cards'] at the top of the script")
        print("     5. Open an issue at https://github.com/coachpat123/linkedin-bot")
        print()

    return critical_ok


# ─────────────────────────────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────────────────────────────

def run_bulk_apply(search_url: str, max_jobs: int = 50):
    log_file = f"{OUTPUT_DIR}/applied_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results = []
    stats = {"applied": 0, "skipped": 0, "already": 0, "error": 0}

    vc.start_run(search_url)
    start_background_workers()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=50)
            context = browser.new_context()

            cookies_loaded = False
            try:
                with open(COOKIES_PATH) as f:
                    context.add_cookies(json.load(f))
                print("✅ Loaded LinkedIn session cookies")
                cookies_loaded = True
            except Exception:
                print("⚠️  No saved cookies found")

            page = context.new_page()

            if not cookies_loaded:
                print("\n🔐 Please log in to LinkedIn in the browser window.")
                print("   Press ENTER here once you're logged in and on your feed...")
                page.goto("https://www.linkedin.com/login", wait_until="domcontentloaded")
                input()
                cookies = context.cookies()
                with open(COOKIES_PATH, "w") as f:
                    json.dump(cookies, f, indent=2)
                os.chmod(COOKIES_PATH, 0o600)  # Owner read/write only — no other apps can read your session
                print(f"✅ Session saved to {COOKIES_PATH}")

            print("\n" + "=" * 55)
            print("🤖 LINKEDIN EASY APPLY BOT")
            print("=" * 55)

            tid = vc.tool_start("Grep", "Scanning LinkedIn job listings")
            print(f"\n🔍 Loading search results...")

            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(search_url)
            keep_params = {k: v for k, v in parse_qs(parsed.query).items()
                           if k in ("keywords", "geoId", "distance", "f_LF", "f_WT", "f_E", "f_TPR", "sortBy", "location")}
            clean_url = urlunparse(parsed._replace(path="/jobs/search/", query=urlencode(keep_params, doseq=True)))
            print(f"  🧹 Clean URL: {clean_url}")

            page.goto(clean_url, wait_until="domcontentloaded", timeout=60000)
            time.sleep(3)

            current_url = page.url
            page_title = page.title()
            print(f"  📍 {page_title}")
            print(f"  🔗 {current_url}")

            if "linkedin.com/login" in current_url or "authwall" in current_url:
                print("  ❌ Redirected to login — cookies expired.")
                print(f"     Delete {COOKIES_PATH} and rerun to log in again.")
                browser.close()
                return

            if "checkpoint" in current_url:
                print("  ❌ LinkedIn security checkpoint — complete it in the browser, then press ENTER.")
                input()

            try:
                page.wait_for_selector(SELECTORS["job_cards"], timeout=15000)
            except Exception:
                pass

            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)

            # Health check — verify selectors before committing to the full run
            if not selector_health_check(page):
                browser.close()
                return

            cards = page.locator(SELECTORS["job_cards"]).all()
            vc.tool_done("Grep", tid)

            print(f"  Found {len(cards)} job cards")

            if not cards:
                snippet = page.content()[:2000]
                print(f"  ⚠️  No job cards found. HTML snippet:\n{snippet}\n")
                browser.close()
                return

            cards = cards[:max_jobs]
            print(f"📋 Will attempt {len(cards)} jobs\n")

            i = 0
            while i < len(cards) and stats["applied"] < max_jobs:
                cards = page.locator(SELECTORS["job_cards"]).all()
                if i >= len(cards):
                    break
                card = cards[i]
                i += 1

                result = apply_to_job(page, card, clean_url)
                results.append(result)
                stats[result["status"]] = stats.get(result["status"], 0) + 1

                with open(log_file, "w") as f:
                    json.dump(results, f, indent=2)

                if result["status"] == "applied":
                    page.goto(clean_url, wait_until="domcontentloaded", timeout=20000)
                    try:
                        page.wait_for_selector("li[data-occludable-job-id]", timeout=10000)
                    except Exception:
                        pass
                    time.sleep(1)

                if i % 5 == 0:
                    print(f"  📊 ✅ {stats['applied']} applied | ⏭️ {stats['skipped']} skipped | 🔄 {stats.get('already', 0)} already applied")

                time.sleep(0.8)

            browser.close()

        print("\n" + "=" * 55)
        print("📊 RESULTS SUMMARY")
        print("=" * 55)
        print(f"  ✅ Applied:         {stats['applied']}")
        print(f"  ⏭️  Skipped:         {stats['skipped']}")
        print(f"  🔄 Already applied: {stats.get('already', 0)}")
        print(f"  ❌ Errors:          {stats.get('error', 0)}")
        print(f"  📁 Log: {log_file}")
        print("=" * 55)

        vc.notify(f"🏁 Done — {stats['applied']} applied, {stats['skipped']} skipped")

    except Exception as e:
        import traceback
        print(f"\n💥 BOT CRASHED: {e}")
        traceback.print_exc()
        vc.notify(f"💥 Bot crashed: {e}")
    finally:
        vc.finish()


# ─────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) >= 2:
        # Called from CLI / n8n / Telegram automation
        search_url = sys.argv[1]
        max_jobs = int(sys.argv[2]) if len(sys.argv) >= 3 and sys.argv[2].isdigit() else 20
        print(f"\n🤖 Running (triggered externally)")
        print(f"   URL: {search_url}")
        print(f"   Max jobs: {max_jobs}")
        run_bulk_apply(search_url, max_jobs=max_jobs)
    else:
        print("\n🎯 LinkedIn Easy Apply Bot")
        print("─" * 40)
        search_url = input("LinkedIn search URL: ").strip()
        if not search_url:
            print("No URL provided.")
            sys.exit(1)
        max_jobs = input("Max jobs to apply to (default 20): ").strip()
        max_jobs = int(max_jobs) if max_jobs.isdigit() else 20
        run_bulk_apply(search_url, max_jobs=max_jobs)
